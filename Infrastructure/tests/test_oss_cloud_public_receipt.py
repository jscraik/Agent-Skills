from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
EMITTER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/emit_oss_cloud_public_receipt.py"
SECRET_OUTPUT_SCANNER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/check_oss_cloud_secret_output.py"


class TestOssCloudPublicReceipt(unittest.TestCase):
    def test_emitter_accepts_only_value_blind_fields(self) -> None:
        completed = subprocess.run(
            [
                sys.executable, str(EMITTER), "--status", "blocked", "--auth-source",
                "1password_desktop_fifo", "--provider-invoked", "true", "--command-present",
                "true", "--exit-code", "1", "--duration-seconds", "1.25", "--findings",
                "oss_cloud_smoke_exit_nonzero,not_a_public_code", "--warnings", "codex_runtime_metadata_fallback",
                "--captured-output-scan", "passed", "--json",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        emitted = json.loads(completed.stdout)
        self.assertEqual(emitted["status"], "blocked")
        self.assertEqual(emitted["captured_output_scan"]["status"], "passed")
        self.assertTrue(emitted["captured_output_safe"])
        self.assertEqual(emitted["findings"][0]["code"], "oss_cloud_smoke_exit_nonzero")
        self.assertEqual(emitted["warnings"][0]["code"], "codex_runtime_metadata_fallback")
        self.assertNotIn("/Users/", completed.stdout)

    def test_basic_authorization_output_is_classified_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            captured = Path(temp_dir) / "stderr.txt"
            captured.write_text("Authorization: Basic redacted-test-value\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SECRET_OUTPUT_SCANNER), str(captured)],
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")

    def test_json_authorization_output_is_classified_without_echoing_it(self) -> None:
        for scheme in ("Basic", "Bearer"):
            with self.subTest(scheme=scheme), tempfile.TemporaryDirectory() as temp_dir:
                captured = Path(temp_dir) / "stderr.json"
                captured.write_text(
                    f'{{"Authorization": "{scheme} redacted-test-value"}}\n',
                    encoding="utf-8",
                )
                completed = subprocess.run(
                    [sys.executable, str(SECRET_OUTPUT_SCANNER), str(captured)],
                    check=False,
                    text=True,
                    capture_output=True,
                )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.stderr, "")

    def test_emitter_rejects_non_finite_or_negative_duration(self) -> None:
        for duration in ("nan", "inf", "-inf", "-0.01"):
            with self.subTest(duration=duration):
                completed = subprocess.run(
                    [
                        sys.executable, str(EMITTER), "--status", "blocked", "--auth-source",
                        "missing_or_invalid", "--provider-invoked", "false", "--command-present",
                        "false", f"--duration-seconds={duration}", "--captured-output-scan", "unavailable",
                    ],
                    check=False,
                    text=True,
                    capture_output=True,
                )

                self.assertEqual(completed.returncode, 2)
                self.assertIn("--duration-seconds must be finite and non-negative", completed.stderr)


if __name__ == "__main__":
    unittest.main()
