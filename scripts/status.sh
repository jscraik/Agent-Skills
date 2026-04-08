#!/usr/bin/env bash
# Quick status overview for agent-skills repository
set -e

echo "📊 Agent Skills Status"
echo "======================"
echo ""

python_cmd=(python3)
if command -v mise >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
    python_cmd=(mise exec -- uv run --python 3.12 python)
elif command -v uv >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 python)
fi

# Count skills from the surfaced flat catalog instead of parsing diagnostics.
skill_count=$("${python_cmd[@]}" scripts/skill_catalog.py --count)
echo "🔧 Skills: $skill_count"

# Genome loop status
rollout_mode=$(cat artifacts/skill-graphs/controls/rollout-mode.txt 2>/dev/null || echo "unknown")
echo "🧬 Genome loop mode: $rollout_mode"

# Pending candidates
pending_count=$(wc -l < artifacts/skill-graphs/telemetry/pending-candidates.jsonl 2>/dev/null || echo "0")
echo "📝 Pending candidates: $pending_count"

# Kill switch
kill_switch=$(cat artifacts/skill-graphs/controls/kill-switch.txt 2>/dev/null || echo "")
if [ "$kill_switch" = "on" ]; then
    echo "🚨 Kill switch: ACTIVE"
else
    echo "✅ Kill switch: inactive"
fi

echo ""
echo "Run 'bash scripts/validate_all.sh' for full validation"
echo "Run 'mise exec -- uv run --python 3.12 python scripts/diagnose_skill.py --all' for skill diagnostics"
