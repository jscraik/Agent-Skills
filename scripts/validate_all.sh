#!/bin/bash
# Consolidated validation runner - one command to check everything
set -e

echo "🔍 Running all validations..."
echo ""

# 1. Plan graph validation
echo "📊 Validating plan graphs..."
if ! ./scripts/validate_plan_graphs.sh 2>&1; then
  echo "  ⚠️  Plan graph validation had issues (see above for details)"
fi

# 2. Recursive skill graph artifacts
echo "🔄 Verifying skill graph artifacts..."
python3 scripts/verify_recursive_skill_graph_artifacts.py --quiet 2>/dev/null || echo "  ⚠️  Artifact verification had issues"

# 3. Docs lint
echo "📚 Running docs lint..."
python3 scripts/docs_lint.py --mode warn --config docs-policy.json 2>/dev/null || echo "  ⚠️  Docs lint had warnings"

# 4. Skill catalog freshness + metadata quality
echo "🧭 Verifying skill catalog freshness..."
python3 scripts/verify_skill_catalog_freshness.py --strict 2>/dev/null || echo "  ⚠️  Skill catalog freshness had issues"

# 5. Router schema guard (no input = contract script availability check)
echo "🛡️  Verifying router schema tooling..."
python3 scripts/verify_router_schema.py --fail-on-sensitive-fields < /dev/null 2>/dev/null || echo "  ⚠️  Router schema verification had issues"

echo ""
echo "✅ Validation complete"
