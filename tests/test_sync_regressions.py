"""감사에서 확인한 데이터 보호 및 경로 계약을 실제 파일로 검증합니다."""

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_rules_template.scripts.common import END_MARKER, START_MARKER, write_json
from agent_rules_template.scripts.sync import LOCAL_METADATA, sync, validate_bundle

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
            {k: v for k, v in original.items() if k != missing} for missing in original
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
