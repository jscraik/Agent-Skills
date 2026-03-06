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

# Run coding-harness preflight checks
harness-check:
    harness preflight-gate --strict --contract harness.contract.json --json

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

# List skill-creator eval cases
skill-creator-list-evals filters='':
    ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py utilities/skill-creator --list-cases {{filters}}

# Run discovery smoke checks for skill-creator
skill-creator-smoke cases='discovery-round-one,discovery-round-six':
    ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py utilities/skill-creator --smoke --case {{cases}}

# Smoke test visual-explainer slide generation (opens browser)
smoke-slides source='/Users/jamiecraik/dev/agent-skills/docs/plans/2026-03-02-feat-skill-genome-loop-draft-pr-copilot-plan.md':
    python3 utilities/visual-explainer/scripts/smoke_generate_slides.py --source {{source}}

# Smoke test visual-explainer slide generation without opening browser
smoke-slides-no-open source='/Users/jamiecraik/dev/agent-skills/docs/plans/2026-03-02-feat-skill-genome-loop-draft-pr-copilot-plan.md':
    python3 utilities/visual-explainer/scripts/smoke_generate_slides.py --no-open --source {{source}}

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
