#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF_DIR="$ROOT_DIR/references"
ADAPTERS_DIR="$ROOT_DIR/adapters"
BRIDGE_DIR="$ROOT_DIR/bridge"
SKILL_FILE="$ROOT_DIR/SKILL.md"

# Exclude non-reference URLs, SVG namespace, and local/example endpoints.
EXCLUDE_RE='(http://www.w3.org/2000/svg|http://www.w3.org/2000/|https?://(127\.0\.0\.1|localhost)|https?://192\.168\.|https?://10\.|https?://172\.(1[6-9]|2[0-9]|3[0-1])\.|https?://oaistatic\.com)'

# Collect URLs from references + adapters + bridge + SKILL.md.
# Filter out SVG namespace and other non-reference URLs (e.g., xmlns attributes).
mapfile -t URLS < <(grep -RhoE 'https?://[^[:space:])"]+' \
  "$REF_DIR" "$ADAPTERS_DIR" "$BRIDGE_DIR" "$SKILL_FILE" 2>/dev/null \
  | sed -E 's/[),.]+$//' \
  | grep -Ev "$EXCLUDE_RE" \
  | sort -u)

if [ ${#URLS[@]} -eq 0 ]; then
  echo "No URLs found in $REF_DIR"
  exit 0
fi

echo "Checking ${#URLS[@]} URLs..."

FAIL=0
CONNECT_TIMEOUT=4
MAX_TIME=10
MAX_URLS="${MAX_URLS:-0}"
CHECKED=0

for url in "${URLS[@]}"; do
  if [ "$MAX_URLS" -gt 0 ] && [ "$CHECKED" -ge "$MAX_URLS" ]; then
    echo "Stopping early: MAX_URLS=$MAX_URLS reached."
    break
  fi

  # Use HEAD, follow redirects. Some servers disallow HEAD; fall back to GET.
  code=$(curl -sS -o /dev/null -L -w '%{http_code}' -I \
    --connect-timeout "$CONNECT_TIMEOUT" --max-time "$MAX_TIME" "$url" || true)
  if [ "$code" = "405" ] || [ "$code" = "000" ]; then
    code=$(curl -sS -o /dev/null -L -w '%{http_code}' \
      --connect-timeout "$CONNECT_TIMEOUT" --max-time "$MAX_TIME" "$url" || true)
  fi
  if [[ "$code" =~ ^2|3 ]]; then
    echo "OK  $code  $url"
  else
    echo "BAD $code  $url"
    FAIL=1
  fi
  CHECKED=$((CHECKED + 1))
  # Gentle pacing to avoid rate limiting.
  sleep 0.05
done

echo "\nDone."
exit $FAIL
