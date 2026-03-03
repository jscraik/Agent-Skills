#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  install_role.sh --role-name NAME --description TEXT --role-config-file PATH [options]

Options:
  --config PATH          Target config.toml (default: ~/.codex/config.toml)
  --update-existing      Allow updating an existing [agents.<role>] definition
  --disable-multi-agent  Do not force features.multi_agent=true
  --max-threads N        Set agents.max_threads (optional)
  --max-depth N          Set agents.max_depth (optional)
  --job-max-runtime-seconds N
                         Set agents.job_max_runtime_seconds (optional)
  -h, --help             Show this help
USAGE
}

config_path="${HOME}/.codex/config.toml"
role_name=""
role_description=""
role_config_file=""
set_multi_agent="true"
update_existing="false"
max_threads=""
max_depth=""
job_max_runtime_seconds=""

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
    --config)
      require_option_value "$1" "${2:-}"
      config_path="$2"; shift 2 ;;
    --role-name)
      require_option_value "$1" "${2:-}"
      role_name="$2"; shift 2 ;;
    --description)
      require_option_value "$1" "${2:-}"
      role_description="$2"; shift 2 ;;
    --role-config-file)
      require_option_value "$1" "${2:-}"
      role_config_file="$2"; shift 2 ;;
    --update-existing)
      update_existing="true"; shift ;;
    --disable-multi-agent)
      set_multi_agent="false"; shift ;;
    --max-threads)
      require_option_value "$1" "${2:-}"
      max_threads="$2"; shift 2 ;;
    --max-depth)
      require_option_value "$1" "${2:-}"
      max_depth="$2"; shift 2 ;;
    --job-max-runtime-seconds)
      require_option_value "$1" "${2:-}"
      job_max_runtime_seconds="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2 ;;
  esac
done

if [[ -z "$role_name" || -z "$role_description" || -z "$role_config_file" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 2
fi

if [[ -n "$max_threads" ]]; then
  if ! [[ "$max_threads" =~ ^[0-9]+$ ]] || [[ "$max_threads" -lt 1 ]]; then
    echo "Invalid --max-threads value (expected integer >= 1): $max_threads" >&2
    exit 1
  fi
fi

if [[ -n "$max_depth" ]]; then
  if ! [[ "$max_depth" =~ ^[0-9]+$ ]]; then
    echo "Invalid --max-depth value (expected integer >= 0): $max_depth" >&2
    exit 1
  fi
fi

if [[ -n "$job_max_runtime_seconds" ]]; then
  if ! [[ "$job_max_runtime_seconds" =~ ^[0-9]+$ ]] || [[ "$job_max_runtime_seconds" -lt 1 ]]; then
    echo "Invalid --job-max-runtime-seconds value (expected integer >= 1): $job_max_runtime_seconds" >&2
    exit 1
  fi
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "Missing dependency: yq (mikefarah/yq v4+)" >&2
  exit 1
fi

mkdir -p "$(dirname "$config_path")"
if [[ ! -f "$config_path" ]]; then
  : > "$config_path"
fi

role_exists="$(ROLE_NAME="$role_name" yq -p=toml -o=json '.agents[strenv(ROLE_NAME)] != null' "$config_path" 2>/dev/null || printf 'false')"
if [[ "$role_exists" == "true" && "$update_existing" != "true" ]]; then
  echo "Role '$role_name' already exists in $config_path. Re-run with --update-existing to modify it." >&2
  exit 1
fi

expr='.agents[strenv(ROLE_NAME)].description = strenv(ROLE_DESCRIPTION) |
      .agents[strenv(ROLE_NAME)].config_file = strenv(ROLE_CONFIG_FILE)'

if [[ "$set_multi_agent" == "true" ]]; then
  expr+=' | .features.multi_agent = true'
fi

if [[ -n "$max_threads" ]]; then
  expr+=' | .agents.max_threads = (strenv(MAX_THREADS) | tonumber)'
fi

if [[ -n "$max_depth" ]]; then
  expr+=' | .agents.max_depth = (strenv(MAX_DEPTH) | tonumber)'
fi

if [[ -n "$job_max_runtime_seconds" ]]; then
  expr+=' | .agents.job_max_runtime_seconds = (strenv(JOB_MAX_RUNTIME_SECONDS) | tonumber)'
fi

backup_path="${config_path}.bak.$(date +%Y%m%d%H%M%S)"
cp "$config_path" "$backup_path"

tmp_file="$(mktemp)"
tmp_json="$(mktemp)"
ROLE_NAME="$role_name" \
ROLE_DESCRIPTION="$role_description" \
ROLE_CONFIG_FILE="$role_config_file" \
MAX_THREADS="$max_threads" \
MAX_DEPTH="$max_depth" \
JOB_MAX_RUNTIME_SECONDS="$job_max_runtime_seconds" \
yq -p=toml -o=json "$expr" "$config_path" > "$tmp_json"

yq -p=json -o=toml '.' "$tmp_json" > "$tmp_file"
rm -f "$tmp_json"

role_installed="$(ROLE_NAME="$role_name" yq -p=toml -o=json '.agents[strenv(ROLE_NAME)] != null' "$tmp_file" 2>/dev/null || printf 'false')"
if [[ "$role_installed" != "true" ]]; then
  echo "Failed to install role '$role_name' at top level under [agents]." >&2
  rm -f "$tmp_file"
  exit 1
fi

mv "$tmp_file" "$config_path"

echo "Installed role '$role_name' in $config_path"
echo "Role config file: $role_config_file"
echo "Backup created at: $backup_path"
