#!/usr/bin/env bash
# Consolidated validation runner - one command to check everything
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash Infrastructure/scripts/validate_all.sh [--ephemeral|--persistent] [--fail-fast] [--changed-files <file>...]

  --ephemeral   Write logs to a temporary directory and do not mutate repo
                validation artifacts. Intended for git hook runs.
  --persistent  Write logs to Infrastructure/artifacts/validation/<timestamp> and refresh
                Infrastructure/artifacts/validation/latest. This is the default behavior.
  --fail-fast   Stop scheduling new checks after the first required failure.
  --changed-files
                Scope checks to files changed in this lane. When omitted, run full validation.
EOF
}

output_mode="${VALIDATE_ALL_OUTPUT_MODE:-persistent}"
fail_fast=0
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

if [[ "$changed_files_mode" -eq 1 ]]; then
  normalized_changed_files=()
  for changed_file in "${changed_files[@]}"; do
    [[ -n "$changed_file" ]] || continue
    normalized_changed_files+=("${changed_file#./}")
  done
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
if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_cmd=("$PYTHON_BIN")
  python_cmd_display="$PYTHON_BIN"
elif command -v mise >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
  if mise exec -- uv run --python 3.12 python -c "import sys, yaml" >/dev/null 2>&1; then
    python_cmd=(mise exec -- uv run --python 3.12 python)
    python_cmd_display="mise exec -- uv run --python 3.12 python"
  elif uv run --python 3.12 python -c "import sys, yaml" >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 python)
    python_cmd_display="uv run --python 3.12 python"
    echo "⚠️  Python launcher fallback: mise probe failed, using uv directly"
  elif python3 -c "import sys, yaml" >/dev/null 2>&1; then
    python_cmd=(python3)
    python_cmd_display="python3"
    echo "⚠️  Python launcher fallback: uv runtime missing yaml, using python3"
  fi
elif command -v uv >/dev/null 2>&1; then
  if uv run --python 3.12 python -c "import sys, yaml" >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 python)
    python_cmd_display="uv run --python 3.12 python"
  elif python3 -c "import sys, yaml" >/dev/null 2>&1; then
    python_cmd=(python3)
    python_cmd_display="python3"
    echo "⚠️  Python launcher fallback: uv runtime missing yaml, using python3"
  fi
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

# should_run_check determines whether a check should run in changed-files mode.
should_run_check() {
  local slug="$1"
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
    docs-lint)
      [[ "$scope_has_docs" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    skill-authoring-family)
      [[ "$scope_has_authoring_family" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    runtime-separation-*)
      [[ "$scope_has_runtime_separation" -eq 1 || "$scope_has_validation_core" -eq 1 ]]
      ;;
    *)
      return 0
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
    mark_blocked_check "$mode" "$slug" "$label" "outside changed-files scope"
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
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  for changed_file in "${changed_files[@]}"; do
    case "$changed_file" in
      *.md|Docs/*|instructions/*)
        scope_has_docs=1
        ;;
    esac

    case "$changed_file" in
      Skills/*|.agents/skills/*|Plugins/*/skills/*|Infrastructure/scripts/skill-graph/*|Infrastructure/scripts/lifecycle-and-sync/*)
        scope_has_skill_graph=1
        ;;
    esac

    case "$changed_file" in
      Plugins/skill-factory/skills/code_quality_review/skill-builder/*|\
      Plugins/skill-factory/skills/scaffolding_templates/skill-creator/*|\
      Plugins/skill-factory/skills/infrastructure_ops/skill-installer/*|\
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

    case "$changed_file" in
      Infrastructure/scripts/validate_all.sh|\
      Infrastructure/bin/ask|\
      Infrastructure/scripts/lib/ask/*|\
      Infrastructure/scripts/validation-and-linting/*)
        scope_has_validation_core=1
        ;;
    esac
  done
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

schedule_check required docs-lint "📚 Running docs lint..." "${python_cmd[@]}" Infrastructure/scripts/docs_lint.py --mode block --config Infrastructure/docs-policy.json
schedule_check required verify-work-scope-flags "🧭 Verifying verify-work governance scope flags..." "${python_cmd[@]}" Infrastructure/scripts/verify_verify_work_scope_flags.py
schedule_check required question-lifecycle "❓ Verifying question lifecycle contract..." "${python_cmd[@]}" Infrastructure/scripts/verify_question_lifecycle_contract.py
schedule_check required skill-lifecycle-tests "🧪 Running lifecycle readiness tests..." "${python_cmd[@]}" Infrastructure/scripts/test_skill_lifecycle_validation.py
schedule_check required skill-catalog "🧭 Verifying skill catalog freshness..." "${python_cmd[@]}" Infrastructure/scripts/verify_skill_catalog_freshness.py --strict
schedule_check required skills-system-upstream-lock "📌 Verifying skills-system upstream lock..." "${python_cmd[@]}" Infrastructure/scripts/verify_skills_system_upstream_lock.py
schedule_check required plugin-shadowing "🪞 Checking plugin skill shadowing..." bash Infrastructure/scripts/check_plugin_skill_shadowing.sh
schedule_check required provider-policy "🔒 Verifying OpenAI provider policy..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_provider_policy.py
schedule_check required runtime-budget "📦 Verifying default skill runtime budget..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py
schedule_check required projection-integrity "🧱 Verifying projection integrity..." env PROJECTION_INTEGRITY_MANIFEST="$projection_manifest" bash Infrastructure/scripts/validate_projection_integrity.sh
schedule_check required path-ownership-boundaries "🧭 Enforcing path ownership boundaries..." bash Infrastructure/scripts/check_path_ownership_boundaries.sh
schedule_check required skill-types "🏷️  Linting semantic skill-type tags..." bash Infrastructure/scripts/lint_skill_types.sh
schedule_check required openai-format "🧩 Linting OpenAI skill format..." bash Infrastructure/scripts/lint_openai_skill_format.sh --mode strict
schedule_check required progressive-disclosure "📐 Linting progressive disclosure quality..." bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict
schedule_check required skill-authoring-family "👨‍👩‍👧‍👦 Validating skill authoring family gate..." bash Infrastructure/scripts/validate_skill_authoring_family.sh "${skill_family_changed_files_args[@]}"
schedule_check required skill-graph-profiles "🕸️  Validating skill graph profile contracts..." "${python_cmd[@]}" Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/validate_skill_graph_profiles.py --repo-root . --expected-count 0 --profile-index-out "$run_dir/skill-graph-profile-index.json" --wave-readiness-out "$run_dir/skill-graph-wave-readiness.json"
schedule_check required gotcha-store "🧠 Validating gotcha candidate store..." "${python_cmd[@]}" Infrastructure/scripts/gotcha_pipeline.py validate
selection_contract_cmd=("${python_cmd[@]}" Infrastructure/scripts/verify_selection_contract.py --artifact "$run_dir/routing-quality.json")
if [[ "$output_mode" == "persistent" ]]; then
  selection_contract_cmd+=(--history-path "Infrastructure/artifacts/selection-quality/history.jsonl")
fi
schedule_check required selection-contract "🎯 Verifying selection contract fixtures..." "${selection_contract_cmd[@]}"
schedule_check required router-schema "🛡️  Verifying router schema tooling..." "${python_cmd[@]}" Infrastructure/scripts/verify_router_schema.py --input "$run_dir/routing-quality.json" --fail-on-sensitive-fields
schedule_check required ask-cli-modularity "🧱 Verifying ask CLI modularity..." "${python_cmd[@]}" Infrastructure/scripts/verify_ask_cli_modularity.py

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

schedule_check required selection-gate-severity "📦 Emitting selection gate severity artifact..." "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/verify_selection_gate_severity.py --check-results "$check_results_file" --output "$run_dir/selection-gate-severity.json" --schema "Infrastructure/config/schemas/selection-gate-severity.v1.schema.json" --run-id "$run_id" --required-check selection-contract --required-check router-schema --required-check skill-catalog --required-check docs-lint --required-check ask-cli-modularity

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
