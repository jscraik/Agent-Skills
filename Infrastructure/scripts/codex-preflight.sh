#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
WORKSPACE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"

usage() {
	cat <<'USAGE'
Usage:
  ./Infrastructure/scripts/codex-preflight.sh [options]

Options:
  --stack <auto|repo|js|py|rust>    Stack mode. Default: auto
  --mode <off|optional|required>    Local Memory mode. Default: required
  --repo-fragment <text>            Require repo root to contain this fragment
  --bins <csv>                      Override required binaries
  --paths <csv>                     Override required paths
  -h, --help                        Show this help

Examples:
  ./Infrastructure/scripts/codex-preflight.sh
  ./Infrastructure/scripts/codex-preflight.sh --stack js
  ./Infrastructure/scripts/codex-preflight.sh --stack py --mode required
  ./Infrastructure/scripts/codex-preflight.sh --repo-fragment local-memory
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

extract_last_json_line() {
	local raw="${1:-}"
	printf '%s\n' "${raw}" | awk '/^\{/{line=$0} END{if (line != "") print line}'
}

extract_local_memory_rest_value() {
	local config_path="$1"
	local key="$2"
	awk -v wanted="${key}" '
		BEGIN { in_rest = 0 }
		/^[[:space:]]*rest_api:[[:space:]]*$/ { in_rest = 1; next }
		in_rest && /^[^[:space:]]/ { in_rest = 0 }
		in_rest && $1 == wanted ":" {
			sub(/^[^:]+:[[:space:]]*/, "", $0)
			gsub(/"/, "", $0)
			gsub(/[[:space:]]+#.*/, "", $0)
			gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
			print $0
			exit
		}
	' "${config_path}"
}

is_local_memory_pidfile_sandbox_block() {
	local output="${1:-}"
	[[ "${output}" == *"failed to write PID file"* && "${output}" == *"operation not permitted"* ]]
}

# wait_for_local_memory_health polls a health endpoint until it reports success or the maximum attempts elapse, printing the successful JSON response.
wait_for_local_memory_health() {
	local health_url="$1"
	local max_attempts="${2:-10}"
	local attempt=1
	local health_json=''
	local health_success='false'

	while (( attempt <= max_attempts )); do
		if health_json="$(curl -fsS "${health_url}" 2>/dev/null)"; then
			health_success="$(echo "${health_json}" | jq -r '.success // false')"
			if [[ "${health_success}" == 'true' ]]; then
				printf '%s\n' "${health_json}"
				return 0
			fi
		fi
		sleep 1
		attempt=$((attempt + 1))
	done
	return 1
}

# local_memory_rest_post_json posts a JSON payload to a REST endpoint, prints the response body, and returns success on HTTP 2xx.
# It retries up to `max_attempts` (default 4) when the response body indicates a transient Local Memory lock ("database is locked" or "SQLITE_BUSY").
# Parameters:
#   url - the target REST URL to POST to.
#   payload - the JSON payload string to send.
#   action_label - short label used in warning messages when retrying.
#   max_attempts - optional number of attempts before giving up (defaults to 4).
# Behavior:
#   - On HTTP 2xx: prints the response body and returns 0.
#   - On transient lock and attempts remain: logs a warning, waits 1s, and retries.
#   - Otherwise: prints the response body and returns 1.
local_memory_rest_post_json() {
	local url="$1"
	local payload="$2"
	local action_label="$3"
	local max_attempts="${4:-4}"
	local attempt=1
	local response=''
	local body=''
	local http_code=''

	while (( attempt <= max_attempts )); do
		response="$(curl -sS -H 'Content-Type: application/json' -d "${payload}" -w $'\n%{http_code}' "${url}" 2>&1)" || true
		http_code="${response##*$'\n'}"
		body="${response%$'\n'*}"

		if [[ "${http_code}" =~ ^2[0-9][0-9]$ ]]; then
			printf '%s\n' "${body}"
			return 0
		fi

		if [[ "${body}" == *"database is locked"* || "${body}" == *"SQLITE_BUSY"* ]]; then
			if (( attempt < max_attempts )); then
				log_warn "${action_label} hit transient Local Memory lock; retrying (${attempt}/${max_attempts})"
				sleep 1
				attempt=$((attempt + 1))
				continue
			fi
		fi

		printf '%s\n' "${body}"
		return 1
	done

	printf '%s\n' "${body}"
	return 1
}

# start_local_memory_daemon_if_needed attempts to start the local-memory daemon when it appears stopped and waits for the daemon health endpoint at the provided health_url to become healthy, returning a non-zero exit status on failure.
start_local_memory_daemon_if_needed() {
	local health_url="$1"
	local start_output=''
	local started=1

	log_warn 'local-memory status reported stopped; attempting daemon start'
	if ! start_output="$(local-memory start 2>&1)"; then
		if is_local_memory_pidfile_sandbox_block "${start_output}"; then
			log_warn 'local-memory start reported sandbox pidfile limits; continuing with REST health probe'
		else
			log_err 'local-memory start failed'
			if [[ -n "${start_output}" ]]; then
				echo "${start_output}" >&2
			fi
			return 1
		fi
	else
		started=0
	fi

	if [[ "${started}" -eq 0 ]]; then
		log_ok 'local-memory start command succeeded'
	fi
	if ! wait_for_local_memory_health "${health_url}" 12 >/dev/null; then
		log_err "local-memory daemon failed to become healthy at ${health_url} after start attempt"
		return 1
	fi
	return 0
}


make_tmp_file() {
	local tmp_root
	tmp_root="${TMPDIR:-/tmp}"
	mktemp "${tmp_root%/}/local-memory-preflight.XXXXXX"
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

stack_bins_csv() {
	case "$1" in
		js) echo 'git,bash,sed,rg,fd,jq,curl,node,npm,python3' ;;
		py) echo 'git,bash,sed,rg,fd,jq,curl,python3' ;;
		rust) echo 'git,bash,sed,rg,fd,jq,curl,python3,cargo' ;;
		repo) echo 'git,bash,sed,rg,fd,jq,curl,python3' ;;
		*) log_err "unknown stack: $1"; return 2 ;;
	esac
}

stack_paths_csv() {
	case "$1" in
		js) echo 'AGENTS.md,package.json,docs,docs/plans' ;;
		py) echo 'AGENTS.md,pyproject.toml,docs,docs/plans' ;;
		rust) echo 'AGENTS.md,Cargo.toml,docs,docs/plans' ;;
		repo) echo 'AGENTS.md,docs,docs/plans' ;;
		*) log_err "unknown stack: $1"; return 2 ;;
	esac
}

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

# preflight_local_memory_gold performs a comprehensive local-memory preflight: verifies required binaries and config policies, ensures the daemon/REST health, executes an observe→relate→search smoke cycle (with CLI then REST fallbacks), runs malformed and duplicate request checks, inspects daemon logs, and returns non‑zero on any critical failure.
preflight_local_memory_gold() {
	log_section "Local Memory Preflight"

	if ! command -v local-memory >/dev/null 2>&1; then
		log_err 'missing binary: local-memory'
		return 1
	fi
	if ! command -v jq >/dev/null 2>&1; then
		log_err 'missing binary: jq (required for local-memory checks)'
		return 1
	fi
	if ! command -v curl >/dev/null 2>&1; then
		log_err 'missing binary: curl (required for REST checks)'
		return 1
	fi

	local version
	version="$(local-memory --version 2>/dev/null | tr -d '\r')"
	echo "local-memory version: ${version}"

	local status_json
	if ! status_json="$(local-memory status --json 2>/dev/null)"; then
		log_err 'local-memory status failed'
		return 1
	fi
	status_json="$(extract_last_json_line "${status_json}")"
	if [[ -z "${status_json}" ]]; then
		log_err 'local-memory status returned no JSON payload'
		return 1
	fi

	local running
	running="$(echo "${status_json}" | jq -r '.data.running // .running // false')"

	local lm_config_path="${LOCAL_MEMORY_CONFIG_PATH:-${HOME}/.local-memory/config.yaml}"
	if [[ ! -f "${lm_config_path}" ]]; then
		log_err "local-memory config missing: ${lm_config_path}"
		echo '   Set LOCAL_MEMORY_CONFIG_PATH if your config lives elsewhere.' >&2
		return 1
	fi

	if ! rg -q '^[[:space:]]*host:[[:space:]]*"?127\.0\.0\.1"?([[:space:]]*#.*)?$' "${lm_config_path}"; then
		log_err 'local-memory config host policy failed: expected host: 127.0.0.1'
		echo "   file: ${lm_config_path}" >&2
		return 1
	fi
	if ! rg -q '^[[:space:]]*auto_port:[[:space:]]*false([[:space:]]*#.*)?$' "${lm_config_path}"; then
		log_err 'local-memory config auto_port policy failed: expected auto_port: false'
		echo "   file: ${lm_config_path}" >&2
		return 1
	fi
	log_ok "config host/auto_port policy ok: ${lm_config_path}"

	local rest_host
	rest_host="$(extract_local_memory_rest_value "${lm_config_path}" host)"
	rest_host="${rest_host:-127.0.0.1}"

	local rest_port
	rest_port="$(extract_local_memory_rest_value "${lm_config_path}" port)"
	rest_port="${rest_port:-3002}"
	if [[ ! "${rest_port}" =~ ^[0-9]+$ ]]; then
		log_err "invalid rest_api_port from config: ${rest_port}"
		return 1
	fi

	local health_url="http://${rest_host}:${rest_port}/api/v1/health"
	local health_json
	if [[ "${running}" != 'true' ]]; then
		if health_json="$(curl -fsS "${health_url}" 2>/dev/null)"; then
			if [[ "$(echo "${health_json}" | jq -r '.success // false')" == 'true' ]]; then
				log_warn "local-memory status reported stopped; REST health succeeded at ${health_url}"
				running='true'
			fi
		fi
	fi
	if [[ "${running}" != 'true' ]]; then
		if ! start_local_memory_daemon_if_needed "${health_url}"; then
			return 1
		fi
		running='true'
		health_json="$(wait_for_local_memory_health "${health_url}" 1 || true)"
	fi
	if [[ -z "${health_json:-}" ]] && ! health_json="$(curl -fsS "${health_url}")"; then
		log_err "REST health endpoint unreachable at ${health_url}"
		return 1
	fi
	if [[ "$(echo "${health_json}" | jq -r '.success // false')" != 'true' ]]; then
		log_err 'REST health endpoint returned success=false'
		return 1
	fi
	log_ok "REST health ok: ${health_url}"

	local probe
	probe="LM-PREFLIGHT-$(date +%Y%m%d-%H%M%S)-$$"
	local content_a="Preflight anchor ${probe}"
	local content_b="Preflight evidence ${probe}"
	local observe_url="http://127.0.0.1:${rest_port}/api/v1/observe"
	local relate_url="http://127.0.0.1:${rest_port}/api/v1/relate"
	local search_url="http://127.0.0.1:${rest_port}/api/v1/memories/search"

	local observe_a_json
	local observe_b_json
	local observe_a_output
	local observe_b_output
	if ! observe_a_output="$(local-memory observe "${content_a}" --domain 'coding-harness' --tags 'preflight,local-memory' --source 'codex_preflight' --json 2>&1)"; then
		if is_local_memory_pidfile_sandbox_block "${observe_a_output}"; then
			log_warn 'local-memory CLI smoke write skipped: sandbox blocked PID file write while daemon health was already verified'
			log_ok 'local-memory preflight passed'
			return 0
		fi
		log_warn 'observe A via CLI failed; falling back to REST observe endpoint'
		observe_a_output="$(jq -nc --arg c "${content_a}" \
			'{content:$c,domain:"coding-harness",source:"codex_preflight",tags:["preflight","local-memory"]}' |
			while IFS= read -r payload; do
				local_memory_rest_post_json "${observe_url}" "${payload}" 'observe A'
			done)" || {
			log_err 'observe A failed'
			if [[ -n "${observe_a_output}" ]]; then
				echo "${observe_a_output}" >&2
			fi
			return 1
		}
	fi
	observe_a_json="$(extract_last_json_line "${observe_a_output}")"
	if ! observe_b_output="$(local-memory observe "${content_b}" --domain 'coding-harness' --tags 'preflight,local-memory' --source 'codex_preflight' --json 2>&1)"; then
		log_warn 'observe B via CLI failed; falling back to REST observe endpoint'
		observe_b_output="$(jq -nc --arg c "${content_b}" \
			'{content:$c,domain:"coding-harness",source:"codex_preflight",tags:["preflight","local-memory"]}' |
			while IFS= read -r payload; do
				local_memory_rest_post_json "${observe_url}" "${payload}" 'observe B'
			done)" || {
			log_err 'observe B failed'
			if [[ -n "${observe_b_output}" ]]; then
				echo "${observe_b_output}" >&2
			fi
			return 1
		}
	fi
	observe_b_json="$(extract_last_json_line "${observe_b_output}")"

	local id_a
	local id_b
	id_a="$(echo "${observe_a_json}" | jq -r '.data.memory_id // .memory_id // .data.id // .id // empty')"
	id_b="$(echo "${observe_b_json}" | jq -r '.data.memory_id // .memory_id // .data.id // .id // empty')"
	if [[ -z "${id_a}" || -z "${id_b}" ]]; then
		log_err 'observe returned no memory IDs'
		return 1
	fi

	local relate_json
	if ! relate_json="$(local-memory relate "${id_a}" "${id_b}" --type 'references' --strength 0.8 --confirm --json 2>/dev/null)"; then
		log_warn 'relate via CLI failed; falling back to REST relate endpoint'
		relate_json="$(jq -nc --arg s "${id_a}" --arg t "${id_b}" \
			'{source_memory_id:$s,target_memory_id:$t,relationship_type:"references",strength:0.8}' |
			while IFS= read -r payload; do
				local_memory_rest_post_json "${relate_url}" "${payload}" 'relate'
			done)" || {
			log_err 'relate failed'
			return 1
		}
	fi
	relate_json="$(extract_last_json_line "${relate_json}")"
	local relationship_id
	relationship_id="$(echo "${relate_json}" | jq -r '.id // .data.id // .relationship_id // .data.relationship_id // empty')"
	local relate_ok
	relate_ok="$(echo "${relate_json}" | jq -r '.success // true')"
	if [[ "${relate_ok}" != 'true' ]]; then
		log_err 'relate reported failure'
		return 1
	fi

	local search_json
	if ! search_json="$(local-memory search "${probe}" --limit 10 --json 2>/dev/null)"; then
		log_warn 'search via CLI failed; falling back to REST search endpoint'
		search_json="$(jq -nc --arg q "${probe}" '{query:$q,limit:10}' |
			while IFS= read -r payload; do
				local_memory_rest_post_json "${search_url}" "${payload}" 'search'
			done)" || {
			log_err 'search failed'
			return 1
		}
	fi
	search_json="$(extract_last_json_line "${search_json}")"
	local search_hits
	search_hits="$(echo "${search_json}" | jq -r '
		if type == "array" then
			length
		else
			((try .results catch null) // (try .data.results catch null) // (try .data catch [])) |
			if type == "array" then length else 0 end
		end
	')"
	if [[ "${search_hits}" -lt 1 ]]; then
		log_err "search returned no results for probe ${probe}"
		return 1
	fi
	log_ok "smoke cycle ok: ids ${id_a}, ${id_b}; relationship ${relationship_id}"

	local malformed_output dup_output_1 dup_output_2
	malformed_output="$(make_tmp_file)" || {
		log_err 'failed to allocate temp file for malformed payload probe'
		return 1
	}
	dup_output_1="$(make_tmp_file)" || {
		log_err 'failed to allocate first temp file for duplicate payload probe'
		rm -f "${malformed_output}"
		return 1
	}
	dup_output_2="$(make_tmp_file)" || {
		log_err 'failed to allocate second temp file for duplicate payload probe'
		rm -f "${malformed_output}" "${dup_output_1}"
		return 1
	}
	trap 'rm -f "${malformed_output:-}" "${dup_output_1:-}" "${dup_output_2:-}"; trap - RETURN' RETURN

	local malformed_code
	malformed_code="$(curl -sS -o "${malformed_output}" -w '%{http_code}' \
		-H 'Content-Type: application/json' \
		-d '{"level":"observation"}' \
		"${observe_url}")"
	if [[ "${malformed_code}" -lt 400 ]]; then
		log_err "malformed payload did not return an error (HTTP ${malformed_code})"
		return 1
	fi
	log_ok "malformed payload rejected: HTTP ${malformed_code}"

	local dup_payload
	dup_payload="$(jq -nc --arg c "${content_a}" '{content:$c,domain:"coding-harness",source:"codex_preflight",tags:["preflight","duplicate-check"]}')"
	local dup_code_1
	local dup_code_2
	dup_code_1="$(curl -sS -o "${dup_output_1}" -w '%{http_code}' \
		-H 'Content-Type: application/json' \
		-d "${dup_payload}" \
		"${observe_url}")"
	dup_code_2="$(curl -sS -o "${dup_output_2}" -w '%{http_code}' \
		-H 'Content-Type: application/json' \
		-d "${dup_payload}" \
		"${observe_url}")"
	echo "ℹ️ duplicate behavior snapshot: first=${dup_code_1}, second=${dup_code_2}"

	local daemon_log="${HOME}/.local-memory/daemon.log"
	if [[ -f "${daemon_log}" ]]; then
		local migration_line
		migration_line="$(tail -n 300 "${daemon_log}" | rg -n '"pending_migrations"|"target_version"|"current_version"' -m 1 || true)"
		if [[ -n "${migration_line}" ]]; then
			echo 'ℹ️ migration status signal found in daemon log'
		else
			log_warn 'no migration status signal found in recent daemon log tail'
		fi
	else
		log_warn "daemon log not found at ${daemon_log}"
	fi

	log_ok 'local-memory preflight passed'
}

main() {
	local stack='auto'
	local local_memory_mode='required'
	local expected_repo=''
	local bins_csv=''
	local paths_csv=''

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

	local root
	if ! root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
		log_err 'not inside a git repo (git rev-parse failed)'
		exit 2
	fi
	if [[ -z "${root}" ]]; then
		log_err 'git rev-parse returned empty root'
		exit 2
	fi
	root="$(cd -- "${root}" && pwd -P)"
	echo "repo root: ${root}"

	if [[ "${root}" != "${WORKSPACE_ROOT}" ]]; then
		log_err "script workspace mismatch: expected ${WORKSPACE_ROOT}"
		exit 2
	fi
	if [[ -n "${expected_repo}" && "${root}" != *"${expected_repo}"* ]]; then
		log_err "repo mismatch: expected fragment '${expected_repo}' in '${root}'"
		exit 2
	fi

	cd "${root}"

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

	check_bins "${bins_csv}"
	check_paths "${root}" "${paths_csv}"

	echo "git branch: $(git rev-parse --abbrev-ref HEAD)"
	echo "clean?: $(git status --porcelain | wc -l | tr -d ' ') changes"

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

main "$@"
