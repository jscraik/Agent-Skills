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
python3 Skills/skill-builder/Infrastructure/scripts/recursive_skill_loop.py \
  --profile-file docs/skill-graphs/schemas/examples/ui-skills-profile.example.json \
  --objective "Improve UI skill response quality for traceable, safe outputs" \
  --out-root Infrastructure/artifacts/skill-graphs/runs \
  --run-owner recursive-loop-operator \
  --rollout-mode observe_only \
  --uplift-gate-mode observe \
  --controls-dir Infrastructure/artifacts/skill-graphs/controls \
  --lessons-jsonl Infrastructure/artifacts/skill-graphs/lessons/canonical-lessons.jsonl \
  --max-injected-lessons 3 \
  --low-confidence-threshold 0.6 \
  --feedback-outcome worked \
  --feedback-note "Output was concise and directly actionable" \
  --kill-switch-file Infrastructure/artifacts/skill-graphs/controls/kill-switch.txt \
  --rollback-required-file Infrastructure/artifacts/skill-graphs/controls/rollback-required.txt
```

## Shadow cycle automation

```bash
bash Infrastructure/scripts/lifecycle-and-sync/run_recursive_skill_shadow_cycle.sh \
  --runs-per-profile 2 \
  --profiles-file docs/skill-graphs/schemas/examples/pilot-profiles.json \
  --window-days 7
```

Focused rerun example:

```bash
bash Infrastructure/scripts/lifecycle-and-sync/run_recursive_skill_shadow_cycle.sh \
  --runs-per-profile 1 \
  --profiles-file docs/skill-graphs/schemas/examples/pilot-profiles.frontend-ui-design.json \
  --window-days 7
```

This generates/updates:

- `/docs/skill-graphs/pilots/ui-skills-shadow-results.md`
- `/docs/skill-graphs/pilots/ui-skills-pilot-readout.md`
- `/Infrastructure/artifacts/skill-graphs/pilot/shadow-dashboard.json`

## Expected output

A run directory with:

- `run.json`
- `iteration_journal.jsonl`
- `promotion_decision.json` (draft decision artifact)
- `events.jsonl` (always-on minimum telemetry envelope; required)
- `capture_record.json` (invocation envelope + output summary + feedback; omitted if `auto_capture` disabled)
- `evidence_packet.json` (assembled events/logs/traces/session/check signals; omitted if `auto_capture` disabled)
- `lesson_candidates.json` (draft candidate lessons derived from advice + implementation + outcome evidence; omitted if `auto_capture` disabled)
- `run_blocker.json` / `rollback_recommendation.json` on blocked or kill-switch paths

Start-of-run retrieval uses canonical lessons from `--lessons-jsonl` filtered by `{scope_skill, scope_profile}`.
Canonical lesson rows can now carry `title`, `summary`, `guidance`, `checkpoints`, `methodology_stage`, and `source_note`, and the loop injects that content directly into the candidate prompt when auto-apply is enabled.
Low-confidence lessons are retained but down-ranked and flagged in injected lesson attribution.
Default rollout mode is `observe_only` (capture on, auto-apply off). Use `--rollout-mode active` to enable lesson injection.
Default uplift gate mode is `enforce`; use `--uplift-gate-mode observe` for pilot dry-runs when counterfactual sample sizes are intentionally sparse.
Profiles may also auto-enable terminal feedback prompts through `learning_posture.feedback_capture`.
When `prompt_on_terminal=true` and the run is interactive, the loop asks a non-blocking one-tap
question after the terminal status is printed. Interactive terminals get a short bounded response
window before the loop records `answer.status=missing` and exits; non-interactive runs still complete
immediately and should keep using
`--feedback-outcome` and `--feedback-note` so smoke and CI workflows remain deterministic.

Optional debug traces are written only when `--emit-debug-artifacts` is set and stored under `run/debug/`.

## Verify graph plans

```bash
python3 "$HOME/.codex/Infrastructure/scripts/plan-graph-lint.py" .agents/PLANS.md
python3 "$HOME/.codex/Infrastructure/scripts/plan-graph-lint.py" Docs/plans/2026-02-19-feat-recursive-skill-self-improvement-loop-plan.md
```

## Next step: human promotion gate

After successful runs, use:

- [Guide: Human Promotion Gate](/docs/guides/recursive-promotion-gate.md)

Related:

- [Skill graphs index](/docs/skill-graphs)
