# CE Review Compaction Context

Read when: you need the full severity table, action-routing matrix, and extended examples moved from `SKILL.md` for line-budget governance.

## Severity Scale
| Level | Meaning | Action |
|---|---|---|
| **P0** | Critical breakage, exploitable vulnerability, data loss/corruption | Must fix before merge |
| **P1** | High-impact defect likely hit in normal usage, breaking contract | Should fix |
| **P2** | Moderate issue with meaningful downside (edge case, perf regression, maintainability trap) | Fix if straightforward |
| **P3** | Low-impact, narrow scope, minor improvement | User's discretion |

## Action Routing
| `autofix_class` | Default owner | Meaning |
|---|---|---|
| `safe_auto` | `review-fixer` | Local deterministic fix suitable for in-skill mutation |
| `gated_auto` | `downstream-resolver` or `human` | Fix exists but impacts behavior/contracts/permissions |
| `manual` | `downstream-resolver` or `human` | Actionable handoff work |
| `advisory` | `human` or `release` | Report-only output |

Routing rules: synthesis owns final route, choose conservative route on disagreement, only `safe_auto -> review-fixer` enters fixer queue, and `requires_verification: true` must be rechecked before completion.

## Additional examples
- "Please review the current branch as a whole package, not just technical nits, and tell me whether browser verification is needed before shipping."
- "I need a review of `docs/plans/2026-03-23-001-feat-example-plan.md` that tells me whether it is ready for `ce-work` or needs another workflow step first."
