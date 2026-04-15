# 5-Minute Success Path

## Table of Contents

- [Goal](#goal)
- [First Validated Outcome](#first-validated-outcome)
- [If Route Is Blocked](#if-route-is-blocked)
- [What To Run Next](#what-to-run-next)

## Goal

Get one useful skill recommendation with contract-backed diagnostics in under five minutes.

## First Validated Outcome

1. Confirm repository and policy state:
   `bash -lc 'python3 bin/ask repo status --json'`
2. Run intent-first selection:
   `bash -lc 'python3 bin/ask skills goal "implement a feature safely" --json'`
3. If the response is `resolved`, run the selected skill command and continue.
4. If the response is `intent_unresolved`, follow `data.goal_decision.disambiguation_prompts` and rerun.

Validated outcome definition:

- A JSON envelope is returned.
- `data.goal_decision.schema_version` equals `goal-decision.v1`.
- `data.goal_decision.policy_identity` is present.
- Non-success responses include a non-empty `operator_action`.

## If Route Is Blocked

Run strict catalog diagnostics:
`bash -lc 'python3 bin/ask repo doctor-catalog --strict --json'`

Use `data.catalog_parity.operator_action` as the next operator step before rerouting.

## What To Run Next

- Full release-readiness checks: `bash Infrastructure/scripts/verify-work.sh`
- Command reference: `/AGENTS.md`
- Workflow and safety defaults: `/Docs/agents/13-workflow-and-safety-guidance.md`
