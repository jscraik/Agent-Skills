# Task Profile Schema (MVP)

Defines runtime configuration for a loop run.

## Table of Contents

- [Required fields](#required-fields)
- [Field definitions](#field-definitions)
- [Delegation block (required for onboarding)](#delegation-block-required-for-onboarding)
- [Example](#example)

## Required fields

- `schema_version`
- `profile_id`
- `scope_skill`
- `scope_profile`
- `rubric_version`
- `evaluator_version`
- `persona_set_id`
- `thresholds`
- `criteria`
- `delegation`

## Field definitions

```yaml
schema_version: string                 # e.g. "1.0"
profile_id: string                     # stable profile key
scope_skill: string                    # skill namespace
scope_profile: string                  # profile namespace
rubric_version: string
evaluator_version: string
persona_set_id: string
thresholds:
  stability_consecutive_passes: int    # TR-01
  critical_non_regression: bool        # TR-02
  max_iterations: int
  max_elapsed_ms: int
  max_tokens: int
  no_improvement_escalation_limit: int # escalation guardrail for repeated no-op deltas
criteria:
  - id: string
    label: string
    threshold: float                    # 0..1
    weight: float                       # 0..1
    critical: bool
delegation:                             # required Cockpit Rule context for onboarding
  mode: string                          # autopilot | co-pilot | manual
                                        # legacy compatibility: collaboration -> co-pilot
  human_baseline_minutes: float         # HBT estimate
  ai_process_minutes: float             # APT estimate
  probability_of_success: float         # Ps estimate 0..1
  rationale: string
```

## Delegation block (required for onboarding)

`delegation` is required for all-skill onboarding so each run artifact captures explicit
Autopilot/Co-pilot/Manual override decisions and agentic cost-benefit assumptions.
`mode` must be emitted canonically as `autopilot`, `co-pilot`, or `manual`.
Legacy `collaboration` may be read for compatibility, but new profiles must not emit it.

## Example

```json
{
  "schema_version": "1.0",
  "profile_id": "ui-ux-creative-coding",
  "scope_skill": "ui-ux-creative-coding",
  "scope_profile": "ui",
  "rubric_version": "2026-02-19",
  "evaluator_version": "v1",
  "persona_set_id": "ui-v1-checkpoint",
  "delegation": {
    "mode": "co-pilot",
    "human_baseline_minutes": 90,
    "ai_process_minutes": 30,
    "probability_of_success": 0.78,
    "rationale": "High-context design work benefits from iterative human + agent review."
  },
  "thresholds": {
    "stability_consecutive_passes": 1,
    "critical_non_regression": true,
    "max_iterations": 4,
    "max_elapsed_ms": 120000,
    "max_tokens": 12000,
    "no_improvement_escalation_limit": 2
  },
  "criteria": [
    {
      "id": "clarity",
      "label": "Instructional clarity",
      "threshold": 0.72,
      "weight": 0.3,
      "critical": true
    },
    {
      "id": "specificity",
      "label": "Concrete implementation detail",
      "threshold": 0.7,
      "weight": 0.3,
      "critical": true
    },
    {
      "id": "safety",
      "label": "Security/safety compliance",
      "threshold": 0.85,
      "weight": 0.4,
      "critical": true
    }
  ]
}
```

Related:
- [Iteration journal schema](/docs/skill-graphs/schemas/iteration-journal.schema.md)
- [Gate contract schema](/docs/skill-graphs/schemas/gate-contract.schema.md)
