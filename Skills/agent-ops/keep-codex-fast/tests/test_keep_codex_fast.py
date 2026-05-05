from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "keep_codex_fast.py"
spec = importlib.util.spec_from_file_location("keep_codex_fast", MODULE_PATH)
assert spec and spec.loader
keep_codex_fast = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = keep_codex_fast
spec.loader.exec_module(keep_codex_fast)


class KeepCodexFastTests(unittest.TestCase):
    def test_likely_subsystem_classifies_core_targets(self) -> None:
        self.assertEqual(
            keep_codex_fast.likely_subsystem(Path("logs_2.sqlite")),
            "codex_event_log_sqlite",
        )
        self.assertEqual(
            keep_codex_fast.likely_subsystem(Path("state_5.sqlite")),
            "codex_app_state_sqlite",
        )
        self.assertEqual(
            keep_codex_fast.likely_subsystem(Path("sessions/rollout.jsonl")),
            "codex_session_rollout_jsonl",
        )

    def test_report_is_read_only_and_bounded_on_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / ".codex"
            sessions = root / "sessions"
            sqlite_dir = root / "sqlite"
            sessions.mkdir(parents=True)
            sqlite_dir.mkdir()
            (sessions / "rollout.jsonl").write_text("{}\n", encoding="utf-8")
            (sqlite_dir / "logs_2.sqlite").write_bytes(b"not sqlite")

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = keep_codex_fast.main(
                    [
                    "report",
                    "--json",
                    "--codex-home",
                    str(root),
                    "--top-n",
                    "3",
                    "--max-files-per-target",
                    "100",
                    "--max-seconds-per-target",
                    "1",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertTrue((sessions / "rollout.jsonl").exists())
            self.assertTrue((sqlite_dir / "logs_2.sqlite").exists())


if __name__ == "__main__":
    unittest.main()
