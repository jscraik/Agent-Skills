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
hook_tmp_dir="${TMPDIR:-/tmp}"
if [[ ! -d "$hook_tmp_dir" || ! -w "$hook_tmp_dir" ]]; then
	if [[ -d "/private/tmp" && -w "/private/tmp" ]]; then
		hook_tmp_dir="/private/tmp"
	else
		hook_tmp_dir="/tmp"
	fi
fi
prek_home="${PREK_HOME:-$hook_tmp_dir/agent-skills-hook-cache/prek}"
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

python3 - "$hook_path" <<'PY'
import sys
from pathlib import Path

hook_path = Path(sys.argv[1])
text = hook_path.read_text(encoding="utf-8")
start = "# agent-skills prek home begin"
end = "# agent-skills prek home end"
block = (
    f"{start}\n"
    "# Keep prek logs/cache outside Git metadata and the worktree.\n"
    'export CODEX_HOOK_CACHE_ROOT="${CODEX_HOOK_CACHE_ROOT:-${TMPDIR:-/tmp}/agent-skills-hook-cache}"\n'
    'export PREK_HOME="${PREK_HOME:-$CODEX_HOOK_CACHE_ROOT/prek}"\n'
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
