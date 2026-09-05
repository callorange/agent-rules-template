"""규칙 validator의 배포 계약 회귀를 검증합니다."""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "repository_rule_validator",
    ROOT / ".agents/skills/rule-validator/scripts/validate_rules.py",
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RuleValidatorTests(unittest.TestCase):
    def test_repository_source_layout_is_valid(self):
        self.assertEqual(VALIDATOR.check_source_layout(), [])

    def test_version_coherence_reports_each_mismatched_source(self):
        with tempfile.TemporaryDirectory(prefix=".validator-version-", dir=ROOT) as raw:
            project = Path(raw)
            bundle = project / "bundle"
            bundle.mkdir()
            (project / "AGENTS.md").write_text("**Version**: 3.0.0 |", encoding="utf-8")
            (project / "pyproject.toml").write_text(
                '[project]\nversion = "2.0.0"\n', encoding="utf-8"
            )
            (project / "README.md").write_text(
                "현재 버전은 **1.0.0**입니다.", encoding="utf-8"
            )
            (project / "CHANGELOG.md").write_text(
                "## [Unreleased]\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps({"template_version": "0.0.0"}), encoding="utf-8"
            )

            errors = VALIDATOR.check_version_coherence(project, bundle)

        self.assertEqual(len(errors), 4)
        self.assertTrue(any("pyproject.toml" in error for error in errors))
        self.assertTrue(any("README.md" in error for error in errors))
        self.assertTrue(any("metadata.json" in error for error in errors))
        self.assertTrue(any("CHANGELOG.md" in error for error in errors))

    def test_stale_bundle_is_a_validation_error(self):
        with tempfile.TemporaryDirectory() as raw:
            bundle = Path(raw) / "bundle"
            shutil.copytree(ROOT / "agent_rules_template/bundle", bundle)
            agents = bundle / "AGENTS.md"
            agents.write_bytes(agents.read_bytes() + b"stale\n")

            with patch.object(VALIDATOR, "BUNDLE_DIR", bundle):
                errors = VALIDATOR.check_dist_freshness()

        self.assertTrue(errors)
        self.assertTrue(any("일치하지 않습니다" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
