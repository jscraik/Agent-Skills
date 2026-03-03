#!/bin/bash
# Local environment check for agent-skills optional harness components.

set -euo pipefail

echo "Checking environment for agent-skills..."

# Ensure uv tool shims are discoverable in non-interactive shells.
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

required_cmds=(rg fd jq python3 node harness)
for cmd in "${required_cmds[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: required command not found: $cmd" >&2
    exit 1
  fi
done

if [[ ! -f harness.contract.json ]]; then
  echo "Error: harness.contract.json not found. Run from repo root." >&2
  exit 1
fi

if [[ ! -f docs-policy.json ]]; then
  echo "Error: docs-policy.json not found. Run from repo root." >&2
  exit 1
fi

if command -v uv >/dev/null 2>&1 && ! command -v ralph >/dev/null 2>&1; then
  echo "Installing ralph-gold via uv..."
  uv tool install ralph-gold
fi

if command -v ralph >/dev/null 2>&1; then
  ralph harness doctor
fi

echo "Environment check passed!"
