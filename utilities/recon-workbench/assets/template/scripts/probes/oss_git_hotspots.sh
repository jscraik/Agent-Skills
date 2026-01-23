#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/probes/oss_git_hotspots.sh --repo <path> --out <dir> [--limit <n>]
USAGE
}

REPO=""
OUT=""
LIMIT="50"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$REPO" || -z "$OUT" ]]; then
  echo "Missing required args"; usage; exit 2
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
