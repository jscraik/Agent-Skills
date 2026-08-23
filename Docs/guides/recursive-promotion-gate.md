# Guide: Human Promotion Gate for Recursive Runs (Phase 3)

Use this guide to create and validate `promotion_decision.json` for a completed run.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Approve a run](#approve-a-run)
- [Reject a run](#reject-a-run)
- [Validate decision directly](#validate-decision-directly)
- [CI enforcement](#ci-enforcement)
- [Expected output](#expected-output)

## Prerequisites

- A completed run directory under `/Infrastructure/artifacts/skill-graphs/runs/<run_id>`.
- A lesson content file for security/PII scanning when approving (required for approved decisions).
- Reviewer policy + signature files:
  - `/docs/skill-graphs/governance/recursive-loop-approvers.yaml`
  - `/docs/skill-graphs/governance/recursive-loop-approvers.sig`

## Approve a run

```bash
bash Infrastructure/scripts/lifecycle-and-sync/human_promote_recursive_run.sh \
  --run-id run_20260220T150021Z_518880 \
  --lesson-id lesson_ui_20260220_001 \
  --reviewer jamie \
  --expected-version v1 \
  --lesson-file docs/skill-graphs/workflows/reviewer-rubric.md \
  --policy-file docs/skill-graphs/governance/recursive-loop-approvers.yaml \
  --policy-sig-file docs/skill-graphs/governance/recursive-loop-approvers.sig \
  --note "Promotion approved after rubric + security checks"
```

## Reject a run

```bash
bash Infrastructure/scripts/lifecycle-and-sync/human_promote_recursive_run.sh \
  --run-id run_20260220T150021Z_518880 \
  --lesson-id lesson_ui_20260220_001 \
  --reviewer jamie \
  --decision rejected \
  --note "Rejected: non-regression failed"
```

## Validate decision directly

```bash
python3 Skills/skill-builder/Infrastructure/scripts/validate_recursive_promotion.py \
  --run-dir Infrastructure/artifacts/skill-graphs/runs/run_20260220T150021Z_518880 \
  --decision-file Infrastructure/artifacts/skill-graphs/runs/run_20260220T150021Z_518880/promotion_decision.json \
  --lesson-file docs/skill-graphs/workflows/reviewer-rubric.md
```

## CI enforcement

Pull requests touching `promotion_decision.json` run:

```bash
bash Infrastructure/scripts/lifecycle-and-sync/validate_recursive_promotions.sh --changed-only --base-sha <base_sha> --head-sha <head_sha>
```

Workflow: `.github/workflows/recursive-promotion-gate.yml`.

## Expected output

- `promotion_decision.json` created/updated in the run directory.
- Validation report emitted to stdout as JSON.
- For approved decisions, canonical lesson lifecycle updated in:
  - `Infrastructure/artifacts/skill-graphs/lessons/canonical-lessons.jsonl`
  - `Infrastructure/artifacts/skill-graphs/lessons/canonical-lesson-index.json`
- For approved decisions, a `promotion_approved` event recorded in `events.jsonl` (idempotent per run+lesson).
- Rejected policy/role/signature paths emit immutable `run_blocked` evidence in `run_blocker.json` + `events.jsonl`.

Related:

- [Promotion gate workflow](/docs/skill-graphs/workflows/promotion-gate.md)
