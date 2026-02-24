#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/recon.sh plan --target-id <id> --kind <kind> --locator <path|url> --goal "..." [--out <path>] [--no-validate]
  scripts/recon.sh summarize --target-id <id> --run-dir <path> --schema <schema.json> --out <findings.json> [--no-validate]

Notes:
- Minimal runner stub; replace probe execution with your pipeline.
- Uses codex exec with --output-schema and -o for deterministic outputs.
- Validation requires scripts/validate_schema.py (jsonschema).
USAGE
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

cmd="$1"; shift

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VALIDATE="1"

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 2
  fi
}

if [[ "$cmd" == "plan" ]]; then
  target_id=""; kind=""; locator=""; goal=""; out=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target-id)
        require_option_value "$1" "$@"
        target_id="$2"
        shift 2
        ;;
      --kind)
        require_option_value "$1" "$@"
        kind="$2"
        shift 2
        ;;
      --locator)
        require_option_value "$1" "$@"
        locator="$2"
        shift 2
        ;;
      --goal)
        require_option_value "$1" "$@"
        goal="$2"
        shift 2
        ;;
      --out)
        require_option_value "$1" "$@"
        out="$2"
        shift 2
        ;;
      --no-validate) VALIDATE="0"; shift 1 ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown option: $1"; usage; exit 2 ;;
    esac
  done
  if [[ -z "$target_id" || -z "$kind" || -z "$locator" || -z "$goal" ]]; then
    echo "Missing required args"; usage; exit 2
  fi
  if [[ -z "$out" ]]; then
    out="$ROOT/runs/${target_id}_probe_plan.json"
  fi
  codex exec --output-schema "$ROOT/schemas/probe-plan.schema.json" -o "$out" \
    "Plan probes for target ${target_id} (${kind}) at ${locator}. Goal: ${goal}."
  if [[ "$VALIDATE" == "1" ]]; then
    "$SCRIPT_DIR/validate_schema.py" --schema "$ROOT/schemas/probe-plan.schema.json" --data "$out"
  fi
  exit 0
fi

if [[ "$cmd" == "summarize" ]]; then
  target_id=""; run_dir=""; schema=""; out=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --target-id)
        require_option_value "$1" "$@"
        target_id="$2"
        shift 2
        ;;
      --run-dir)
        require_option_value "$1" "$@"
        run_dir="$2"
        shift 2
        ;;
      --schema)
        require_option_value "$1" "$@"
        schema="$2"
        shift 2
        ;;
      --out)
        require_option_value "$1" "$@"
        out="$2"
        shift 2
        ;;
      --no-validate) VALIDATE="0"; shift 1 ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown option: $1"; usage; exit 2 ;;
    esac
  done
  if [[ -z "$target_id" || -z "$run_dir" || -z "$schema" || -z "$out" ]]; then
    echo "Missing required args"; usage; exit 2
  fi
  codex exec --output-schema "$schema" -o "$out" \
    "Summarize findings for target ${target_id} using artifacts under ${run_dir}. Evidence-only."
  if [[ "$VALIDATE" == "1" ]]; then
    "$SCRIPT_DIR/validate_schema.py" --schema "$schema" --data "$out"
  fi
  exit 0
fi

usage
exit 2
