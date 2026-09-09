"""감사에서 확인한 데이터 보호 및 경로 계약을 실제 파일로 검증합니다."""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_rules_template.scripts.common import END_MARKER, START_MARKER, write_json
from agent_rules_template.scripts.sync import (
    LOCAL_METADATA,
    PROJECT_RULES_GUIDANCE,
    _staged_writes,
    main,
    sync,
    validate_bundle,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "repository_build", ROOT / "scripts/build_dist.py"
)
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix=".sync-regression-", dir=ROOT
        )
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.bundle = self.base / "bundle"
        self.bundle.mkdir()
        (self.bundle / "rules").mkdir()
        (self.bundle / "rules/a.md").write_bytes(b"original\n")
        self.project = self.base / "project"
        self.update_bundle("1.0")

    def update_bundle(self, version):
        (self.bundle / "AGENTS.md").write_text(
            f"{START_MARKER}\n{version}\n{END_MARKER}", encoding="utf-8"
        )
        BUILD.build_metadata(self.bundle)
        metadata = json.loads((self.bundle / "metadata.json").read_text())
        metadata["template_version"] = version
        write_json(self.bundle / "metadata.json", metadata)

    def snapshot(self):
        return {
            p.relative_to(self.project).as_posix(): p.read_bytes()
            for p in self.project.rglob("*")
            if p.is_file()
        }

    def test_new_install_creates_project_rules_guidance(self):
        sync(self.project, self.bundle)

        content = (self.project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(content.count(PROJECT_RULES_GUIDANCE), 1)
        self.assertLess(content.index("# Project Rules"), content.index(PROJECT_RULES_GUIDANCE))
        self.assertTrue(
            json.loads((self.project / LOCAL_METADATA).read_text())["project_rules_guidance_added"]
        )

    def test_markerless_migration_adds_guidance_and_preserves_existing_content(self):
        self.project.mkdir()
        original = "# 기존 규칙\r\n프로젝트 고유 내용\r\n"
        (self.project / "AGENTS.md").write_bytes(original.encode("utf-8"))

        sync(self.project, self.bundle)

        content = (self.project / "AGENTS.md").read_text(encoding="utf-8", newline="")
        self.assertIn(PROJECT_RULES_GUIDANCE, content)
        self.assertIn(original, content)
        self.assertLess(content.index(PROJECT_RULES_GUIDANCE), content.index(original))

    def test_existing_guidance_and_repeated_sync_do_not_duplicate_it(self):
        sync(self.project, self.bundle)
        agents = self.project / "AGENTS.md"
        agents.write_bytes(agents.read_bytes().replace(b"\n", b"\r\n"))
        local_path = self.project / LOCAL_METADATA
        local = json.loads(local_path.read_text())
        local.pop("project_rules_guidance_added")
        write_json(local_path, local)

        sync(self.project, self.bundle)
        sync(self.project, self.bundle)

        with agents.open(encoding="utf-8", newline="") as stream:
            content = stream.read()
        self.assertEqual(content.replace("\r\n", "\n").count(PROJECT_RULES_GUIDANCE), 1)

    def test_project_owned_guidance_is_not_restored_after_edit_or_deletion(self):
        sync(self.project, self.bundle)
        agents = self.project / "AGENTS.md"
        custom = "이 프로젝트의 안내 문구입니다."
        agents.write_text(
            agents.read_text(encoding="utf-8").replace(PROJECT_RULES_GUIDANCE, custom),
            encoding="utf-8",
        )

        sync(self.project, self.bundle, force=True)
        self.assertIn(custom, agents.read_text(encoding="utf-8"))
        self.assertNotIn(PROJECT_RULES_GUIDANCE, agents.read_text(encoding="utf-8"))

        agents.write_text(
            agents.read_text(encoding="utf-8").replace(custom, ""),
            encoding="utf-8",
        )
        sync(self.project, self.bundle, force=True)
        self.assertNotIn(custom, agents.read_text(encoding="utf-8"))
        self.assertNotIn(PROJECT_RULES_GUIDANCE, agents.read_text(encoding="utf-8"))

    def test_incomplete_local_baseline_never_overwrites_edits(self):
        sync(self.project, self.bundle)
        agents = self.project / "AGENTS.md"
        agents.write_bytes(agents.read_bytes().replace(b"1.0", b"USER"))
        local = self.project / LOCAL_METADATA
        original = json.loads(local.read_text())
        variants = [
            {},
            {**original, "managed_files": []},
            {**original, "managed_block": {"sha256": "bad"}},
            {**original, "managed_files": {"rules/a.md": {"type": "text"}}},
        ]
        variants += [
            {k: v for k, v in original.items() if k != missing}
            for missing in original
            if missing != "project_rules_guidance_added"
        ]
        for value in variants:
            for force in (False, True):
                with self.subTest(value=value, force=force):
                    write_json(local, value)
                    before = self.snapshot()
                    with self.assertRaises(ValueError):
                        sync(self.project, self.bundle, force=force)
                    self.assertEqual(before, self.snapshot())
        local.write_text("{broken")
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle)
        local.unlink()
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle)
        self.assertIn(b"USER", agents.read_bytes())

    def test_directory_conflict_force_is_preflighted(self):
        sync(self.project, self.bundle)
        target = self.project / "rules/a.md"
        target.unlink()
        target.mkdir()
        self.update_bundle("2.0")
        before = self.snapshot()
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle, force=True)
        self.assertEqual(before, self.snapshot())
        self.assertTrue(target.is_dir())

    def test_apply_failure_rolls_back_all_bytes_and_deletions(self):
        sync(self.project, self.bundle)
        (self.bundle / "rules/a.md").unlink()
        (self.bundle / "rules/new.md").write_bytes(b"new")
        self.update_bundle("2.0")
        before = self.snapshot()
        replace = os.replace
        for fail_at in (1, 2, 3):
            count = 0

            def fail_once(source, target, failure=fail_at):
                nonlocal count
                count += 1
                if count == failure:
                    raise OSError("주입된 디스크 실패")
                return replace(source, target)

            with patch(
                "agent_rules_template.scripts.sync.os.replace", side_effect=fail_once
            ):
                with self.assertRaises(OSError):
                    sync(self.project, self.bundle)
            self.assertEqual(before, self.snapshot())
        sync(self.project, self.bundle)
        self.assertFalse((self.project / "rules/a.md").exists())
        self.assertEqual(
            json.loads((self.project / LOCAL_METADATA).read_text())[
                "installed_version"
            ],
            "2.0",
        )

    def test_windows_staging_uses_each_destination_parent(self):
        first = self.project / "rules/a.md"
        second = self.project / "other/b.md"
        first.parent.mkdir(parents=True)
        second.parent.mkdir(parents=True)

        with patch("agent_rules_template.scripts.sync.IS_WINDOWS", True):
            with _staged_writes(
                self.project, {first: b"first", second: b"second"}, []
            ) as staged:
                self.assertEqual(staged[first].parent.parent, first.parent)
                self.assertEqual(staged[second].parent.parent, second.parent)
                self.assertEqual(staged[first].read_bytes(), b"first")
                self.assertEqual(staged[second].read_bytes(), b"second")

    def test_posix_staging_remains_single_private_project_directory(self):
        first = self.project / "rules/a.md"
        second = self.project / "other/b.md"
        self.project.mkdir()

        with patch("agent_rules_template.scripts.sync.IS_WINDOWS", False):
            with _staged_writes(
                self.project, {first: b"first", second: b"second"}, []
            ) as staged:
                self.assertEqual(staged[first].parent, staged[second].parent)
                self.assertEqual(staged[first].parent.parent, self.project)

    @unittest.skipUnless(os.name == "nt", "Windows ACL regression")
    def test_windows_install_and_update_inherit_managed_file_acl(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell is None:
            self.skipTest("PowerShell is required for the Windows ACL assertion")

        def acl(path):
            environment = {**os.environ, "AGENT_RULES_ACL_TARGET": str(path)}
            command = (
                "$value = Get-Acl -LiteralPath $env:AGENT_RULES_ACL_TARGET; "
                "[pscustomobject]@{Protected=$value.AreAccessRulesProtected; "
                "Inherited=@($value.Access | ForEach-Object {$_.IsInherited})} "
                "| ConvertTo-Json -Compress"
            )
            result = subprocess.run(
                [shell, "-NoProfile", "-Command", command],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8-sig",
                env=environment,
            )
            return json.loads(result.stdout)

        sync(self.project, self.bundle)
        target = self.project / "rules/a.md"
        for phase in ("install", "update"):
            with self.subTest(phase=phase):
                information = acl(target)
                self.assertFalse(information["Protected"])
                self.assertTrue(information["Inherited"])
                self.assertTrue(all(information["Inherited"]))
            if phase == "install":
                (self.bundle / "rules/a.md").write_bytes(b"updated\n")
                self.update_bundle("2.0")
                sync(self.project, self.bundle)

    def test_nfd_bundle_rejected_and_nested_names_included(self):
        for name in ("AGENTS.md", "metadata.json", "é.md"):
            (self.bundle / "rules" / name).write_text("nested")
        BUILD.build_metadata(self.bundle)
        metadata = validate_bundle(self.bundle)
        self.assertTrue(
            {"rules/AGENTS.md", "rules/metadata.json", "rules/é.md"}
            <= metadata["managed_files"].keys()
        )
        (self.bundle / "rules/e\u0301.md").write_text("NFD")
        with self.assertRaises(ValueError):
            BUILD.build_metadata(self.bundle)
        with self.assertRaises(ValueError):
            validate_bundle(self.bundle)

    def test_metadata_keys_use_platform_independent_ordinal_order(self):
        skill_dir = self.bundle / ".agents/skills/example"
        (skill_dir / "scripts").mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("skill", encoding="utf-8")
        (skill_dir / "scripts/run.py").write_text("script", encoding="utf-8")

        BUILD.build_metadata(self.bundle)

        metadata = json.loads(
            (self.bundle / "metadata.json").read_text(encoding="utf-8")
        )
        managed_paths = list(metadata["managed_files"])
        self.assertEqual(managed_paths, sorted(managed_paths))

    def test_nfd_consumer_lookup_and_collision(self):
        (self.bundle / "rules/é.md").write_text("upstream")
        self.update_bundle("1.0")
        sync(self.project, self.bundle)
        nfc = self.project / "rules/é.md"
        nfd = self.project / "rules/e\u0301.md"
        nfc.rename(nfd)
        self.update_bundle("2.0")
        sync(self.project, self.bundle)
        self.assertTrue(nfd.exists())
        self.assertFalse(nfc.exists())
        nfc.write_text("owned")
        before = self.snapshot()
        for force in (False, True):
            with self.assertRaisesRegex(ValueError, "collision"):
                sync(self.project, self.bundle, force=force)
            self.assertEqual(before, self.snapshot())

    def test_nfd_source_fails_before_replacing_bundle(self):
        source = self.base / "source"
        source.mkdir()
        (source / "e\u0301.md").write_text("NFD")
        before = (self.bundle / "AGENTS.md").read_bytes()
        with patch.object(BUILD, "RULES_DIR", source):
            with self.assertRaises(ValueError):
                BUILD.build_dist(self.bundle)
        self.assertEqual(before, (self.bundle / "AGENTS.md").read_bytes())

    def test_build_rejects_missing_core_and_unknown_rule_categories(self):
        source = self.base / "rules"
        core = source / "core"
        core.mkdir(parents=True)
        for name in BUILD.REQUIRED_CORE_FILES - {"03-integrity.md"}:
            (core / name).write_text(name, encoding="utf-8")
        for name in BUILD.CATEGORY_METADATA:
            (source / name).mkdir()

        with self.assertRaisesRegex(ValueError, "03-integrity.md"):
            BUILD.validate_source_layout(source)

        (core / "03-integrity.md").write_text("required", encoding="utf-8")
        (source / "unpackaged").mkdir()
        with self.assertRaisesRegex(ValueError, "unpackaged"):
            BUILD.validate_source_layout(source)

    def test_template_version_fails_closed(self):
        agents = self.base / "AGENTS.md"
        agents.write_text("# no version", encoding="utf-8")
        with patch.object(BUILD, "PROJECT_ROOT", self.base):
            with self.assertRaisesRegex(ValueError, "Version"):
                BUILD.template_version()

        agents.write_text("**Version**: invalid |", encoding="utf-8")
        with patch.object(BUILD, "PROJECT_ROOT", self.base):
            with self.assertRaisesRegex(ValueError, "SemVer"):
                BUILD.template_version()

    def test_replace_repairs_markers_but_not_file_modifications(self):
        sync(self.project, self.bundle)
        agents = self.project / "AGENTS.md"
        agents.write_text(END_MARKER)
        sync(self.project, self.bundle, replace=True)
        self.assertIn(START_MARKER, agents.read_text())
        agents.write_text(END_MARKER)
        (self.project / "rules/a.md").write_text("changed")
        before = self.snapshot()
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle, replace=True)
        self.assertEqual(before, self.snapshot())
        sync(self.project, self.bundle, replace=True, force=True)
        self.assertEqual((self.project / "rules/a.md").read_bytes(), b"original\n")

    def test_all_options_preserve_unowned_files(self):
        target = self.project / "rules/a.md"
        target.parent.mkdir(parents=True)
        target.write_text("owned")
        for force in (False, True):
            for replace in (False, True):
                with self.assertRaises(ValueError):
                    sync(self.project, self.bundle, force, replace)
                self.assertEqual(target.read_text(), "owned")

    def test_identical_legacy_files_are_adopted_without_force(self):
        target = self.project / "rules/a.md"
        target.parent.mkdir(parents=True)
        target.write_bytes((self.bundle / "rules/a.md").read_bytes())

        sync(self.project, self.bundle)

        local = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(
            local["managed_files"]["rules/a.md"],
            json.loads((self.bundle / "metadata.json").read_text())["managed_files"][
                "rules/a.md"
            ],
        )

    def test_multiple_identical_legacy_files_are_adopted(self):
        (self.bundle / "rules/b.md").write_bytes(b"second\n")
        self.update_bundle("1.0")
        for raw in json.loads((self.bundle / "metadata.json").read_text())["managed_files"]:
            target = self.project / raw
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((self.bundle / raw).read_bytes())

        sync(self.project, self.bundle)

        local = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(
            set(local["managed_files"]),
            set(json.loads((self.bundle / "metadata.json").read_text())["managed_files"]),
        )

    def test_adopted_file_detects_changes_and_force_restores_it(self):
        target = self.project / "rules/a.md"
        target.parent.mkdir(parents=True)
        target.write_bytes((self.bundle / "rules/a.md").read_bytes())
        sync(self.project, self.bundle)
        target.write_text("local change")

        with self.assertRaisesRegex(ValueError, "Local modifications"):
            sync(self.project, self.bundle)
        sync(self.project, self.bundle, force=True)

        self.assertEqual(target.read_bytes(), b"original\n")

    def test_adoption_and_conflict_mixture_makes_no_changes(self):
        (self.bundle / "rules/b.md").write_bytes(b"second\n")
        self.update_bundle("1.0")
        adopted = self.project / "rules/a.md"
        adopted.parent.mkdir(parents=True)
        adopted.write_bytes((self.bundle / "rules/a.md").read_bytes())
        conflict = self.project / "rules/b.md"
        conflict.write_text("project-owned")
        before = self.snapshot()

        with self.assertRaisesRegex(ValueError, "rules/b.md"):
            sync(self.project, self.bundle)

        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.project / LOCAL_METADATA).exists())

    def test_all_project_owned_conflicts_are_sorted_and_reported(self):
        for name in ("b.md", "c.md"):
            (self.bundle / "rules" / name).write_text(name)
        self.update_bundle("1.0")
        for raw in ("rules/c.md", "rules/a.md", "rules/b.md"):
            target = self.project / raw
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("project-owned")

        with self.assertRaises(ValueError) as context:
            sync(self.project, self.bundle, force=True, replace=True)

        self.assertEqual(
            str(context.exception),
            "Project-owned 파일과 충돌합니다:\n- rules/a.md\n- rules/b.md\n- rules/c.md",
        )

    def test_symlink_targets_are_rejected(self):
        outside = self.base / "outside"
        outside.write_bytes(b"outside")
        self.project.mkdir()
        for raw in ("AGENTS.md", LOCAL_METADATA, "rules/a.md"):
            target = self.project / raw
            target.parent.mkdir(exist_ok=True)
            try:
                target.symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlink 생성 권한 없음: {error}")
            try:
                with self.assertRaises(ValueError):
                    sync(self.project, self.bundle, force=True, replace=True)
                self.assertEqual(outside.read_bytes(), b"outside")
            finally:
                target.unlink()

    def test_cross_platform_unsafe_paths_and_schema_are_rejected(self):
        original = json.loads((self.bundle / "metadata.json").read_text())
        for raw in (
            "../victim",
            "/absolute",
            "C:/absolute",
            "C:relative",
            "rules/../../outside",
            "rules\\file",
        ):
            value = {
                **original,
                "managed_files": {raw: next(iter(original["managed_files"].values()))},
            }
            write_json(self.bundle / "metadata.json", value)
            with self.assertRaises(ValueError):
                sync(self.project, self.bundle)
        for field, value in (("schema_version", 99), ("hash_policy", {})):
            write_json(self.bundle / "metadata.json", {**original, field: value})
            with self.assertRaises(ValueError):
                sync(self.project, self.bundle)

    def test_orphan_directory_prompt_yes_deletes_directory_and_files(self):
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)
        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        with patch("sys.stdin.isatty", return_value=True), patch("builtins.input", return_value="y"):
            sync(self.project, self.bundle)

        self.assertFalse((self.project / ".agents/skills/handoff").exists())
        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "3.0")
        self.assertNotIn(".agents/skills/handoff/SKILL.md", metadata["managed_files"])

    def test_orphan_directory_prompt_no_keeps_directory_and_files_as_project_owned(self):
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)
        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        with patch("sys.stdin.isatty", return_value=True), patch("builtins.input", return_value="n"):
            sync(self.project, self.bundle)

        # File and directory must remain intact
        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())
        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "3.0")
        # Must no longer be in managed_files
        self.assertNotIn(".agents/skills/handoff/SKILL.md", metadata["managed_files"])

        # Modifying the kept project-owned file must NOT raise Local modifications detected on next sync
        (self.project / ".agents/skills/handoff/SKILL.md").write_bytes(b"user custom content\n")
        sync(self.project, self.bundle)

    def test_orphan_directory_clean_orphans_flag_deletes_without_prompt(self):
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        with patch("builtins.input", side_effect=AssertionError("input should not be called")):
            sync(self.project, self.bundle, clean_orphans=True)

        self.assertFalse((self.project / ".agents/skills/handoff").exists())

    def test_orphan_directory_keep_orphans_flag_keeps_without_prompt(self):
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        with patch("builtins.input", side_effect=AssertionError("input should not be called")):
            sync(self.project, self.bundle, clean_orphans=False)

        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())

    def test_orphan_directory_non_tty_defaults_to_keep(self):
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        with patch("sys.stdin.isatty", return_value=False), patch(
            "builtins.input", side_effect=AssertionError("input should not be called")
        ):
            sync(self.project, self.bundle)

        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())

    def test_orphan_directory_cli_main_flags(self):
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        # Mutually exclusive options error
        with patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                main(["--clean-orphans", "--keep-orphans"])

        # main with -y should clean orphans
        code = main([
            "--project", str(self.project),
            "--bundle", str(self.bundle),
            "-y",
        ])
        self.assertEqual(code, 0)
        self.assertFalse((self.project / ".agents/skills/handoff").exists())

    def test_orphan_transaction_failure_before_commit_rolls_back(self):
        """Test A: 트랜잭션 커밋 전 실패 시 orphan 디렉터리가 100% 온전하게 원위치로 롤백되고 이전 baseline이 유지되어야 합니다."""
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        (self.bundle / "rules/a.md").write_bytes(b"updated rule\n")
        self.update_bundle("3.0")

        before = self.snapshot()

        # 설치 결과 검증 실패를 주입하여 commit 직전 롤백 유발
        with patch(
            "agent_rules_template.scripts.sync.managed_block_hash",
            side_effect=RuntimeError("결과 검증 실패 주입"),
        ):
            with self.assertRaises(RuntimeError):
                sync(self.project, self.bundle, clean_orphans=True)

        self.assertEqual(before, self.snapshot())
        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())
        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "2.0")
        self.assertIn(".agents/skills/handoff/SKILL.md", metadata["managed_files"])

        # staging 임시 디렉터리가 남아있지 않아야 함
        staged_residues = list((self.project / ".agents/skills").glob(".agent-rules-orphan-*"))
        self.assertEqual(staged_residues, [])

        # 실패 주입 해제 후 다음 sync에서 정상 감지 및 삭제됨
        sync(self.project, self.bundle, clean_orphans=True)
        self.assertFalse((self.project / ".agents/skills/handoff").exists())
        after_metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(after_metadata["installed_version"], "3.0")
        self.assertEqual((self.project / "rules/a.md").read_bytes(), b"updated rule\n")

    def test_orphan_clean_semantics_consistency_with_local_edits(self):
        """Test B: orphan directory 내부 수정 시 interactive y, --clean-orphans, -y 모두 삭제 승인으로 일관되게 동작해야 합니다."""
        for method in ("prompt_y", "flag_clean", "cli_yes"):
            # 매 회차 독립된 프로젝트 설정
            subproject = self.base / f"project_{method}"
            sync(subproject, self.bundle)

            skill_dir = self.bundle / ".agents/skills/handoff"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
            self.update_bundle("2.0")
            sync(subproject, self.bundle)

            # orphan 내부 former-managed 파일 로컬 수정
            (subproject / ".agents/skills/handoff/SKILL.md").write_bytes(b"locally modified\n")

            shutil.rmtree(skill_dir)
            self.update_bundle("3.0")

            if method == "prompt_y":
                with patch("sys.stdin.isatty", return_value=True), patch("builtins.input", return_value="y"):
                    sync(subproject, self.bundle)
            elif method == "flag_clean":
                sync(subproject, self.bundle, clean_orphans=True)
            elif method == "cli_yes":
                code = main([
                    "--project", str(subproject),
                    "--bundle", str(self.bundle),
                    "-y",
                ])
                self.assertEqual(code, 0)

            self.assertFalse((subproject / ".agents/skills/handoff").exists())
            metadata = json.loads((subproject / LOCAL_METADATA).read_text())
            self.assertEqual(metadata["installed_version"], "3.0")

        # keep 방식들: prompt_n, flag_keep, non_tty
        for keep_method in ("prompt_n", "flag_keep", "non_tty"):
            subproject = self.base / f"project_keep_{keep_method}"
            sync(subproject, self.bundle)

            skill_dir = self.bundle / ".agents/skills/handoff"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
            self.update_bundle("2.0")
            sync(subproject, self.bundle)

            (subproject / ".agents/skills/handoff/SKILL.md").write_bytes(b"locally modified\n")

            shutil.rmtree(skill_dir)
            self.update_bundle("3.0")

            if keep_method == "prompt_n":
                with patch("sys.stdin.isatty", return_value=True), patch("builtins.input", return_value="n"):
                    sync(subproject, self.bundle)
            elif keep_method == "flag_keep":
                sync(subproject, self.bundle, clean_orphans=False)
            elif keep_method == "non_tty":
                with patch("sys.stdin.isatty", return_value=False), patch(
                    "builtins.input", side_effect=AssertionError("input should not be called")
                ):
                    sync(subproject, self.bundle)

            self.assertTrue((subproject / ".agents/skills/handoff/SKILL.md").is_file())
            metadata = json.loads((subproject / LOCAL_METADATA).read_text())
            self.assertEqual(metadata["installed_version"], "3.0")
            self.assertNotIn(".agents/skills/handoff/SKILL.md", metadata["managed_files"])

            # Project-owned로 전환되었으므로 다음 sync에서도 로컬 수정 오류 없음
            sync(subproject, self.bundle)

    def test_orphan_directory_with_user_added_files(self):
        """Test C: orphan directory 내에 former-managed 파일과 user-added 파일이 공존할 때의 clean/keep 계약 검증."""
        # 1. clean 승인 시 전체 디렉터리(user-added 포함) 삭제
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        # 사용자 추가 파일 생성
        (self.project / ".agents/skills/handoff/user_note.txt").write_bytes(b"user note\n")
        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        sync(self.project, self.bundle, clean_orphans=True)
        self.assertFalse((self.project / ".agents/skills/handoff").exists())

        # 2. keep 선택 시 둘 다 보존 & former-managed는 baseline에서 제거
        subproject = self.base / "project_user_files_keep"
        sync(subproject, self.bundle)
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(subproject, self.bundle)

        (subproject / ".agents/skills/handoff/user_note.txt").write_bytes(b"user note\n")
        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        sync(subproject, self.bundle, clean_orphans=False)
        self.assertTrue((subproject / ".agents/skills/handoff/SKILL.md").is_file())
        self.assertTrue((subproject / ".agents/skills/handoff/user_note.txt").is_file())
        metadata = json.loads((subproject / LOCAL_METADATA).read_text())
        self.assertNotIn(".agents/skills/handoff/SKILL.md", metadata["managed_files"])

    def test_unrelated_modifications_protected_during_orphan_clean(self):
        """Test D: orphan directory 삭제 승인 중에도 orphan 외부의 managed 파일 수정은 보호되어야 합니다."""
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        # 무관한 관리 파일 rules/a.md 수정
        (self.project / "rules/a.md").write_bytes(b"unrelated modified\n")

        with self.assertRaises(ValueError) as ctx:
            sync(self.project, self.bundle, clean_orphans=True)
        self.assertIn("Local modifications detected", str(ctx.exception))
        self.assertIn("rules/a.md", str(ctx.exception))

        # main with -y 도 무관한 수정 앞에서는 실패해야 함
        with patch("sys.stderr"):
            code = main([
                "--project", str(self.project),
                "--bundle", str(self.bundle),
                "-y",
            ])
        self.assertEqual(code, 1)
        self.assertTrue((self.project / ".agents/skills/handoff/SKILL.md").is_file())
        self.assertEqual((self.project / "rules/a.md").read_bytes(), b"unrelated modified\n")

    def test_orphan_rmtree_immediate_failure_keeps_committed_sync(self):
        """Test B: post-commit rmtree 즉시 실패 시 sync 성공 상태를 유지하고 잔여 임시 디렉터리를 warning으로 안내해야 합니다."""
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        (self.bundle / "rules/a.md").write_bytes(b"updated rule\n")
        self.update_bundle("3.0")

        real_rmtree = shutil.rmtree

        def fail_on_orphan(target_path, *args, **kwargs):
            if ".agent-rules-orphan-" in Path(target_path).name:
                raise OSError("디스크 에러 주입")
            return real_rmtree(target_path, *args, **kwargs)

        stderr_buf = io.StringIO()
        with patch("shutil.rmtree", side_effect=fail_on_orphan), patch("sys.stderr", stderr_buf):
            sync(self.project, self.bundle, clean_orphans=True)

        # 1. 원래 경로는 제거되었고 sync 결과는 정상 커밋됨
        self.assertFalse((self.project / ".agents/skills/handoff").exists())
        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "3.0")
        self.assertEqual((self.project / "rules/a.md").read_bytes(), b"updated rule\n")

        # 2. 임시 staging 경로가 residue로 남아있고 warning 출력됨
        staged_residues = list((self.project / ".agents/skills").glob(".agent-rules-orphan-*"))
        self.assertEqual(len(staged_residues), 1)
        self.assertIn("WARNING:", stderr_buf.getvalue())
        self.assertIn(str(staged_residues[0]), stderr_buf.getvalue())

    def test_orphan_partial_rmtree_failure_preserves_committed_sync(self):
        """Test C: rmtree 도중 일부 파일만 삭제되고 실패하더라도 sync를 롤백하지 않고 원래 경로를 재생성하지 않아야 합니다."""
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        # orphan 디렉터리에 여러 파일 생성
        (self.project / ".agents/skills/handoff/first.txt").write_bytes(b"first\n")
        (self.project / ".agents/skills/handoff/second.txt").write_bytes(b"second\n")
        (self.project / ".agents/skills/handoff/third.txt").write_bytes(b"third\n")

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        real_rmtree = shutil.rmtree

        # partial deletion 시뮬레이션: first.txt 삭제 후 OSError 발생
        def partial_rmtree(target_path, *args, **kwargs):
            p = Path(target_path)
            if ".agent-rules-orphan-" in p.name:
                f = p / "first.txt"
                if f.exists():
                    f.unlink()
                raise OSError("잠긴 파일(second.txt)로 인한 삭제 실패")
            return real_rmtree(target_path, *args, **kwargs)

        stderr_buf = io.StringIO()
        with patch("shutil.rmtree", side_effect=partial_rmtree), patch("sys.stderr", stderr_buf):
            sync(self.project, self.bundle, clean_orphans=True)

        # 원래 경로는 재생성되지 않음 (broken state 원위치 롤백 없음)
        self.assertFalse((self.project / ".agents/skills/handoff").exists())
        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "3.0")

        # staged 임시 디렉터리에 first.txt는 없고 second.txt, third.txt 잔여
        staged_residues = list((self.project / ".agents/skills").glob(".agent-rules-orphan-*"))
        self.assertEqual(len(staged_residues), 1)
        residue = staged_residues[0]
        self.assertFalse((residue / "first.txt").exists())
        self.assertTrue((residue / "second.txt").is_file())
        self.assertTrue((residue / "third.txt").is_file())
        self.assertIn("WARNING:", stderr_buf.getvalue())
        self.assertIn(str(residue), stderr_buf.getvalue())

    def test_multiple_orphans_partial_cleanup(self):
        """Test D: 복수의 orphan 중 하나는 삭제 성공하고 다른 하나는 실패하더라도, 전체 sync를 롤백하지 않아야 합니다."""
        sync(self.project, self.bundle)
        skill_dir_a = self.bundle / ".agents/skills/orphan_a"
        skill_dir_b = self.bundle / ".agents/skills/orphan_b"
        skill_dir_a.mkdir(parents=True)
        skill_dir_b.mkdir(parents=True)
        (skill_dir_a / "SKILL.md").write_bytes(b"a\n")
        (skill_dir_b / "SKILL.md").write_bytes(b"b\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir_a)
        shutil.rmtree(skill_dir_b)
        self.update_bundle("3.0")

        real_rmtree = shutil.rmtree

        def rmtree_fail_on_b(target_path, *args, **kwargs):
            p = Path(target_path)
            if "orphan_b" in p.name:
                raise OSError("orphan_b 삭제 권한 없음")
            return real_rmtree(target_path, *args, **kwargs)

        stderr_buf = io.StringIO()
        with patch("shutil.rmtree", side_effect=rmtree_fail_on_b), patch("sys.stderr", stderr_buf):
            sync(self.project, self.bundle, clean_orphans=True)

        # 둘 다 원래 경로는 제거됨
        self.assertFalse((self.project / ".agents/skills/orphan_a").exists())
        self.assertFalse((self.project / ".agents/skills/orphan_b").exists())
        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "3.0")

        # orphan_a residue는 없고 orphan_b residue만 남음
        residues = list((self.project / ".agents/skills").glob(".agent-rules-orphan-*"))
        self.assertEqual(len(residues), 1)
        self.assertIn("orphan_b", residues[0].name)
        self.assertIn(str(residues[0]), stderr_buf.getvalue())

    def test_cleanup_residue_does_not_affect_subsequent_sync(self):
        """Test E: post-commit cleanup 잔여물이 존재하는 상태에서도 다음 일반 sync가 오염되지 않고 정상 동작해야 합니다."""
        sync(self.project, self.bundle)
        skill_dir = self.bundle / ".agents/skills/handoff"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_bytes(b"skill content\n")
        self.update_bundle("2.0")
        sync(self.project, self.bundle)

        shutil.rmtree(skill_dir)
        self.update_bundle("3.0")

        real_rmtree = shutil.rmtree

        def fail_on_orphan(target_path, *args, **kwargs):
            if ".agent-rules-orphan-" in Path(target_path).name:
                raise OSError("임시 잔여물 생성용")
            return real_rmtree(target_path, *args, **kwargs)

        # post-commit 실패 유발하여 residue 남김
        with patch("shutil.rmtree", side_effect=fail_on_orphan):
            with patch("sys.stderr"):
                sync(self.project, self.bundle, clean_orphans=True)

        residues = list((self.project / ".agents/skills").glob(".agent-rules-orphan-*"))
        self.assertEqual(len(residues), 1)

        # 다음 4.0 업데이트 실행 (새 번들)
        (self.bundle / "rules/new_rule.md").write_bytes(b"new rule 4.0\n")
        self.update_bundle("4.0")

        # 일반 sync가 잔여물 때문에 conflict 또는 orphan 오인 없이 정상 성공해야 함
        sync(self.project, self.bundle)

        metadata = json.loads((self.project / LOCAL_METADATA).read_text())
        self.assertEqual(metadata["installed_version"], "4.0")
        self.assertTrue((self.project / "rules/new_rule.md").is_file())
        self.assertNotIn(str(residues[0]), metadata["managed_files"])



