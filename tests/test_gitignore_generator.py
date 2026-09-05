"""gitignore-generator의 기존 파일 보존 계약을 검증합니다."""

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/gitignore-generator/scripts/gitignore.sh"
START = b"# >>> gitignore-generator managed section start >>>"
END = b"# <<< gitignore-generator managed section end <<<"


@unittest.skipIf(sys.platform == "win32", "Bash 동작 검증은 Linux CI에서 실행합니다.")
class GitignoreGeneratorTests(unittest.TestCase):
    def test_bash_replaces_only_managed_block_and_preserves_crlf(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            fake_bin = base / "bin"
            fake_bin.mkdir()
            curl = fake_bin / "curl"
            curl.write_text("#!/usr/bin/env sh\nprintf '# generated rule\\n'\n", encoding="utf-8")
            curl.chmod(curl.stat().st_mode | stat.S_IXUSR)
            target = base / ".gitignore"
            target.write_bytes(
                b"custom-rule\r\n\r\n"
                + START
                + b"\r\nold-rule\r\n"
                + END
                + b"\r\nfooter-rule\r\n"
            )
            env = {**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]}

            for _ in range(2):
                subprocess.run(
                    ["bash", str(SCRIPT), "-t", "python", "-o", str(target), "-n"],
                    check=True,
                    env=env,
                    capture_output=True,
                    text=True,
                )

            content = target.read_bytes()

        self.assertIn(b"custom-rule\r\n", content)
        self.assertIn(b"footer-rule\r\n", content)
        self.assertNotIn(b"old-rule", content)
        self.assertEqual(content.count(START), 1)
        self.assertEqual(content.count(END), 1)
        self.assertNotIn(b"\n", content.replace(b"\r\n", b""))


if __name__ == "__main__":
    unittest.main()
