# Canonical Lesson Schema (MVP + Phase 4 forward-compat)

Defines promoted lesson records and lifecycle lineage.

## Table of Contents

- [Required fields](#required-fields)
- [Lifecycle states](#lifecycle-states)
- [Integrity rules](#integrity-rules)
- [Example](#example)

## Required fields

```yaml
schema_version: string
lesson_id: string
scope_skill: string
scope_profile: string
status: string                         # promoted | active | superseded | deprecated | revoked
effective_from: string                 # ISO-8601
effective_to: string|null
supersedes_lesson_id: string|null
superseded_by_lesson_id: string|null
confidence: float                      # 0..1
provenance:
  run_id: string
  iteration_ids: [int]
  prompt_hash: string
  rubric_version: string
  evaluator_version: string
review:
  reviewer_ids: [string]
  decision: string                     # approved | rejected
  security_checklist_passed: bool
```

## Lifecycle states

- `promoted -> active`
- `active -> superseded | revoked | deprecated`
- `superseded -> revoked | deprecated`

## Integrity rules

- At most one overlapping `active` lesson window per `{scope_skill, scope_profile}`.
- `revoked` lessons are excluded from retrieval immediately.
- Retrieval tie-break (Phase 4+): `status_priority -> confidence -> recency -> lesson_id`.

## Example

```json
{
  "schema_version": "1.0",
  "lesson_id": "lesson_ui_20260220_001",
  "scope_skill": "ui-ux-creative-coding",
  "scope_profile": "ui",
  "status": "active",
  "effective_from": "2026-02-20T19:50:00Z",
  "effective_to": null,
  "supersedes_lesson_id": null,
  "superseded_by_lesson_id": null,
  "confidence": 0.82,
  "provenance": {
    "run_id": "run_20260220_8f4c8d",
    "iteration_ids": [
      1,
      2
    ],
    "prompt_hash": "sha256:...",
    "rubric_version": "2026-02-19",
    "evaluator_version": "v1"
  },
  "review": {
    "reviewer_ids": [
      "jamie"
    ],
    "decision": "approved",
    "security_checklist_passed": true
  }
}
```
