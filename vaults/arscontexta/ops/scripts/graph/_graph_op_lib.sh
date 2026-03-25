#!/usr/bin/env bash
set -euo pipefail

in_array() {
  local needle="$1"
  shift
  local token
  for token in "$@"; do
    [[ "$token" == "$needle" ]] && return 0
  done
  return 1
}

usage() {
  cat <<'USAGE'
Usage:
  run_graph_op.sh <operation> [global flags] [-- op_flags]

Operations:
  visual       Build Mermaid graph visual and summary
  communities  Detect communities and emit recommendations
  evolution    Snapshot metrics and render trend report

Global flags:
  -h, --help                     Show this help text
  --json                          Emit run_graph_op.v1 JSON payload
  --dry-run                       Validate and print planned actions only
  --timeout-seconds <n>           Global shell timeout in seconds (default: 120)
  --vault-root <path>             Vault root override
  --artifacts-dir <path>          Artifact output directory override
  --op-timeout-seconds <n>        Optional per-operation timeout (default: 30)

Operation flags (after --):
  --max-nodes <n>                Truncate node output (default: 200)
  --max-edges <n>                Truncate edge output (default: 1000)
  --min-size <n>                  Minimum community size threshold (default: 3)
USAGE
}

emit_error() {
  local code="$1"
  local stage="$2"
  local message="$3"
  if [[ "${RUN_GRAPH_JSON:-0}" == "1" ]]; then
    python3 - "$code" "$stage" "$message" "$RUN_GRAPH_OPERATION" "$RUN_GRAPH_INPUTS" <<'PY'
import json
import sys

code, stage, message, operation, raw_inputs = sys.argv[1:6]
try:
    inputs = json.loads(raw_inputs)
except Exception:
    inputs = {}

payload = {
    "schema": "run_graph_op.v1",
    "operation": operation,
    "status": "failed",
    "exit_code": 1,
    "inputs": inputs,
    "artifacts": [],
    "warnings": [],
    "errors": [{"code": code, "stage": stage, "message": message}],
    "stage": {
        "preflight": "failed",
        "operation": "skipped",
        "artifact_write": "skipped",
    },
    "planned_actions": [],
}
print(json.dumps(payload, sort_keys=True, indent=2))
PY
  else
    printf 'ERROR %s %s\n' "$code" "$message" >&2
  fi
}

preflight() {
  local vault_root="$1"
  local artifacts_dir="$2"
  local script_dir="$3"

  if ! command -v python3 >/dev/null 2>&1; then
    return 1
  fi

  if [[ ! -d "$vault_root" ]]; then
    return 1
  fi

  if [[ -n "$artifacts_dir" ]]; then
    # Validate artifacts_dir: fail if it's an existing file
    if [[ -e "$artifacts_dir" && ! -d "$artifacts_dir" ]]; then
      return 1
    fi
    mkdir -p "$artifacts_dir"
    if [[ ! -w "$artifacts_dir" ]]; then
      return 1
    fi
  fi

  local required=(
    "$script_dir/_graph_lib.py"
    "$script_dir/build_graph_index.py"
    "$script_dir/render_mermaid.py"
    "$script_dir/detect_communities.py"
    "$script_dir/snapshot_metrics.py"
    "$script_dir/render_evolution.py"
    "$script_dir/run_graph_op.v1.schema.json"
  )

  local script
  for script in "${required[@]}"; do
    if [[ ! -f "$script" ]]; then
      return 1
    fi
  done

  return 0
}

emit_plan() {
  local operation="$1"
  case "$operation" in
    visual)
      echo '["build graph index","render mermaid","write graph-visual.md"]'
      ;;
    communities)
      echo '["build graph index","detect communities","write graph-communities.json","write graph-communities.md"]'
      ;;
    evolution)
      echo '["build graph index","append metrics snapshot","write evolution artifacts"]'
      ;;
    *)
      echo '[]'
      ;;
  esac
}
