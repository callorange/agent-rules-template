from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_rules_template.scripts.common import (
    canonical_text_bytes,
    file_record,
    write_json,
)
from agent_rules_template.scripts.sync import LOCAL_METADATA, sync, validate_bundle


class SyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = ROOT / ".sync-test-work" / self.id().rsplit(".", 1)[-1]
        if self.base.exists():
            shutil.rmtree(self.base)
        self.base.mkdir(parents=True)
        self.bundle = self.base / "bundle"
        shutil.copytree(ROOT / "agent_rules_template" / "bundle", self.bundle)
        self.project = self.base / "project"

    def tearDown(self) -> None:
        shutil.rmtree(self.base)

    def metadata(self):
        return json.loads((self.bundle / "metadata.json").read_text(encoding="utf-8"))

    def test_new_install_and_migration(self) -> None:
        self.project.mkdir()
        (self.project / "AGENTS.md").write_bytes(b"# Existing\r\nKeep\r\n")
        sync(self.project, self.bundle)
        self.assertIn("Keep", (self.project / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertTrue((self.project / LOCAL_METADATA).exists())

    def test_new_managed_path_collision_is_never_overwritten(self) -> None:
        raw = next(iter(self.metadata()["managed_files"]))
        target = self.project / raw
        target.parent.mkdir(parents=True)
        target.write_text("owned\n")
        for force in (False, True):
            with self.assertRaisesRegex(ValueError, "Project-owned"):
                sync(self.project, self.bundle, force=force)
        self.assertEqual(target.read_text(), "owned\n")

    def test_traversal_and_absolute_paths_are_rejected(self) -> None:
        metadata = self.metadata()
        raw = next(iter(metadata["managed_files"]))
        record = metadata["managed_files"].pop(raw)
        metadata["managed_files"]["../victim.md"] = record
        write_json(self.bundle / "metadata.json", metadata)
        with self.assertRaises(ValueError):
            validate_bundle(self.bundle)

    def test_malformed_metadata_rejected_before_write(self) -> None:
        metadata = self.metadata()
        metadata.pop("template_version")
        write_json(self.bundle / "metadata.json", metadata)
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle)
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_parent_file_conflict_has_no_partial_apply(self) -> None:
        self.project.mkdir()
        (self.project / "AGENTS.md").write_text("project\n")
        (self.project / "rules").write_text("file")
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle)
        self.assertEqual((self.project / "AGENTS.md").read_text(), "project\n")

    def test_update_force_replace_and_owned_files(self) -> None:
        sync(self.project, self.bundle)
        agents = self.project / "AGENTS.md"
        agents.write_text(agents.read_text() + "Project rule\r\n", newline="")
        raw = next(iter(self.metadata()["managed_files"]))
        target = self.project / raw
        target.write_text("changed\n")
        owned = self.project / "rules" / "project.md"
        owned.write_text("owned")
        with self.assertRaises(ValueError):
            sync(self.project, self.bundle, replace=True)
        sync(self.project, self.bundle, force=True)
        self.assertIn(b"Project rule\r\n", agents.read_bytes())
        self.assertEqual(owned.read_text(), "owned")
        sync(self.project, self.bundle, force=True, replace=True)
        self.assertNotIn("Project rule", agents.read_text())

    def test_text_nfc_bom_eol_and_binary_hash(self) -> None:
        self.assertEqual(
            canonical_text_bytes("café\r\n\r\n".encode()),
            canonical_text_bytes(b"\xef\xbb\xbfcafe\xcc\x81\n"),
        )
        binary = self.base / "binary.bin"
        binary.write_bytes(b"\0data\n")
        self.assertEqual(file_record(binary)["type"], "binary")

    def test_nested_names_are_managed(self) -> None:
        nested = self.bundle / "rules" / "AGENTS.md"
        nested.write_text("nested")
        metadata = self.metadata()
        metadata["managed_files"]["rules/AGENTS.md"] = file_record(nested)
        write_json(self.bundle / "metadata.json", metadata)
        validate_bundle(self.bundle)
        sync(self.project, self.bundle)
        self.assertTrue((self.project / "rules" / "AGENTS.md").exists())


class WheelTests(unittest.TestCase):
    def test_bundle_includes_agents_and_metadata_files(self) -> None:
        bundle = ROOT / "agent_rules_template" / "bundle"
        metadata = json.loads((bundle / "metadata.json").read_text())
        self.assertTrue((bundle / ".agents").is_dir())
        self.assertTrue(
            all((bundle / raw).is_file() for raw in metadata["managed_files"])
        )

    def test_built_wheel_contains_every_managed_file(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix=".wheel-regression-", dir=ROOT)
        output = Path(temporary.name)
        cache = output / "cache"
        try:
            environment = os.environ | {"UV_CACHE_DIR": str(cache)}
            result = subprocess.run(
                ["uv", "build", "--wheel", "--out-dir", str(output)],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode:
                self.fail(result.stderr)
            wheel = next(output.glob("*.whl"))
            metadata = json.loads(
                (ROOT / "agent_rules_template" / "bundle" / "metadata.json").read_text()
            )
            with zipfile.ZipFile(wheel) as archive:
                names = set(archive.namelist())
                bundle = ROOT / "agent_rules_template" / "bundle"
                for path in bundle.rglob("*"):
                    if path.is_file():
                        self.assertEqual(
                            archive.read(
                                "agent_rules_template/bundle/"
                                + path.relative_to(bundle).as_posix()
                            ),
                            path.read_bytes(),
                        )
                self.assertFalse(any(name.startswith("scripts/") for name in names))
            expected = {
                "agent_rules_template/bundle/AGENTS.md",
                "agent_rules_template/bundle/metadata.json",
            }
            expected |= {
                f"agent_rules_template/bundle/{path}"
                for path in metadata["managed_files"]
            }
            self.assertTrue(expected <= names)
            self.assertTrue(any("/bundle/.agents/" in name for name in names))
            consumer = output / "consumer"
            command = [
                "uvx",
                "--offline",
                "--python",
                sys.executable,
                "--from",
                str(wheel),
                "agent-rules",
            ]
            for arguments in (
                ["--help"],
                ["--project", str(consumer)],
                ["--project", str(consumer)],
            ):
                result = subprocess.run(
                    command + arguments,
                    cwd=output,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((consumer / LOCAL_METADATA).is_file())
        finally:
            temporary.cleanup()
