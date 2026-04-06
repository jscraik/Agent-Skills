#!/usr/bin/env bash
set -euo pipefail

MODE="${1:---check}"
case "${MODE}" in
  --check|--repair) ;;
  *)
    echo "Usage: $0 [--check|--repair]" >&2
    exit 2
    ;;
esac

CONFIG_ROOT="${CLAUDE_CONFIG_ROOT:-${HOME}/dev/config}"
CLAUDE_DIR="${CONFIG_ROOT}/claude"
CANON_ALIAS="${CLAUDE_DIR}/bin/claude-aliases.sh"
CANON_KIMI_SETTINGS="${CLAUDE_DIR}/kimi_settings.json"
CANON_ZAI_SETTINGS="${CLAUDE_DIR}/zai_settings.json"

TARGET_ALIAS="${HOME}/.claude/claude-aliases.sh"
TARGET_KIMI_SETTINGS="${HOME}/.claude/kimi_settings.json"
TARGET_ZAI_SETTINGS="${HOME}/.claude/zai_settings.json"
ZSHRC="${HOME}/.zshrc"
SOURCE_LINE='[ -f "$HOME/.claude/claude-aliases.sh" ] && source "$HOME/.claude/claude-aliases.sh"'

checks_run=0
checks_failed=0

pass() {
  checks_run=$((checks_run + 1))
  printf 'PASS: %s\n' "$1"
}

fail() {
  checks_run=$((checks_run + 1))
  checks_failed=$((checks_failed + 1))
  printf 'FAIL: %s\n' "$1" >&2
}

require_file() {
  local path="$1"
  local label="$2"
  if [[ -f "${path}" ]]; then
    pass "${label} exists (${path})"
  else
    fail "${label} missing (${path})"
  fi
}

check_symlink_target() {
  local link_path="$1"
  local expected="$2"
  local label="$3"

  if [[ ! -L "${link_path}" ]]; then
    fail "${label} is not a symlink (${link_path})"
    return
  fi

  local resolved
  resolved="$(readlink "${link_path}")"
  if [[ "${resolved}" == "${expected}" ]]; then
    pass "${label} points to canonical source"
  else
    fail "${label} points to ${resolved}, expected ${expected}"
  fi
}

ensure_symlink() {
  local link_path="$1"
  local expected="$2"
  mkdir -p "$(dirname "${link_path}")"
  ln -snf "${expected}" "${link_path}"
  printf 'REPAIR: linked %s -> %s\n' "${link_path}" "${expected}"
}

check_contains() {
  local path="$1"
  local needle="$2"
  local label="$3"

  if rg -Fq "${needle}" "${path}"; then
    pass "${label}"
  else
    fail "${label} (missing literal: ${needle})"
  fi
}

check_zshrc_source_line() {
  local count="0"
  if [[ -f "${ZSHRC}" ]]; then
    count="$(rg -n 'claude-aliases\.sh' "${ZSHRC}" 2>/dev/null | wc -l | tr -d ' ')"
  fi

  if [[ "${count}" == "1" ]]; then
    pass "~/.zshrc has one claude-aliases source line"
  else
    fail "~/.zshrc has ${count} claude-aliases source lines (expected 1)"
  fi
}

repair_zshrc_source_line() {
  local tmp
  tmp="$(mktemp "${TMPDIR:-/tmp}/zshrc-claude-alias.XXXXXX")"

  if [[ -f "${ZSHRC}" ]]; then
    awk '!/claude-aliases\.sh/' "${ZSHRC}" > "${tmp}"
  fi

  printf '\n%s\n' "${SOURCE_LINE}" >> "${tmp}"
  mv "${tmp}" "${ZSHRC}"
  printf 'REPAIR: normalized %s source line for claude aliases\n' "${ZSHRC}"
}

check_json_expr() {
  local file_path="$1"
  local expr="$2"
  local label="$3"

  if ! command -v jq >/dev/null 2>&1; then
    fail "jq unavailable; cannot validate ${label}"
    return
  fi

  if jq -e "${expr}" "${file_path}" >/dev/null 2>&1; then
    pass "${label}"
  else
    fail "${label}"
  fi
}

run_checks() {
  require_file "${CANON_ALIAS}" "Canonical alias script"
  require_file "${CANON_KIMI_SETTINGS}" "Canonical Kimi settings"
  require_file "${CANON_ZAI_SETTINGS}" "Canonical Z.AI settings"

  check_symlink_target "${TARGET_ALIAS}" "${CANON_ALIAS}" "~/.claude/claude-aliases.sh"
  check_symlink_target "${TARGET_KIMI_SETTINGS}" "${CANON_KIMI_SETTINGS}" "~/.claude/kimi_settings.json"
  check_symlink_target "${TARGET_ZAI_SETTINGS}" "${CANON_ZAI_SETTINGS}" "~/.claude/zai_settings.json"

  check_zshrc_source_line

  check_contains "${CANON_ALIAS}" 'ck() {' 'ck function exists'
  check_contains "${CANON_ALIAS}" 'claude-kimi --dangerously-skip-permissions "$@"' 'ck routes to claude-kimi'
  check_contains "${CANON_ALIAS}" 'cz() {' 'cz function exists'
  check_contains "${CANON_ALIAS}" 'claude-zai --dangerously-skip-permissions "$@"' 'cz routes to claude-zai'
  check_contains "${CANON_ALIAS}" 'cc() {' 'cc function exists'
  check_contains "${CANON_ALIAS}" 'claude --dangerously-skip-permissions "$@"' 'cc routes to claude'
  check_contains "${CANON_ALIAS}" 'kimi_model="${KIMI_MODEL:-kimi-for-coding}"' 'Kimi model default is pinned'
  check_contains "${CANON_ALIAS}" 'zai_model="${ZAI_MODEL:-glm-5.1}"' 'Z.AI model default is pinned'

  check_json_expr "${CANON_KIMI_SETTINGS}" '.env.ANTHROPIC_MODEL == "kimi-for-coding" and .env.ANTHROPIC_DEFAULT_SONNET_MODEL == "kimi-for-coding" and .env.CLAUDE_CODE_SUBAGENT_MODEL == "kimi-for-coding"' 'Kimi settings model pins are correct'
  check_json_expr "${CANON_ZAI_SETTINGS}" '.env.ANTHROPIC_MODEL == "glm-5.1" and .env.ANTHROPIC_DEFAULT_SONNET_MODEL == "glm-4.7" and .env.ANTHROPIC_DEFAULT_HAIKU_MODEL == "glm-4.5-air"' 'Z.AI settings model pins are correct'
  check_json_expr "${CANON_KIMI_SETTINGS}" '([(.env // {})[] | strings | select(test("\\$\\{"))] | length) == 0' 'Kimi settings do not contain ${VAR} placeholders'
  check_json_expr "${CANON_ZAI_SETTINGS}" '([(.env // {})[] | strings | select(test("\\$\\{"))] | length) == 0' 'Z.AI settings do not contain ${VAR} placeholders'
}

if [[ "${MODE}" == "--repair" ]]; then
  ensure_symlink "${TARGET_ALIAS}" "${CANON_ALIAS}"
  ensure_symlink "${TARGET_KIMI_SETTINGS}" "${CANON_KIMI_SETTINGS}"
  ensure_symlink "${TARGET_ZAI_SETTINGS}" "${CANON_ZAI_SETTINGS}"
  repair_zshrc_source_line
fi

run_checks

printf '\nSummary: %s checks, %s failures\n' "${checks_run}" "${checks_failed}"
if [[ "${checks_failed}" -gt 0 ]]; then
  exit 1
fi
