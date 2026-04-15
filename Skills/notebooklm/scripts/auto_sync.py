#!/usr/bin/env python3
"""
NotebookLM Auto Sync

Incrementally sync local files into a NotebookLM notebook by re-uploading only
new or modified files. This is a safer "industry" alternative to brittle
Drive-picker UI automation.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).parent))

from add_source import add_file_source
from auth_manager import AuthManager
from notebook_manager import NotebookLibrary
from config import DATA_DIR


DEFAULT_EXTENSIONS = ".pdf,.txt,.md,.doc,.docx,.ppt,.pptx,.csv,.json,.xml"
DEFAULT_EXCLUDES = ".git,.svn,.hg,.venv,node_modules,__pycache__,.DS_Store"
DEFAULT_MAX_FILES = 20


def parse_csv_set(value: str, lowercase: bool = True, prefix_dot: bool = False) -> Set[str]:
    """Parse comma-separated values into a normalized set."""
    items = set()
    for raw in (value or "").split(","):
        item = raw.strip()
        if not item:
            continue
        if lowercase:
            item = item.lower()
        if prefix_dot and not item.startswith("."):
            item = f".{item}"
        items.add(item)
    return items


def load_state(state_file: Path) -> Dict:
    """Load persisted sync state."""
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"⚠️ Could not read state file {state_file}: {exc}")
    return {"version": 1, "files": {}, "updated_at": None}


def save_state(state_file: Path, state: Dict) -> None:
    """Persist sync state to disk."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.utcnow().isoformat() + "Z"
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def should_exclude(path: Path, excludes: Set[str]) -> bool:
    """Check whether a path should be excluded."""
    lowered_parts = {part.lower() for part in path.parts}
    return any(ex in lowered_parts for ex in excludes)


def collect_files(
    root: Path,
    recursive: bool,
    extensions: Set[str],
    excludes: Set[str],
) -> List[Path]:
    """Collect candidate files for syncing."""
    pattern = "**/*" if recursive else "*"
    candidates = []

    for path in root.glob(pattern):
        if not path.is_file():
            continue
        if should_exclude(path, excludes):
            continue
        ext = path.suffix.lower()
        if extensions and ext not in extensions:
            continue
        candidates.append(path)

    return sorted(candidates)


def resolve_notebook(notebook_url: Optional[str], notebook_id: Optional[str]) -> Dict[str, str]:
    """Resolve notebook URL and identifier from args/library."""
    if notebook_url:
        return {"url": notebook_url, "id": notebook_id or "direct-url", "name": notebook_id or "Direct URL"}

    library = NotebookLibrary()
    if notebook_id:
        notebook = library.get_notebook(notebook_id)
        if not notebook:
            raise ValueError(f"Notebook '{notebook_id}' not found")
        return {"url": notebook["url"], "id": notebook["id"], "name": notebook["name"]}

    active = library.get_active_notebook()
    if not active:
        raise ValueError("No active notebook. Use --notebook-id or --notebook-url.")

    return {"url": active["url"], "id": active["id"], "name": active["name"]}


def file_fingerprint(path: Path) -> Dict[str, int]:
    """Return lightweight fingerprint for incremental tracking."""
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Incrementally sync local files into NotebookLM by uploading changed files only."
    )
    parser.add_argument("--local", required=True, help="Local folder to sync")
    parser.add_argument("--notebook-url", help="NotebookLM notebook URL")
    parser.add_argument("--notebook-id", help="Notebook ID from library (or active notebook if omitted)")
    parser.add_argument("--extensions", default=DEFAULT_EXTENSIONS,
                        help=f"Comma-separated extensions (default: {DEFAULT_EXTENSIONS})")
    parser.add_argument("--exclude", default=DEFAULT_EXCLUDES,
                        help=f"Comma-separated folder/file names to exclude (default: {DEFAULT_EXCLUDES})")
    parser.add_argument("--state-file", default=str(DATA_DIR / "sync_state.json"),
                        help="Path to sync state file")
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES,
                        help=f"Maximum files to upload per run (default: {DEFAULT_MAX_FILES})")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subdirectories")
    parser.add_argument("--force", action="store_true", help="Upload all matching files, ignore state")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without uploading")
    parser.add_argument("--show-browser", action="store_true", help="Show browser during uploads")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first upload failure")
    args = parser.parse_args()

    root = Path(args.local).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"❌ Local folder not found: {root}")
        return 1

    auth = AuthManager()
    if not auth.is_authenticated():
        print("❌ Not authenticated. Run: python3 Infrastructure/scripts/run.py auth_manager.py setup")
        return 1

    try:
        notebook = resolve_notebook(args.notebook_url, args.notebook_id)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1

    extensions = parse_csv_set(args.extensions, lowercase=True, prefix_dot=True)
    excludes = parse_csv_set(args.exclude, lowercase=True, prefix_dot=False)
    state_file = Path(args.state_file).expanduser().resolve()
    state = load_state(state_file)
    state_files = state.setdefault("files", {})

    candidates = collect_files(root, recursive=args.recursive, extensions=extensions, excludes=excludes)
    if not candidates:
        print(f"📭 No matching files found in {root}")
        return 0

    changed: List[Path] = []
    for path in candidates:
        key = str(path)
        current = file_fingerprint(path)
        previous = state_files.get(key, {})
        if args.force or previous.get("size") != current["size"] or previous.get("mtime_ns") != current["mtime_ns"]:
            changed.append(path)

    if not changed:
        print(f"✅ Up to date. {len(candidates)} file(s) checked, 0 changed.")
        return 0

    if len(changed) > args.max_files:
        changed = changed[:args.max_files]
        print(f"⚠️ Limiting run to first {args.max_files} changed files. Re-run to continue.")

    print("🚀 NotebookLM incremental sync")
    print(f"📂 Local folder: {root}")
    print(f"📚 Notebook: {notebook['name']} ({notebook['id']})")
    print(f"📄 Changed files: {len(changed)}")

    if args.dry_run:
        for path in changed:
            print(f"  - {path}")
        print("🧪 Dry run only; no files uploaded.")
        return 0

    success_count = 0
    failed_count = 0

    for path in changed:
        print(f"\n➡️ Syncing: {path.name}")
        result = add_file_source(
            notebook_url=notebook["url"],
            file_path=str(path),
            headless=not args.show_browser,
        )

        if result:
            fp = file_fingerprint(path)
            state_files[str(path)] = {
                "size": fp["size"],
                "mtime_ns": fp["mtime_ns"],
                "last_synced_at": datetime.utcnow().isoformat() + "Z",
                "notebook_id": notebook["id"],
                "notebook_name": notebook["name"],
            }
            success_count += 1
            print(f"✅ {path.name}")
        else:
            failed_count += 1
            print(f"❌ {path.name}")
            if args.fail_fast:
                break

    save_state(state_file, state)

    print("\n" + "=" * 60)
    print("Sync summary")
    print("=" * 60)
    print(f"Attempted: {success_count + failed_count}")
    print(f"Succeeded: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"State file: {state_file}")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
