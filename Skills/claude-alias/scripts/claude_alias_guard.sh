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
    awk '
      BEGIN { skip_alias_block = 0 }

      # Remove canonical multi-line block:
      # if [ -f ~/.claude/claude-aliases.sh ]; then
      #   source ~/.claude/claude-aliases.sh
      # fi
      skip_alias_block == 0 && $0 ~ /^[[:space:]]*if[[:space:]].*claude-aliases\.sh.*;[[:space:]]*then[[:space:]]*$/ {
        skip_alias_block = 1
        next
      }

      skip_alias_block == 1 && $0 ~ /^[[:space:]]*fi[[:space:]]*$/ {
        skip_alias_block = 0
        next
      }

      # Remove any one-line source forms that mention claude-aliases.sh.
      skip_alias_block == 0 && $0 ~ /claude-aliases\.sh/ { next }

      { print }
    ' "${ZSHRC}" > "${tmp}"
  fi

  printf '\n%s\n' "${SOURCE_LINE}" >> "${tmp}"
  mv "${tmp}" "${ZSHRC}"
  printf 'REPAIR: normalized %s source line for claude aliases\n' "${ZSHRC}"
}

repair_canonical_alias_script() {
  if [[ ! -f "${CANON_ALIAS}" ]]; then
    printf 'REPAIR: skipped canonical alias hardening (missing %s)\n' "${CANON_ALIAS}" >&2
    return
  fi

  local repair_state
  repair_state="$(
    python3 - "${CANON_ALIAS}" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
original = text

replacements = [
    (
        '''    unset ANTHROPIC_BASE_URL ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN \\
          ANTHROPIC_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL \\
          ANTHROPIC_DEFAULT_HAIKU_MODEL CLAUDE_CODE_SUBAGENT_MODEL
''',
        '''    unset ANTHROPIC_BASE_URL ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN \\
          ANTHROPIC_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL \\
          ANTHROPIC_DEFAULT_HAIKU_MODEL CLAUDE_CODE_SUBAGENT_MODEL \\
          CLAUDE_CONFIG_DIR CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC ENABLE_TOOL_SEARCH \\
          API_TIMEOUT_MS
''',
    ),
    (
        '''    export ANTHROPIC_MODEL="kimi-for-coding"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="kimi-for-coding"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="kimi-for-coding"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="kimi-for-coding"
    export CLAUDE_CODE_SUBAGENT_MODEL="kimi-for-coding"
''',
        '''    local kimi_model
    kimi_model="${KIMI_MODEL:-kimi-for-coding}"
    export ANTHROPIC_MODEL="$kimi_model"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="$kimi_model"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="$kimi_model"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="$kimi_model"
    export CLAUDE_CODE_SUBAGENT_MODEL="$kimi_model"
''',
    ),
    (
        '''    export ANTHROPIC_MODEL="glm-5"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-5"
    export CLAUDE_CODE_SUBAGENT_MODEL="glm-5"
''',
        '''    local zai_model
    zai_model="${ZAI_MODEL:-glm-5.1}"
    export ANTHROPIC_MODEL="$zai_model"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="$zai_model"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="$zai_model"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="$zai_model"
    export CLAUDE_CODE_SUBAGENT_MODEL="$zai_model"
''',
    ),
    (
        'if [[ -n "$BASH_VERSION" ]]; then',
        'if [[ -n "${BASH_VERSION:-}" ]]; then',
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)

text = text.replace(
    '''if [[ -f "$CLAUDE_KIMI_SETTINGS" ]]; then
        command claude --settings "$CLAUDE_KIMI_SETTINGS" "${args[@]}"
    else
        command claude "${args[@]}"
    fi
''',
    '''if [[ -f "$CLAUDE_KIMI_SETTINGS" ]]; then
        command claude --bare --settings "$CLAUDE_KIMI_SETTINGS" "${args[@]}"
    else
        command claude --bare "${args[@]}"
    fi
''',
)
text = text.replace(
    '''if [[ -f "$CLAUDE_ZAI_SETTINGS" ]]; then
        command claude --settings "$CLAUDE_ZAI_SETTINGS" "${args[@]}"
    else
        command claude "${args[@]}"
    fi
''',
    '''if [[ -f "$CLAUDE_ZAI_SETTINGS" ]]; then
        command claude --bare --settings "$CLAUDE_ZAI_SETTINGS" "${args[@]}"
    else
        command claude --bare "${args[@]}"
    fi
''',
)

legacy_clear_oauth = '''# Helper to backup OAuth and remove it from claude.json (for API key auth)
_claude_clear_oauth() {
    if [ -f ~/.claude.json ]; then
        # Check if it has oauthAccount before backing up
        if grep -q '"oauthAccount"' ~/.claude.json 2>/dev/null; then
            # Backup the OAuth session
            cp ~/.claude.json "${CLAUDE_BACKUP_DIR}/claude.json.backup" 2>/dev/null || true
            # Remove oauthAccount from claude.json using jq
            jq 'del(.oauthAccount)' ~/.claude.json > "${CLAUDE_BACKUP_DIR}/claude.json.tmp" 2>/dev/null && \\
                mv "${CLAUDE_BACKUP_DIR}/claude.json.tmp" ~/.claude.json 2>/dev/null || true
        fi
    fi
}
'''

hardened_clear_oauth = '''# Helper to backup OAuth and remove it from Claude state files (for API key auth)
_claude_clear_oauth_file() {
    local target_file="$1"
    local backup_dir="$2"

    if [ ! -f "${target_file}" ]; then
        return 0
    fi
    if ! grep -q '"oauthAccount"' "${target_file}" 2>/dev/null; then
        return 0
    fi

    mkdir -p "${backup_dir}"
    cp "${target_file}" "${backup_dir}/.claude.json.backup.$(date +%s%3N)" 2>/dev/null || true

    local tmp_file
    tmp_file="$(mktemp "${TMPDIR:-/tmp}/claude-oauth-clear.XXXXXX")"
    if jq 'del(.oauthAccount)' "${target_file}" > "${tmp_file}" 2>/dev/null; then
        mv "${tmp_file}" "${target_file}" 2>/dev/null || true
    else
        rm -f "${tmp_file}" 2>/dev/null || true
    fi
}

_claude_clear_oauth() {
    _claude_clear_oauth_file "${HOME}/.claude.json" "${CLAUDE_BACKUP_DIR}"
    _claude_clear_oauth_file "${HOME}/.claude/.claude.json" "${HOME}/.claude/backups"
    _claude_clear_oauth_file "${HOME}/.claude_kimi/.claude.json" "${HOME}/.claude_kimi/backups"
    _claude_clear_oauth_file "${HOME}/.claude_zai/.claude.json" "${HOME}/.claude_zai/backups"
}
'''

if '_claude_clear_oauth_file()' not in text and legacy_clear_oauth in text:
    text = text.replace(legacy_clear_oauth, hardened_clear_oauth)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("updated")
else:
    print("unchanged")
PY
  )"

  printf 'REPAIR: canonical alias script hardening %s (%s)\n' "${repair_state}" "${CANON_ALIAS}"
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
  check_contains "${CANON_ALIAS}" 'command claude --bare --settings "$CLAUDE_KIMI_SETTINGS" "${args[@]}"' 'Kimi launches in API-key-only mode (--bare)'
  check_contains "${CANON_ALIAS}" 'command claude --bare --settings "$CLAUDE_ZAI_SETTINGS" "${args[@]}"' 'Z.AI launches in API-key-only mode (--bare)'
  check_contains "${CANON_ALIAS}" 'CLAUDE_CONFIG_DIR CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC ENABLE_TOOL_SEARCH' 'claude() clears provider-only env vars'
  check_contains "${CANON_ALIAS}" '_claude_clear_oauth_file "${HOME}/.claude_kimi/.claude.json"' 'OAuth scrub covers Kimi config dir'
  check_contains "${CANON_ALIAS}" '_claude_clear_oauth_file "${HOME}/.claude_zai/.claude.json"' 'OAuth scrub covers Z.AI config dir'
  check_contains "${CANON_ALIAS}" 'kimi_model="${KIMI_MODEL:-kimi-for-coding}"' 'Kimi model default is pinned'
  check_contains "${CANON_ALIAS}" 'zai_model="${ZAI_MODEL:-glm-5.1}"' 'Z.AI model default is pinned'
  check_contains "${CANON_ALIAS}" 'if [[ -n "${BASH_VERSION:-}" ]]; then' 'bash export guard is nounset-safe'

  check_json_expr "${CANON_KIMI_SETTINGS}" '.env.ANTHROPIC_MODEL == "kimi-for-coding" and .env.ANTHROPIC_DEFAULT_SONNET_MODEL == "kimi-for-coding" and .env.CLAUDE_CODE_SUBAGENT_MODEL == "kimi-for-coding"' 'Kimi settings model pins are correct'
  check_json_expr "${CANON_ZAI_SETTINGS}" '.env.ANTHROPIC_MODEL == "glm-5.1" and .env.ANTHROPIC_DEFAULT_SONNET_MODEL == "glm-4.7" and .env.ANTHROPIC_DEFAULT_HAIKU_MODEL == "glm-4.5-air"' 'Z.AI settings model pins are correct'
  check_json_expr "${CANON_KIMI_SETTINGS}" '([(.env // {})[] | strings | select(test("\\$\\{"))] | length) == 0' 'Kimi settings do not contain ${VAR} placeholders'
  check_json_expr "${CANON_ZAI_SETTINGS}" '([(.env // {})[] | strings | select(test("\\$\\{"))] | length) == 0' 'Z.AI settings do not contain ${VAR} placeholders'
}

if [[ "${MODE}" == "--repair" ]]; then
  repair_canonical_alias_script
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
