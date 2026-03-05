# Skill Router Runbook

## Table of Contents
- [Purpose](#purpose)
- [Usage](#usage)
- [Control hierarchy](#control-hierarchy)
- [Validation](#validation)
- [Rollback](#rollback)

## Purpose
Operate the deterministic intent-first skill router in safe modes while preserving telemetry and redaction guarantees.

## Usage
```bash
python3 utilities/skill-creator/scripts/skill_router.py \
  --query "help me design a ChatGPT app" \
  --actor-type human \
  --policy-mode observe_only \
  --events-out artifacts/skill-graphs/telemetry/skill-router-events.jsonl
```

JSON mode:
```bash
python3 utilities/skill-creator/scripts/skill_router.py \
  --query "review PR checks and fix CI" \
  --actor-type agent \
  --policy-mode co_pilot \
  --json \
  --events-out artifacts/skill-graphs/telemetry/skill-router-events.jsonl
```

## Control hierarchy
Apply controls in this order:
1. kill-switch
2. rollback-required
3. rollout-mode

Unknown/invalid controls fail closed to safe state (`observe_only`).

## Validation
```bash
python3 scripts/verify_router_schema.py --input /tmp/router-result.json --fail-on-sensitive-fields
python3 scripts/verify_skill_catalog_freshness.py --strict
python3 scripts/skill_router_metrics.py --events artifacts/skill-graphs/telemetry/skill-router-events.jsonl --json
```

Calibration profile (v1):
- human: clarify when confidence `<= 0.60`
- agent: confirm when confidence `< 0.70`, allow autopilot only when confidence `>= 0.90` and risk tier is low

Uncertainty handling:
- Router emits `uncertainty_reasons` (for example: `possible_multi_intent`, `top_candidates_close_score`)
- Any uncertainty in agent mode forces confirmation behavior.

## Rollback
If routing quality or safety guardrails regress:
1. set rollout mode to `observe_only`
2. activate kill-switch if needed
3. run rollback drill checks and capture evidence
