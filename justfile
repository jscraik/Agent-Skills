# Agent Skills Task Runner
# Usage: just <command>

# Default: show available commands
default:
    @just --list

# Quick status overview
status:
    ./scripts/status.sh

# Run all validation
validate:
    ./scripts/validate_all.sh

# Diagnose all skills
diagnose:
    python3 scripts/diagnose_skill.py --all

# Run skill genome loop (dry-run)
genome-loop:
    python3 scripts/run_skill_genome_loop.py --dry-run

# Run skill genome loop (live)
genome-loop-live:
    python3 scripts/run_skill_genome_loop.py

# Sync skills to agent directories
sync:
    ./scripts/sync_skills.sh

# Install cron job for nightly genome loop
install-cron:
    ./scripts/install_cron.sh

# Run docs lint
docs-lint:
    python3 scripts/docs_lint.py --mode warn --config docs-policy.json

# Run pre-commit hooks on all files
lint:
    prek run --all-files

# Check for nested .git directories (common skill issue)
check-nested-git:
    @find . -path "./.git" -prune -o -name ".git" -type d -print | grep -q . && echo "❌ Nested .git found" && exit 1 || echo "✅ No nested .git"

# Count skills
count-skills:
    @python3 scripts/diagnose_skill.py --all 2>&1 | grep -E "Diagnosing [0-9]+" | grep -oE "[0-9]+"

# Run CI checks locally
ci-local:
    ./scripts/validate_all.sh && python3 scripts/diagnose_skill.py --all && python3 scripts/docs_lint.py --mode warn --config docs-policy.json
