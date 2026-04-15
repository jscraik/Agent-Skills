# Promotion Decision Schema (v1.1)

Defines the promotion decision artifact contract for recursive skill runs.

## Table of Contents

- [Required fields](#required-fields)
- [Counterfactual uplift contract](#counterfactual-uplift-contract)

## Required fields

```yaml
schema_version: "1.1"
run_id: string
lesson_id: string
decision: "draft|candidate|approved|rejected"
reviewer_ids: string[]
expected_version: string
gate_decision:
  runtime_gates_passed: bool
  provenance_complete: bool
  security_checklist_passed: bool
provenance:
  prompt_hash: string
  rubric_version: string
  evaluator_version: string
  iteration_ids: int[]
runtime_controls:
  rollout_mode: "off|observe_only|active"
  effective_rollout_mode: "off|observe_only|active"
  auto_capture_enabled: bool
  auto_apply_enabled: bool
counterfactual_uplift: object
```

## Counterfactual uplift contract

```yaml
counterfactual_uplift:
  analysis_method_version: "counterfactual_uplift_v1"
  decision_window_days: int
  sample_size: int
  treated_sample_size: int
  control_sample_size: int
  treatment_outcome: float|null
  control_outcome: float|null
  uplift_delta: float|null
  uplift_confidence_band:
    method: string
    level: float
    lower: float|null
    upper: float|null
  match_quality_metrics:
    treated_unmatched_rate: float
    max_allowed_unmatched_rate: float
    valid: bool
  promotion_thresholds:
    min_pairs_total: int
    min_pairs_per_skill: int
    delta_min: float
    ci_lower_min: float
  auto_apply_thresholds:
    min_pairs_total: int
    min_pairs_per_skill: int
    delta_min: float
    ci_lower_min: float
  promotion_decision: "pass|hold|regressed|insufficient_data|insufficient_match_quality"
  auto_apply_decision: "pass|hold|regressed|insufficient_data|insufficient_match_quality"
```
