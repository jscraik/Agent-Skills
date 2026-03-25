# Skill Lesson Observation Schema

Defines the per-run observation artifact that sits between `capture_record.json` and
promotable lessons. Use it to record what was good, what was weak, and what should
change before a candidate lesson is proposed.

## Table of Contents

- [Purpose](#purpose)
- [Artifact location](#artifact-location)
- [Required fields](#required-fields)
- [Observation rules](#observation-rules)
- [Promotion guidance](#promotion-guidance)
- [Example](#example)

## Purpose

Use `lesson_observations.json` when you want the skill graph to learn from real runs
without editing the skill after every invocation.

This artifact is for:

- scoring a run against a skill-specific rubric;
- capturing repeated positive and negative signals;
- pointing to the exact part of the skill or reference docs that should change;
- separating "interesting feedback" from "safe to promote".

## Artifact location

- Per-run artifact: `artifacts/skill-graphs/runs/<run_id>/lesson_observations.json`
- Candidate lesson output: `artifacts/skill-graphs/runs/<run_id>/lesson_candidates.json`
- Promoted lesson store: `artifacts/skill-graphs/lessons/canonical-lessons.jsonl`

## Required fields

```yaml
schema_version: "1.0"
observation_id: string
run_id: string
profile_id: string
scope_skill: string
scope_profile: string
rubric_version: string
created_at: string                    # ISO-8601
source: string                        # post_run_review | shadow_cycle | manual_review | user_feedback
feedback_status: string               # worked | partly | didnt_work | missing
summary:
  outcome_label: string               # strengthen | hold | investigate | reject_candidate
  rationale: string
  strongest_positive_dimensions: [string]
  strongest_negative_dimensions: [string]
observations:
  - dimension_id: string
    verdict: string                   # positive | negative | mixed | unknown
    confidence: float                 # 0..1
    summary: string
    evidence: [string]
    recommendation: string
    target_paths: [string]
promotion_hint:
  patch_strategy: string              # eval_only | reference_doc | skill_text | hold
  min_confirming_runs: int
  blocking_reasons: [string]
  related_lesson_ids: [string]
```

## Observation rules

- One run can produce multiple observations.
- Observations should be rubric-bound, not vague taste notes.
- `target_paths` should point to the smallest useful patch area, for example:
  - `frontend/ui/frontend-ui-design/SKILL.md#Validation`
  - `frontend/ui/frontend-ui-design/references/learning-rubric.yaml`
  - `frontend/ui/frontend-ui-design/references/redesign-audit-lens.md`
- Single-run observations may inform review, but must not directly rewrite a skill.
- If the run quality was weak because the request was underspecified, record that in
  `summary.rationale` and prefer `patch_strategy: hold`.

## Promotion guidance

- `eval_only`
  - Use when the signal is real but the skill text should not change yet.
  - Good for adding a regression test before touching the skill itself.
- `reference_doc`
  - Use when the lesson belongs in a focused reference file instead of the main skill.
- `skill_text`
  - Use only after repeated confirming runs or a measured benchmark lift.
- `hold`
  - Use when evidence is thin, contradictory, or likely caused by request-specific noise.

Recommended thresholds:

- 1 run: capture only
- 2 matching runs: candidate lesson plus eval coverage
- 3 or more matching runs, or clear benchmark lift: propose a skill patch

## Example

```json
{
  "schema_version": "1.0",
  "observation_id": "obs_frontend_ui_design_20260321_001",
  "run_id": "run_20260321T182400Z_a18c4f",
  "profile_id": "frontend-ui-frontend-ui-design",
  "scope_skill": "frontend/ui/frontend-ui-design",
  "scope_profile": "frontend",
  "rubric_version": "2026-03-21",
  "created_at": "2026-03-21T18:25:10Z",
  "source": "post_run_review",
  "feedback_status": "partly",
  "summary": {
    "outcome_label": "investigate",
    "rationale": "The output was accessible and implementation-ready, but the first viewport lacked a dominant anchor and collapsed into a generic card grid.",
    "strongest_positive_dimensions": [
      "accessibility_contract",
      "implementation_readiness"
    ],
    "strongest_negative_dimensions": [
      "visual_distinction",
      "restraint_and_composition"
    ]
  },
  "observations": [
    {
      "dimension_id": "visual_distinction",
      "verdict": "negative",
      "confidence": 0.84,
      "summary": "The proposed landing layout felt interchangeable with a generic SaaS hero.",
      "evidence": [
        "Hero relied on stacked cards instead of one dominant composition.",
        "No memorable visual anchor was established in the first viewport."
      ],
      "recommendation": "Strengthen the visually led surface guidance so the first viewport starts from composition and one dominant takeaway.",
      "target_paths": [
        "frontend/ui/frontend-ui-design/SKILL.md#Visually-Led-Surfaces",
        "frontend/ui/frontend-ui-design/references/learning-rubric.yaml"
      ]
    }
  ],
  "promotion_hint": {
    "patch_strategy": "reference_doc",
    "min_confirming_runs": 3,
    "blocking_reasons": [
      "single_run_only"
    ],
    "related_lesson_ids": []
  }
}
```
