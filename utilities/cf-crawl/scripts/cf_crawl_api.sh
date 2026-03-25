#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/cf_crawl_api.sh env-check
  scripts/cf_crawl_api.sh start --payload <payload.json>
  scripts/cf_crawl_api.sh status --job-id <job_id>
  scripts/cf_crawl_api.sh page-status --job-id <job_id> --status <state> [--cursor <cursor>]
  scripts/cf_crawl_api.sh cancel --job-id <job_id>

Required env vars:
  CLOUDFLARE_ACCOUNT_ID
  CLOUDFLARE_API_TOKEN
USAGE
}

require_env() {
  local missing=0
  for key in CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN; do
    local value="${!key:-}"
    if [[ -z "$value" || "$value" == *'${'* ]]; then
      echo "missing_or_placeholder: $key" >&2
      missing=1
    fi
  done
  if [[ "$missing" -ne 0 ]]; then
    exit 2
  fi
}

api_base() {
  echo "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/browser-rendering/crawl"
}

curl_json() {
  curl -sS "$@" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json"
}

cmd="${1:-}"
if [[ -z "$cmd" ]]; then
  usage
  exit 2
fi
shift || true

case "$cmd" in
  env-check)
    require_env
    echo '{"ok":true,"required":["CLOUDFLARE_ACCOUNT_ID","CLOUDFLARE_API_TOKEN"]}'
    ;;

  start)
    require_env
    payload=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --payload) payload="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$payload" || ! -f "$payload" ]]; then
      echo "invalid payload path: $payload" >&2
      exit 2
    fi
    curl_json -X POST "$(api_base)" --data @"$payload"
    ;;

  status)
    require_env
    job_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --job-id) job_id="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$job_id" ]]; then
      echo "missing --job-id" >&2
      exit 2
    fi
    curl_json "$(api_base)/${job_id}"
    ;;

  page-status)
    require_env
    job_id=""
    status=""
    cursor=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --job-id) job_id="${2:-}"; shift 2 ;;
        --status) status="${2:-}"; shift 2 ;;
        --cursor) cursor="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$job_id" || -z "$status" ]]; then
      echo "missing --job-id or --status" >&2
      exit 2
    fi
    query="status=${status}"
    if [[ -n "$cursor" ]]; then
      query="${query}&cursor=${cursor}"
    fi
    curl_json "$(api_base)/${job_id}?${query}"
    ;;

  cancel)
    require_env
    job_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --job-id) job_id="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$job_id" ]]; then
      echo "missing --job-id" >&2
      exit 2
    fi
    curl_json -X POST "$(api_base)/${job_id}/cancel"
    ;;

  *)
    echo "unknown command: $cmd" >&2
    usage
    exit 2
    ;;
esac
