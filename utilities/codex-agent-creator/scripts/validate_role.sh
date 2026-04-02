#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  validate_role.sh --agent-name NAME --agent-file PATH [options]

Optional:
  --config PATH
  --schema PATH                           (optional compatibility arg; not required)
  --expect-max-threads N
  --expect-max-depth N
  --expect-job-max-runtime-seconds N
USAGE
}

agent_name=""
agent_file=""
config_path=""
schema_path=""
expect_max_threads=""
expect_max_depth=""
expect_job_max_runtime_seconds=""

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-name|--role-name)
      require_option_value "$1" "${2:-}"
      agent_name="$2"; shift 2 ;;
    --agent-file|--role-config)
      require_option_value "$1" "${2:-}"
      agent_file="$2"; shift 2 ;;
    --config)
      require_option_value "$1" "${2:-}"
      config_path="$2"; shift 2 ;;
    --schema)
      require_option_value "$1" "${2:-}"
      schema_path="$2"; shift 2 ;;
    --expect-max-threads)
      require_option_value "$1" "${2:-}"
      expect_max_threads="$2"; shift 2 ;;
    --expect-max-depth)
      require_option_value "$1" "${2:-}"
      expect_max_depth="$2"; shift 2 ;;
    --expect-job-max-runtime-seconds)
      require_option_value "$1" "${2:-}"
      expect_job_max_runtime_seconds="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2 ;;
  esac
done

if [[ -z "$agent_name" || -z "$agent_file" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 2
fi

for pair in \
  "expect_max_threads:$expect_max_threads" \
  "expect_max_depth:$expect_max_depth" \
  "expect_job_max_runtime_seconds:$expect_job_max_runtime_seconds"
do
  key="${pair%%:*}"
  value="${pair#*:}"
  if [[ -n "$value" ]] && ! [[ "$value" =~ ^[0-9]+$ ]]; then
    echo "Invalid --${key//_/-} value (expected integer): $value" >&2
    exit 1
  fi
done

if ! command -v yq >/dev/null 2>&1; then
  echo "Missing dependency: yq (mikefarah/yq v4+)" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Missing dependency: jq" >&2
  exit 1
fi

if [[ ! -f "$agent_file" ]]; then
  echo "Missing custom agent file: $agent_file" >&2
  exit 1
fi

if [[ -n "$schema_path" && ! -f "$schema_path" ]]; then
  echo "Schema path provided but not found: $schema_path" >&2
  exit 1
fi

for required_key in name description developer_instructions model model_reasoning_effort; do
  present="$(REQUIRED_KEY="$required_key" yq -p=toml -o=json '.[strenv(REQUIRED_KEY)] != null and .[strenv(REQUIRED_KEY)] != ""' "$agent_file")"
  if [[ "$present" != "true" ]]; then
    echo "Missing required custom-agent key: $required_key" >&2
    exit 1
  fi
done

actual_name="$(yq -p=toml -o=json '.name // ""' "$agent_file")"
actual_name="${actual_name%\"}"
actual_name="${actual_name#\"}"
if [[ "$actual_name" != "$agent_name" ]]; then
  echo "Agent name mismatch: expected '$agent_name' but file declares '$actual_name'" >&2
  exit 1
fi

reasoning="$(yq -p=toml -o=json '.model_reasoning_effort // ""' "$agent_file")"
reasoning="${reasoning%\"}"
reasoning="${reasoning#\"}"
case "$reasoning" in
  minimal|low|medium|high|xhigh) ;;
  *)
    echo "Invalid model_reasoning_effort value: $reasoning" >&2
    exit 1 ;;
esac

nickname_candidates_present="$(yq -p=toml -o=json '.nickname_candidates != null' "$agent_file")"
if [[ "$nickname_candidates_present" == "true" ]]; then
  nickname_candidates_json="$(yq -p=toml -o=json '.nickname_candidates' "$agent_file")"
  is_valid_array="$(jq -n --argjson nicks "$nickname_candidates_json" '$nicks | type == "array" and length > 0')"
  if [[ "$is_valid_array" != "true" ]]; then
    echo "nickname_candidates must be a non-empty array when provided" >&2
    exit 1
  fi

  unique_ok="$(jq -n --argjson nicks "$nickname_candidates_json" '$nicks | length == (unique | length)')"
  if [[ "$unique_ok" != "true" ]]; then
    echo "nickname_candidates entries must be unique" >&2
    exit 1
  fi

  chars_ok="$(jq -n --argjson nicks "$nickname_candidates_json" '$nicks | all(.[]; test("^[A-Za-z0-9 _-]+$"))')"
  if [[ "$chars_ok" != "true" ]]; then
    echo "nickname_candidates may only use ASCII letters, digits, spaces, hyphens, and underscores" >&2
    exit 1
  fi
fi

if [[ -n "$expect_max_threads" || -n "$expect_max_depth" || -n "$expect_job_max_runtime_seconds" ]]; then
  if [[ -z "$config_path" ]]; then
    echo "--config is required when asserting global [agents] limits" >&2
    exit 1
  fi
  if [[ ! -f "$config_path" ]]; then
    echo "Missing config file for [agents] assertions: $config_path" >&2
    exit 1
  fi
fi

if [[ -n "$expect_max_threads" ]]; then
  actual="$(yq -p=toml -o=json '.agents.max_threads' "$config_path")"
  if [[ "$actual" != "$expect_max_threads" ]]; then
    echo "Expected agents.max_threads=$expect_max_threads but found $actual" >&2
    exit 1
  fi
fi

if [[ -n "$expect_max_depth" ]]; then
  actual="$(yq -p=toml -o=json '.agents.max_depth' "$config_path")"
  if [[ "$actual" != "$expect_max_depth" ]]; then
    echo "Expected agents.max_depth=$expect_max_depth but found $actual" >&2
    exit 1
  fi
fi

if [[ -n "$expect_job_max_runtime_seconds" ]]; then
  actual="$(yq -p=toml -o=json '.agents.job_max_runtime_seconds' "$config_path")"
  if [[ "$actual" != "$expect_job_max_runtime_seconds" ]]; then
    echo "Expected agents.job_max_runtime_seconds=$expect_job_max_runtime_seconds but found $actual" >&2
    exit 1
  fi
fi

echo "Custom-agent validation passed for '$agent_name'."
