# Guide: Run the Recursive Skill Loop (MVP)

This guide runs the MVP loop engine in bounded mode and emits auditable artifacts.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Single run command](#single-run-command)
- [Shadow cycle automation](#shadow-cycle-automation)
- [Expected output](#expected-output)
- [Verify graph plans](#verify-graph-plans)
- [Next step: human promotion gate](#next-step-human-promotion-gate)

## Prerequisites

- Python 3.10+
- Profile JSON (example: `/docs/skill-graphs/schemas/examples/ui-skills-profile.example.json`)

## Single run command

```bash
python3 utilities/skill-creator/scripts/recursive_skill_loop.py start_run \
  --profile-file docs/skill-graphs/schemas/examples/ui-skills-profile.example.json \
  --objective "Improve UI skill response quality for traceable, safe outputs" \
  --idempotency-key "manual-ui-skill-run-001" \
  --out-root artifacts/skill-graphs/runs
```

Operator control primitives:

```bash
# Escalate an active run
python3 utilities/skill-creator/scripts/recursive_skill_loop.py escalate_run \
  --run-id "<run_id>" \
  --reason-code "no_improvement_limit" \
  --idempotency-key "ops-escalate-001"

# Abort an active run
python3 utilities/skill-creator/scripts/recursive_skill_loop.py abort_run \
  --run-id "<run_id>" \
  --reason "operator_abort" \
  --idempotency-key "ops-abort-001"
```

## Shadow cycle automation

```bash
bash scripts/run_recursive_skill_shadow_cycle.sh \
  --runs-per-profile 2 \
  --window-days 7
```

This generates/updates:
- `/docs/skill-graphs/pilots/ui-skills-shadow-results.md`
- `/docs/skill-graphs/pilots/ui-skills-pilot-readout.md`
- `/artifacts/skill-graphs/pilot/shadow-dashboard.json`

## Expected output

A run directory with:
- `run.json`
- `iteration_journal.jsonl`
- `promotion_decision.json` (draft decision artifact)

Optional debug traces are written only when `--emit-debug-artifacts` is set and stored under `run/debug/`.

## Verify graph plans

```bash
python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py docs/plans/2026-02-19-feat-recursive-skill-self-improvement-loop-plan.md
python3 scripts/validate_recursive_operator_parity.py
```

## Next step: human promotion gate

After successful runs, use:
- [Guide: Human Promotion Gate](/docs/guides/recursive-promotion-gate.md)

Related:
- [Skill graphs index](/docs/skill-graphs)
