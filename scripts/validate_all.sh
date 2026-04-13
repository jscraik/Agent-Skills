#!/bin/bash
# Consolidated validation runner - one command to check everything
set -u

usage() {
  cat <<'EOF'
Usage: bash scripts/validate_all.sh [--ephemeral|--persistent]

  --ephemeral   Write logs to a temporary directory and do not mutate repo
                validation artifacts. Intended for git hook runs.
  --persistent  Write logs to artifacts/validation/<timestamp> and refresh
                artifacts/validation/latest. This is the default behavior.
EOF
}

output_mode="${VALIDATE_ALL_OUTPUT_MODE:-persistent}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ephemeral)
      output_mode="ephemeral"
      ;;
    --persistent)
      output_mode="persistent"
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

run_id="$(date -u +"%Y%m%dT%H%M%SZ")"
required_failures=0
warn_only_issues=0
cleanup_ephemeral_logs=0
check_results_file=""

python_cmd=(python3)
python_cmd_display="python3"
if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_cmd=("$PYTHON_BIN")
  python_cmd_display="$PYTHON_BIN"
elif command -v mise >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
  if mise exec -- uv run --python 3.12 python -c "import sys" >/dev/null 2>&1; then
    python_cmd=(mise exec -- uv run --python 3.12 python)
    python_cmd_display="mise exec -- uv run --python 3.12 python"
  elif uv run --python 3.12 python -c "import sys" >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 python)
    python_cmd_display="uv run --python 3.12 python"
    echo "⚠️  Python launcher fallback: mise/uv probe failed, using uv directly"
  fi
elif command -v uv >/dev/null 2>&1; then
  python_cmd=(uv run --python 3.12 python)
  python_cmd_display="uv run --python 3.12 python"
fi

if [[ "$output_mode" == "ephemeral" ]]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-validate-all.XXXXXX")"
  cleanup_ephemeral_logs=1
else
  log_root="artifacts/validation"
  run_dir="$log_root/$run_id"
  latest_dir="$log_root/latest"

  mkdir -p "$run_dir"
  rm -rf "$latest_dir"
  cp -R "$run_dir" "$latest_dir"
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

# run_check prints a label, runs the given command redirecting its stdout/stderr to a per-check log, records the outcome in the run's check-results TSV, increments `required_failures` (if `mode` is `required`) or `warn_only_issues` otherwise, refreshes the `latest` directory when applicable and always returns 0.
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
    if [ "$mode" = "required" ]; then
      required_failures=$((required_failures + 1))
      echo "  ❌ Failed (see $log_file)"
    else
      warn_only_issues=$((warn_only_issues + 1))
      echo "  ⚠️  Issues detected (see $log_file)"
    fi
  fi

  printf '%s\t%s\t%s\t%s\n' "$slug" "$mode" "$outcome" "$log_file" >> "$check_results_file"

  refresh_latest_dir
  return 0
}

echo "🔍 Running all validations..."
echo "📁 Validation logs: $run_dir"
echo "🐍 Python launcher: $python_cmd_display"
if [[ "$output_mode" == "ephemeral" ]]; then
  echo "🧹 Ephemeral mode: repo validation artifacts will not be updated"
fi
echo ""

projection_manifest="$run_dir/projection-integrity.json"
recursive_artifacts_cmd=("${python_cmd[@]}" scripts/verify_recursive_skill_graph_artifacts.py --quiet)
if [[ "$output_mode" == "ephemeral" ]]; then
  recursive_artifacts_cmd+=(--manifest "$run_dir/artifact-parity-manifest.json")
fi
run_check warn plan-graphs "📊 Validating plan graphs..." ./scripts/validate_plan_graphs.sh
run_check warn recursive-artifacts "🔄 Verifying skill graph artifacts..." "${recursive_artifacts_cmd[@]}"
run_check required docs-lint "📚 Running docs lint..." "${python_cmd[@]}" scripts/docs_lint.py --mode block --config docs-policy.json
run_check required verify-work-scope-flags "🧭 Verifying verify-work governance scope flags..." "${python_cmd[@]}" scripts/verify_verify_work_scope_flags.py
run_check required question-lifecycle "❓ Verifying question lifecycle contract..." "${python_cmd[@]}" scripts/verify_question_lifecycle_contract.py
run_check required skill-lifecycle-tests "🧪 Running lifecycle readiness tests..." "${python_cmd[@]}" scripts/test_skill_lifecycle_validation.py
run_check required skill-catalog "🧭 Verifying skill catalog freshness..." "${python_cmd[@]}" scripts/verify_skill_catalog_freshness.py --strict
run_check required plugin-shadowing "🪞 Checking plugin skill shadowing..." bash scripts/check_plugin_skill_shadowing.sh
run_check required projection-integrity "🧱 Verifying projection integrity..." env PROJECTION_INTEGRITY_MANIFEST="$projection_manifest" bash scripts/validate_projection_integrity.sh
run_check required path-ownership-boundaries "🧭 Enforcing path ownership boundaries..." bash scripts/check_path_ownership_boundaries.sh
run_check required skill-types "🏷️  Linting semantic skill-type tags..." bash scripts/lint_skill_types.sh
run_check required openai-format "🧩 Linting OpenAI skill format..." bash scripts/lint_openai_skill_format.sh --mode strict
run_check required progressive-disclosure "📐 Linting progressive disclosure quality..." bash scripts/lint_progressive_disclosure.sh --mode strict
run_check required skill-authoring-family "👨‍👩‍👧‍👦 Validating skill authoring family gate..." bash scripts/validate_skill_authoring_family.sh
run_check required gotcha-store "🧠 Validating gotcha candidate store..." "${python_cmd[@]}" scripts/gotcha_pipeline.py validate
selection_contract_cmd=("${python_cmd[@]}" scripts/verify_selection_contract.py --artifact "$run_dir/routing-quality.json")
if [[ "$output_mode" == "persistent" ]]; then
  selection_contract_cmd+=(--history-path "artifacts/selection-quality/history.jsonl")
fi
run_check required selection-contract "🎯 Verifying selection contract fixtures..." "${selection_contract_cmd[@]}"
run_check required router-schema "🛡️  Verifying router schema tooling..." "${python_cmd[@]}" scripts/verify_router_schema.py --input "$run_dir/routing-quality.json" --fail-on-sensitive-fields
run_check required ask-cli-modularity "🧱 Verifying ask CLI modularity..." "${python_cmd[@]}" scripts/verify_ask_cli_modularity.py

runtime_separation_current="$run_dir/runtime-separation-current.json"
if [[ "$output_mode" == "persistent" ]]; then
  runtime_separation_current="GOVERNANCE/runtime-separation/current.json"
fi

runtime_consumer_scan_cmd=(
  "${python_cmd[@]}"
  scripts/scan_runtime_separation_consumers.py
  --emit-readers
  --emit-path-consumers
  --strict
)
if [[ "$output_mode" == "persistent" ]]; then
  runtime_consumer_scan_cmd+=(--emit-digests)
fi

run_check required runtime-separation-manifest "🧬 Validating runtime-separation manifest..." "${python_cmd[@]}" scripts/validate_runtime_separation_manifest.py --strict
run_check required runtime-separation-consumers "🧪 Scanning runtime-separation consumer inventories..." "${runtime_consumer_scan_cmd[@]}"
run_check required runtime-separation-reader-compat "🧪 Verifying runtime-separation reader compatibility..." "${python_cmd[@]}" scripts/verify_runtime_separation_reader_compat.py --schema-current GOVERNANCE/runtime-separation/slices.yaml --schema-prev GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml
run_check required runtime-separation-current "🧱 Building runtime-separation current artifact..." "${python_cmd[@]}" scripts/build_runtime_separation_current.py --output "$runtime_separation_current"
run_check required runtime-separation-wrapper-fixtures "🧾 Verifying runtime-separation wrapper fixtures..." bash scripts/verify_wrapper_contract_fixtures.sh --runtime-separation
run_check required runtime-separation-baseline-compare "🧭 Comparing runtime-separation baseline..." "${python_cmd[@]}" scripts/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current "$runtime_separation_current"
run_check required runtime-separation-writer-mutations "🛡️  Verifying runtime-separation writer authority..." bash scripts/verify_runtime_separation_writer_mutations.sh --strict
run_check required runtime-separation-profile-home "🏠 Building runtime-separation profile-home artifact..." bash scripts/validate_runtime_separation_profile_home.sh --repo-current "$runtime_separation_current" --output "$run_dir/runtime-separation-profile-home.json"

run_check required selection-gate-severity "📦 Emitting selection gate severity artifact..." "${python_cmd[@]}" scripts/verify_selection_gate_severity.py --check-results "$check_results_file" --output "$run_dir/selection-gate-severity.json" --schema "config/schemas/selection-gate-severity.v1.schema.json" --run-id "$run_id" --required-check selection-contract --required-check router-schema --required-check skill-catalog --required-check docs-lint --required-check ask-cli-modularity

echo ""
echo "Validation summary:"
echo "- required_failures: $required_failures"
echo "- warn_only_issues: $warn_only_issues"
echo "- logs: $run_dir"
echo "- selection_gate_severity: $run_dir/selection-gate-severity.json"

if [ "$required_failures" -gt 0 ]; then
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
