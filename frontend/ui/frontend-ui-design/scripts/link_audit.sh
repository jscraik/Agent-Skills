#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  link_audit.sh --allow-network [--max-urls N]

Notes:
  - This script performs network requests. It requires --allow-network.
  - Limit work with --max-urls or MAX_URLS env var.
TXT
}

ALLOW_NETWORK=0
MAX_URLS_ARG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-network) ALLOW_NETWORK=1; shift 1 ;;
    --max-urls) MAX_URLS_ARG="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ "$ALLOW_NETWORK" != "1" ]]; then
  echo "ERROR: --allow-network is required for link checks."
  usage
  exit 2
fi

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

if [[ -n "$MAX_URLS_ARG" ]]; then
  export MAX_URLS_ARG
fi
export MAX_URLS="${MAX_URLS:-0}"

printf '%s\n' "${URLS[@]}" | python3 - <<'PY'
import sys
import time
import urllib.request
import urllib.error

urls = [line.strip() for line in sys.stdin if line.strip()]

connect_timeout = 4
max_time = 10
max_urls_env = 0

try:
    max_urls_env = int(__import__("os").environ.get("MAX_URLS", "0"))
except ValueError:
    max_urls_env = 0

max_urls_arg = 0
try:
    max_urls_arg = int(__import__("os").environ.get("MAX_URLS_ARG", "0"))
except ValueError:
    max_urls_arg = 0

max_urls = max_urls_arg if max_urls_arg > 0 else max_urls_env

def check(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=connect_timeout) as resp:
            return resp.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        # fallback to GET
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=max_time) as resp:
                return resp.getcode()
        except urllib.error.HTTPError as exc:
            return exc.code
        except Exception:
            return 0

fail = 0
checked = 0
for url in urls:
    if max_urls > 0 and checked >= max_urls:
        print(f"Stopping early: MAX_URLS={max_urls} reached.")
        break
    code = check(url)
    if 200 <= code < 400:
        print(f"OK  {code}  {url}")
    else:
        print(f"BAD {code}  {url}")
        fail = 1
    checked += 1
    time.sleep(0.05)

print("\nDone.")
sys.exit(fail)
PY
