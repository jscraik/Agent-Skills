#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source "$SCRIPT_DIR/lib/secure-hook-cache.sh"
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

git_common_dir="$(git rev-parse --path-format=absolute --git-common-dir)"
if [[ "$git_common_dir" = /* ]]; then
	git_hooks_dir="$git_common_dir/hooks"
else
	git_hooks_dir="$REPO_ROOT/$git_common_dir/hooks"
fi
configured_hooks_path="$(git config --local --get core.hooksPath 2>/dev/null || true)"
configured_hooks_dir="$(git rev-parse --path-format=absolute --git-path hooks)"
restore_hooks_path=0
if [[ -n "$configured_hooks_path" ]]; then
	if [[ "$configured_hooks_dir" != "$git_hooks_dir" ]]; then
		echo "[install-prek-hooks] unexpected core.hooksPath: $configured_hooks_path" >&2
		echo "[install-prek-hooks] expected common hooks directory: $git_hooks_dir" >&2
		exit 1
	fi
	restore_hooks_path=1
	git config --local --unset-all core.hooksPath
fi

restore_configured_hooks_path() {
	if [[ "$restore_hooks_path" -eq 1 ]]; then
		git config --local --replace-all core.hooksPath "$configured_hooks_path"
	fi
}

trap restore_configured_hooks_path EXIT
hook_tmp_dir="${TMPDIR:-/tmp}"
if [[ ! -d "$hook_tmp_dir" || ! -w "$hook_tmp_dir" ]]; then
	if [[ -d "/private/tmp" && -w "/private/tmp" ]]; then
		hook_tmp_dir="/private/tmp"
	else
		hook_tmp_dir="/tmp"
	fi
fi
if [[ -n "${CODEX_HOOK_CACHE_ROOT:-}" ]]; then
	hook_cache_root="$CODEX_HOOK_CACHE_ROOT"
else
	hook_cache_root="$(new_hook_cache_root "$hook_tmp_dir")"
fi
prek_home="${PREK_HOME:-$hook_cache_root/prek}"
hook_cache_root="$(validate_hook_cache_path "$hook_cache_root" "$REPO_ROOT" "$git_common_dir")"
prek_home="$(validate_hook_cache_path "$prek_home" "$REPO_ROOT" "$git_common_dir")"
if [[ "$prek_home" != "$hook_cache_root/prek" ]]; then
	echo "[install-prek-hooks] PREK_HOME must equal CODEX_HOOK_CACHE_ROOT/prek" >&2
	exit 1
fi
secure_hook_cache_dir "$hook_cache_root"
secure_hook_cache_dir "$prek_home"

echo "[install-prek-hooks] installing prek hooks"
PREK_HOME="$prek_home" prek install --overwrite

patch_hook() {
	local hook_name="$1"
	local hook_path="$git_hooks_dir/$hook_name"
	if [[ ! -f "$hook_path" ]]; then
		echo "[install-prek-hooks] expected generated hook missing: $hook_path" >&2
		exit 1
	fi

python3 - "$hook_path" "$hook_cache_root" "$prek_home" <<'PY'
import shlex
import sys
from pathlib import Path

hook_path = Path(sys.argv[1])
hook_cache_root = sys.argv[2]
prek_home = sys.argv[3]
text = hook_path.read_text(encoding="utf-8")
start = "# agent-skills prek home begin"
end = "# agent-skills prek home end"
block = (
    f"{start}\n"
    "# Keep prek logs/cache outside Git metadata and the worktree.\n"
    f"export CODEX_HOOK_CACHE_ROOT={shlex.quote(hook_cache_root)}\n"
    'export PREK_HOME="$CODEX_HOOK_CACHE_ROOT/prek"\n'
    'AGENT_SKILLS_REPO_ROOT="$(git rev-parse --show-toplevel)"\n'
    'AGENT_SKILLS_GIT_COMMON_DIR="$(git rev-parse --path-format=absolute --git-common-dir)"\n'
    'source "$AGENT_SKILLS_REPO_ROOT/Infrastructure/scripts/lib/secure-hook-cache.sh"\n'
    'CODEX_HOOK_CACHE_ROOT="$(validate_hook_cache_path "$CODEX_HOOK_CACHE_ROOT" "$AGENT_SKILLS_REPO_ROOT" "$AGENT_SKILLS_GIT_COMMON_DIR")"\n'
    'PREK_HOME="$(validate_hook_cache_path "$PREK_HOME" "$AGENT_SKILLS_REPO_ROOT" "$AGENT_SKILLS_GIT_COMMON_DIR")"\n'
    'secure_hook_cache_dir "$CODEX_HOOK_CACHE_ROOT"\n'
    'secure_hook_cache_dir "$PREK_HOME"\n'
    'cd "$AGENT_SKILLS_REPO_ROOT"\n'
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

patch_hook pre-push

write_pre_commit_hook() {
	local hook_path="$git_hooks_dir/pre-commit"
	cat >"$hook_path" <<'HOOK'
#!/bin/sh
# Agent Skills direct pre-commit shim.
# Git owns the current worktree index lock while invoking pre-commit. Prek's
# changed-file discovery writes a tree before it can run the repository hook,
# so invoke the fail-closed repository validation directly.
REPO_ROOT="$(git rev-parse --show-toplevel)" || exit 1
exec bash "$REPO_ROOT/scripts/hooks/pre-commit.sh" "$@"
HOOK
	chmod +x "$hook_path"
}

write_commit_msg_hook() {
	local hook_path="$git_hooks_dir/commit-msg"
	cat >"$hook_path" <<'HOOK'
#!/bin/sh
# Agent Skills direct commit-message shim.
# Git holds the current index lock during this stage; invoking Prek here makes
# its changed-file discovery attempt a second index write before validation.
REPO_ROOT="$(git rev-parse --show-toplevel)" || exit 1
exec bash "$REPO_ROOT/scripts/hooks/commit-msg.sh" "$@"
HOOK
	chmod +x "$hook_path"
}

write_pre_commit_hook
write_commit_msg_hook

echo "[install-prek-hooks] using PREK_HOME=$prek_home"
echo "[install-prek-hooks] hooks ready"
