# Gate Contract Schema (MVP)

Single source of truth for run-time and rolling health gates.

## Table of Contents

- [Threshold registry](#threshold-registry)
- [Run-time gates](#run-time-gates)
- [Program health SLOs](#program-health-slos)
- [Event enum](#event-enum)

## Threshold registry

| ID | Definition | Target | Enforcement |
|---|---|---|---|
| `TR-01` | Stability consecutive pass count | `N>=1` MVP, `N>=3` Phase 4+ | Blocking in MVP |
| `TR-02` | Critical non-regression | `100%` | Blocking |
| `TR-03` | Budget compliance | `>=95%` | Blocking |
| `TR-04` | Evaluator consistency flip rate | `<=3%` | Advisory MVP, hard Phase 3+ |
| `TR-05` | Judge calibration agreement | `>=80%` | Advisory MVP, hard Phase 3+ |
| `TR-06` | Promotion precision | `>=70%` | Hard Phase 4+ |

## Run-time gates

```yaml
gates:
  - id: stability
    threshold_ref: TR-01
    class: blocking
    evidence: iteration_journal
  - id: critical_non_regression
    threshold_ref: TR-02
    class: blocking
    evidence: criterion_deltas
  - id: budget_compliance
    threshold_ref: TR-03
    class: blocking
    evidence: runtime_counters
  - id: promotion_safety
    threshold_ref: required
    class: blocking
    evidence: promotion_decision.gate_decision
  - id: evaluator_consistency
    threshold_ref: TR-04
    class: advisory_mvp_blocking_phase3
    evidence: evaluation_report
  - id: judge_calibration_eligibility
    threshold_ref: TR-05
    class: advisory_mvp_blocking_phase3
    evidence: judge_registry
```

## Program health SLOs

```yaml
slos:
  - metric: evaluator_consistency_flip_rate
    threshold_ref: TR-04
    window: 7d
  - metric: judge_calibration_agreement
    threshold_ref: TR-05
    window: 14d
  - metric: budget_compliance
    threshold_ref: TR-03
    window: 7d
  - metric: promotion_precision
    threshold_ref: TR-06
    window: 14d
```

## Event enum

MVP core:
- `run_initialized`
- `run_state_changed`
- `promotion_approved`
- `failure_event`

Deferred (Phase 4+):
- `run_inspected`
- `lesson_revised`
- `scan_summary`
- `pattern_candidate`

Related:
- [Skill graph index](/docs/skill-graphs)
