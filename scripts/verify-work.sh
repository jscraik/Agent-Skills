#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

skip_preflight=0
skip_sync=0

usage() {
  cat <<'USAGE'
Usage: scripts/verify-work.sh [options]

Repository-local verification runner for agent-skills.

Options:
  --skip-preflight   Skip scripts/codex-preflight.sh
  --skip-sync        Skip scripts/sync_skills.sh
  -h, --help         Show this help text
USAGE
}

while (($# > 0)); do
  case "$1" in
    --skip-preflight)
      skip_preflight=1
      shift
      ;;
    --skip-sync)
      skip_sync=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[verify-work] unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

declare -a passed_checks=()
declare -a failed_checks=()
declare -a skipped_checks=()

run_check() {
  local name="$1"
  shift

  echo
  echo "==> $name"
  if "$@"; then
    passed_checks+=("$name")
  else
    failed_checks+=("$name")
  fi
}

skip_check() {
  local name="$1"
  local reason="$2"

  skipped_checks+=("$name ($reason)")
  echo
  echo "==> $name"
  echo "[verify-work] skip $name: $reason"
}

run_skill_sync_check() {
  local sync_log
  local sync_start
  local sync_end
  local sync_elapsed
  sync_log="$(mktemp "${TMPDIR:-/tmp}/verify-work-sync.XXXXXX")"
  sync_start="$(date +%s)"
  echo
  echo "==> skill-sync"
  if bash "scripts/sync_skills.sh" >"${sync_log}" 2>&1; then
    sync_end="$(date +%s)"
    sync_elapsed="$((sync_end - sync_start))"
    passed_checks+=("skill-sync")
    cat "${sync_log}"
    echo "[verify-work] skill-sync duration: ${sync_elapsed}s"
    if [[ -n "${SYNC_SKILLS_MAX_SECONDS:-}" ]]; then
      if [[ "${SYNC_SKILLS_MAX_SECONDS}" =~ ^[0-9]+$ ]]; then
        if ((sync_elapsed > SYNC_SKILLS_MAX_SECONDS)); then
          failed_checks+=("skill-sync-performance")
          echo "[verify-work] skill-sync exceeded SYNC_SKILLS_MAX_SECONDS=${SYNC_SKILLS_MAX_SECONDS}s (observed ${sync_elapsed}s)." >&2
          rm -f "${sync_log}"
          return 1
        fi
      else
        echo "[verify-work] ignoring invalid SYNC_SKILLS_MAX_SECONDS='${SYNC_SKILLS_MAX_SECONDS}' (expected integer)." >&2
      fi
    fi
    rm -f "${sync_log}"
    return 0
  fi

  cat "${sync_log}" >&2
  if rg -q "Operation not permitted|is not writable|Unable to update symlink|rsync error: .*code 23" "${sync_log}"; then
    skipped_checks+=("skill-sync (sandbox/permission-limited environment)")
    echo "[verify-work] skip skill-sync: sandbox/permission-limited environment" >&2
    rm -f "${sync_log}"
    return 0
  fi

  failed_checks+=("skill-sync")
  rm -f "${sync_log}"
  return 1
}

echo "[verify-work] repo root: $repo_root"

if [[ "$skip_preflight" -eq 0 ]]; then
  run_check "codex-preflight" bash "scripts/codex-preflight.sh" --stack auto --mode required
else
  skip_check "codex-preflight" "disabled by --skip-preflight"
fi

if [[ "$skip_sync" -eq 0 ]]; then
  run_skill_sync_check
else
  skip_check "skill-sync" "disabled by --skip-sync"
fi

run_check "repo-validation" bash "scripts/validate_all.sh"

echo
echo "=== verify-work summary ==="
echo "passed:  ${#passed_checks[@]}"
for check in "${passed_checks[@]}"; do
  echo "  - $check"
done

echo "skipped: ${#skipped_checks[@]}"
for check in "${skipped_checks[@]}"; do
  echo "  - $check"
done

echo "failed:  ${#failed_checks[@]}"
for check in "${failed_checks[@]}"; do
  echo "  - $check"
done

if ((${#failed_checks[@]} > 0)); then
  exit 1
fi
