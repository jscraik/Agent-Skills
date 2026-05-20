#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
fi

cd "$REPO_ROOT"

if ! command -v prek >/dev/null 2>&1; then
	echo "[install-prek-hooks] prek is required but is not on PATH" >&2
	exit 1
fi

if [[ ! -f "$REPO_ROOT/prek.toml" ]]; then
	echo "[install-prek-hooks] missing prek.toml at $REPO_ROOT/prek.toml" >&2
	exit 1
fi

git_common_dir="$(git rev-parse --git-common-dir)"
if [[ "$git_common_dir" = /* ]]; then
	git_hooks_dir="$git_common_dir/hooks"
else
	git_hooks_dir="$REPO_ROOT/$git_common_dir/hooks"
fi
prek_home="${PREK_HOME:-$REPO_ROOT/.cache/prek}"
mkdir -p "$prek_home"

echo "[install-prek-hooks] installing prek hooks"
PREK_HOME="$prek_home" prek install --overwrite

patch_hook() {
	local hook_name="$1"
	local hook_path="$git_hooks_dir/$hook_name"
	if [[ ! -f "$hook_path" ]]; then
		echo "[install-prek-hooks] expected generated hook missing: $hook_path" >&2
		exit 1
	fi

	python3 - "$hook_path" "$REPO_ROOT" <<'PY'
import shlex
import sys
from pathlib import Path

hook_path = Path(sys.argv[1])
repo_root = sys.argv[2]
text = hook_path.read_text(encoding="utf-8")
start = "# agent-skills prek home begin"
end = "# agent-skills prek home end"
block = (
    f"{start}\n"
    "# Keep prek logs/cache inside the workspace so sandboxed Codex git hooks\n"
    "# do not need home-directory cache write access.\n"
    f"REPO_ROOT={shlex.quote(repo_root)}\n"
    'export PREK_HOME="${PREK_HOME:-$REPO_ROOT/.cache/prek}"\n'
    'mkdir -p "$PREK_HOME"\n'
    f"{end}\n"
)
if start in text:
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    text = before + block + after.lstrip("\n")
else:
    marker = 'HERE="$(cd "$(dirname "$0")" && pwd)"\n'
    if marker not in text:
        raise SystemExit(f"cannot find insertion marker in {hook_path}")
    text = text.replace(marker, marker + block + "\n", 1)
hook_path.write_text(text, encoding="utf-8")
PY
}

patch_hook pre-commit
patch_hook commit-msg
patch_hook pre-push

echo "[install-prek-hooks] using PREK_HOME=$prek_home"
echo "[install-prek-hooks] hooks ready"
