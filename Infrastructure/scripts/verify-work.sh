#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

skip_preflight=0
skip_sync=0
governance_scope="project-local"
validate_output_mode="${VERIFY_WORK_VALIDATE_MODE:-}"

usage() {
  cat <<'USAGE'
Usage: Infrastructure/scripts/verify-work.sh [options]

Repository-local verification runner for agent-skills.

Options:
  --skip-preflight   Skip Infrastructure/scripts/codex-preflight.sh
  --skip-sync        Skip Infrastructure/scripts/sync_skills.sh
  --project-governance
                     Run checks in project-local scope (default).
                     Validation artifacts are ephemeral.
  --workspace-governance
                     Run checks in workspace scope.
                     Validation artifacts are persistent.
  --persistent-artifacts
                     Backward-compatible alias for --workspace-governance
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
    --project-governance)
      governance_scope="project-local"
      shift
      ;;
    --workspace-governance)
      governance_scope="workspace"
      shift
      ;;
    --persistent-artifacts)
      governance_scope="workspace"
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

if [[ -n "$validate_output_mode" && "$validate_output_mode" != "ephemeral" && "$validate_output_mode" != "persistent" ]]; then
  echo "[verify-work] invalid VERIFY_WORK_VALIDATE_MODE='${validate_output_mode}' (expected ephemeral or persistent)" >&2
  exit 2
fi

if [[ "$governance_scope" == "project-local" ]]; then
  if [[ "${validate_output_mode:-}" == "persistent" ]]; then
    echo "[verify-work] ignoring VERIFY_WORK_VALIDATE_MODE=persistent in project-local scope" >&2
  fi
  validate_output_mode="ephemeral"
else
  if [[ "${validate_output_mode:-}" == "ephemeral" ]]; then
    echo "[verify-work] ignoring VERIFY_WORK_VALIDATE_MODE=ephemeral in workspace scope" >&2
  fi
  validate_output_mode="persistent"
fi

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
  local -a sync_args=("$@")
  local sync_log
  local sync_start
  local sync_end
  local sync_elapsed
  sync_log="$(mktemp "${TMPDIR:-/tmp}/verify-work-sync.XXXXXX")"
  sync_start="$(date +%s)"
  echo
  echo "==> skill-sync"
  if bash "Infrastructure/scripts/sync_skills.sh" "${sync_args[@]}" >"${sync_log}" 2>&1; then
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
echo "[verify-work] governance scope: $governance_scope"
echo "[verify-work] validation artifact mode: $validate_output_mode"

if [[ "$skip_preflight" -eq 0 ]]; then
  run_check "codex-preflight" bash "Infrastructure/scripts/codex-preflight.sh" --stack auto --mode required
else
  skip_check "codex-preflight" "disabled by --skip-preflight"
fi

if [[ "$skip_sync" -eq 0 ]]; then
  if [[ "$governance_scope" == "project-local" ]]; then
    run_skill_sync_check --project-local
  else
    run_skill_sync_check --workspace
  fi
else
  skip_check "skill-sync" "disabled by --skip-sync"
fi

run_check "repo-validation" bash "Infrastructure/scripts/validate_all.sh" "--${validate_output_mode}"

echo
echo "=== verify-work summary ==="
echo "passed:  ${#passed_checks[@]}"
if ((${#passed_checks[@]} > 0)); then
  for check in "${passed_checks[@]}"; do
    echo "  - $check"
  done
fi

echo "skipped: ${#skipped_checks[@]}"
if ((${#skipped_checks[@]} > 0)); then
  for check in "${skipped_checks[@]}"; do
    echo "  - $check"
  done
fi

echo "failed:  ${#failed_checks[@]}"
if ((${#failed_checks[@]} > 0)); then
  for check in "${failed_checks[@]}"; do
    echo "  - $check"
  done
fi

if ((${#failed_checks[@]} > 0)); then
  exit 1
fi
