#!/usr/bin/env bash

set -euo pipefail

# extract_last_json_line prints the last input line that begins with `{`
# (commonly the final JSON object line) to stdout. If no such line exists it
# extract_last_json_line prints the last line that begins with `{` from the given raw string, or prints nothing if no such line exists.
extract_last_json_line() {
	local raw="${1:-}"
	printf '%s\n' "${raw}" | awk '/^\{/{line=$0} END{if (line != "") print line}'
}

# extract_local_memory_rest_value extracts the value for a key from the `rest_api:` section of a YAML-like config file and echoes it.
# It searches only within the indented `rest_api:` block, stops at the next top-level line, and prints the first matching key's value.
# The printed value has surrounding quotes removed, trailing inline comments stripped, and leading/trailing whitespace trimmed.
# CONFIG_PATH is the path to the config file. KEY is the name of the key to look up (for example `host` or `port`).
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

# is_local_memory_pidfile_sandbox_block returns success if the provided output contains both "failed to write PID file" and "operation not permitted".
is_local_memory_pidfile_sandbox_block() {
	local output="${1:-}"
	[[ "${output}" == *"failed to write PID file"* && "${output}" == *"operation not permitted"* ]]
}

# wait_for_local_memory_health waits for the local-memory REST health endpoint to report `.success == true` and prints the returned health JSON when successful.
wait_for_local_memory_health() {
	local health_url="$1"
	local max_attempts="${2:-10}"
	local attempt=1
	local health_json=''
	local health_success='false'

	while (( attempt <= max_attempts )); do
		if health_json="$(curl -fsS --connect-timeout 2 --max-time 5 "${health_url}" 2>/dev/null)"; then
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

# start_local_memory_daemon_if_needed attempts to start the local-memory daemon when it's not running and waits until the provided health URL reports healthy, returning non-zero on failure.
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

# make_tmp_file creates a temporary file in ${TMPDIR:-/tmp} with prefix 'local-memory-preflight.' and echoes the new file path.
make_tmp_file() {
	mktemp "${TMPDIR:-/tmp}/local-memory-preflight.XXXXXX"
}

# cleanup_tmp_files removes files for each non-empty path argument using `rm -f`.
cleanup_tmp_files() {
	local path
	for path in "$@"; do
		[[ -n "${path}" ]] || continue
		rm -f -- "${path}"
	done
}

# set_cleanup_trap installs a RETURN trap that invokes `cleanup_tmp_files` with the provided file paths to remove those temporary files when the surrounding function or script returns.
set_cleanup_trap() {
	local trap_cmd='cleanup_tmp_files'
	local path
	for path in "$@"; do
		trap_cmd+=" $(printf '%q' "${path}")"
	done
	trap "${trap_cmd}" RETURN
}

# create_tmp_file creates a temporary file using mktemp, echoes its path to stdout, and returns non-zero on failure; the optional label is included in error messages.
create_tmp_file() {
	local label="$1"
	local tmp_file=''

	if ! tmp_file="$(make_tmp_file)"; then
		log_err "mktemp failed for ${label}"
		return 1
	fi
	if [[ -z "${tmp_file}" ]]; then
		log_err "mktemp returned empty path for ${label}"
		return 1
	fi
	printf '%s\n' "${tmp_file}"
}

# post_json_to_file sends a JSON payload via HTTP POST to a URL, writes the response body to the specified file, and echoes the HTTP status code.
post_json_to_file() {
	local output_path="$1"
	local url="$2"
	local payload="$3"

	curl -sS -o "${output_path}" -w '%{http_code}' \
		-H 'Content-Type: application/json' \
		-d "${payload}" \
		"${url}"
}

# preflight_local_memory_shell_fallback performs a local-memory preflight: verifies required binaries and config policy, ensures or starts the daemon until REST health is OK, exercises observe/relationship/search endpoints (including malformed and duplicate checks), inspects daemon logs for migration signals, and returns non-zero on any failure.
preflight_local_memory_shell_fallback() {
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

	local rest_host
	rest_host="$(extract_local_memory_rest_value "${lm_config_path}" host)"
	if [[ "${rest_host}" != '127.0.0.1' ]]; then
		log_err 'local-memory config host policy failed: expected host: 127.0.0.1'
		echo "   file: ${lm_config_path}" >&2
		return 1
	fi

	local rest_auto_port
	rest_auto_port="$(extract_local_memory_rest_value "${lm_config_path}" auto_port)"
	if [[ "${rest_auto_port}" != 'false' ]]; then
		log_err 'local-memory config auto_port policy failed: expected auto_port: false'
		echo "   file: ${lm_config_path}" >&2
		return 1
	fi

	local rest_port
	rest_port="$(extract_local_memory_rest_value "${lm_config_path}" port)"
	rest_port="${rest_port:-3002}"
	if [[ ! "${rest_port}" =~ ^[0-9]+$ ]]; then
		log_err "invalid rest_api_port from config: ${rest_port}"
		return 1
	fi
	log_ok "config host/auto_port policy ok: ${lm_config_path}"

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
	local observe_url="http://${rest_host}:${rest_port}/api/v1/observe"
	local relationships_url="http://${rest_host}:${rest_port}/api/v1/relationships"
	local relate_url="http://${rest_host}:${rest_port}/api/v1/relate"
	local search_url="http://${rest_host}:${rest_port}/api/v1/memories/search"
	local malformed_output=''
	local dup_output_1=''
	local dup_output_2=''
	local observe_a_output=''
	local observe_b_output=''
	local relate_output=''
	local search_output=''

	if ! malformed_output="$(create_tmp_file 'malformed payload response')"; then
		return 1
	fi
	if ! dup_output_1="$(create_tmp_file 'duplicate response one')"; then
		cleanup_tmp_files "${malformed_output}"
		return 1
	fi
	if ! dup_output_2="$(create_tmp_file 'duplicate response two')"; then
		cleanup_tmp_files "${malformed_output}" "${dup_output_1}"
		return 1
	fi
	if ! observe_a_output="$(create_tmp_file 'observe response A')"; then
		cleanup_tmp_files "${malformed_output}" "${dup_output_1}" "${dup_output_2}"
		return 1
	fi
	if ! observe_b_output="$(create_tmp_file 'observe response B')"; then
		cleanup_tmp_files "${malformed_output}" "${dup_output_1}" "${dup_output_2}" "${observe_a_output}"
		return 1
	fi
	if ! relate_output="$(create_tmp_file 'relationship response')"; then
		cleanup_tmp_files "${malformed_output}" "${dup_output_1}" "${dup_output_2}" "${observe_a_output}" "${observe_b_output}"
		return 1
	fi
	if ! search_output="$(create_tmp_file 'search response')"; then
		cleanup_tmp_files "${malformed_output}" "${dup_output_1}" "${dup_output_2}" "${observe_a_output}" "${observe_b_output}" "${relate_output}"
		return 1
	fi
	set_cleanup_trap \
		"${malformed_output}" \
		"${dup_output_1}" \
		"${dup_output_2}" \
		"${observe_a_output}" \
		"${observe_b_output}" \
		"${relate_output}" \
		"${search_output}"

	local observe_a_payload
	observe_a_payload="$(jq -nc --arg c "${content_a}" '{content:$c,domain:"coding-harness",source:"codex_preflight",tags:["preflight","local-memory"]}')"
	local observe_b_payload
	observe_b_payload="$(jq -nc --arg c "${content_b}" '{content:$c,domain:"coding-harness",source:"codex_preflight",tags:["preflight","local-memory"]}')"

	local observe_code_a
	local observe_code_b
	if ! observe_code_a="$(post_json_to_file "${observe_a_output}" "${observe_url}" "${observe_a_payload}")"; then
		log_err 'observe A failed'
		return 1
	fi
	if [[ "${observe_code_a}" -ge 400 ]]; then
		log_err "observe A returned HTTP ${observe_code_a}"
		return 1
	fi
	if ! observe_code_b="$(post_json_to_file "${observe_b_output}" "${observe_url}" "${observe_b_payload}")"; then
		log_err 'observe B failed'
		return 1
	fi
	if [[ "${observe_code_b}" -ge 400 ]]; then
		log_err "observe B returned HTTP ${observe_code_b}"
		return 1
	fi

	local observe_a_json
	local observe_b_json
	observe_a_json="$(cat "${observe_a_output}")"
	observe_b_json="$(cat "${observe_b_output}")"

	local id_a
	local id_b
	id_a="$(echo "${observe_a_json}" | jq -r '.id // .data.id // .memory_id // .data.memory_id // empty')"
	id_b="$(echo "${observe_b_json}" | jq -r '.id // .data.id // .memory_id // .data.memory_id // empty')"
	if [[ -z "${id_a}" || -z "${id_b}" ]]; then
		log_err 'observe returned no memory IDs'
		return 1
	fi

	local relate_payload
	relate_payload="$(jq -nc \
		--arg source "${id_a}" \
		--arg target "${id_b}" \
		'{source_memory_id:$source,target_memory_id:$target,relationship_type:"references",strength:0.8,context:"codex preflight smoke cycle"}')"
	local relate_code
	if ! relate_code="$(post_json_to_file "${relate_output}" "${relationships_url}" "${relate_payload}")"; then
		log_err 'relationships create failed'
		return 1
	fi
	if [[ "${relate_code}" -ge 400 ]]; then
		if ! relate_code="$(post_json_to_file "${relate_output}" "${relate_url}" "${relate_payload}")"; then
			log_err 'relate fallback failed'
			return 1
		fi
	fi
	if [[ "${relate_code}" -ge 400 ]]; then
		log_err "relationship create returned HTTP ${relate_code}"
		return 1
	fi
	local relate_json
	relate_json="$(cat "${relate_output}")"
	local relationship_id
	relationship_id="$(echo "${relate_json}" | jq -r '.id // .data.id // .relationship_id // .data.relationship_id // empty')"
	local relate_ok
	relate_ok="$(echo "${relate_json}" | jq -r '.success // true')"
	if [[ "${relate_ok}" != 'true' ]]; then
		log_err 'relate reported failure'
		return 1
	fi

	local search_payload
	search_payload="$(jq -nc --arg query "${probe}" '{query:$query,limit:10,response_format:"ids_only"}')"
	local search_code=''
	local search_attempt=1
	while (( search_attempt <= 5 )); do
		if ! search_code="$(post_json_to_file "${search_output}" "${search_url}" "${search_payload}")"; then
			log_err 'search failed'
			return 1
		fi
		if [[ "${search_code}" -ge 400 ]]; then
			log_err "search returned HTTP ${search_code}"
			return 1
		fi
		local search_json_attempt
		search_json_attempt="$(cat "${search_output}")"
		local search_hits_attempt
		search_hits_attempt="$(echo "${search_json_attempt}" | jq -r '
			if type == "array" then length
			elif .search_info.total_results != null then .search_info.total_results
			elif .results then (.results | length)
			elif .data.results then (.data.results | length)
			elif .data then (.data | length)
			else 0 end
		')"
		if [[ "${search_hits_attempt}" -ge 1 ]]; then
			break
		fi
		sleep 0.2
		search_attempt=$((search_attempt + 1))
	done
	local search_json
	search_json="$(cat "${search_output}")"
	local search_hits
	search_hits="$(echo "${search_json}" | jq -r '
		if type == "array" then length
		elif .search_info.total_results != null then .search_info.total_results
		elif .results then (.results | length)
		elif .data.results then (.data.results | length)
		elif .data then (.data | length)
		else 0 end
	')"
	if [[ "${search_hits}" -lt 1 ]]; then
		log_err "search returned no results for probe ${probe}"
		return 1
	fi
	log_ok "smoke cycle ok: ids ${id_a}, ${id_b}; relationship ${relationship_id}"

	local malformed_code
	malformed_code="$(post_json_to_file "${malformed_output}" "${observe_url}" '{"level":"observation"}')"
	if [[ "${malformed_code}" -lt 400 ]]; then
		log_err "malformed payload did not return an error (HTTP ${malformed_code})"
		return 1
	fi
	log_ok "malformed payload rejected: HTTP ${malformed_code}"

	local dup_payload
	dup_payload="$(jq -nc --arg c "${content_a}" '{content:$c,domain:"coding-harness",source:"codex_preflight",tags:["preflight","duplicate-check"]}')"
	local dup_code_1
	local dup_code_2
	dup_code_1="$(post_json_to_file "${dup_output_1}" "${observe_url}" "${dup_payload}")"
	dup_code_2="$(post_json_to_file "${dup_output_2}" "${observe_url}" "${dup_payload}")"
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
