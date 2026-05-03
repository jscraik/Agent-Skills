#!/usr/bin/env python3
"""Smoke tests for keep-codex-fast using a fake Codex home."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "agent-ops" / "keep_codex_fast.py"


def load_module():
    spec = importlib.util.spec_from_file_location("keep_codex_fast", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["keep_codex_fast"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.codex_processes_running = lambda: module.ProcessCheck(True, [])
    module.report_codex_processes = lambda details=False: module.report("top_node_processes skipped_in_smoke")
    return module


def make_fake_home(root: Path) -> dict[str, Path]:
    codex_home = root / ".codex"
    sessions = codex_home / "sessions" / "2026" / "01" / "01"
    sessions.mkdir(parents=True)
    rollout = sessions / "rollout-2026-01-01T00-00-00-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa.jsonl"
    rollout.write_text('{"type":"test"}\n', encoding="utf-8")
    old_time = time.time() - 30 * 86400
    os.utime(rollout, (old_time, old_time))

    (codex_home / ".codex-global-state.json").write_text('{"pinned-thread-ids":[]}', encoding="utf-8")
    (codex_home / "config.toml").write_text(
        '[projects."C:\\\\DefinitelyMissingKeepCodexFast"]\ntrust_level = "trusted"\n',
        encoding="utf-8",
    )
    worktree = codex_home / "worktrees" / "oldtree"
    worktree.mkdir(parents=True)
    (worktree / "file.txt").write_text("x", encoding="utf-8")
    os.utime(worktree, (old_time, old_time))
    log_file = codex_home / "logs_2.sqlite"
    log_file.write_text("log", encoding="utf-8")

    state_db = codex_home / "state_5.sqlite"
    conn = sqlite3.connect(state_db)
    conn.execute(
        "create table threads ("
        "id text primary key, title text, rollout_path text, cwd text, "
        "updated_at integer, archived_at integer, archived integer)"
    )
    conn.execute(
        "insert into threads values (?,?,?,?,?,?,?)",
        (
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "Old test thread",
            str(rollout),
            r"\\?\C:\DefinitelyMissingKeepCodexFast",
            int(old_time),
            None,
            0,
        ),
    )
    conn.commit()
    conn.close()

    return {
        "codex_home": codex_home,
        "rollout": rollout,
        "worktree": worktree,
        "log_file": log_file,
        "state_db": state_db,
    }


def run_text(module, argv: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.run(module.parse_args(argv))
    return code, output.getvalue()


def assert_report_mode(module) -> None:
    with tempfile.TemporaryDirectory() as td:
        paths = make_fake_home(Path(td))
        code, text = run_text(
            module,
            ["report", "--codex-home", str(paths["codex_home"]), "--backup-root", str(Path(td) / "backup")],
        )
        assert code == 0
        assert paths["rollout"].exists()
        assert paths["worktree"].exists()
        assert paths["log_file"].exists()
        assert not (Path(td) / "backup").exists()
        assert "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" not in text
        assert "Old test thread" not in text
        assert str(paths["codex_home"]) not in text


def assert_apply_requires_confirmation(module) -> None:
    with tempfile.TemporaryDirectory() as td:
        paths = make_fake_home(Path(td))
        code, text = run_text(module, ["apply", "--codex-home", str(paths["codex_home"])])
        assert code == 2
        assert "apply_blocked confirmation_mismatch" in text
        assert paths["rollout"].exists()


def assert_apply_blocks_unverified_process_state(module) -> None:
    with tempfile.TemporaryDirectory() as td:
        paths = make_fake_home(Path(td))
        module.codex_processes_running = lambda: module.ProcessCheck(False, [], "ps denied")
        code, text = run_text(
            module,
            ["apply", "--codex-home", str(paths["codex_home"]), "--confirm-codex-home", str(paths["codex_home"])],
        )
        assert code == 2
        assert "apply_blocked process_detection_unavailable" in text
        assert paths["rollout"].exists()


def assert_apply_mode(module) -> None:
    with tempfile.TemporaryDirectory() as td:
        paths = make_fake_home(Path(td))
        backup = Path(td) / "backup"
        code, _text = run_text(
            module,
            [
                "apply",
                "--codex-home",
                str(paths["codex_home"]),
                "--confirm-codex-home",
                str(paths["codex_home"]),
                "--backup-root",
                str(backup),
                "--rotate-logs-above-mb",
                "0",
            ],
        )
        assert code == 0
        assert not paths["rollout"].exists()
        assert not paths["worktree"].exists()
        assert not paths["log_file"].exists()
        assert "DefinitelyMissingKeepCodexFast" in (paths["codex_home"] / "config.toml").read_text(encoding="utf-8")
        assert (backup / "restore-sessions.py").exists()
        assert (backup / "moved-sessions.jsonl").exists()
        assert (backup / "moved-worktrees.jsonl").exists()


def main() -> int:
    module = load_module()
    assert_report_mode(module)
    assert_apply_requires_confirmation(module)
    assert_apply_blocks_unverified_process_state(module)
    module = load_module()
    assert_apply_mode(module)
    print("keep-codex-fast smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
