# Iteration Journal Schema (MVP)

Immutable per-iteration evidence artifact for the recursive loop.

## Table of Contents

- [Required fields](#required-fields)
- [Embedded reports](#embedded-reports)
- [Example](#example)

## Required fields

```yaml
schema_version: string
run_id: string
iteration_id: int
run_version: int
state: string                         # accepted | rejected
created_at: string                    # ISO-8601
created_by: string
rubric_version: string
evaluator_version: string
persona_set_id: string
prompt_hash: string                   # sha256
applied_lessons: []                   # must be empty in MVP Phases 1-3
generated:
  content_ref: string
  token_estimate: int
evaluation_report: object             # immutable embedded document
diagnosis: object
improvement_action: object
reevaluation_report: object
criterion_deltas:                     # key=criterion_id, value=float
  <criterion_id>: float
```

## Embedded reports

`evaluation_report` minimum:
- `judge_mode` (`standard` or `adversarial`)
- `scores` map by criterion ID
- `overall_score`
- `findings[]`
- `eligible_for_gate_check`

`reevaluation_report` minimum:
- same score shape as `evaluation_report`
- `non_regression_passed`
- `gate_decision` (`continue | pass | fail | escalate`)

## Example

```json
{
  "schema_version": "1.0",
  "run_id": "run_20260220_8f4c8d",
  "iteration_id": 1,
  "run_version": 1,
  "state": "accepted",
  "created_at": "2026-02-20T19:44:00Z",
  "created_by": "recursive-skill-loop",
  "rubric_version": "2026-02-19",
  "evaluator_version": "v1",
  "persona_set_id": "ui-v1-checkpoint",
  "prompt_hash": "sha256:...",
  "applied_lessons": [],
  "generated": {
    "content_ref": "artifacts/skill-graphs/runs/run_20260220_8f4c8d/iter-1-generated.txt",
    "token_estimate": 1210
  },
  "evaluation_report": {
    "judge_mode": "standard",
    "scores": {
      "clarity": 0.73,
      "specificity": 0.69,
      "safety": 0.9
    },
    "overall_score": 0.78,
    "findings": [
      {
        "severity": "warn",
        "message": "Specificity below threshold"
      }
    ],
    "eligible_for_gate_check": true
  },
  "diagnosis": {
    "weakest_criteria": [
      "specificity"
    ],
    "reason": "Need concrete file paths and acceptance checks"
  },
  "improvement_action": {
    "action_type": "tighten_constraints",
    "summary": "Add explicit file path + measurable acceptance criteria"
  },
  "reevaluation_report": {
    "judge_mode": "standard",
    "scores": {
      "clarity": 0.78,
      "specificity": 0.74,
      "safety": 0.9
    },
    "overall_score": 0.81,
    "non_regression_passed": true,
    "gate_decision": "pass"
  },
  "criterion_deltas": {
    "clarity": 0.05,
    "specificity": 0.05,
    "safety": 0.0
  }
}
```

Related:
- [Task profile schema](/docs/skill-graphs/schemas/task-profile.schema.md)
- [Gate contract schema](/docs/skill-graphs/schemas/gate-contract.schema.md)
