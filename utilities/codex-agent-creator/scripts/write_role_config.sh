#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  write_role_config.sh --output PATH --role-name NAME --model MODEL --reasoning EFFORT [options]

Required:
  --output PATH
  --role-name NAME
  --model MODEL
  --reasoning none|minimal|low|medium|high|xhigh

Developer instructions (choose one):
  --developer-instructions TEXT
  --developer-instructions-file PATH

Optional:
  --sandbox-mode read-only|workspace-write|danger-full-access
  --network-access true|false                (for workspace-write)
  --writable-roots path1,path2               (for workspace-write)
  --web-search disabled|cached|live
  --mcp-clear                                (set mcp_servers = {})
  --mcp-enable name1,name2                   (set mcp_servers.<name>.enabled = true)
  --mcp-disable name1,name2                  (set mcp_servers.<name>.enabled = false)
  -h, --help
USAGE
}

output_path=""
role_name=""
model=""
reasoning=""
developer_instructions=""
developer_instructions_file=""
sandbox_mode=""
network_access=""
writable_roots_csv=""
web_search=""
mcp_clear="false"
mcp_enable_csv=""
mcp_disable_csv=""

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      require_option_value "$1" "$@"
      output_path="$2"; shift 2 ;;
    --role-name)
      require_option_value "$1" "$@"
      role_name="$2"; shift 2 ;;
    --model)
      require_option_value "$1" "$@"
      model="$2"; shift 2 ;;
    --reasoning)
      require_option_value "$1" "$@"
      reasoning="$2"; shift 2 ;;
    --developer-instructions)
      require_option_value "$1" "$@"
      developer_instructions="$2"; shift 2 ;;
    --developer-instructions-file)
      require_option_value "$1" "$@"
      developer_instructions_file="$2"; shift 2 ;;
    --sandbox-mode)
      require_option_value "$1" "$@"
      sandbox_mode="$2"; shift 2 ;;
    --network-access)
      require_option_value "$1" "$@"
      network_access="$2"; shift 2 ;;
    --writable-roots)
      require_option_value "$1" "$@"
      writable_roots_csv="$2"; shift 2 ;;
    --web-search)
      require_option_value "$1" "$@"
      web_search="$2"; shift 2 ;;
    --mcp-clear)
      mcp_clear="true"; shift ;;
    --mcp-enable)
      require_option_value "$1" "$@"
      mcp_enable_csv="$2"; shift 2 ;;
    --mcp-disable)
      require_option_value "$1" "$@"
      mcp_disable_csv="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$output_path" || -z "$role_name" || -z "$model" || -z "$reasoning" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 1
fi

case "$reasoning" in
  none|minimal|low|medium|high|xhigh) ;;
  *)
    echo "Invalid reasoning effort: $reasoning" >&2
    exit 1 ;;
esac

if [[ -n "$sandbox_mode" ]]; then
  case "$sandbox_mode" in
    read-only|workspace-write|danger-full-access) ;;
    *)
      echo "Invalid sandbox mode: $sandbox_mode" >&2
      exit 1 ;;
  esac
fi

if [[ -n "$web_search" ]]; then
  case "$web_search" in
    disabled|cached|live) ;;
    *)
      echo "Invalid web_search mode: $web_search" >&2
      exit 1 ;;
  esac
fi

if [[ -n "$network_access" ]]; then
  case "$network_access" in
    true|false) ;;
    *)
      echo "Invalid --network-access value: $network_access" >&2
      exit 1 ;;
  esac
fi

if [[ -n "$developer_instructions" && -n "$developer_instructions_file" ]]; then
  echo "Use only one of --developer-instructions or --developer-instructions-file" >&2
  exit 1
fi

if [[ -n "$developer_instructions_file" ]]; then
  if [[ ! -f "$developer_instructions_file" ]]; then
    echo "Developer instructions file not found: $developer_instructions_file" >&2
    exit 1
  fi
  developer_instructions="$(cat "$developer_instructions_file")"
fi

LOCAL_MEMORY_SNIPPET=$'local-memory-mcp policy:\n- Use local-memory-mcp for durable context and cross-run continuity.\n- Mandatory workflow:\n  - `bootstrap(mode="minimal", include_questions=true, session_id="repo:<name>:task:<id>")`\n  - `search(query="...", session_id="repo:<name>:task:<id>")`\n- Record durable facts only with `observe(...)` (level `observation|learning`) and stable tags.\n- Do not store secrets, tokens, keys, or PII.'

if [[ -z "$developer_instructions" ]]; then
  developer_instructions="You are the ${role_name} role.\nOwn the assigned task end-to-end.\nState assumptions clearly, fail fast on invalid inputs, and report concrete evidence for results.\nStay within scope and do not modify unrelated files.\n\n${LOCAL_MEMORY_SNIPPET}"
fi

if [[ "$developer_instructions" != *"local-memory-mcp policy:"* ]]; then
  developer_instructions="${developer_instructions}\n\n${LOCAL_MEMORY_SNIPPET}"
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Missing dependency: jq" >&2
  exit 1
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "Missing dependency: yq (mikefarah/yq v4+)" >&2
  exit 1
fi

mkdir -p "$(dirname "$output_path")"

config_json="$(jq -n \
  --arg MODEL "$model" \
  --arg REASONING "$reasoning" \
  --arg DEVELOPER_INSTRUCTIONS "$developer_instructions" \
  '{model: $MODEL, model_reasoning_effort: $REASONING, developer_instructions: $DEVELOPER_INSTRUCTIONS}')"

if [[ -n "$sandbox_mode" ]]; then
  config_json="$(printf '%s' "$config_json" | jq --arg SANDBOX_MODE "$sandbox_mode" '.sandbox_mode = $SANDBOX_MODE')"
fi

if [[ -n "$network_access" ]]; then
  config_json="$(printf '%s' "$config_json" | jq --arg NETWORK_ACCESS "$network_access" '.sandbox_workspace_write.network_access = ($NETWORK_ACCESS == "true")')"
fi

if [[ -n "$writable_roots_csv" ]]; then
  writable_roots_json="$(printf '%s' "$writable_roots_csv" | jq -Rc 'split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length > 0))')"
  config_json="$(printf '%s' "$config_json" | jq --argjson WRITABLE_ROOTS "$writable_roots_json" '.sandbox_workspace_write.writable_roots = $WRITABLE_ROOTS')"
fi

if [[ -n "$web_search" ]]; then
  config_json="$(printf '%s' "$config_json" | jq --arg WEB_SEARCH "$web_search" '.web_search = $WEB_SEARCH')"
fi

if [[ "$mcp_clear" == "true" ]]; then
  config_json="$(printf '%s' "$config_json" | jq '.mcp_servers = {}')"
fi

if [[ -n "$mcp_enable_csv" ]]; then
  IFS=',' read -r -a mcp_enable_arr <<< "$mcp_enable_csv"
  for name in "${mcp_enable_arr[@]}"; do
    trimmed="$(printf '%s' "$name" | xargs)"
    if [[ -n "$trimmed" ]]; then
      config_json="$(printf '%s' "$config_json" | jq --arg NAME "$trimmed" '.mcp_servers[$NAME].enabled = true')"
    fi
  done
fi

if [[ -n "$mcp_disable_csv" ]]; then
  IFS=',' read -r -a mcp_disable_arr <<< "$mcp_disable_csv"
  for name in "${mcp_disable_arr[@]}"; do
    trimmed="$(printf '%s' "$name" | xargs)"
    if [[ -n "$trimmed" ]]; then
      config_json="$(printf '%s' "$config_json" | jq --arg NAME "$trimmed" '.mcp_servers[$NAME].enabled = false')"
    fi
  done
fi

printf '%s\n' "$config_json" | yq -p=json -o=toml '.' > "$output_path"

echo "Wrote role config to $output_path"
