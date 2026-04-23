#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
fi

changed_only=1
fast_mode=0
strict_mode=0
governance_scope="project-local"
repo_root=""

# usage prints the help and usage text for validate-codestyle.sh, describing supported command-line options and their effects.
usage() {
	cat <<'USAGE'
Usage: scripts/validation-and-linting/validate-codestyle.sh [options]

Fail-closed codestyle validation for harness-managed repositories.

Options:
  --all                      Run full test coverage in --fast mode
  --changed-only             Prefer changed-file validation in --fast mode (default)
  --strict                   Fail when optional fast-mode fallbacks are needed
  --fast                     Run lint + docs + typecheck + tests instead of the full check bundle
  --repo-root PATH           Run checks in a specific repository root
  --project-governance       Use project-local governance scope (default)
  --workspace-governance     Use workspace-level governance scope
  --persistent-artifacts     Equivalent to --workspace-governance
  -h, --help                 Show this help text
USAGE
}

has_package_script() {
	local script_name="$1"
	[[ -f "$repo_root/package.json" ]] || return 1
	jq -e --arg script_name "$script_name" '(.scripts // {}) | has($script_name)' "$repo_root/package.json" >/dev/null 2>&1
}

run_script() {
	local script_name="$1"

	echo
	echo "==> $script_name"
	pnpm run "$script_name"
}

run_required_script() {
	local script_name="$1"

	if ! has_package_script "$script_name"; then
		echo "[validate-codestyle] missing package script: $script_name" >&2
		exit 1
	fi

	run_script "$script_name"
}

# run_optional_script runs the named script from package.json if present; if the script is missing and `strict_mode` is `1` it prints an error to stderr and exits with status 1, otherwise it prints a skip message and returns success.
run_optional_script() {
	local script_name="$1"

	if has_package_script "$script_name"; then
		run_script "$script_name"
		return 0
	fi

	if [[ "$strict_mode" -eq 1 ]]; then
		echo "[validate-codestyle] missing package script: $script_name" >&2
		exit 1
	fi

	echo "[validate-codestyle] skip $script_name: package script not defined"
}

# run_non_package_lane delegates validation for repositories without package.json to Infrastructure/scripts/validate_all.sh using `--persistent` when `governance_scope` is "workspace" or `--ephemeral` otherwise; in fast mode it prints a skip message and returns success.
run_non_package_lane() {
	local validate_all_mode="--ephemeral"
	if [[ "$governance_scope" == "workspace" ]]; then
		validate_all_mode="--persistent"
	fi

	if [[ "$fast_mode" -eq 1 ]]; then
		echo "[validate-codestyle] skip pnpm codestyle lane: package.json not present"
		echo "[validate-codestyle] non-package fast mode completed (scope=$governance_scope)"
		return 0
	fi

	echo "[validate-codestyle] non-package repository detected; delegating to validate_all $validate_all_mode"
	bash "$repo_root/Infrastructure/scripts/validate_all.sh" "$validate_all_mode"
}

while (( $# > 0 )); do
	case "$1" in
		--all)
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
		--project-governance)
			governance_scope="project-local"
			shift
			;;
		--workspace-governance|--persistent-artifacts)
			governance_scope="workspace"
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "[validate-codestyle] unknown argument: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

if [[ -z "$repo_root" ]]; then
	repo_root="$REPO_ROOT"
fi

cd "$repo_root"
echo "[validate-codestyle] repo root: $repo_root"

if [[ ! -f "$repo_root/CODESTYLE.md" ]]; then
	echo "[validate-codestyle] missing CODESTYLE.md" >&2
	exit 1
fi

if [[ ! -f "$repo_root/package.json" ]]; then
	run_non_package_lane
	exit $?
fi

if ! command -v pnpm >/dev/null 2>&1; then
	echo "[validate-codestyle] missing required binary: pnpm" >&2
	exit 1
fi

if [[ "$fast_mode" -eq 0 ]]; then
	run_required_script "check"
	exit 0
fi

run_required_script "lint"
run_optional_script "docs:lint"
run_optional_script "skill:validate"
run_optional_script "workflow:validate"
run_required_script "typecheck"

if [[ "$changed_only" -eq 1 ]]; then
	if has_package_script "test:related"; then
		run_script "test:related"
	else
		if [[ "$strict_mode" -eq 1 ]]; then
			echo "[validate-codestyle] missing package script: test:related" >&2
			exit 1
		fi
		echo "[validate-codestyle] test:related unavailable; falling back to full test run"
		run_required_script "test"
	fi
else
	run_required_script "test"
fi