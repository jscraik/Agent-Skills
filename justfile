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
    mise exec -- uv run --python 3.12 python scripts/diagnose_skill.py --all

# Run skill genome loop (dry-run)
genome-loop:
    mise exec -- uv run --python 3.12 python scripts/run_skill_genome_loop.py --dry-run

# Run skill genome loop (live)
genome-loop-live:
    mise exec -- uv run --python 3.12 python scripts/run_skill_genome_loop.py

# Sync skills to agent directories
sync:
    ./scripts/sync_skills.sh

# Install cron job for nightly genome loop
install-cron:
    ./scripts/install_cron.sh

# Run docs lint
docs-lint:
    mise exec -- uv run --python 3.12 python scripts/docs_lint.py --mode warn --config docs-policy.json

# List skill-builder eval cases
skill-builder-list-evals filters='':
    mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python utilities/skill-builder/scripts/run_skill_evals.py utilities/skill-builder --list-cases {{filters}}

# Run discovery smoke checks for skill-builder
skill-builder-smoke cases='discovery-round-one,discovery-round-six':
    mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python utilities/skill-builder/scripts/run_skill_evals.py utilities/skill-builder --smoke --case {{cases}}

# Smoke test visual-explainer slide generation (opens browser)
smoke-slides source='/Users/jamiecraik/dev/agent-skills/docs/plans/2026-03-02-feat-skill-genome-loop-draft-pr-copilot-plan.md':
    mise exec -- uv run --python 3.12 python utilities/visual-explainer/scripts/smoke_generate_slides.py --source {{source}}

# Smoke test visual-explainer slide generation without opening browser
smoke-slides-no-open source='/Users/jamiecraik/dev/agent-skills/docs/plans/2026-03-02-feat-skill-genome-loop-draft-pr-copilot-plan.md':
    mise exec -- uv run --python 3.12 python utilities/visual-explainer/scripts/smoke_generate_slides.py --no-open --source {{source}}

# Run pre-commit hooks on all files
lint:
    prek run --all-files

# Check for nested .git directories (common skill issue)
check-nested-git:
    @find . -path "./.git" -prune -o -name ".git" -type d -print | grep -q . && echo "❌ Nested .git found" && exit 1 || echo "✅ No nested .git"

# Count skills
count-skills:
    @mise exec -- uv run --python 3.12 python scripts/skill_catalog.py --count

# Run CI checks locally
ci-local:
    ./scripts/validate_all.sh && mise exec -- uv run --python 3.12 python scripts/diagnose_skill.py --all && mise exec -- uv run --python 3.12 python scripts/docs_lint.py --mode warn --config docs-policy.json

# Generate skill spotlight for daily health report (shows skills needing attention)
spotlight:
    mise exec -- uv run --python 3.12 python scripts/skill_spotlight.py

# Generate subject-level scoreboard from skill feedback (ui, backend, security, etc.)
subject-scoreboard:
    mise exec -- uv run --python 3.12 python utilities/skill-builder/scripts/skill_subject_scoreboard.py --write-report

# Run rollback drill scenarios for resilience testing (kill-switch, rollout modes)
rollout-drill:
    bash scripts/run_recursive_rollout_drill.sh

# Check Agentation watch-mode readiness for a project
watch-readiness project-root='.':
    mise exec -- uv run --python 3.12 python frontend/tools/agentation/scripts/check_watch_mode_readiness.py \
        --project-root {{project-root}} \
        --format json

# Analyze router telemetry metrics (first-hit rates, guardrail performance)
router-metrics events='artifacts/skill-graphs/telemetry/route-events.jsonl':
    mise exec -- uv run --python 3.12 python scripts/skill_router_metrics.py --events {{events}} --json
