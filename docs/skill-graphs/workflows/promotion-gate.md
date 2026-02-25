# Promotion Gate Workflow (MVP)

Canonical promotions are human-gated and must include provenance + security evidence.

## Table of Contents

- [Inputs](#inputs)
- [Gate checks](#gate-checks)
- [Decision states](#decision-states)
- [Commands](#commands)
- [CI enforcement](#ci-enforcement)
- [Output artifact](#output-artifact)

## Inputs

- `run.json`
- `iteration_journal.jsonl`
- candidate lesson payload
- reviewer identity

## Gate checks

1. **Runtime gate completeness**
   - Run has terminal status.
   - Stop reason is explicit.
2. **Evidence completeness**
   - Latest iteration includes evaluation + re-evaluation + criterion deltas.
3. **Provenance integrity**
   - Required immutable fields present (`schema_version`, `rubric_version`, `evaluator_version`, `persona_set_id`, `prompt_hash`).
4. **Security/privacy**
   - No secrets/PII in lesson body or attached logs.
   - Approved decisions must include lesson scan evidence (`lesson_source_path` + `lesson_content_sha256`).
   - Retention + redaction policy acknowledged.
5. **Reviewer checklist**
   - At least one authorized reviewer signs off.

## Decision states

- `draft` -> `candidate` -> `approved`
- `draft` -> `rejected`
- `candidate` -> `rejected`

## Commands

Approve run:

```bash
bash scripts/human_promote_recursive_run.sh \
  --run-id <run_id> \
  --lesson-id <lesson_id> \
  --reviewer <reviewer_id> \
  --expected-version <version_token> \
  --lesson-file <path_to_lesson_file>
```

Validate decision directly:

```bash
python3 utilities/skill-creator/scripts/validate_recursive_promotion.py \
  --run-dir artifacts/skill-graphs/runs/<run_id> \
  --decision-file artifacts/skill-graphs/runs/<run_id>/promotion_decision.json \
  --lesson-file <path_to_lesson_file>
```

## CI enforcement

Promotion artifacts are validated in CI by:

```bash
bash scripts/validate_recursive_promotions.sh --changed-only --base-sha <base_sha> --head-sha <head_sha>
```

Workflow: `.github/workflows/recursive-promotion-gate.yml`.

## Output artifact

`promotion_decision.json` must include:

- `decision`: `approved|rejected|candidate|draft`
- `reviewer_ids[]`
- `gate_decision` summary
- `expected_version`
- security checklist fields
- provenance references (`run_id`, `iteration_ids`, `prompt_hash`)
- `lesson_source_path` and `lesson_content_sha256` for approved decisions
- confidence contract fields (`confidence.score`, `confidence.bucket`, `confidence.calibration_bucket`)
- evidence completeness linkage (`evidence_packet.evidence_packet_id`, `evidence_packet.completeness_score`)
- draft candidate payload(s) in `lesson_candidates[]` for queueing/reviewer triage
- retrieval attribution in `injected_lesson_ids[]` for traceability
- runtime control snapshot in `runtime_controls{rollout_mode, auto_capture_enabled, auto_apply_enabled}` for rollback audits

Approved promotions emit a deduplicated `promotion_approved` debug event in `run/debug/events.jsonl`.

Related:
- [Reviewer rubric](/docs/skill-graphs/workflows/reviewer-rubric.md)
- [Human promotion guide](/docs/guides/recursive-promotion-gate.md)
- [Canonical lesson schema](/docs/skill-graphs/schemas/canonical-lesson.schema.md)
