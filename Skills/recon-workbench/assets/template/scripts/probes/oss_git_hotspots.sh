#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/probes/oss_git_hotspots.sh --repo <path> --out <dir> [--limit <n>]
USAGE
}

REPO=""
OUT=""
LIMIT="50"

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
    --repo)
      require_option_value "$1" "${2:-}"
      REPO="$2"
      shift 2
      ;;
    --out)
      require_option_value "$1" "${2:-}"
      OUT="$2"
      shift 2
      ;;
    --limit)
      require_option_value "$1" "${2:-}"
      LIMIT="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$REPO" || -z "$OUT" ]]; then
  echo "Missing required args"; usage; exit 2
fi

if [[ ! "$LIMIT" =~ ^[0-9]+$ ]] || [[ "$LIMIT" -eq 0 ]]; then
  echo "ERROR: --limit must be a positive integer" >&2
  exit 2
fi

if [[ ! -d "$REPO/.git" ]]; then
  echo "ERROR: not a git repo: $REPO"; exit 2
fi

mkdir -p "$OUT"

git -C "$REPO" log --name-only --pretty=format: \
  | awk 'NF{print}' \
  | sort \
  | uniq -c \
  | sort -rn \
  | head -n "$LIMIT" \
  > "$OUT/hotspots.txt"

echo "OK" > "$OUT/status.txt"
