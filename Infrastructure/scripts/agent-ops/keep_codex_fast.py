#!/usr/bin/env python3
"""Report-first Codex local-state maintenance.

Default mode is read-only. Mutating modes require explicit confirmation.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


PROJECT_HEADER_RE = re.compile(r"^\[projects\.([\"'])(.+)\1\]\s*$")
TEMP_PROJECT_RE = re.compile(
    r"(\\AppData\\Local\\Temp\\|/AppData/Local/Temp/|\\Temp\\codex-|/Temp/codex-|\\Temp\\spark-|/Temp/spark-)",
    re.I,
)
BACKUP_NAMES = (
    ".codex-global-state.json",
    "config.toml",
    "history.jsonl",
    "installation_id",
    "models_cache.json",
    "session_index.jsonl",
    "version.json",
    "memories",
    "skills",
    "rules",
    "plugins",
    "automations",
)
IGNORED_BACKUP_DIRS = ("node_modules", ".git", ".next", "dist", "build", ".venv", "__pycache__", ".pytest_cache")


@dataclass(frozen=True)
class ProcessCheck:
    available: bool
    processes: list[str]
    error: str | None = None


@dataclass(frozen=True)
class SessionCandidate:
    size: int
    thread_id: str
    title: str
    source: Path
    relative: Path


def report(line: str) -> None:
    print(line)


def canonical_path(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=False)
    except OSError:
        return path.expanduser().absolute()


def codex_home_from_args(value: str | None) -> Path:
    if value:
        return canonical_path(Path(value))
    if os.environ.get("CODEX_HOME"):
        return canonical_path(Path(os.environ["CODEX_HOME"]))
    return Path.home() / ".codex"


def default_backup_parent() -> Path:
    docs = Path.home() / "Documents" / "Codex" / "codex-backups"
    return docs if docs.parent.exists() or platform.system() == "Windows" else Path.home() / ".codex" / "backups"


def format_size(size: int, unit: str) -> str:
    divisor = 1024 * 1024 * 1024 if unit == "gb" else 1024 * 1024
    precision = 3 if unit == "gb" else 1
    return f"{size / divisor:.{precision}f}"


def size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def sqlite_connect(path: Path, readonly: bool) -> sqlite3.Connection:
    if readonly:
        return sqlite3.connect(f"{canonical_path(path).as_uri()}?mode=ro", uri=True)
    return sqlite3.connect(path)


def codex_processes_running() -> ProcessCheck:
    try:
        if platform.system() == "Windows":
            command = (
                "Get-CimInstance Win32_Process | "
                "Select-Object Name,ProcessId,CommandLine | ConvertTo-Json -Compress"
            )
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", command],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            rows = json.loads(output) if output.strip() else []
            data = rows if isinstance(rows, list) else [rows]
            hits = [
                f"{row.get('ProcessId')} {row.get('Name')}"
                for row in data
                if str(row.get("Name") or "").lower() == "codex.exe"
            ]
            return ProcessCheck(True, hits)
        output = subprocess.check_output(["ps", "-axo", "pid=,comm=,args="], text=True)
        hits = [
            line.strip()
            for line in output.splitlines()
            if "codex" in line.lower()
            and ("app-server" in line.lower() or "openai.codex" in line.lower() or "codex desktop" in line.lower())
        ]
        return ProcessCheck(True, hits)
    except Exception as exc:
        return ProcessCheck(False, [], str(exc))


def wait_for_codex_exit() -> ProcessCheck:
    check = codex_processes_running()
    while check.available and check.processes:
        time.sleep(2)
        check = codex_processes_running()
    return check


def copy_if_exists(source: Path, dest: Path) -> None:
    if not source.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, dest, ignore=shutil.ignore_patterns(*IGNORED_BACKUP_DIRS), dirs_exist_ok=True)
    else:
        shutil.copy2(source, dest)
    report(f"backed_up {source.name}")


def backup_metadata(codex_home: Path, backup_root: Path) -> None:
    backup_root.mkdir(parents=True, exist_ok=True)
    for name in BACKUP_NAMES:
        copy_if_exists(codex_home / name, backup_root / name)
    state_db = codex_home / "state_5.sqlite"
    if state_db.exists():
        source = sqlite_connect(state_db, readonly=True)
        target = sqlite3.connect(backup_root / "state_5.sqlite")
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()


def normalize_extended_path(value: str) -> str:
    if value.startswith("\\\\?\\UNC\\"):
        return "\\\\" + value[8:]
    return value[4:] if value.startswith("\\\\?\\") else value


def normalize_sqlite_paths(conn: sqlite3.Connection, apply: bool) -> int:
    total = 0
    tables = conn.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall()
    for (table,) in tables:
        text_columns = [
            col[1]
            for col in conn.execute(f'pragma table_info("{table}")').fetchall()
            if "TEXT" in (col[2] or "").upper() or col[2] == ""
        ]
        for column in text_columns:
            rows = conn.execute(
                f'select rowid, "{column}" from "{table}" where "{column}" like ?',
                ("\\\\?\\%",),
            ).fetchall()
            changed = [
                (rowid, value)
                for rowid, value in rows
                if isinstance(value, str) and value.startswith("\\\\?\\")
            ]
            if not changed:
                continue
            total += len(changed)
            report(f"extended_paths {table}.{column} {len(changed)}")
            if apply:
                conn.executemany(
                    f'update "{table}" set "{column}"=? where rowid=?',
                    [(normalize_extended_path(value), rowid) for rowid, value in changed],
                )
    if total == 0:
        report("extended_paths 0")
    return total


def load_pinned(codex_home: Path) -> set[str]:
    try:
        data = json.loads((codex_home / ".codex-global-state.json").read_text(encoding="utf-8"))
        return set(data.get("pinned-thread-ids", []))
    except Exception:
        return set()


def active_session_candidates(conn: sqlite3.Connection, codex_home: Path, days: int) -> list[SessionCandidate]:
    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
    sessions_root = canonical_path(codex_home / "sessions")
    pinned = load_pinned(codex_home)
    try:
        rows = conn.execute(
            "select id, title, rollout_path, updated_at from threads where archived_at is null"
        ).fetchall()
    except sqlite3.Error as exc:
        report(f"session_scan_skipped {exc}")
        return []
    candidates: list[SessionCandidate] = []
    for thread_id, title, rollout_path, updated_at in rows:
        source = Path(rollout_path or "")
        if thread_id in pinned or not rollout_path or not source.exists() or (updated_at and int(updated_at) >= cutoff):
            continue
        try:
            relative = canonical_path(source).relative_to(sessions_root)
        except ValueError:
            continue
        candidates.append(SessionCandidate(source.stat().st_size, thread_id, title or "", source, relative))
    return sorted(candidates, key=lambda item: item.size, reverse=True)


def write_restore_script(manifest: Path, state_db: Path, backup_root: Path) -> None:
    restore = backup_root / "restore-sessions.py"
    restore.write_text(
        f'''#!/usr/bin/env python3
import json
import shutil
import sqlite3
from pathlib import Path

manifest = Path(r"{manifest}")
db = Path(r"{state_db}")
conn = sqlite3.connect(db)
conn.execute("pragma busy_timeout=10000")
for line in manifest.read_text(encoding="utf-8").splitlines():
    rec = json.loads(line)
    src = Path(rec["to"])
    dest = Path(rec["from"])
    if src.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    if rec.get("thread_id"):
        conn.execute(
            "update threads set rollout_path=?, archived=0, archived_at=NULL where id=?",
            (str(dest), rec["thread_id"]),
        )
conn.commit()
conn.close()
''',
        encoding="utf-8",
    )
    report(f"session_restore_script {restore}")


def archive_sessions(
    conn: sqlite3.Connection,
    candidates: list[SessionCandidate],
    codex_home: Path,
    backup_root: Path,
    stamp: str,
    apply: bool,
    details: bool,
) -> None:
    report(f"old_session_candidates {len(candidates)}")
    report(f"old_session_candidate_gb {format_size(sum(item.size for item in candidates), 'gb')}")
    for index, item in enumerate(candidates[:10], start=1):
        suffix = f" thread_id={item.thread_id} title={item.title[:70]}" if details else ""
        report(f"large_session_mb {format_size(item.size, 'mb')} session_{index:03d}{suffix}")
    if not apply or not candidates:
        return
    archive_root = codex_home / "archived_sessions" / f"keep-codex-fast-{stamp}"
    manifest = backup_root / "moved-sessions.jsonl"
    archive_root.mkdir(parents=True, exist_ok=True)
    now = int(time.time())
    with manifest.open("w", encoding="utf-8") as handle:
        for item in candidates:
            dest = archive_root / item.relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item.source), str(dest))
            handle.write(
                json.dumps(
                    {
                        "thread_id": item.thread_id,
                        "from": str(item.source),
                        "to": str(dest),
                        "bytes": item.size,
                    }
                )
                + "\n"
            )
            conn.execute(
                "update threads set rollout_path=?, archived=1, archived_at=? where id=?",
                (str(dest), now, item.thread_id),
            )
    write_restore_script(manifest, codex_home / "state_5.sqlite", backup_root)
    report(f"archived_sessions_root {archive_root}")
    report(f"archived_sessions_manifest {manifest}")


def report_config_prune_candidates(codex_home: Path, details: bool) -> list[str]:
    config = codex_home / "config.toml"
    if not config.exists():
        report("config_prune_candidates 0")
        return []
    candidates = []
    for line in config.read_text(encoding="utf-8-sig").splitlines():
        match = PROJECT_HEADER_RE.match(line)
        if match and (TEMP_PROJECT_RE.search(match.group(2)) or not Path(match.group(2)).exists()):
            candidates.append(match.group(2))
    report(f"config_prune_candidates {len(candidates)}")
    if details:
        for index, path_value in enumerate(candidates, start=1):
            report(f"config_prune_candidate_{index:03d} {path_value}")
    return candidates


def archive_old_dirs(root: Path, archive_root: Path, manifest: Path, days: int, apply: bool, label: str) -> None:
    if not root.exists():
        report(f"{label}_candidates 0")
        return
    cutoff = time.time() - days * 24 * 60 * 60
    candidates = [path for path in root.iterdir() if path.is_dir() and path.stat().st_mtime < cutoff]
    report(f"{label}_candidates {len(candidates)}")
    report(f"{label}_candidate_gb {format_size(sum(size_bytes(path) for path in candidates), 'gb')}")
    if not apply or not candidates:
        return
    archive_root.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", encoding="utf-8") as handle:
        for source in candidates:
            dest = archive_root / source.name
            item_size = size_bytes(source)
            shutil.move(str(source), str(dest))
            handle.write(json.dumps({"from": str(source), "to": str(dest), "bytes": item_size}) + "\n")
    report(f"{label}_archive_root {archive_root}")
    report(f"{label}_manifest {manifest}")


def rotate_logs(codex_home: Path, threshold_mb: int, stamp: str, apply: bool) -> None:
    files = [path for path in codex_home.glob("logs_2.sqlite*") if path.is_file()]
    total = sum(path.stat().st_size for path in files)
    report(f"logs_mb {format_size(total, 'mb')}")
    if total < threshold_mb * 1024 * 1024:
        report("logs_rotate skipped_below_threshold")
    elif apply and files:
        archive_root = codex_home / "archived_logs" / f"keep-codex-fast-{stamp}"
        archive_root.mkdir(parents=True, exist_ok=True)
        for path in files:
            shutil.move(str(path), str(archive_root / path.name))
        report(f"logs_archive_root {archive_root}")


def report_sizes(codex_home: Path) -> None:
    for rel in ("sessions", "archived_sessions", "worktrees", "archived_worktrees", "archived_logs"):
        path = codex_home / rel
        if path.exists():
            report(f"size_{rel}_gb {format_size(size_bytes(path), 'gb')}")


def report_codex_processes(details: bool) -> None:
    report("top_node_processes")
    check = codex_processes_running()
    if not check.available:
        report(f"node_process_report_skipped {check.error}")
    elif details:
        for index, proc in enumerate(check.processes[:10], start=1):
            report(f"codex_process_{index:03d} {proc}")


def validate_apply_safety(args: argparse.Namespace, codex_home: Path) -> int:
    expected = canonical_path(Path(args.confirm_codex_home)) if args.confirm_codex_home else None
    if expected != canonical_path(codex_home):
        report("apply_blocked confirmation_mismatch")
        report(f"expected_confirm_codex_home {codex_home}")
        return 2
    check = codex_processes_running()
    if args.wait_for_codex_exit and check.available and check.processes:
        report("waiting_for_codex_exit")
        check = wait_for_codex_exit()
    if not check.available and not args.allow_unverified_process_state:
        report(f"apply_blocked process_detection_unavailable {check.error}")
        return 2
    if check.processes:
        report("apply_blocked codex_running")
        for index, proc in enumerate(check.processes, start=1):
            report(f"blocking_process_{index:03d} {proc if args.details else 'codex'}")
        return 2
    return 0


def maintain_state(args: argparse.Namespace, codex_home: Path, backup_root: Path, stamp: str, apply: bool) -> None:
    state_db = codex_home / "state_5.sqlite"
    if not state_db.exists():
        report("state_db_missing")
        return
    conn = sqlite_connect(state_db, readonly=not apply)
    try:
        conn.execute("pragma busy_timeout=10000")
        normalize_sqlite_paths(conn, apply)
        archive_sessions(
            conn,
            active_session_candidates(conn, codex_home, args.archive_older_than_days),
            codex_home,
            backup_root,
            stamp,
            apply,
            args.details,
        )
        if apply:
            conn.commit()
            try:
                conn.execute("pragma wal_checkpoint(truncate)")
                conn.execute("pragma optimize")
            except sqlite3.Error as exc:
                report(f"sqlite_maintenance_skipped {exc}")
    finally:
        conn.close()


def run(args: argparse.Namespace) -> int:
    codex_home = codex_home_from_args(args.codex_home)
    if not codex_home.exists():
        report(f"codex_home_missing {codex_home}")
        return 2
    apply = args.mode == "apply"
    backup = args.mode in {"backup", "apply"}
    if apply:
        safety = validate_apply_safety(args, codex_home)
        if safety != 0:
            return safety
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = (
        canonical_path(Path(args.backup_root))
        if args.backup_root
        else default_backup_parent() / f"keep-codex-fast-{stamp}"
    )
    report("schema_version 1")
    report(f"requested_mode {args.mode}")
    report(f"codex_home {codex_home if args.details else 'redacted'}")
    if backup:
        report(f"backup_root {backup_root}")
        backup_metadata(codex_home, backup_root)
    else:
        report("mode_safety read_only=true privacy=pseudonymous")
    maintain_state(args, codex_home, backup_root, stamp, apply)
    report_config_prune_candidates(codex_home, args.details)
    archive_old_dirs(
        codex_home / "worktrees",
        codex_home / "archived_worktrees" / f"keep-codex-fast-{stamp}",
        backup_root / "moved-worktrees.jsonl",
        args.worktree_older_than_days,
        apply,
        "worktree",
    )
    rotate_logs(codex_home, args.rotate_logs_above_mb, stamp, apply)
    report_sizes(codex_home)
    report_codex_processes(args.details)
    report("done")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report-first, backup-first Codex local-state maintenance.")
    parser.add_argument("mode", choices=["report", "backup", "apply"], nargs="?", default="report")
    parser.add_argument("--codex-home", help="Override Codex home. Defaults to CODEX_HOME or ~/.codex.")
    parser.add_argument("--backup-root", help="Override backup output folder.")
    parser.add_argument("--confirm-codex-home", help="Required for apply; must match the resolved Codex home.")
    parser.add_argument("--details", action="store_true", help="Print raw thread IDs, titles, and local paths.")
    parser.add_argument("--wait-for-codex-exit", action="store_true", help="Wait for Codex to exit before applying.")
    parser.add_argument(
        "--allow-unverified-process-state",
        action="store_true",
        help="Unsafe escape hatch when process detection is unavailable.",
    )
    parser.add_argument("--archive-older-than-days", type=int, default=10)
    parser.add_argument("--worktree-older-than-days", type=int, default=7)
    parser.add_argument("--rotate-logs-above-mb", type=int, default=64)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(run(parse_args(sys.argv[1:])))
