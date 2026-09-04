"""지원 Python 버전에서 sync의 파일 I/O 계약을 확인합니다."""

import tempfile
import unittest
from pathlib import Path

from agent_rules_template.scripts.sync import LOCAL_METADATA, sync

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "agent_rules_template" / "bundle"


class RuntimeCompatibilityTests(unittest.TestCase):
    """버전 matrix에서 실행할 최소 runtime 호환성 사례입니다."""

    def test_existing_agents_migration_preserves_crlf(self) -> None:
        """기존 AGENTS.md를 읽고 유지할 때 지원 API와 줄바꿈을 확인합니다."""
        with tempfile.TemporaryDirectory(prefix="agent-rules-runtime-") as temporary:
            project = Path(temporary)
            agents = project / "AGENTS.md"
            agents.write_bytes(b"# Existing\r\nProject rule\r\n")

            sync(project, BUNDLE)

            self.assertIn(b"Project rule\r\n", agents.read_bytes())
            self.assertTrue((project / LOCAL_METADATA).is_file())
