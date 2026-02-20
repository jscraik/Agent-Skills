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

- A completed run directory under `/artifacts/skill-graphs/runs/<run_id>`.
- A lesson content file for security/PII scanning when approving (required for approved decisions).

## Approve a run

```bash
bash scripts/human_promote_recursive_run.sh \
  --run-id run_20260220T150021Z_518880 \
  --lesson-id lesson_ui_20260220_001 \
  --reviewer jamie \
  --expected-version v1 \
  --lesson-file docs/skill-graphs/workflows/reviewer-rubric.md \
  --note "Promotion approved after rubric + security checks"
```

## Reject a run

```bash
bash scripts/human_promote_recursive_run.sh \
  --run-id run_20260220T150021Z_518880 \
  --lesson-id lesson_ui_20260220_001 \
  --reviewer jamie \
  --decision rejected \
  --note "Rejected: non-regression failed"
```

## Validate decision directly

```bash
python3 utilities/skill-creator/scripts/validate_recursive_promotion.py \
  --run-dir artifacts/skill-graphs/runs/run_20260220T150021Z_518880 \
  --decision-file artifacts/skill-graphs/runs/run_20260220T150021Z_518880/promotion_decision.json \
  --lesson-file docs/skill-graphs/workflows/reviewer-rubric.md
```

## CI enforcement

Pull requests touching `promotion_decision.json` run:

```bash
bash scripts/validate_recursive_promotions.sh --changed-only --base-sha <base_sha> --head-sha <head_sha>
```

Workflow: `.github/workflows/recursive-promotion-gate.yml`.

## Expected output

- `promotion_decision.json` created/updated in the run directory.
- Validation report emitted to stdout as JSON.
- For approved decisions, a `promotion_approved` event recorded in `debug/events.jsonl` (idempotent per run+lesson).

Related:
- [Promotion gate workflow](/docs/skill-graphs/workflows/promotion-gate.md)
