#!/usr/bin/env bash
set -euo pipefail

resolve_script_path() {
	if [[ -n "${ZSH_VERSION:-}" ]]; then
		eval 'printf "%s\n" "${(%):-%N}"'
		return
	fi
	printf '%s\n' "${BASH_SOURCE[0]:-$0}"
}

is_script_sourced() {
	if [[ -n "${ZSH_VERSION:-}" ]]; then
		local source_path
		source_path="$(resolve_script_path)"
		[[ "${source_path}" != "$0" ]]
		return
	fi
	[[ "${BASH_SOURCE[0]:-$0}" != "$0" ]]
}

SCRIPT_PATH="$(resolve_script_path)"
SCRIPT_DIR="$(cd -- "$(dirname -- "${SCRIPT_PATH}")" && pwd -P)"
WORKSPACE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
PREFLIGHT_OVERRIDES_FILE="${WORKSPACE_ROOT}/.harness/memory/codex-preflight-overrides.env"
LOCAL_MEMORY_FALLBACK_SCRIPT="${SCRIPT_DIR}/codex-preflight-local-memory-legacy.sh"

# usage prints the CLI usage text, available options, examples, and the legacy positional-interface note for the codex preflight script.
usage() {
	cat <<'USAGE'
Usage:
  ./scripts/codex-preflight.sh [options]

Options:
  --stack <auto|repo|js|py|rust>    Stack mode. Default: auto
  --mode <off|optional|required>    Local Memory mode. Default: required
  --repo-fragment <text>            Require repo root to contain this fragment
  --bins <csv>                      Override required binaries
  --paths <csv>                     Override required paths
  -h, --help                        Show this help

Examples:
  ./scripts/codex-preflight.sh
  ./scripts/codex-preflight.sh --stack js
  ./scripts/codex-preflight.sh --stack py --mode required
  ./scripts/codex-preflight.sh --repo-fragment local-memory

Legacy compatibility:
  ./scripts/codex-preflight.sh <repo-fragment> [bins-csv] [paths-csv]
  This preserves the older positional interface used by parent-repo checks and
  runs with Local Memory disabled unless the new flag-based mode is used.
USAGE
}

log_section() {
	printf '== %s ==\n' "$*"
}

log_ok() {
	printf '✅ %s\n' "$*"
}

log_warn() {
	printf '⚠️ %s\n' "$*"
}

log_err() {
	printf '❌ %s\n' "$*" >&2
}

# append_csv_values combines two comma-separated lists: if one is empty returns the other, otherwise returns both joined with a single comma.
append_csv_values() {
	local base_csv="${1:-}"
	local extra_csv="${2:-}"

	if [[ -z "${base_csv}" ]]; then
		printf '%s\n' "${extra_csv}"
		return
	fi
	if [[ -z "${extra_csv}" ]]; then
		printf '%s\n' "${base_csv}"
		return
	fi
	printf '%s,%s\n' "${base_csv}" "${extra_csv}"
}

# load_preflight_overrides loads preflight override variables from a file into PREFLIGHT_OVERRIDE_BINS, PREFLIGHT_OVERRIDE_PATHS, and PREFLIGHT_OVERRIDE_ALLOWED_EXTERNAL_PATHS.
# override_file is the path to an optional overrides file; if the file does not exist the variables are set to empty and the function returns success (0).
load_preflight_overrides() {
	local override_file="$1"

	PREFLIGHT_OVERRIDE_BINS=''
	PREFLIGHT_OVERRIDE_PATHS=''
	PREFLIGHT_OVERRIDE_ALLOWED_EXTERNAL_PATHS="${CODEX_PREFLIGHT_ALLOWED_EXTERNAL_PATHS:-}"
	if [[ ! -f "${override_file}" ]]; then
		return 0
	fi

	# shellcheck source=/dev/null
	source "${override_file}"
	PREFLIGHT_OVERRIDE_BINS="${CODEX_PREFLIGHT_EXTRA_BINS:-}"
	PREFLIGHT_OVERRIDE_PATHS="${CODEX_PREFLIGHT_EXTRA_PATHS:-}"
	PREFLIGHT_OVERRIDE_ALLOWED_EXTERNAL_PATHS="${CODEX_PREFLIGHT_ALLOWED_EXTERNAL_PATHS:-}"
}

# detect_stack determines the project stack by checking for standard manifest files and echoes one of: `js`, `py`, `rust`, or `repo`.
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

stack_bins_csv() {
	case "$1" in
		js) echo 'git,bash,sed,rg,jq,curl,node,npm,python3' ;;
		py) echo 'git,bash,sed,rg,jq,curl,python3' ;;
		rust) echo 'git,bash,sed,rg,jq,curl,python3,cargo' ;;
		repo) echo 'git,bash,sed,rg,jq,curl,python3' ;;
		*) log_err "unknown stack: $1"; return 2 ;;
	esac
}

# stack_paths_csv returns a comma-separated list of repository paths required for the specified stack (`js`, `py`, `rust`, or `repo`).
# stack_paths_csv returns a comma-separated list of repository paths required for the given stack (js, py, rust, repo); on unknown stack it logs an error and returns exit code 2.
stack_paths_csv() {
	case "$1" in
		js) echo 'package.json,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		py) echo 'pyproject.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		rust) echo 'Cargo.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		repo) echo 'CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh' ;;
		*) log_err "unknown stack: $1"; return 2 ;;
	esac
}

# check_bins verifies each binary named in a comma-separated list is available on PATH; logs missing binaries and returns 2 if any are absent.
check_bins() {
	local bins_csv="$1"
	local -a bins=()
	local -a missing_bins=()
	local b

	IFS=',' read -r -a bins <<<"${bins_csv}"
	for b in "${bins[@]}"; do
		[[ -z "${b}" ]] && continue
		if ! command -v "${b}" >/dev/null 2>&1; then
			missing_bins+=("${b}")
		fi
	done

	if (( ${#missing_bins[@]} > 0 )); then
		log_err "missing binaries: ${missing_bins[*]}"
		return 2
	fi
	log_ok "binaries ok: ${bins_csv}"
}

# is_allowed_repo_external_path determines whether a symlinked CODESTYLE.md or its resolved absolute path is allowed to point outside the repository by matching against entries in `${root}/.codex/preflight-allowed-external-paths.txt` and the `PREFLIGHT_OVERRIDE_ALLOWED_EXTERNAL_PATHS` overrides.
# `root` is the repository root used for variable substitution; `match` is expected to be "CODESTYLE.md" (must be a symlink); `abs` is the resolved absolute path of `match`.
is_allowed_repo_external_path() {
	local root="$1"
	local match="$2"
	local abs="$3"
	local link_target=''
	local config_path="${root}/.codex/preflight-allowed-external-paths.txt"
	local candidate=''
	local candidate_abs=''
	if [[ "${match}" != "CODESTYLE.md" ]]; then
		return 1
	fi
	if [[ ! -L "${match}" ]]; then
		return 1
	fi

	link_target="$(readlink "${match}" 2>/dev/null || true)"
	case "${link_target}" in
		*/.codex/instructions/CODESTYLE.md) ;;
		*) return 1 ;;
	esac

	while IFS= read -r candidate; do
		[[ -z "${candidate}" ]] && continue
		candidate="${candidate//\$\{HOME\}/${HOME}}"
		candidate="${candidate//\$HOME/${HOME}}"
		candidate="${candidate//\$\{REPO_ROOT\}/${root}}"
		candidate="${candidate//\$REPO_ROOT/${root}}"
		if [[ "${link_target}" == "${candidate}" || "${abs}" == "${candidate}" ]]; then
			return 0
		fi
		if candidate_abs="$(
			python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "${candidate}" 2>/dev/null
		)" && [[ "${abs}" == "${candidate_abs}" ]]; then
			return 0
		fi
	done < <(
		{
			if [[ -f "${config_path}" ]]; then
				sed -e 's/#.*$//' -e '/^[[:space:]]*$/d' "${config_path}"
			fi
			if [[ -n "${PREFLIGHT_OVERRIDE_ALLOWED_EXTERNAL_PATHS:-}" ]]; then
				printf '%s\n' "${PREFLIGHT_OVERRIDE_ALLOWED_EXTERNAL_PATHS}" | tr ',' '\n'
			fi
		}
	)

	return 1
}

# check_paths validates that each path (comma-separated, supports globs) exists and is located inside the repository root.
# It treats unmatched globs as literal entries, resolves symlinks/real paths, and returns nonzero if any required path is missing or resolves outside `root` (except for allowed external exceptions).
# @param root repository root absolute path used as the containment boundary
# check_paths validates each comma-separated path or glob exists and resolves to a real path inside the given repository root, allowing explicitly approved external symlink targets; it logs a descriptive error and returns exit code 2 on missing paths, on paths that escape the repo root (and are not allowed), or on realpath resolution failures.
check_paths() {
	local root="$1"
	local paths_csv="$2"
	local -a paths=()
	local p

	IFS=',' read -r -a paths <<<"${paths_csv}"
	for p in "${paths[@]}"; do
		[[ -z "${p}" ]] && continue

		local -a matches=()
		local match
		shopt -s nullglob
		for match in ${p}; do
			matches+=("${match}")
		done
		shopt -u nullglob

		if (( ${#matches[@]} == 0 )); then
			matches+=("${p}")
		fi

		local found=0
		local abs
		for match in "${matches[@]}"; do
			if [[ -e "${match}" ]]; then
				found=1
				if ! abs="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "${match}")"; then
					log_err "failed to resolve path: ${match}"
					return 2
				fi
				if [[ "${abs}" != "${root}" && "${abs}" != "${root}"/* ]]; then
					if is_allowed_repo_external_path "${root}" "${match}" "${abs}"; then
						continue
					fi
					log_err "path escapes repo root: ${match} -> ${abs}"
					return 2
				fi
			fi
		done

		if (( found == 0 )); then
			log_err "missing path: ${p}"
			return 2
		fi
	done
	log_ok "paths ok: ${paths_csv}"
}

# run_local_memory_preflight_with_runner runs the given Local Memory helper command, appends a `--config` argument when a config path is available, prints the helper's output on success, writes the helper's output to stderr on failure, returns `0` on success, returns `3` when the output indicates a module-resolution/unknown-command error, and otherwise returns the helper's exit status.
run_local_memory_preflight_with_runner() {
	local runner_label="$1"
	shift
	local -a command=("$@")
	local config_path="${LOCAL_MEMORY_CONFIG_PATH:-${HOME}/.local-memory/config.yaml}"
	local output=''
	local status=0

	if [[ -n "${config_path}" ]]; then
		command+=(--config "${config_path}")
	fi

	if output="$("${command[@]}" 2>&1)"; then
		if [[ -n "${output}" ]]; then
			printf '%s\n' "${output}"
		fi
		return 0
	fi

	status=$?
	if [[ -n "${output}" ]]; then
		printf '%s\n' "${output}" >&2
	fi
	case "${output}" in
		*"Unknown command"*|*"local @brainwav/coding-harness could not be resolved"*|*"MODULE_NOT_FOUND"*|*"Cannot find module"*)
			return 3
			;;
	esac
	log_warn "Local Memory helper runner failed: ${runner_label}"
	return "${status}"
}

# run_local_memory_preflight_via_harness attempts to run the local-memory preflight using available harness runners in preferred order (repo source via pnpm+tsx, repo dist CLI via node, repo wrapper script, then global `harness`), returning the executed runner's exit status or `3` if no runner is available.
run_local_memory_preflight_via_harness() {
	local status=3

	if [[ -f "${WORKSPACE_ROOT}/src/dev/run-local-memory-preflight.ts" ]] && command -v pnpm >/dev/null 2>&1; then
		if command -v tsx >/dev/null 2>&1 || [[ -x "${WORKSPACE_ROOT}/node_modules/.bin/tsx" ]]; then
			run_local_memory_preflight_with_runner \
				"repo source helper (pnpm exec tsx src/dev/run-local-memory-preflight.ts)" \
				pnpm exec tsx "${WORKSPACE_ROOT}/src/dev/run-local-memory-preflight.ts"
			status=$?
			if [[ "${status}" -ne 3 ]]; then
				return "${status}"
			fi
		fi
	fi

	if [[ -f "${WORKSPACE_ROOT}/dist/cli.js" ]] && command -v node >/dev/null 2>&1; then
		run_local_memory_preflight_with_runner \
			"repo dist CLI (node dist/cli.js)" \
			node "${WORKSPACE_ROOT}/dist/cli.js" local-memory-preflight
		status=$?
		if [[ "${status}" -ne 3 ]]; then
			return "${status}"
		fi
	fi

	if [[ -x "${WORKSPACE_ROOT}/scripts/harness-cli.sh" ]]; then
		run_local_memory_preflight_with_runner \
			"repo wrapper (bash scripts/harness-cli.sh)" \
			bash "${WORKSPACE_ROOT}/scripts/harness-cli.sh" local-memory-preflight
		status=$?
		if [[ "${status}" -ne 3 ]]; then
			return "${status}"
		fi
	fi

	if command -v harness >/dev/null 2>&1; then
		run_local_memory_preflight_with_runner \
			"global npm harness ($(command -v harness))" \
			harness local-memory-preflight
		status=$?
		if [[ "${status}" -ne 3 ]]; then
			return "${status}"
		fi
	fi

	return 3
}

# preflight_local_memory_gold attempts to run a Local Memory preflight using available harness runners; if none are usable it falls back to the legacy shell preflight and returns the resulting exit status.
preflight_local_memory_gold() {
	local helper_status=0

	run_local_memory_preflight_via_harness
	helper_status=$?
	if [[ "${helper_status}" -eq 0 ]]; then
		return 0
	fi
	if [[ "${helper_status}" -ne 3 ]]; then
		return "${helper_status}"
	fi

	log_warn 'no harness Local Memory helper runner available; falling back to legacy shell implementation'
	if [[ ! -f "${LOCAL_MEMORY_FALLBACK_SCRIPT}" ]]; then
		log_err "missing Local Memory fallback script: ${LOCAL_MEMORY_FALLBACK_SCRIPT}"
		return 1
	fi
	# shellcheck source=/dev/null
	source "${LOCAL_MEMORY_FALLBACK_SCRIPT}"
	preflight_local_memory_shell_fallback
}

# run_preflight_profile constructs argument flags for the given stack, optional expected repo fragment, bins CSV, paths CSV, and local memory mode (defaults to "required"), then invokes main with those flags.
run_preflight_profile() {
	local stack="$1"
	local expected_repo="${2:-}"
	local bins_csv="${3:-}"
	local paths_csv="${4:-}"
	local local_memory_mode="${5:-required}"
	local -a args=(
		--stack "${stack}"
		--mode "${local_memory_mode}"
	)

	if [[ -n "${expected_repo}" ]]; then
		args+=(--repo-fragment "${expected_repo}")
	fi
	if [[ -n "${bins_csv}" ]]; then
		args+=(--bins "${bins_csv}")
	fi
	if [[ -n "${paths_csv}" ]]; then
		args+=(--paths "${paths_csv}")
	fi

	main "${args[@]}"
}

# preflight_repo runs the Codex preflight profile for a generic repository stack using sensible defaults.
# preflight_repo [expected_repo_fragment] [bins_csv] [paths_csv] [local_memory_mode]
# - expected_repo_fragment: optional substring to validate against the repository root (default: none).
# - bins_csv: comma-separated required executables (default: git,bash,sed,rg,jq,curl,python3).
# - paths_csv: comma-separated required repository files/paths (default includes CODESTYLE.md, CONTRIBUTING.md, Makefile, scripts, and preflight scripts).
# - local_memory_mode: one of off|optional|required (default: required).
preflight_repo() {
	run_preflight_profile \
		repo \
		"${1:-}" \
		"${2:-git,bash,sed,rg,jq,curl,python3}" \
		"${3:-CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh}" \
		"${4:-required}"
}

# preflight_js runs the preflight profile for the JavaScript (js) stack using defaults for expected repo fragment, required binaries, required repository paths, and local memory mode; positional arguments (expected_repo, bins_csv, paths_csv, local_memory_mode) override those defaults.
preflight_js() {
	run_preflight_profile \
		js \
		"${1:-}" \
		"${2:-git,bash,sed,rg,jq,curl,node,npm,python3}" \
		"${3:-package.json,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh}" \
		"${4:-required}"
}

# preflight_py runs the Codex preflight using the Python stack defaults; accepts optional arguments to override (1) expected repository fragment, (2) comma-separated binaries (default "git,bash,sed,rg,jq,curl,python3"), (3) comma-separated repository paths (default "pyproject.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh"), and (4) local memory mode (`off`|`optional`|`required`, default `required`).
preflight_py() {
	run_preflight_profile \
		py \
		"${1:-}" \
		"${2:-git,bash,sed,rg,jq,curl,python3}" \
		"${3:-pyproject.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh}" \
		"${4:-required}"
}

# preflight_rust runs the preflight profile for the Rust stack using sensible defaults for binaries, paths, and local-memory mode.
# 
# Arguments:
#   $1 - optional repository fragment to validate the workspace root contains (default: none).
#   $2 - optional comma-separated list of required binaries (default: "git,bash,sed,rg,jq,curl,python3,cargo").
#   $3 - optional comma-separated list of required repository paths/globs (default: "Cargo.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh").
#   $4 - local memory mode: one of "off", "optional", or "required" (default: "required").
preflight_rust() {
	run_preflight_profile \
		rust \
		"${1:-}" \
		"${2:-git,bash,sed,rg,jq,curl,python3,cargo}" \
		"${3:-Cargo.toml,CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh}" \
		"${4:-required}"
}

# preflight_repo_local_memory runs a repository preflight configured for the `repo` stack with Local Memory set to required, using sensible default binaries and path lists; optional positional arguments override `expected_repo`, `bins_csv`, and `paths_csv`.
preflight_repo_local_memory() {
	preflight_repo "${1:-}" "${2:-git,bash,sed,rg,jq,curl,python3}" "${3:-CODESTYLE.md,CONTRIBUTING.md,Makefile,scripts,scripts/codex-preflight.sh,scripts/codex-preflight-local-memory-legacy.sh,scripts/verify-work.sh,scripts/validate-codestyle.sh}" required
}

# main orchestrates the Codex preflight checks: it parses CLI arguments (legacy positional or flags), determines the repo stack and required binaries/paths (including overrides), verifies git and workspace expectations, runs binary and path validations, invokes the Local Memory preflight according to --mode (off|optional|required), and exits non‑zero on validation failures.
main() {
	local stack='auto'
	local local_memory_mode='required'
	local expected_repo=''
	local bins_csv=''
	local paths_csv=''

	if (( $# > 0 )) && [[ "${1}" != --* ]] && [[ "${1}" != '-h' ]]; then
		if (( $# > 3 )); then
			log_err "legacy positional mode accepts at most 3 arguments"
			usage >&2
			exit 2
		fi
		expected_repo="${1:-}"
		bins_csv="${2:-}"
		paths_csv="${3:-}"
		local_memory_mode='off'
		set --
	fi

	while (( $# > 0 )); do
		case "$1" in
			--stack)
				stack="${2:-}"
				shift 2
				;;
			--mode)
				local_memory_mode="${2:-}"
				shift 2
				;;
			--repo-fragment)
				expected_repo="${2:-}"
				shift 2
				;;
			--bins)
				bins_csv="${2:-}"
				shift 2
				;;
			--paths)
				paths_csv="${2:-}"
				shift 2
				;;
			-h|--help)
				usage
				exit 0
				;;
			*)
				log_err "unknown argument: $1"
				usage >&2
				exit 2
				;;
		esac
	done

	case "${local_memory_mode}" in
		off|optional|required) ;;
		*) log_err "invalid --mode: ${local_memory_mode}"; exit 2 ;;
	esac

	log_section 'Codex Preflight'
	echo "pwd: $(pwd)"

	if ! command -v git >/dev/null 2>&1; then
		log_err 'missing binary: git'
		exit 2
	fi

	local git_root
	if ! git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
		log_err 'not inside a git repo (git rev-parse failed)'
		exit 2
	fi
	if [[ -z "${git_root}" ]]; then
		log_err 'git rev-parse returned empty root'
		exit 2
	fi
	git_root="$(cd -- "${git_root}" && pwd -P)"
	echo "git root: ${git_root}"
	echo "workspace root: ${WORKSPACE_ROOT}"

	if [[ "${WORKSPACE_ROOT}" != "${git_root}" && "${WORKSPACE_ROOT}" != "${git_root}"/* ]]; then
		log_err "script workspace mismatch: ${WORKSPACE_ROOT} is not inside git root ${git_root}"
		exit 2
	fi
	if [[ -n "${expected_repo}" && "${WORKSPACE_ROOT}" != *"${expected_repo}"* ]]; then
		log_err "repo mismatch: expected fragment '${expected_repo}' in '${WORKSPACE_ROOT}'"
		exit 2
	fi

	cd "${WORKSPACE_ROOT}"

	if [[ "${stack}" == 'auto' ]]; then
		stack="$(detect_stack)"
	fi
	echo "stack: ${stack}"

	if [[ -z "${bins_csv}" ]]; then
		bins_csv="$(stack_bins_csv "${stack}")"
	fi
	if [[ -z "${paths_csv}" ]]; then
		paths_csv="$(stack_paths_csv "${stack}")"
	fi
	load_preflight_overrides "${PREFLIGHT_OVERRIDES_FILE}"
	bins_csv="$(append_csv_values "${bins_csv}" "${PREFLIGHT_OVERRIDE_BINS}")"
	paths_csv="$(append_csv_values "${paths_csv}" "${PREFLIGHT_OVERRIDE_PATHS}")"

	check_bins "${bins_csv}"
	check_paths "${WORKSPACE_ROOT}" "${paths_csv}"

	local branch_name
	branch_name="$(git -C "${WORKSPACE_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
	echo "git branch: ${branch_name:-HEAD}"
	echo "clean?: $(git -C "${WORKSPACE_ROOT}" status --porcelain -- . | wc -l | tr -d ' ') changes"

	if [[ "${local_memory_mode}" != 'off' ]]; then
		if ! preflight_local_memory_gold; then
			if [[ "${local_memory_mode}" == 'required' ]]; then
				log_err 'local-memory preflight failed (required mode)'
				exit 2
			fi
			log_warn 'local-memory preflight failed (optional mode)'
		fi
	fi

	log_ok 'preflight passed'
}

if ! is_script_sourced; then
	main "$@"
fi
