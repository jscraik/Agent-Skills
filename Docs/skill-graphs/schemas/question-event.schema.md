# Question Event Schema (v1.0)

Defines the machine-readable event contract for all user-facing question events in the skill graph runtime.

## Table of Contents

- [Required fields](#required-fields)
- [Field definitions](#field-definitions)
- [Phase and type constraints](#phase-and-type-constraints)
- [Answer contract](#answer-contract)
- [Example](#example)

## Required fields

- `schema_version`
- `question_id`
- `run_id`
- `skill_id`
- `question_type`
- `phase`
- `origin_layer`
- `blocking`
- `required_for`
- `prompt_style`
- `header`
- `question`
- `options`
- `recommended_option_id`
- `created_at`

## Field definitions

```yaml
schema_version: "1.0"
question_id: string                   # stable per question emission
run_id: string                        # runtime invocation id
skill_id: string                      # owning skill identifier
question_type: string                 # route_clarification | preflight_clarification | approval_checkpoint | post_run_feedback
phase: string                         # route | hydrate_context | preflight | execution | approval_gate | terminal | feedback_capture
origin_layer: string                  # router | executor | guardrail | graph_capture
blocking: bool
required_for: string                  # route_selection | missing_required_input | policy_approval | outcome_feedback
prompt_style: string                  # multiple_choice | binary | one_tap_feedback
header: string
question: string
options:
  - id: string
    label: string
    description: string
recommended_option_id: string
confidence_trigger: float | null      # threshold that caused the question, when applicable
risk_tier: string | null              # low | medium | high
supersedes_question_id: string | null
created_at: string                    # ISO-8601
expires_at: string | null             # ISO-8601
answer:
  status: string                      # answered | skipped | timed_out | superseded | missing
  selected_option_id: string | null
  free_text: string | null
  answered_at: string | null          # ISO-8601
  answer_latency_ms: int | null
downstream_effect: string             # route_selected | execution_started | approval_granted | feedback_recorded | no_effect
```

## Phase and type constraints

Allowed combinations:

| `question_type` | Allowed `phase` values |
| --- | --- |
| `route_clarification` | `route` |
| `preflight_clarification` | `hydrate_context`, `preflight` |
| `approval_checkpoint` | `approval_gate` |
| `post_run_feedback` | `terminal`, `feedback_capture` |

Blocking defaults:

| `question_type` | Default `blocking` |
| --- | --- |
| `route_clarification` | `true` |
| `preflight_clarification` | `true` |
| `approval_checkpoint` | `true` |
| `post_run_feedback` | `false` |

Validation rules:

- `post_run_feedback` MUST be non-blocking.
- `route_clarification` MUST NOT appear after execution begins.
- `approval_checkpoint` MUST NOT be emitted as generic discovery.
- `required_for=outcome_feedback` MUST only be used with `post_run_feedback`.

## Answer contract

- `answer.status=missing` means the question was emitted but no explicit response was captured.
- `answer.status=superseded` means a later question replaced this one before an answer was used.
- `answer.free_text` should be redacted/sanitized before downstream promotion use.
- `downstream_effect=no_effect` is valid for skipped or missing post-run feedback.

## Example

```json
{
  "schema_version": "1.0",
  "question_id": "q_20260306_01",
  "run_id": "run_20260306T181500Z_abc123",
  "skill_id": "graph",
  "question_type": "post_run_feedback",
  "phase": "feedback_capture",
  "origin_layer": "graph_capture",
  "blocking": false,
  "required_for": "outcome_feedback",
  "prompt_style": "one_tap_feedback",
  "header": "Outcome",
  "question": "How did this recommendation perform?",
  "options": [
    {
      "id": "good",
      "label": "Good (Recommended)",
      "description": "The recommendation improved the outcome."
    },
    {
      "id": "neutral",
      "label": "Neutral",
      "description": "The recommendation had limited or mixed impact."
    },
    {
      "id": "bad",
      "label": "Bad",
      "description": "The recommendation made the outcome worse."
    }
  ],
  "recommended_option_id": "good",
  "confidence_trigger": null,
  "risk_tier": null,
  "supersedes_question_id": null,
  "created_at": "2026-03-06T18:15:40Z",
  "expires_at": null,
  "answer": {
    "status": "answered",
    "selected_option_id": "good",
    "free_text": "Reduced orphan notes",
    "answered_at": "2026-03-06T18:15:46Z",
    "answer_latency_ms": 6000
  },
  "downstream_effect": "feedback_recorded"
}
```

Related:
- [Question lifecycle contract](/docs/skill-graphs/question-lifecycle.md)
- [Capture record schema](/docs/skill-graphs/schemas/capture-record.schema.md)
