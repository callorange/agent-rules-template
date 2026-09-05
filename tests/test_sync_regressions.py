"""감사에서 확인한 데이터 보호 및 경로 계약을 실제 파일로 검증합니다."""

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_rules_template.scripts.common import END_MARKER, START_MARKER, write_json
from agent_rules_template.scripts.sync import (
    LOCAL_METADATA,
    PROJECT_RULES_GUIDANCE,
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
