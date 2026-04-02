#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  install_role.sh --agent-name NAME --agent-file PATH [options]

Options:
  --scope global|project   Install target scope (default: global)
  --project-root PATH      Project root for --scope project (default: current directory)
  --agents-dir PATH        Override target agents directory
  --config PATH            Override target config.toml for optional [agents] limits
  --nickname-candidates CSV
                           Optional comma-separated display names to write to nickname_candidates
  --update-existing        Allow updating an existing custom agent file
  --disable-multi-agent    Deprecated no-op; subagents are enabled by default in current releases
  --max-threads N          Set agents.max_threads (optional)
  --max-depth N            Set agents.max_depth (optional)
  --job-max-runtime-seconds N
                           Set agents.job_max_runtime_seconds (optional)
  -h, --help               Show this help
USAGE
}

scope="global"
project_root="$(pwd)"
config_path=""
agents_dir=""
agent_name=""
agent_file=""
nickname_candidates_csv=""
update_existing="false"
deprecated_disable_multi_agent="false"
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
    --scope)
      require_option_value "$1" "${2:-}"
      scope="$2"; shift 2 ;;
    --project-root)
      require_option_value "$1" "${2:-}"
      project_root="$2"; shift 2 ;;
    --agents-dir)
      require_option_value "$1" "${2:-}"
      agents_dir="$2"; shift 2 ;;
    --config)
      require_option_value "$1" "${2:-}"
      config_path="$2"; shift 2 ;;
    --agent-name|--role-name)
      require_option_value "$1" "${2:-}"
      agent_name="$2"; shift 2 ;;
    --agent-file|--role-config-file)
      require_option_value "$1" "${2:-}"
      agent_file="$2"; shift 2 ;;
    --nickname-candidates)
      require_option_value "$1" "${2:-}"
      nickname_candidates_csv="$2"; shift 2 ;;
    --update-existing)
      update_existing="true"; shift ;;
    --disable-multi-agent)
      deprecated_disable_multi_agent="true"; shift ;;
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

if [[ -z "$agent_name" || -z "$agent_file" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 2
fi

case "$scope" in
  global|project) ;;
  *)
    echo "Invalid --scope value (expected global|project): $scope" >&2
    exit 1 ;;
esac

for pair in \
  "max_threads:$max_threads:1" \
  "max_depth:$max_depth:0" \
  "job_max_runtime_seconds:$job_max_runtime_seconds:1"
do
  key="${pair%%:*}"
  rest="${pair#*:}"
  value="${rest%%:*}"
  min_value="${rest##*:}"
  if [[ -n "$value" ]]; then
    if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ "$value" -lt "$min_value" ]]; then
      echo "Invalid --${key//_/-} value (expected integer >= ${min_value}): $value" >&2
      exit 1
    fi
  fi
done

if [[ ! -f "$agent_file" ]]; then
  echo "Missing custom agent file: $agent_file" >&2
  exit 1
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "Missing dependency: yq (mikefarah/yq v4+)" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Missing dependency: jq" >&2
  exit 1
fi

declared_name="$(yq -p=toml -o=json '.name // ""' "$agent_file" 2>/dev/null || printf '""')"
declared_name="${declared_name%\"}"
declared_name="${declared_name#\"}"

if [[ -z "$declared_name" ]]; then
  echo "Custom agent file must define a non-empty name field: $agent_file" >&2
  exit 1
fi

if [[ "$declared_name" != "$agent_name" ]]; then
  echo "Agent name mismatch: --agent-name '$agent_name' but file declares '$declared_name'" >&2
  exit 1
fi

if [[ -n "$agents_dir" ]]; then
  target_agents_dir="$agents_dir"
elif [[ "$scope" == "global" ]]; then
  target_agents_dir="${HOME}/.codex/agents"
else
  target_agents_dir="${project_root}/.codex/agents"
fi

if [[ -z "$config_path" ]]; then
  if [[ "$scope" == "global" ]]; then
    config_path="${HOME}/.codex/config.toml"
  else
    config_path="${project_root}/.codex/config.toml"
  fi
fi

mkdir -p "$target_agents_dir"
target_agent_file="${target_agents_dir}/${agent_name}.toml"

if [[ -f "$target_agent_file" && "$update_existing" != "true" ]]; then
  echo "Custom agent '$agent_name' already exists at $target_agent_file. Re-run with --update-existing to modify it." >&2
  exit 1
fi

cp "$agent_file" "$target_agent_file"

if [[ -n "$nickname_candidates_csv" ]]; then
  nickname_candidates_json="$(printf '%s' "$nickname_candidates_csv" | jq -Rc 'split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length > 0))')"
  tmp_json="$(mktemp)"
  tmp_toml="$(mktemp)"
  yq -p=toml -o=json '.' "$target_agent_file" | jq --argjson NICKS "$nickname_candidates_json" '.nickname_candidates = $NICKS' > "$tmp_json"
  yq -p=json -o=toml '.' "$tmp_json" > "$tmp_toml"
  mv "$tmp_toml" "$target_agent_file"
  rm -f "$tmp_json"
fi

if [[ -n "$max_threads" || -n "$max_depth" || -n "$job_max_runtime_seconds" ]]; then
  mkdir -p "$(dirname "$config_path")"
  if [[ ! -f "$config_path" ]]; then
    : > "$config_path"
  fi

  backup_path="${config_path}.bak.$(date +%Y%m%d%H%M%S)"
  cp "$config_path" "$backup_path"

  expr='.'
  if [[ -n "$max_threads" ]]; then
    expr+=' | .agents.max_threads = (strenv(MAX_THREADS) | tonumber)'
  fi
  if [[ -n "$max_depth" ]]; then
    expr+=' | .agents.max_depth = (strenv(MAX_DEPTH) | tonumber)'
  fi
  if [[ -n "$job_max_runtime_seconds" ]]; then
    expr+=' | .agents.job_max_runtime_seconds = (strenv(JOB_MAX_RUNTIME_SECONDS) | tonumber)'
  fi

  tmp_json="$(mktemp)"
  tmp_toml="$(mktemp)"
  MAX_THREADS="$max_threads" \
  MAX_DEPTH="$max_depth" \
  JOB_MAX_RUNTIME_SECONDS="$job_max_runtime_seconds" \
  yq -p=toml -o=json "$expr" "$config_path" > "$tmp_json"

  yq -p=json -o=toml '.' "$tmp_json" > "$tmp_toml"
  mv "$tmp_toml" "$config_path"
  rm -f "$tmp_json"

  echo "Updated [agents] runtime limits in $config_path"
  echo "Backup created at: $backup_path"
fi

if [[ "$deprecated_disable_multi_agent" == "true" ]]; then
  echo "Warning: --disable-multi-agent is deprecated and ignored. Subagent availability is controlled by current Codex runtime behavior." >&2
fi

echo "Installed custom agent '$agent_name' to $target_agent_file"
if [[ -n "$nickname_candidates_csv" ]]; then
  echo "Nickname candidates: $nickname_candidates_csv"
fi
