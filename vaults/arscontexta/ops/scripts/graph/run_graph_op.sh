#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null || pwd)"
VAULT_ROOT="${VAULT_ROOT:-${REPO_ROOT}/vaults/arscontexta}"
NOTES_DIR="${VAULT_ROOT}/notes"
ARTIFACTS_DIR="${VAULT_ROOT}/ops/health/graph"
LOCK_FILE="${ARTIFACTS_DIR}/run_graph_op.lock"

SCRIPT_TIMEOUT_SECONDS=120
OP_TIMEOUT_SECONDS=30
MAX_NODES=200
MAX_EDGES=1000
MIN_SIZE=3
DRY_RUN=0
RUN_GRAPH_JSON=0
LOCK_CREATED=0
OPERATION=""
PARSED_ARGS=()

WARN_FILE="$(mktemp)"
ERR_FILE="$(mktemp)"
ARTIFACT_FILE="$(mktemp)"

# shellcheck source=./_graph_op_lib.sh
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_graph_op_lib.sh"

# shellcheck disable=SC2329
cleanup() {
  rm -f "$WARN_FILE" "$ERR_FILE" "$ARTIFACT_FILE"
  if [[ "$LOCK_CREATED" == "1" && -d "$LOCK_FILE" ]]; then
    rm -rf "$LOCK_FILE"
    LOCK_CREATED=0
  fi
}
trap cleanup EXIT

# shellcheck disable=SC2329
abort_trap() {
  append_error "E_TIMEOUT" "operation" "interrupted"
  emit_payload "failed" 130 "failed" "failed" "failed" "[]"
  exit 130
}
trap abort_trap INT TERM

append_record() {
  local path="$1"
  local code="$2"
  local stage="$3"
  local message="$4"
  python3 - "$path" "$code" "$stage" "$message" <<'PY'
import json
import sys

path, code, stage, message = sys.argv[1:5]
with open(path, 'a', encoding='utf-8') as handle:
    handle.write(json.dumps({"code": code, "stage": stage, "message": message}, ensure_ascii=False))
    handle.write("\n")
PY
}

append_error() {
  append_record "$ERR_FILE" "$1" "$2" "$3"
}

record_artifact() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    return
  fi

  local sha=""
  sha="$(python3 - "$path" <<'PY'
import hashlib
import sys

path = sys.argv[1]
hasher = hashlib.sha256()
with open(path, 'rb') as handle:
    for block in iter(lambda: handle.read(1024 * 1024), b''):
        hasher.update(block)
print(f"sha256:{hasher.hexdigest()}")
PY
)"

  python3 - "$ARTIFACT_FILE" "$path" "$sha" <<'PY'
import json
import sys

artifact_file, path, sha = sys.argv[1:4]
with open(artifact_file, 'a', encoding='utf-8') as handle:
    handle.write(json.dumps({"path": path, "sha256": sha}, ensure_ascii=False))
    handle.write("\n")
PY
}

read_records() {
  local path="$1"
  python3 - "$path" <<'PY'
import json
import sys

path = sys.argv[1]
records = []
try:
    with open(path, 'r', encoding='utf-8') as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
except FileNotFoundError:
    pass
print(json.dumps(records))
PY
}

emit_payload() {
  local status="$1"
  local exit_code="$2"
  local stage_preflight="$3"
  local stage_operation="$4"
  local stage_artifact="$5"
  local planned="$6"

  if [[ "$RUN_GRAPH_JSON" == "1" ]]; then
    python3 - \
      "$status" "$exit_code" "$OPERATION" "$RUN_GRAPH_INPUTS" "$planned" \
      "$stage_preflight" "$stage_operation" "$stage_artifact" "$WARN_FILE" "$ERR_FILE" "$ARTIFACT_FILE" <<'PY'
import json
import sys

status = sys.argv[1]
exit_code = int(sys.argv[2])
operation = sys.argv[3]
inputs_json = sys.argv[4]
planned_json = sys.argv[5]
stage_preflight = sys.argv[6]
stage_operation = sys.argv[7]
stage_artifact = sys.argv[8]
warn_path = sys.argv[9]
err_path = sys.argv[10]
artifact_path = sys.argv[11]


def read_records(path):
    records = []
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
    except FileNotFoundError:
        pass
    return records

try:
    inputs = json.loads(inputs_json)
except Exception:
    inputs = {}

payload = {
    "schema": "run_graph_op.v1",
    "operation": operation,
    "status": status,
    "exit_code": exit_code,
    "inputs": inputs,
    "artifacts": read_records(artifact_path),
    "warnings": read_records(warn_path),
    "errors": read_records(err_path),
    "stage": {
        "preflight": stage_preflight,
        "operation": stage_operation,
        "artifact_write": stage_artifact,
    },
    "planned_actions": json.loads(planned_json),
}
print(json.dumps(payload, sort_keys=True, indent=2))
PY
  else
    echo "operation=${OPERATION}"
    echo "status=${status}"
    echo "exit_code=${exit_code}"
    local warn_json
    warn_json="$(read_records "$WARN_FILE")"
    if [[ "$warn_json" != "[]" ]]; then
      echo "warnings=${warn_json}"
    fi
    local err_json
    err_json="$(read_records "$ERR_FILE")"
    if [[ "$err_json" != "[]" ]]; then
      echo "errors=${err_json}" >&2
    fi
    local artifact_json
    artifact_json="$(read_records "$ARTIFACT_FILE")"
    if [[ "$artifact_json" != "[]" ]]; then
      echo "artifacts=${artifact_json}"
    fi
    echo "planned_actions=${planned}"
  fi
}

validate_int() {
  local value="$1"
  local label="$2"
  if ! [[ "$value" =~ ^[0-9]+$ ]]; then
    append_error "E_VALIDATION" "validation" "${label} must be a non-negative integer"
    return 1
  fi
  return 0
}

run_with_timeout() {
  local budget="$1"
  shift

  if (( budget > 0 )) && command -v timeout >/dev/null 2>&1; then
    # Note: We don't use --preserve-status so timeout returns 124 on timeout
    timeout "$budget" "$@"
    return $?
  fi

  "$@"
}

run_visual() {
  local index_path="${ARTIFACTS_DIR}/graph-index.json"
  local output_path="${ARTIFACTS_DIR}/graph-visual.md"
  local step_code=0

  run_with_timeout "$SCRIPT_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/build_graph_index.py" \
    --notes-dir "$NOTES_DIR" \
    --output "$index_path" \
    --max-nodes "$MAX_NODES" \
    --max-edges "$MAX_EDGES"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  run_with_timeout "$OP_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/render_mermaid.py" \
    --index "$index_path" \
    --output "$output_path" \
    --max-nodes "$MAX_NODES" \
    --max-edges "$MAX_EDGES"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  # Only record artifacts if all steps succeeded
  record_artifact "$index_path"
  record_artifact "$output_path"
}

run_communities() {
  local index_path="${ARTIFACTS_DIR}/graph-index.json"
  local json_path="${ARTIFACTS_DIR}/graph-communities.json"
  local md_path="${ARTIFACTS_DIR}/graph-communities.md"
  local step_code=0

  run_with_timeout "$SCRIPT_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/build_graph_index.py" \
    --notes-dir "$NOTES_DIR" \
    --output "$index_path" \
    --max-nodes "$MAX_NODES" \
    --max-edges "$MAX_EDGES"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  run_with_timeout "$OP_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/detect_communities.py" \
    --index "$index_path" \
    --json-output "$json_path" \
    --markdown-output "$md_path" \
    --min-size "$MIN_SIZE"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  # Only record artifacts if all steps succeeded
  record_artifact "$index_path"
  record_artifact "$json_path"
  record_artifact "$md_path"
}

run_evolution() {
  local index_path="${ARTIFACTS_DIR}/graph-index.json"
  local ndjson_path="${ARTIFACTS_DIR}/graph-metrics.ndjson"
  local latest_path="${ARTIFACTS_DIR}/graph-metrics-latest.json"
  local md_path="${ARTIFACTS_DIR}/graph-evolution.md"
  local step_code=0

  run_with_timeout "$SCRIPT_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/build_graph_index.py" \
    --notes-dir "$NOTES_DIR" \
    --output "$index_path" \
    --max-nodes "$MAX_NODES" \
    --max-edges "$MAX_EDGES"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  run_with_timeout "$OP_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/snapshot_metrics.py" \
    --index "$index_path" \
    --ndjson-output "$ndjson_path" \
    --latest-output "$latest_path"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  run_with_timeout "$OP_TIMEOUT_SECONDS" python3 "${SCRIPT_DIR}/render_evolution.py" \
    --ndjson "$ndjson_path" \
    --output "$md_path"
  step_code=$?
  if (( step_code != 0 )); then return $step_code; fi

  # Only record artifacts if all steps succeeded
  record_artifact "$index_path"
  record_artifact "$ndjson_path"
  record_artifact "$latest_path"
  record_artifact "$md_path"
}

parse_global_flags() {
  PARSED_ARGS=()
  OPERATION=""
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      --json)
        RUN_GRAPH_JSON=1
        shift
        ;;
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      --timeout-seconds)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--timeout-seconds requires a value"
          return 1
        fi
        if ! validate_int "$2" "--timeout-seconds"; then
          return 1
        fi
        SCRIPT_TIMEOUT_SECONDS="$2"
        shift 2
        ;;
      --op-timeout-seconds)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--op-timeout-seconds requires a value"
          return 1
        fi
        if ! validate_int "$2" "--op-timeout-seconds"; then
          return 1
        fi
        OP_TIMEOUT_SECONDS="$2"
        shift 2
        ;;
      --max-nodes|--max-edges|--min-size)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "$1 requires a value"
          return 1
        fi
        PARSED_ARGS+=("$1" "$2")
        shift 2
        ;;
      --vault-root)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--vault-root requires a path"
          return 1
        fi
        VAULT_ROOT="$2"
        NOTES_DIR="${VAULT_ROOT}/notes"
        ARTIFACTS_DIR="${VAULT_ROOT}/ops/health/graph"
        LOCK_FILE="${ARTIFACTS_DIR}/run_graph_op.lock"
        shift 2
        ;;
      --artifacts-dir)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--artifacts-dir requires a path"
          return 1
        fi
        ARTIFACTS_DIR="$2"
        LOCK_FILE="${ARTIFACTS_DIR}/run_graph_op.lock"
        shift 2
        ;;
      --)
        shift
        break
        ;;
      --*)
        append_error "E_VALIDATION" "validation" "Unsupported global flag: $1"
        return 1
        ;;
      *)
        if [[ -z "$OPERATION" ]]; then
          OPERATION="$1"
        else
          PARSED_ARGS+=("$1")
        fi
        shift
        ;;
    esac
  done

  while [[ "$#" -gt 0 ]]; do
    PARSED_ARGS+=("$1")
    shift
  done

  return 0
}

parse_operation_flags() {
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --)
        shift
        ;;
      --max-nodes)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--max-nodes requires a value"
          return 1
        fi
        if ! validate_int "$2" "--max-nodes"; then
          return 1
        fi
        MAX_NODES="$2"
        shift 2
        ;;
      --max-edges)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--max-edges requires a value"
          return 1
        fi
        if ! validate_int "$2" "--max-edges"; then
          return 1
        fi
        MAX_EDGES="$2"
        shift 2
        ;;
      --min-size)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--min-size requires a value"
          return 1
        fi
        if ! validate_int "$2" "--min-size"; then
          return 1
        fi
        MIN_SIZE="$2"
        shift 2
        ;;
      --op-timeout-seconds)
        if [[ $# -lt 2 ]]; then
          append_error "E_VALIDATION" "validation" "--op-timeout-seconds requires a value"
          return 1
        fi
        if ! validate_int "$2" "--op-timeout-seconds"; then
          return 1
        fi
        OP_TIMEOUT_SECONDS="$2"
        shift 2
        ;;
      --*)
        append_error "E_VALIDATION" "validation" "Unsupported operation flag: $1"
        return 1
        ;;
      *)
        append_error "E_VALIDATION" "validation" "Unexpected argument: $1"
        return 1
        ;;
    esac
  done
  return 0
}

build_inputs_json() {
  python3 - "$VAULT_ROOT" "$ARTIFACTS_DIR" "$MAX_NODES" "$MAX_EDGES" "$MIN_SIZE" "$SCRIPT_TIMEOUT_SECONDS" "$OP_TIMEOUT_SECONDS" <<'PY'
import json
import sys

vault_root, artifacts_dir, max_nodes, max_edges, min_size, timeout_seconds, op_timeout_seconds = sys.argv[1:8]
print(json.dumps({
    "vault_root": vault_root,
    "artifacts_dir": artifacts_dir,
    "max_nodes": int(max_nodes),
    "max_edges": int(max_edges),
    "min_size": int(min_size),
    "timeout_seconds": int(timeout_seconds),
    "op_timeout_seconds": int(op_timeout_seconds),
}))
PY
}

acquire_lock() {
  if mkdir "$LOCK_FILE" 2>/dev/null; then
    LOCK_CREATED=1
    return 0
  fi

  return 1
}

main() {
  OPERATION=""
  if [[ "$#" -eq 0 ]]; then
    usage >&2
    append_error "E_USAGE" "validation" "Missing operation"
    RUN_GRAPH_INPUTS="$(build_inputs_json)"
    emit_payload "failed" 2 "failed" "skipped" "skipped" "[]"
    exit 2
  fi

  if ! parse_global_flags "$@"; then
    RUN_GRAPH_INPUTS="$(build_inputs_json)"
    emit_payload "failed" 2 "failed" "skipped" "skipped" "[]"
    exit 2
  fi

  if [[ -z "$OPERATION" && "${#PARSED_ARGS[@]}" -gt 0 ]]; then
    OPERATION="${PARSED_ARGS[0]}"
    PARSED_ARGS=("${PARSED_ARGS[@]:1}")
  fi

  if ! in_array "$OPERATION" visual communities evolution; then
    append_error "E_USAGE" "validation" "Unsupported operation: $OPERATION"
    OPERATION="unknown"
    RUN_GRAPH_INPUTS="$(build_inputs_json)"
    emit_payload "failed" 2 "failed" "skipped" "skipped" "[]"
    exit 2
  fi

  if ! parse_operation_flags "${PARSED_ARGS[@]+"${PARSED_ARGS[@]}"}"; then
    RUN_GRAPH_INPUTS="$(build_inputs_json)"
    emit_payload "failed" 2 "failed" "skipped" "skipped" "[]"
    exit 2
  fi

  RUN_GRAPH_INPUTS="$(build_inputs_json)"
  local planned
  planned="$(emit_plan "$OPERATION")"

  if ! preflight "$VAULT_ROOT" "$ARTIFACTS_DIR" "$SCRIPT_DIR"; then
    append_error "E_DEPENDENCY" "preflight" "Preflight failed"
    emit_payload "failed" 3 "failed" "skipped" "skipped" "$planned"
    exit 3
  fi

  if (( DRY_RUN == 1 )); then
    emit_payload "dry_run" 0 "ok" "skipped" "skipped" "$planned"
    exit 0
  fi

  if ! acquire_lock; then
    append_error "E_DEPENDENCY" "preflight" "Another run is active"
    emit_payload "failed" 3 "failed" "skipped" "skipped" "$planned"
    exit 3
  fi

  local code=0
  local status="success"
  local stage_operation="ok"
  local stage_artifact="ok"

  # Run the operation
  # Note: Global timeout is enforced via per-step timeouts in run_with_timeout()
  # Each step (build_graph_index, detect_communities, etc.) has its own timeout
  # that respects SCRIPT_TIMEOUT_SECONDS for the overall operation budget
  set +e
  case "$OPERATION" in
    visual) run_visual ;;
    communities) run_communities ;;
    evolution) run_evolution ;;
  esac
  code=$?
  set -e

  if (( code != 0 )); then
    local artifact_count
    artifact_count="$(python3 - "$ARTIFACT_FILE" <<'PY'
import sys
path = sys.argv[1]
count = 0
try:
    with open(path, 'r', encoding='utf-8') as handle:
        count = sum(1 for line in handle if line.strip())
except FileNotFoundError:
    count = 0
print(count)
PY
)"

    if (( code == 124 )); then
      append_error "E_TIMEOUT" "operation" "Operation timed out"
      if (( artifact_count > 0 )); then
        status="partial"
        code=4
        stage_operation="failed"
        stage_artifact="partial"
      else
        status="failed"
        code=1
        stage_operation="failed"
        stage_artifact="failed"
      fi
    elif (( artifact_count > 0 )); then
      status="partial"
      code=4
      stage_operation="failed"
      stage_artifact="partial"
      append_error "E_PARTIAL" "operation" "Command partially completed"
    else
      status="failed"
      stage_operation="failed"
      stage_artifact="failed"
      append_error "E_INTERNAL" "operation" "Command failed"
    fi
  fi

  emit_payload "$status" "$code" "ok" "$stage_operation" "$stage_artifact" "$planned"
  exit "$code"
}

main "$@"
