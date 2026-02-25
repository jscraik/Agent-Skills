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
python3 utilities/skill-creator/scripts/recursive_skill_loop.py \
  --profile-file docs/skill-graphs/schemas/examples/ui-skills-profile.example.json \
  --objective "Improve UI skill response quality for traceable, safe outputs" \
  --out-root artifacts/skill-graphs/runs \
  --run-owner recursive-loop-operator \
  --lessons-jsonl artifacts/skill-graphs/lessons/canonical-lessons.jsonl \
  --max-injected-lessons 3 \
  --low-confidence-threshold 0.6 \
  --feedback-outcome worked \
  --feedback-note "Output was concise and directly actionable" \
  --kill-switch-file artifacts/skill-graphs/controls/kill-switch.txt \
  --rollback-required-file artifacts/skill-graphs/controls/rollback-required.txt
```

## Shadow cycle automation

```bash
bash scripts/run_recursive_skill_shadow_cycle.sh \
  --runs-per-profile 2 \
  --profiles-file docs/skill-graphs/schemas/examples/pilot-profiles.json \
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
- `capture_record.json` (invocation envelope + output summary + feedback)
- `evidence_packet.json` (assembled events/logs/traces/session/check signals)
- `lesson_candidates.json` (draft candidate lessons derived from advice + implementation + outcome evidence)
- `events.jsonl` (always-on event stream)
- `run_blocker.json` / `rollback_recommendation.json` on blocked or kill-switch paths

Start-of-run retrieval uses canonical lessons from `--lessons-jsonl` filtered by `{scope_skill, scope_profile}`.
Low-confidence lessons are retained but down-ranked and flagged in injected lesson attribution.

Optional debug traces are written only when `--emit-debug-artifacts` is set and stored under `run/debug/`.

## Verify graph plans

```bash
python3 "$HOME/.codex/scripts/plan-graph-lint.py" .agent/PLANS.md
python3 "$HOME/.codex/scripts/plan-graph-lint.py" docs/plans/2026-02-19-feat-recursive-skill-self-improvement-loop-plan.md
```

## Next step: human promotion gate

After successful runs, use:
- [Guide: Human Promotion Gate](/docs/guides/recursive-promotion-gate.md)

Related:
- [Skill graphs index](/docs/skill-graphs)
