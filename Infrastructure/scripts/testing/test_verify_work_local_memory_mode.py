"""Behavioral contract for the verify-work Local Memory preflight mode."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFY_WORK = REPO_ROOT / "Infrastructure/scripts/verify-work_impl.sh"


class VerifyWorkLocalMemoryModeTests(unittest.TestCase):
    def test_fast_verification_keeps_local_memory_optional(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scripts = root / "scripts"
            scripts.mkdir()
            log_path = root / "calls.log"
            (root / "CODESTYLE.md").touch()
            (root / "CONTRIBUTING.md").touch()
            (root / "Makefile").touch()
            (scripts / "codex-preflight-local-memory-legacy.sh").touch()
            (scripts / "verify-work.sh").touch()
            self._write_recorder(scripts / "codex-preflight.sh", "preflight")
            self._write_recorder(scripts / "validate-codestyle.sh", "codestyle")

            result = subprocess.run(
                ["bash", str(VERIFY_WORK), "--fast", "--repo-root", str(root)],
                capture_output=True,
                check=False,
                env={**os.environ, "VERIFY_WORK_CALL_LOG": str(log_path)},
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            calls = log_path.read_text(encoding="utf-8").splitlines()
            self.assertIn("preflight --stack repo --mode optional", calls[0])
            self.assertNotIn("--mode required", calls[0])
            self.assertTrue(calls[1].startswith("codestyle --repo-root "))

    @staticmethod
    def _write_recorder(path: Path, label: str) -> None:
        path.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f'printf "%s %s\\n" "{label}" "$*" >>"$VERIFY_WORK_CALL_LOG"\n',
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
