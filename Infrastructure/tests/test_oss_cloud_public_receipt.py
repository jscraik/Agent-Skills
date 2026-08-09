from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
EMITTER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/emit_oss_cloud_public_receipt.py"


class TestOssCloudPublicReceipt(unittest.TestCase):
    def test_emitter_accepts_only_value_blind_fields(self) -> None:
        completed = subprocess.run(
            [
                sys.executable, str(EMITTER), "--status", "blocked", "--auth-source",
                "1password_desktop_fifo", "--provider-invoked", "true", "--command-present",
                "true", "--exit-code", "1", "--duration-seconds", "1.25", "--findings",
                "oss_cloud_smoke_exit_nonzero", "--warnings", "codex_runtime_metadata_fallback",
                "--secret-status", "clear", "--json",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        emitted = json.loads(completed.stdout)
        self.assertEqual(emitted["status"], "blocked")
        self.assertEqual(emitted["findings"][0]["code"], "oss_cloud_smoke_exit_nonzero")
        self.assertEqual(emitted["warnings"][0]["code"], "codex_runtime_metadata_fallback")
        self.assertNotIn("/Users/", completed.stdout)


if __name__ == "__main__":
    unittest.main()
