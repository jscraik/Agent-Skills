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
  -h, --help             Show this help
USAGE
}

config_path="${HOME}/.codex/config.toml"
role_name=""
role_description=""
role_config_file=""
set_multi_agent="true"
update_existing="false"

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

backup_path="${config_path}.bak.$(date +%Y%m%d%H%M%S)"
cp "$config_path" "$backup_path"

tmp_file="$(mktemp)"
tmp_json="$(mktemp)"
ROLE_NAME="$role_name" \
ROLE_DESCRIPTION="$role_description" \
ROLE_CONFIG_FILE="$role_config_file" \
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
