#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  validate_role.sh --role-name NAME --config PATH --role-config PATH --schema PATH

Optional assertions:
  --expect-max-threads N
  --expect-max-depth N
  --expect-job-max-runtime-seconds N
USAGE
}

role_name=""
config_path=""
role_config_path=""
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
    --role-name)
      require_option_value "$1" "${2:-}"
      role_name="$2"; shift 2 ;;
    --config)
      require_option_value "$1" "${2:-}"
      config_path="$2"; shift 2 ;;
    --role-config)
      require_option_value "$1" "${2:-}"
      role_config_path="$2"; shift 2 ;;
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

if [[ -z "$role_name" || -z "$config_path" || -z "$role_config_path" || -z "$schema_path" ]]; then
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

if ! command -v jq >/dev/null 2>&1; then
  echo "Missing dependency: jq" >&2
  exit 1
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "Missing dependency: yq (mikefarah/yq v4+)" >&2
  exit 1
fi

for path in "$config_path" "$role_config_path" "$schema_path"; do
  if [[ ! -f "$path" ]]; then
    echo "Missing file: $path" >&2
    exit 1
  fi
done

allowed_decl='["description","config_file","nickname_candidates"]'
decl_keys="$(ROLE_NAME="$role_name" yq -p=toml -o=json '.agents[strenv(ROLE_NAME)] // {} | keys' "$config_path")"
unsupported_decl="$(jq -n --argjson have "$decl_keys" --argjson allowed "$allowed_decl" '$have - $allowed')"
if [[ "$unsupported_decl" != "[]" ]]; then
  echo "Unsupported keys under [agents.$role_name]: $unsupported_decl" >&2
  exit 1
fi

required_decl_present="$(ROLE_NAME="$role_name" yq -p=toml -o=json '.agents[strenv(ROLE_NAME)].description != null and .agents[strenv(ROLE_NAME)].config_file != null' "$config_path")"
if [[ "$required_decl_present" != "true" ]]; then
  echo "Role declaration must include description and config_file under [agents.$role_name]" >&2
  exit 1
fi

allowed_top_keys="$(jq -c '.properties | keys' "$schema_path")"
role_top_keys="$(yq -p=toml -o=json 'keys' "$role_config_path")"
unsupported_top="$(jq -n --argjson have "$role_top_keys" --argjson allowed "$allowed_top_keys" '$have - $allowed')"
if [[ "$unsupported_top" != "[]" ]]; then
  echo "Unsupported top-level keys in role config: $unsupported_top" >&2
  exit 1
fi

for required_key in model model_reasoning_effort developer_instructions; do
  present="$(REQUIRED_KEY="$required_key" yq -p=toml -o=json '.[strenv(REQUIRED_KEY)] != null and .[strenv(REQUIRED_KEY)] != ""' "$role_config_path")"
  if [[ "$present" != "true" ]]; then
    echo "Missing required role config key: $required_key" >&2
    exit 1
  fi
done

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

echo "Role validation passed for '$role_name'."
