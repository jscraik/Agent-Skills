#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  install_role.sh --agent-name NAME --agent-file PATH [options]

Options:
  --scope global|project   Install target scope (default: global)
  --project-root PATH      Project root for --scope project (default: current directory)
  --canonical-root PATH    Canonical global Codex root (default: ~/dev/configs/codex)
  --agents-dir PATH        Override target agents directory
  --config PATH            Override target config.toml for optional [agents] limits
  --allow-noncanonical-global-paths
                          Allow global installs outside <canonical-root> (off by default)
  --allow-project-config-write
                          Allow writing <project>/.codex/config.toml when --scope project
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
canonical_root="${CODEX_CANONICAL_ROOT:-${HOME}/dev/configs/codex}"
config_path=""
agents_dir=""
agent_name=""
agent_file=""
nickname_candidates_csv=""
update_existing="false"
deprecated_disable_multi_agent="false"
allow_project_config_write="false"
allow_noncanonical_global_paths="false"
max_threads=""
max_depth=""
job_max_runtime_seconds=""
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

normalize_path() {
  local raw_path="$1"
  python3 - "$raw_path" <<'PY'
import os
import sys

value = sys.argv[1]
print(os.path.normpath(os.path.realpath(os.path.abspath(value))))
PY
}

validate_agent_name() {
  local candidate="$1"
  if [[ -z "$candidate" ]]; then
    echo "Agent name cannot be empty." >&2
    exit 1
  fi
  if [[ "$candidate" == *"/"* || "$candidate" == *"\\"* || "$candidate" == "." || "$candidate" == ".." ]]; then
    echo "Invalid agent name '$candidate': path separators and traversal markers are not allowed." >&2
    exit 1
  fi
  if ! [[ "$candidate" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
    echo "Invalid agent name '$candidate': expected pattern ^[A-Za-z0-9][A-Za-z0-9_-]*$." >&2
    exit 1
  fi
}

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
    --canonical-root)
      require_option_value "$1" "${2:-}"
      canonical_root="$2"; shift 2 ;;
    --agents-dir)
      require_option_value "$1" "${2:-}"
      agents_dir="$2"; shift 2 ;;
    --config)
      require_option_value "$1" "${2:-}"
      config_path="$2"; shift 2 ;;
    --allow-noncanonical-global-paths)
      allow_noncanonical_global_paths="true"; shift ;;
    --allow-project-config-write)
      allow_project_config_write="true"; shift ;;
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

validate_agent_name "$agent_name"

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

validate_agent_name "$declared_name"

validate_role_script="${script_dir}/validate_role.sh"
if [[ ! -x "$validate_role_script" ]]; then
  echo "Missing executable validator script: $validate_role_script" >&2
  exit 1
fi
bash "$validate_role_script" --agent-name "$agent_name" --agent-file "$agent_file"

canonical_root="$(normalize_path "$canonical_root")"
canonical_agents_dir="${canonical_root%/}/agents"
canonical_config_path="${canonical_root%/}/config.toml"

if [[ -n "$agents_dir" ]]; then
  target_agents_dir="$agents_dir"
elif [[ "$scope" == "global" ]]; then
  target_agents_dir="$canonical_agents_dir"
else
  target_agents_dir="${project_root}/.codex/agents"
fi

if [[ -z "$config_path" ]]; then
  if [[ "$scope" == "global" ]]; then
    config_path="$canonical_config_path"
  else
    config_path="${project_root}/.codex/config.toml"
  fi
fi

if [[ "$scope" == "global" && "$allow_noncanonical_global_paths" != "true" ]]; then
  effective_agents_dir="$(normalize_path "$target_agents_dir")"
  effective_config_path="$(normalize_path "$config_path")"
  if [[ "$effective_agents_dir" != "$(normalize_path "$canonical_agents_dir")" ]]; then
    echo "Refusing non-canonical global agents dir: $target_agents_dir" >&2
    echo "Expected canonical path under: $canonical_agents_dir" >&2
    echo "Use --allow-noncanonical-global-paths only for explicit compatibility overrides." >&2
    exit 1
  fi
  if [[ "$effective_config_path" != "$(normalize_path "$canonical_config_path")" ]]; then
    echo "Refusing non-canonical global config path: $config_path" >&2
    echo "Expected canonical path: $canonical_config_path" >&2
    echo "Use --allow-noncanonical-global-paths only for explicit compatibility overrides." >&2
    exit 1
  fi
fi

if [[ -n "$max_threads" || -n "$max_depth" || -n "$job_max_runtime_seconds" ]]; then
  if [[ "$scope" == "project" && "$allow_project_config_write" != "true" ]]; then
    project_codex_config="$(normalize_path "${project_root%/}/.codex/config.toml")"
    cwd_codex_config="$(normalize_path ".codex/config.toml")"
    effective_config_path="$(normalize_path "$config_path")"
    if [[ "$effective_config_path" == "$project_codex_config" || "$effective_config_path" == "$cwd_codex_config" ]]; then
      echo "Refusing to write project-scoped Codex config: $config_path" >&2
      echo "Use --allow-project-config-write to opt in explicitly, or pass --config to a global Codex config path." >&2
      exit 1
    fi
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

# Re-validate the installed file after any post-copy mutation (for example nickname injection).
bash "$validate_role_script" --agent-name "$agent_name" --agent-file "$target_agent_file"

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

if [[ "$scope" == "global" && "$allow_noncanonical_global_paths" == "true" ]]; then
  echo "Warning: non-canonical global install override enabled." >&2
fi

echo "Installed custom agent '$agent_name' to $target_agent_file"
if [[ -n "$nickname_candidates_csv" ]]; then
  echo "Nickname candidates: $nickname_candidates_csv"
fi
