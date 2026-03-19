#!/bin/bash
# Consolidated validation runner - one command to check everything
set -u

run_id="$(date -u +"%Y%m%dT%H%M%SZ")"
log_root="artifacts/validation"
run_dir="$log_root/$run_id"
latest_dir="$log_root/latest"
required_failures=0
warn_only_issues=0

mkdir -p "$run_dir"
rm -rf "$latest_dir"
cp -R "$run_dir" "$latest_dir"

refresh_latest_dir() {
  rm -rf "$latest_dir"
  cp -R "$run_dir" "$latest_dir"
}

run_check() {
  local mode="$1"
  local slug="$2"
  local label="$3"
  shift 3

  local log_file="$run_dir/${slug}.log"
  local exit_code=0

  echo "$label"
  if "$@" >"$log_file" 2>&1; then
    echo "  ✅ OK"
  else
    exit_code=$?
    if [ "$mode" = "required" ]; then
      required_failures=$((required_failures + 1))
      echo "  ❌ Failed (see $log_file)"
    else
      warn_only_issues=$((warn_only_issues + 1))
      echo "  ⚠️  Issues detected (see $log_file)"
    fi
  fi

  refresh_latest_dir
  return 0
}

echo "🔍 Running all validations..."
echo "📁 Validation logs: $run_dir"
echo ""

run_check warn plan-graphs "📊 Validating plan graphs..." ./scripts/validate_plan_graphs.sh
run_check warn recursive-artifacts "🔄 Verifying skill graph artifacts..." python3 scripts/verify_recursive_skill_graph_artifacts.py --quiet
run_check warn docs-lint "📚 Running docs lint..." python3 scripts/docs_lint.py --mode warn --config docs-policy.json
run_check required question-lifecycle "❓ Verifying question lifecycle contract..." python3 scripts/verify_question_lifecycle_contract.py
run_check warn skill-catalog "🧭 Verifying skill catalog freshness..." python3 scripts/verify_skill_catalog_freshness.py --strict
run_check required skill-types "🏷️  Linting semantic skill-type tags..." bash scripts/lint_skill_types.sh
run_check required openai-format "🧩 Linting OpenAI skill format..." bash scripts/lint_openai_skill_format.sh --mode strict
run_check required progressive-disclosure "📐 Linting progressive disclosure quality..." bash scripts/lint_progressive_disclosure.sh --mode strict
run_check required gotcha-store "🧠 Validating gotcha candidate store..." python3 scripts/gotcha_pipeline.py validate
run_check warn router-schema "🛡️  Verifying router schema tooling..." python3 scripts/verify_router_schema.py --fail-on-sensitive-fields

echo ""
echo "Validation summary:"
echo "- required_failures: $required_failures"
echo "- warn_only_issues: $warn_only_issues"
echo "- logs: $run_dir"

if [ "$required_failures" -gt 0 ]; then
  echo ""
  echo "❌ Validation failed. Review the logs above for exact command output."
  exit 1
fi

echo ""
echo "✅ Validation complete"
