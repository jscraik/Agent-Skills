#!/usr/bin/env bash
# Quick status overview for agent-skills repository
set -e

echo "📊 Agent Skills Status"
echo "======================"
echo ""

# Count skills
skill_count=$(python3 scripts/diagnose_skill.py --all 2>&1 | grep -E "Diagnosing [0-9]+" | grep -oE "[0-9]+")
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
echo "Run 'python3 scripts/diagnose_skill.py --all' for skill diagnostics"
