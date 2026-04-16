#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

changed_only=1
fast_mode=0
strict_mode=0
repo_root=""

usage() {
	cat <<'USAGE'
Usage: scripts/verify-work.sh [options]

Canonical repo-local verification runner.

Options:
  --all              Run full test coverage in --fast mode
  --changed-only     Prefer changed-file validation in --fast mode (default)
  --strict           Fail when fast-mode fallbacks are needed
  --fast             Run preflight + lint + typecheck + tests instead of the full check bundle
  --repo-root PATH   Run checks in a specific repository root
  -h, --help         Show this help text
USAGE
}

detect_stack() {
	if [[ -f package.json ]]; then
		echo js
		return
	fi
	if [[ -f pyproject.toml ]]; then
		echo py
		return
	fi
	if [[ -f Cargo.toml ]]; then
		echo rust
		return
	fi
	echo repo
}

preflight_bins_csv() {
	case "$1" in
		js) echo 'git,bash,sed,rg,jq,curl,node,python3,pnpm' ;;
		py) echo 'git,bash,sed,rg,jq,curl,python3' ;;
		rust) echo 'git,bash,sed,rg,jq,curl,python3,cargo' ;;
		repo) echo 'git,bash,sed,rg,jq,curl,python3' ;;
		*) echo "[verify-work] unknown stack: $1" >&2; return 2 ;;
	esac
}

# preflight_paths_csv returns a comma-separated list of repository paths required for preflight verification for the given project stack.
preflight_paths_csv() {
	case "$1" in
		js) echo 'package.json,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		py) echo 'pyproject.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		rust) echo 'Cargo.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		repo) echo 'CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		*) echo "[verify-work] unknown stack: $1" >&2; return 2 ;;
	esac
}

has_package_script() {
	local script_name="$1"
	[[ -f "$repo_root/package.json" ]] || return 1
	jq -e --arg script_name "$script_name" '(.scripts // {}) | has($script_name)' "$repo_root/package.json" >/dev/null 2>&1
}

while (( $# > 0 )); do
	case "$1" in
		--all|--all-skills)
			changed_only=0
			shift
			;;
		--changed-only)
			changed_only=1
			shift
			;;
		--strict)
			strict_mode=1
			shift
			;;
		--fast)
			fast_mode=1
			shift
			;;
		--repo-root)
			repo_root="${2:-}"
			shift 2
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "[verify-work] unknown argument: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

if [[ -z "$repo_root" ]]; then
	repo_root="$REPO_ROOT"
fi

cd "$repo_root"
echo "[verify-work] repo root: $repo_root"

stack="$(detect_stack)"
bins_csv="$(preflight_bins_csv "$stack")"
paths_csv="$(preflight_paths_csv "$stack")"

echo
echo "==> codex-preflight"
bash "$repo_root/scripts/codex-preflight.sh" \
	--stack "$stack" \
	--mode required \
	--bins "$bins_csv" \
	--paths "$paths_csv"

if [[ "$fast_mode" -eq 0 ]]; then
	echo
	echo "==> validate-codestyle"
	bash "$repo_root/scripts/validate-codestyle.sh" --repo-root "$repo_root"
	exit 0
fi

echo
echo "==> validate-codestyle --fast"
validate_args=(--repo-root "$repo_root" --fast)
if [[ "$changed_only" -eq 1 ]]; then
	validate_args+=(--changed-only)
else
	validate_args+=(--all)
fi
if [[ "$strict_mode" -eq 1 ]]; then
	validate_args+=(--strict)
fi

bash "$repo_root/scripts/validate-codestyle.sh" "${validate_args[@]}"
