#!/usr/bin/env bash

# Shared Codex environment bootstrap for .codex/environments/environment.toml.
# Keep this script idempotent because setup/actions can source it repeatedly.
# Note: sourced library — only set nounset to avoid leaking errexit/pipefail to callers.
set -u

if [ -z "${BASH_VERSION:-}" ]; then
  echo "codex_env_common.sh must be sourced from bash, not zsh." >&2
  echo "Run: bash -lc 'source Infrastructure/scripts/codex-preflight/codex_env_common.sh && codex_apply_env'" >&2
  return 1 2>/dev/null || exit 1
fi

_codex_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
CODEX_REPO_ROOT="$(
  git -C "$_codex_script_dir" rev-parse --show-toplevel 2>/dev/null \
    || (cd -- "$_codex_script_dir/.." && pwd -P)
)"
unset _codex_script_dir

# codex_prepend_path_if_exists prepends the specified directory to PATH if the argument names an existing directory and is not already present; it does nothing for empty or non-directory arguments.
codex_prepend_path_if_exists() {
  local entry="$1"
  if [[ -z "$entry" || ! -d "$entry" ]]; then
    return 0
  fi
  case ":${PATH}:" in
    *":${entry}:"*) ;;
    *) PATH="${entry}:${PATH}" ;;
  esac
}

# codex_append_path_if_exists appends the specified directory to PATH if the argument names an existing directory and is not already present; it does nothing for empty or non-directory arguments.
codex_append_path_if_exists() {
  local entry="$1"
  if [[ -z "$entry" || ! -d "$entry" ]]; then
    return 0
  fi
  case ":${PATH}:" in
    *":${entry}:"*) ;;
    *) PATH="${PATH}:${entry}" ;;
  esac
}

# codex_configure_mise_sandbox_state keeps mise trust/cache/state writes inside the current repository by default.
codex_configure_mise_sandbox_state() {
  local state_root="${CODEX_MISE_SANDBOX_ROOT:-$CODEX_REPO_ROOT/.cache/codex-mise}"
  mkdir -p "$state_root/cache" "$state_root/state" "$state_root/xdg-state" 2>/dev/null || true

  export MISE_CACHE_DIR="${MISE_CACHE_DIR:-$state_root/cache}"
  export MISE_STATE_DIR="${MISE_STATE_DIR:-$state_root/state}"
  export XDG_STATE_HOME="${XDG_STATE_HOME:-$state_root/xdg-state}"

  local mise_config="$CODEX_REPO_ROOT/.mise.toml"
  if [[ -f "$mise_config" ]]; then
    case ":${MISE_TRUSTED_CONFIG_PATHS:-}:" in
      *":${mise_config}:"*) ;;
      *) export MISE_TRUSTED_CONFIG_PATHS="${MISE_TRUSTED_CONFIG_PATHS:+$MISE_TRUSTED_CONFIG_PATHS:}$mise_config" ;;
    esac
  fi
}

# codex_apply_env updates PATH with common user, package-manager, and repository bin directories, configures a repository-scoped mise sandbox state, and attempts to activate mise for bash.
codex_apply_env() {
  # Ensure repo entrypoints like `ask` resolve without requiring ./bin prefixes.
  codex_prepend_path_if_exists "$HOME/.local/bin"
  codex_prepend_path_if_exists "$HOME/.local/share/mise/shims"
  codex_prepend_path_if_exists "/home/linuxbrew/.linuxbrew/bin"
  codex_prepend_path_if_exists "/usr/local/bin"
  codex_prepend_path_if_exists "/opt/homebrew/bin"
  codex_append_path_if_exists "$CODEX_REPO_ROOT/bin"
  export PATH

  codex_configure_mise_sandbox_state

  if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)" >/dev/null 2>&1 || true
  fi
}
