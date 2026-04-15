#!/usr/bin/env bash

# Shared Codex environment bootstrap for .codex/environments/environment.toml.
# Keep this script idempotent because setup/actions can source it repeatedly.

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

# codex_apply_env prepends repository, user and common package-manager bin directories to PATH when they exist and then attempts to activate `mise` for bash.
codex_apply_env() {
  # Ensure repo entrypoints like `ask` resolve without requiring ./bin prefixes.
  codex_prepend_path_if_exists "$HOME/.local/bin"
  codex_prepend_path_if_exists "$HOME/.local/share/mise/shims"
  codex_prepend_path_if_exists "/home/linuxbrew/.linuxbrew/bin"
  codex_prepend_path_if_exists "/usr/local/bin"
  codex_prepend_path_if_exists "/opt/homebrew/bin"
  codex_prepend_path_if_exists "$CODEX_REPO_ROOT/bin"
  export PATH

  if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)" >/dev/null 2>&1 || true
  fi
}
