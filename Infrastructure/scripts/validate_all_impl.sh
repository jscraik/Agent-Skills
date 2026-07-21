#!/usr/bin/env bash
# Consolidated validation runner - one command to check everything
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash Infrastructure/scripts/validate_all.sh [--ephemeral|--persistent] [--fail-fast] [--staged-source] [--head-source] [--scope <name>] [--changed-files <file>...] [--changed-files-from <path>]

  --ephemeral   Write logs to a temporary directory and do not mutate repo
                validation artifacts. Intended for git hook runs.
  --persistent  Write logs to Infrastructure/artifacts/validation/<timestamp> and refresh
                Infrastructure/artifacts/validation/latest. This is the default behavior.
  --fail-fast   Stop scheduling new checks after the first required failure.
  --staged-source
                Validate staged Git index blobs for the program-design check.
                Only use this from the pre-commit staged validation lane.
  --head-source Validate HEAD Git blobs for the program-design check. Use this
                from pre-push validation so dirty worktree edits cannot mask a
                violation in the pushed commit.
  --scope       Run a named validation subset. Valid scopes: all, lint,
                typecheck, test, audit, check, skills-sdk,
                consistency-advisory, consistency-health.
  --changed-files
                Scope checks to files changed in this lane. When omitted, run full validation.
  --changed-files-from
                Read changed-file paths from a newline-delimited file. Prefer this for
                large merge commits so hook invocations do not exceed argv limits.
EOF
}

output_mode="${VALIDATE_ALL_OUTPUT_MODE:-persistent}"
fail_fast=0
staged_source_mode=0
head_source_mode=0
validation_scope="all"
changed_files=()
changed_files_mode=0
parallel_limit="${VALIDATE_ALL_MAX_PARALLEL:-2}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ephemeral)
      output_mode="ephemeral"
      ;;
    --persistent)
      output_mode="persistent"
      ;;
    --fail-fast)
      fail_fast=1
      ;;
    --staged-source)
      staged_source_mode=1
      ;;
    --head-source)
      head_source_mode=1
      ;;
    --scope)
      shift
      if [[ $# -eq 0 || "$1" == --* ]]; then
        echo "Error: --scope requires a value" >&2
        usage >&2
        exit 2
      fi
      validation_scope="$1"
      ;;
    --scope=*)
      validation_scope="${1#--scope=}"
      ;;
    --changed-files)
      changed_files_mode=1
      shift
      while [[ $# -gt 0 ]]; do
        if [[ "$1" == --* ]]; then
          break
        fi
        changed_files+=("$1")
        shift
      done
      continue
      ;;
    --changed-files-from)
      shift
      if [[ $# -eq 0 || "$1" == --* ]]; then
        echo "Error: --changed-files-from requires a path" >&2
        usage >&2
        exit 2
      fi
      if [[ ! -f "$1" ]]; then
        echo "Error: --changed-files-from path does not exist: $1" >&2
        usage >&2
        exit 2
      fi
      changed_files_mode=1
      while IFS= read -r changed_file || [[ -n "$changed_file" ]]; do
        changed_files+=("$changed_file")
      done < "$1"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument '$1'" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

case "$validation_scope" in
  all|lint|typecheck|test|audit|check|skills-sdk|consistency-advisory|consistency-health)
    ;;
  *)
    echo "Error: unknown validation scope '$validation_scope'" >&2
    usage >&2
    exit 2
    ;;
esac

if [[ "$changed_files_mode" -eq 1 ]]; then
  normalized_changed_files=()
  if [[ ${#changed_files[@]} -gt 0 ]]; then
    for changed_file in "${changed_files[@]}"; do
      [[ -n "$changed_file" ]] || continue
      normalized_changed_files+=("${changed_file#./}")
    done
  fi
  changed_files=("${normalized_changed_files[@]}")
fi

if ! [[ "$parallel_limit" =~ ^[0-9]+$ ]] || [[ "$parallel_limit" -lt 1 ]]; then
  parallel_limit=1
fi

if [[ "$parallel_limit" -gt 4 ]]; then
  parallel_limit=4
fi

run_id="$(date -u +"%Y%m%dT%H%M%SZ")"
required_failures=0
warn_only_issues=0
cleanup_ephemeral_logs=0
check_results_file=""
fail_fast_halted=0
projection_drift_halted=0
scope_reason=""

python_cmd=(python3)
python_cmd_display="python3"

use_locked_infrastructure_python_launcher() {
  command -v uv >/dev/null 2>&1 || return 1
  uv run --frozen --project Infrastructure --group test --group lint python -c "import sys, yaml" >/dev/null 2>&1 || return 1
  python_cmd=(uv run --frozen --project Infrastructure --group test --group lint python)
  python_cmd_display="uv run --frozen --project Infrastructure --group test --group lint python"
  return 0
}

if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_cmd=("$PYTHON_BIN")
  python_cmd_display="$PYTHON_BIN"
elif ! use_locked_infrastructure_python_launcher; then
  echo "[validate-all] locked Infrastructure Python with PyYAML is required" >&2
  echo "[validate-all] run bash scripts/bootstrap-ask.sh --json before validation" >&2
  exit 1
fi

if [[ "$output_mode" == "ephemeral" ]]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-validate-all.XXXXXX")"
  cleanup_ephemeral_logs=1
else
  log_root="Infrastructure/artifacts/validation"
  run_dir="$log_root/$run_id"
  latest_dir="$log_root/latest"

  mkdir -p "$run_dir"
fi

check_results_file="$run_dir/check-results.tsv"
: > "$check_results_file"

# cleanup deletes the ephemeral run directory when ephemeral logs are enabled and the run had no required failures.
cleanup() {
  if [[ "$cleanup_ephemeral_logs" -eq 1 && "$required_failures" -eq 0 ]]; then
    rm -rf "$run_dir"
  fi
}

trap cleanup EXIT

refresh_latest_dir() {
  if [[ "$output_mode" != "persistent" ]]; then
    return 0
  fi

  rm -rf "$latest_dir"
  cp -R "$run_dir" "$latest_dir"
}

# record_check_result stores one check outcome in the TSV and updates summary counters.
record_check_result() {
  local mode="$1"
  local slug="$2"
  local outcome="$3"
  local log_file="$4"

  if [[ "$outcome" == "fail" ]]; then
    if [[ "$mode" == "required" ]]; then
      required_failures=$((required_failures + 1))
    else
      warn_only_issues=$((warn_only_issues + 1))
    fi
  fi

  printf '%s\t%s\t%s\t%s\n' "$slug" "$mode" "$outcome" "$log_file" >> "$check_results_file"
}

# mark_blocked_check records a blocked outcome for gated/short-circuited checks.
mark_blocked_check() {
  local mode="$1"
  local slug="$2"
  local label="$3"
  local reason="$4"
  local log_file="$run_dir/${slug}.log"

  echo "$label"
  echo "  ⏭️ Blocked (${reason})"
  : >"$log_file"
  record_check_result "$mode" "$slug" "blocked" "$log_file"
}

# mark_skipped_check records an intentionally out-of-scope check without
# turning changed-files validation red.
mark_skipped_check() {
  local mode="$1"
  local slug="$2"
  local label="$3"
  local reason="$4"
  local log_file="$run_dir/${slug}.log"

  echo "$label"
  echo "  ⏭️ Skipped (${reason})"
  : >"$log_file"
  record_check_result "$mode" "$slug" "skipped" "$log_file"
}

# should_run_check determines whether a check should run in changed-files mode.
check_matches_validation_scope() {
  local slug="$1"

  case "$validation_scope" in
    all|check)
      return 0
      ;;
    lint)
      case "$slug" in
        docs-lint|ask-bootstrap-docs|steering-uptake|no-command-handles|no-breadcrumbs|project-pm-receipts|ask-cli-modularity|program-design|skill-types|openai-format|progressive-disclosure|skills-sdk-typed-artifacts)
          return 0
          ;;
      esac
      ;;
    skills-sdk)
      case "$slug" in
        skills-sdk-typed-artifacts)
          return 0
          ;;
      esac
      ;;
    typecheck)
      case "$slug" in
        verify-work-scope-flags|question-lifecycle|skills-system-upstream-lock|selection-contract|router-schema|ask-cli-modularity|program-design)
          return 0
          ;;
      esac
      ;;
    test)
      case "$slug" in
        skill-lifecycle-tests|skill-authoring-family|skill-graph-profiles|gotcha-store)
          return 0
          ;;
      esac
      ;;
    audit)
      case "$slug" in
        ci-validation-toolchain|skill-catalog|plugin-shadowing|provider-policy|repo-surface-inventory|runtime-budget|context-budget|projection-integrity|path-ownership-boundaries|selection-contract|runtime-separation-*)
          return 0
          ;;
      esac
      ;;
    consistency-advisory)
      case "$slug" in
        plan-graphs|recursive-artifacts|docs-lint|projection-integrity|selection-contract|router-schema|selection-gate-severity)
          return 0
          ;;
      esac
      ;;
    consistency-health)
      case "$slug" in
        runtime-separation-*|selection-contract|router-schema|selection-gate-severity)
          return 0
          ;;
      esac
      ;;
  esac

  return 1
}

should_run_check() {
  local slug="$1"
  if ! check_matches_validation_scope "$slug"; then
    return 1
  fi

  if [[ "$changed_files_mode" -eq 0 || ${#changed_files[@]} -eq 0 ]]; then
    return 0
  fi

  case "$slug" in
    plan-graphs)
      [[ "$scope_has_docs" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    recursive-artifacts)
      [[ "$scope_has_skill_graph" -eq 1 || "$scope_has_authoring_family" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    docs-lint|ask-bootstrap-docs)
      [[ "$scope_has_docs" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    no-breadcrumbs)
      [[ "$scope_has_docs" -eq 1 || "$scope_has_validation_core" -eq 1 || "$scope_has_python_quality" -eq 1 ]]
      ;;
    no-command-handles)
      [[ "$scope_has_docs" -eq 1 || "$scope_has_skill_graph" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    project-pm-receipts)
      [[ "$scope_has_project_pm_reports" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    skills-sdk-typed-artifacts)
      [[ "$scope_has_skills_sdk" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    steering-uptake)
      [[ "$scope_has_docs" -eq 1 || "$scope_has_validation_core" -eq 1 || "$scope_has_steering" -eq 1 ]]
      ;;
    ci-validation-toolchain|verify-work-scope-flags|question-lifecycle|skills-system-upstream-lock|provider-policy|selection-contract|router-schema|selection-gate-severity)
      [[ "$scope_has_validation_core" -eq 1 ]]
      ;;
    repo-surface-inventory)
      return 0
      ;;
    ask-cli-modularity|program-design)
      [[ "$scope_has_validation_core" -eq 1 || "$scope_has_python_quality" -eq 1 ]]
      ;;
    skill-lifecycle-tests|skill-catalog|plugin-shadowing|runtime-budget|context-budget|projection-integrity|path-ownership-boundaries|skill-types|openai-format|progressive-disclosure|skill-graph-profiles|gotcha-store)
      [[ "$scope_has_skill_graph" -eq 1 ]]
      ;;
    skill-authoring-family)
      [[ "$scope_has_authoring_family" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    runtime-separation-*)
      [[ "$scope_has_runtime_separation" -eq 1 ]]
      ;;
    *)
      return 1
      ;;
  esac
}

is_program_design_scanned_path() {
  local changed_file="$1"
  case "$changed_file" in
    Infrastructure/bin/*|Infrastructure/scripts/*|Plugins/*|Skills/*|skills-system/*)
      case "$changed_file" in
        */.venv/*|*/__pycache__/*|*/fixtures/*|*/references/*|*/tests/*|*/test/*|*/testing/*)
          return 1
          ;;
        *)
          return 0
          ;;
      esac
      ;;
    *)
      return 1
      ;;
  esac
}

# run_check prints a label, executes the check and records pass/fail outcomes.
run_check() {
  local mode="$1"
  local slug="$2"
  local label="$3"
  shift 3

  local log_file="$run_dir/${slug}.log"
  local outcome="pass"

  echo "$label"
  if "$@" >"$log_file" 2>&1; then
    echo "  ✅ OK"
  else
    outcome="fail"
    if [[ "$mode" == "required" ]]; then
      echo "  ❌ Failed (see $log_file)"
      if [[ -s "$log_file" ]]; then
        echo "  -- ${slug} log tail --"
        python3 - "$log_file" <<'PY'
from collections import deque
import pathlib
import sys

for line in deque(pathlib.Path(sys.argv[1]).open(encoding="utf-8", errors="replace"), maxlen=80):
    print(f"  | {line.rstrip()}")
PY
        echo "  -- end ${slug} log tail --"
      fi
    else
      echo "  ⚠️  Issues detected (see $log_file)"
    fi
  fi

  record_check_result "$mode" "$slug" "$outcome" "$log_file"

  if [[ "$slug" == "projection-integrity" && "$outcome" == "fail" ]]; then
    if grep -Fq "[projection-integrity] ERROR: drift detected" "$log_file"; then
      projection_drift_halted=1
      scope_reason="projection drift detected"
      echo "  ⏭️ Projection drift detected; remaining checks are blocked until projections are synced"
    fi
  fi

  if [[ "$mode" == "required" && "$outcome" == "fail" && "$fail_fast" -eq 1 && "$fail_fast_halted" -eq 0 ]]; then
    fail_fast_halted=1
    scope_reason="fail-fast enabled after first required failure"
    echo "  ⏭️ Fail-fast enabled; remaining checks are blocked"
  fi

  return 0
}

# schedule_check applies short-circuit and changed-file scope policies before running checks.
schedule_check() {
  local mode="$1"
  local slug="$2"
  local label="$3"
  shift 3

  if [[ "$projection_drift_halted" -eq 1 ]]; then
    mark_blocked_check "$mode" "$slug" "$label" "$scope_reason"
    return 0
  fi

  if [[ "$fail_fast_halted" -eq 1 ]]; then
    mark_blocked_check "$mode" "$slug" "$label" "$scope_reason"
    return 0
  fi

  if ! should_run_check "$slug"; then
    mark_skipped_check "$mode" "$slug" "$label" "outside changed-files scope"
    return 0
  fi

  run_check "$mode" "$slug" "$label" "$@"
}

# run_initial_warn_checks executes two independent warn checks in parallel when enabled.
run_initial_warn_checks() {
  local plan_label="📊 Validating plan graphs..."
  local recursive_label="🔄 Verifying skill graph artifacts..."
  local plan_enabled=1
  local recursive_enabled=1

  if ! should_run_check "plan-graphs"; then
    mark_blocked_check "warn" "plan-graphs" "$plan_label" "outside changed-files scope"
    plan_enabled=0
  fi

  if ! should_run_check "recursive-artifacts"; then
    mark_blocked_check "warn" "recursive-artifacts" "$recursive_label" "outside changed-files scope"
    recursive_enabled=0
  fi

  if [[ "$plan_enabled" -eq 1 && "$recursive_enabled" -eq 1 && "$parallel_limit" -gt 1 ]]; then
    echo "⚡ Running independent warn checks in parallel (max ${parallel_limit})"

    local plan_log="$run_dir/plan-graphs.log"
    local recursive_log="$run_dir/recursive-artifacts.log"
    local plan_outcome="pass"
    local recursive_outcome="pass"
    local plan_pid=""
    local recursive_pid=""

    echo "$plan_label"
    ./Infrastructure/scripts/validate_plan_graphs.sh >"$plan_log" 2>&1 &
    plan_pid="$!"

    echo "$recursive_label"
    "${recursive_artifacts_cmd[@]}" >"$recursive_log" 2>&1 &
    recursive_pid="$!"

    if wait "$plan_pid"; then
      echo "  ✅ OK"
    else
      plan_outcome="fail"
      echo "  ⚠️  Issues detected (see $plan_log)"
    fi

    if wait "$recursive_pid"; then
      echo "  ✅ OK"
    else
      recursive_outcome="fail"
      echo "  ⚠️  Issues detected (see $recursive_log)"
    fi

    record_check_result "warn" "plan-graphs" "$plan_outcome" "$plan_log"
    record_check_result "warn" "recursive-artifacts" "$recursive_outcome" "$recursive_log"
    return 0
  fi

  if [[ "$plan_enabled" -eq 1 ]]; then
    run_check warn plan-graphs "$plan_label" ./Infrastructure/scripts/validate_plan_graphs.sh
  fi

  if [[ "$recursive_enabled" -eq 1 ]]; then
    run_check warn recursive-artifacts "$recursive_label" "${recursive_artifacts_cmd[@]}"
  fi
}

echo "🔍 Running all validations..."
echo "📁 Validation logs: $run_dir"
echo "🐍 Python launcher: $python_cmd_display"
if [[ "$validation_scope" != "all" ]]; then
  echo "🎯 Validation scope: $validation_scope"
fi
if [[ "$output_mode" == "ephemeral" ]]; then
  echo "🧹 Ephemeral mode: repo validation artifacts will not be updated"
fi
if [[ "$changed_files_mode" -eq 1 ]]; then
  if [[ ${#changed_files[@]} -eq 0 ]]; then
    echo "🧭 Changed-files mode enabled without file list; running full validation"
  else
    echo "🧭 Changed-files mode enabled with ${#changed_files[@]} file(s)"
  fi
fi
if [[ "$fail_fast" -eq 1 ]]; then
  echo "🧯 Fail-fast mode enabled for required checks"
fi
echo ""

scope_has_docs=0
scope_has_skill_graph=0
scope_has_authoring_family=0
scope_has_runtime_separation=0
scope_has_validation_core=0
scope_has_steering=0
scope_has_skills_sdk=0
scope_has_python_quality=0
scope_has_project_pm_reports=0
scope_forced_validation_fallback=0
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  for changed_file in "${changed_files[@]}"; do
    case "$changed_file" in
      *.md|Docs/*|instructions/*)
        scope_has_docs=1
        ;;
    esac

    case "$changed_file" in
      .harness/quality/steering-uptake.md)
        scope_has_steering=1
        ;;
    esac

    case "$changed_file" in
      .harness/reports/project-pm/*|.harness/reports/project-pm/**)
        scope_has_project_pm_reports=1
        ;;
    esac

    case "$changed_file" in
      Infrastructure/config/schemas/skills-sdk/*|\
      Infrastructure/config/schemas/skills-sdk/**|\
      Infrastructure/scripts/lib/ask/skills_sdk/*|\
      Infrastructure/scripts/lib/ask/skills_sdk/**|\
      Infrastructure/scripts/lib/ask/envelope.py|\
      Infrastructure/scripts/lib/ask/commands/*|\
      Infrastructure/scripts/lib/ask/commands/**|\
      Infrastructure/tests/test_skills_sdk*.py|\
      Infrastructure/tests/fixtures/skills_sdk/*|\
      Infrastructure/tests/fixtures/skills_sdk/**|\
      .harness/specs/*skills-sdk*.md|\
      .harness/plan/*skills-sdk*.md|\
      .harness/implementation-notes/*skills-sdk*|\
      artifacts/*skills-sdk*.html)
        scope_has_skills_sdk=1
        ;;
    esac

    case "$changed_file" in
      Skills/*|.agents/skills/*|Plugins/*/skills/*|Infrastructure/scripts/skill-graph/*|Infrastructure/scripts/lifecycle-and-sync/*)
        scope_has_skill_graph=1
        ;;
    esac

    case "$changed_file" in
      Plugins/skill-factory/skills/code_quality_review/skill-builder/*|\
      Plugins/skill-factory/scripts/skill-builder/*|Plugins/skill-factory/scripts/skill-builder/**|\
      skills-system/skill-creator/*|\
      skills-system/skill-installer/*|\
      Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/*|\
      Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh|\
      Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py|\
      Infrastructure/scripts/testing/test_validate_skill_authoring_family_benchmarks.py)
        scope_has_authoring_family=1
        ;;
    esac

    case "$changed_file" in
      GOVERNANCE/runtime-separation/*|\
      Infrastructure/scripts/runtime-separation/*|\
      Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.sh|\
      Infrastructure/scripts/testing/test_validate_all_runtime_separation.py)
        scope_has_runtime_separation=1
        ;;
    esac

    staged_source_line=""
    if [[ "$staged_source_mode" -eq 1 ]]; then
      staged_source_line="$(git show ":$changed_file" 2>/dev/null | head -n 1 || true)"
    elif [[ "$head_source_mode" -eq 1 ]]; then
      staged_source_line="$(git show "HEAD:$changed_file" 2>/dev/null | head -n 1 || true)"
    elif [[ -f "$changed_file" ]]; then
      staged_source_line="$(head -n 1 "$changed_file" || true)"
    fi
    if is_program_design_scanned_path "$changed_file"; then
      if [[ "$changed_file" == *.py || "$changed_file" == *.pyw ]] || \
        [[ "$staged_source_line" =~ ^#!.*[Pp]ython ]]; then
        scope_has_python_quality=1
      fi
    fi

    case "$changed_file" in
      Infrastructure/scripts/validate_all.sh|\
      Infrastructure/bin/ask|\
      .github/workflows/pr-pipeline.yml|\
      Infrastructure/scripts/lib/ask/*|\
      Infrastructure/scripts/validation-and-linting/validate_skills_sdk_typed_artifacts.py|\
      Infrastructure/scripts/validation-and-linting/*)
        scope_has_validation_core=1
        ;;
    esac
  done

  if [[ "$scope_has_docs" -eq 0 && "$scope_has_skill_graph" -eq 0 && "$scope_has_authoring_family" -eq 0 && "$scope_has_runtime_separation" -eq 0 && "$scope_has_validation_core" -eq 0 && "$scope_has_steering" -eq 0 && "$scope_has_skills_sdk" -eq 0 && "$scope_has_python_quality" -eq 0 && "$scope_has_project_pm_reports" -eq 0 ]]; then
    echo "🧭 Changed-files scope classification missed all known buckets; falling back to baseline required validation"
    scope_has_validation_core=1
    scope_forced_validation_fallback=1
  fi
fi

projection_manifest="$run_dir/projection-integrity.json"
recursive_artifacts_cmd=("${python_cmd[@]}" Infrastructure/scripts/verify_recursive_skill_graph_artifacts.py --quiet)
if [[ "$output_mode" == "ephemeral" ]]; then
  recursive_artifacts_cmd+=(--manifest "$run_dir/artifact-parity-manifest.json")
fi
run_initial_warn_checks

skill_family_changed_files_args=()
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  skill_family_changed_files_args=(--changed-files "${changed_files[@]}")
fi

repo_surface_inventory_cmd=("${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py --strict)
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  repo_surface_inventory_cmd+=(--changed-files "${changed_files[@]}")
fi

schedule_check required docs-lint "📚 Running docs lint..." "${python_cmd[@]}" Infrastructure/scripts/docs_lint.py --mode block --config Infrastructure/docs-policy.json
schedule_check required ask-bootstrap-docs "🧭 Verifying ask bootstrap docs..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py
schedule_check required steering-uptake "🧭 Verifying steering uptake ledger..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py
schedule_check required ci-validation-toolchain "🧰 Verifying PR validation job toolchains..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_pr_pipeline_toolchain.py --json
schedule_check required no-command-handles "🧭 Verifying command-handle guidance is retired..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_no_command_handles.py
schedule_check required repo-surface-inventory "🧭 Enforcing repo surface ownership..." "${repo_surface_inventory_cmd[@]}"
schedule_check required skills-sdk-typed-artifacts "🧾 Verifying Skills SDK typed artifact contracts..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_skills_sdk_typed_artifacts.py --repo-root .
schedule_check required verify-work-scope-flags "🧭 Verifying verify-work governance scope flags..." "${python_cmd[@]}" Infrastructure/scripts/verify_verify_work_scope_flags.py
schedule_check required question-lifecycle "❓ Verifying question lifecycle contract..." "${python_cmd[@]}" Infrastructure/scripts/verify_question_lifecycle_contract.py
schedule_check required skill-lifecycle-tests "🧪 Running lifecycle readiness tests..." "${python_cmd[@]}" Infrastructure/scripts/test_skill_lifecycle_validation.py
schedule_check required skill-catalog "🧭 Verifying skill catalog freshness..." "${python_cmd[@]}" Infrastructure/scripts/verify_skill_catalog_freshness.py --strict
schedule_check required skills-system-upstream-lock "📌 Verifying skills-system upstream lock..." "${python_cmd[@]}" Infrastructure/scripts/verify_skills_system_upstream_lock.py
schedule_check required plugin-shadowing "🪞 Checking plugin skill shadowing..." bash Infrastructure/scripts/check_plugin_skill_shadowing.sh
schedule_check required provider-policy "🔒 Verifying OpenAI provider policy..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_provider_policy.py
schedule_check required runtime-budget "📦 Verifying default skill runtime budget..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py
# Detect active projection mode so the budget gate matches the live runtime.
active_projection_mode="flat"
if should_run_check "context-budget"; then
  if detected_projection_mode="$(python3 Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py --json 2>/dev/null | python3 -c 'import sys, json; print(json.load(sys.stdin).get("projection_mode", "flat"))')"; then
    active_projection_mode="${detected_projection_mode:-flat}"
  else
    echo "  ⚠️  Could not detect active projection mode; context-budget will use flat"
  fi
fi
schedule_check required context-budget "🌳 Verifying context-budgeted skill tree gates..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection "${active_projection_mode:-flat}"
schedule_check required projection-integrity "🧱 Verifying projection integrity..." env PROJECTION_INTEGRITY_MANIFEST="$projection_manifest" bash Infrastructure/scripts/validate_projection_integrity.sh
schedule_check required path-ownership-boundaries "🧭 Enforcing path ownership boundaries..." bash Infrastructure/scripts/check_path_ownership_boundaries.sh
schedule_check required skill-types "🏷️  Linting semantic skill-type tags..." bash Infrastructure/scripts/lint_skill_types.sh
schedule_check required openai-format "🧩 Linting OpenAI skill format..." bash Infrastructure/scripts/lint_openai_skill_format.sh --mode strict
schedule_check required progressive-disclosure "📐 Linting progressive disclosure quality..." bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict
skill_authoring_family_cmd=(bash Infrastructure/scripts/validate_skill_authoring_family.sh)
if [[ ${#skill_family_changed_files_args[@]} -gt 0 ]]; then
  skill_authoring_family_cmd+=("${skill_family_changed_files_args[@]}")
fi
schedule_check required skill-authoring-family "👨‍👩‍👧‍👦 Validating skill authoring family gate..." "${skill_authoring_family_cmd[@]}"
schedule_check required skill-graph-profiles "🕸️  Validating skill graph profile contracts..." "${python_cmd[@]}" Plugins/skill-factory/scripts/skill-builder/validate_skill_graph_profiles.py --repo-root . --expected-count 0 --profile-index-out "$run_dir/skill-graph-profile-index.json" --wave-readiness-out "$run_dir/skill-graph-wave-readiness.json"
schedule_check required gotcha-store "🧠 Validating gotcha candidate store..." "${python_cmd[@]}" Infrastructure/scripts/gotcha_pipeline.py validate
selection_contract_cmd=("${python_cmd[@]}" Infrastructure/scripts/verify_selection_contract.py --artifact "$run_dir/routing-quality.json")
if [[ "$output_mode" == "persistent" ]]; then
  selection_contract_cmd+=(--history-path "Infrastructure/artifacts/selection-quality/history.jsonl")
fi
schedule_check required selection-contract "🎯 Verifying selection contract fixtures..." "${selection_contract_cmd[@]}"
schedule_check required router-schema "🛡️  Verifying router schema tooling..." "${python_cmd[@]}" Infrastructure/scripts/verify_router_schema.py --input "$run_dir/routing-quality.json" --fail-on-sensitive-fields
ask_cli_modularity_cmd=("${python_cmd[@]}" Infrastructure/scripts/verify_ask_cli_modularity.py)
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  ask_cli_modularity_cmd+=(--changed-files "${changed_files[@]}")
fi
schedule_check required ask-cli-modularity "🧱 Verifying ask CLI modularity..." "${ask_cli_modularity_cmd[@]}"

program_design_cmd=("${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_program_design.py)
if [[ "$staged_source_mode" -eq 1 ]]; then
  program_design_cmd+=(--staged-source)
fi
if [[ "$head_source_mode" -eq 1 ]]; then
  program_design_cmd+=(--source-ref HEAD)
fi
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  program_design_cmd+=(--changed-files "${changed_files[@]}")
fi
schedule_check required program-design "🧭 Verifying changed Python program design..." "${program_design_cmd[@]}"

no_breadcrumbs_cmd=("${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_no_breadcrumbs.py)
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  no_breadcrumbs_cmd+=(--changed-files "${changed_files[@]}")
fi
schedule_check required no-breadcrumbs "🧹 Verifying changed docs/comments have no unresolved breadcrumbs..." "${no_breadcrumbs_cmd[@]}"

project_pm_receipts_cmd=("${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_project_pm_receipts.py)
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  project_pm_receipts_cmd+=(--changed-files "${changed_files[@]}")
fi
schedule_check required project-pm-receipts "📬 Verifying changed Project PM receipts have outbound closeout shape..." "${project_pm_receipts_cmd[@]}"

runtime_artifact_targets=(
  "GOVERNANCE/runtime-separation/current.json"
  "GOVERNANCE/runtime-separation/readers.sha256"
  "GOVERNANCE/runtime-separation/path-consumers.sha256"
)
runtime_artifact_backup_manifest="$run_dir/runtime-separation-artifact-backups.tsv"

# prepare_runtime_artifact_backups snapshots canonical runtime-separation artifacts before
# runtime checks so persistent-mode failures can restore the previous repository state.
prepare_runtime_artifact_backups() {
  if [[ "$output_mode" != "persistent" ]]; then
    return 0
  fi

  : > "$runtime_artifact_backup_manifest"

  local target=""
  local backup_name=""
  for target in "${runtime_artifact_targets[@]}"; do
    backup_name="$(echo "$target" | tr '/' '__').bak"
    if [[ -f "$target" ]]; then
      cp "$target" "$run_dir/$backup_name"
      printf '%s\tpresent\t%s\n' "$target" "$backup_name" >> "$runtime_artifact_backup_manifest"
    else
      printf '%s\tmissing\t-\n' "$target" >> "$runtime_artifact_backup_manifest"
    fi
  done
}

# restore_runtime_artifact_backups restores canonical runtime-separation artifacts to
# their pre-run state when a persistent-mode validation run fails.
restore_runtime_artifact_backups() {
  if [[ "$output_mode" != "persistent" || ! -f "$runtime_artifact_backup_manifest" ]]; then
    return 0
  fi

  local target=""
  local state=""
  local backup_name=""
  while IFS=$'\t' read -r target state backup_name; do
    if [[ "$state" == "present" ]]; then
      cp "$run_dir/$backup_name" "$target"
    else
      rm -f "$target"
    fi
  done < "$runtime_artifact_backup_manifest"
}

prepare_runtime_artifact_backups

runtime_separation_current="$run_dir/runtime-separation-current.json"
if [[ "$output_mode" == "persistent" ]]; then
  runtime_separation_current="GOVERNANCE/runtime-separation/current.json"
fi

runtime_consumer_scan_cmd=(
  "${python_cmd[@]}"
  Infrastructure/scripts/runtime-separation/scan_runtime_separation_consumers.py
  --emit-readers
  --emit-path-consumers
  --strict
)
if [[ "$output_mode" == "persistent" ]]; then
  runtime_consumer_scan_cmd+=(--emit-digests)
fi

schedule_check required runtime-separation-manifest "🧬 Validating runtime-separation manifest..." "${python_cmd[@]}" Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py --strict
schedule_check required runtime-separation-consumers "🧪 Scanning runtime-separation consumer inventories..." "${runtime_consumer_scan_cmd[@]}"
schedule_check required runtime-separation-reader-compat "🧪 Verifying runtime-separation reader compatibility..." "${python_cmd[@]}" Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py --schema-current GOVERNANCE/runtime-separation/slices.yaml --schema-prev GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml
schedule_check required runtime-separation-current "🧱 Building runtime-separation current artifact..." env RECURSIVE_VALIDATION_GUARD=1 "${python_cmd[@]}" Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py --output "$runtime_separation_current" --recursive-validation-guard
schedule_check required runtime-separation-wrapper-fixtures "🧾 Verifying runtime-separation wrapper fixtures..." bash Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.sh --runtime-separation
schedule_check required runtime-separation-baseline-compare "🧭 Comparing runtime-separation baseline..." "${python_cmd[@]}" Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current "$runtime_separation_current"
schedule_check required runtime-separation-writer-mutations "🛡️  Verifying runtime-separation writer authority..." bash Infrastructure/scripts/runtime-separation/verify_runtime_separation_writer_mutations.sh --strict
schedule_check required runtime-separation-profile-home "🏠 Building runtime-separation profile-home artifact..." bash Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh --repo-current "$runtime_separation_current" --output "$run_dir/runtime-separation-profile-home.json"

schedule_check required selection-gate-severity "📦 Emitting selection gate severity artifact..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py --check-results "$check_results_file" --output "$run_dir/selection-gate-severity.json" --schema "Infrastructure/config/schemas/selection-gate-severity.v1.schema.json" --run-id "$run_id" --required-check selection-contract --required-check router-schema --required-check skill-catalog --required-check docs-lint --required-check ask-cli-modularity --required-check program-design

refresh_latest_dir

echo ""
echo "Validation summary:"
echo "- required_failures: $required_failures"
echo "- warn_only_issues: $warn_only_issues"
echo "- logs: $run_dir"
echo "- selection_gate_severity: $run_dir/selection-gate-severity.json"

if [ "$required_failures" -gt 0 ]; then
  restore_runtime_artifact_backups
  echo ""
  echo "❌ Validation failed. Review the logs above for exact command output."
  cleanup_ephemeral_logs=0
  exit 1
fi

echo ""
echo "✅ Validation complete"
if [[ "$output_mode" == "ephemeral" ]]; then
  echo "ℹ️ Ephemeral logs are removed automatically after a successful run"
fi
