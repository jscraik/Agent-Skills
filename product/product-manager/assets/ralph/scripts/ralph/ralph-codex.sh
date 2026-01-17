#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'HELP'
ralph-codex.sh --branch <name> [-a <approval>] [-s <sandbox>] [--dry-run]

Runs the RALPH loop using Codex CLI with guardrails.

Options:
  --branch <name>    Branch name to use (required)
  -a <approval>      Approval policy (default: on-request)
  -s <sandbox>       Sandbox mode (default: workspace-write)
  --dry-run          Print the command without executing
  -h, --help         Show this help
HELP
}

BRANCH=""
APPROVAL="on-request"
SANDBOX="workspace-write"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    -a)
      APPROVAL="${2:-}"
      shift 2
      ;;
    -s)
      SANDBOX="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      show_help
      exit 2
      ;;
  esac
done

if [[ -z "$BRANCH" ]]; then
  echo "ERROR: --branch is required" >&2
  show_help
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "ERROR: codex CLI not found in PATH." >&2
  echo "Install or make it available before running the loop." >&2
  exit 1
fi

CMD=(codex exec --branch "$BRANCH" -a "$APPROVAL" -s "$SANDBOX" -p scripts/ralph/prompt.md)

echo "Running: ${CMD[*]}"
if [[ "$DRY_RUN" == "1" ]]; then
  exit 0
fi

"${CMD[@]}"
