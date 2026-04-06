# Quality Criteria: Skill Authoring Family

**Canonical governance surface for skill-authoring family release-grade quality.**

## Table of Contents
- [Active Metrics](#active-metrics)
- [Failure Routing](#failure-routing)
- [Governance Cadence](#governance-cadence)
- [Related Artifacts](#related-artifacts)

This file is the authoritative quality gate for the active skill-authoring family:
- `utilities/skill-builder`
- `skills-system/skill-creator`
- `skills-system/skill-installer`
- `skills-system/plugin-creator`

## Active Metrics

| Metric | Owner | Threshold | SLO | Evidence path |
|---|---|---|---|---|
| Live-eval pass rate | codex | 100% per skill per gate run | Trusted run required for every release-grade claim | `artifacts/validation/baselines/family-gate-baseline.json` (checked-in baseline) or CI artifact upload |
| Flake rate (live runner) | codex | ≤1 transient failure before successful rerun is acceptable; >1 requires investigation | Retry-limited; block closeout if no successful rerun | `.harness/memory/LEARNINGS.md` operational notes |
| OpenClaw warning count | codex | 0 unresolved warnings | Zero-warning policy; residual must be risk-accepted | `docs/reference/skill-authoring-family-risk-acceptance.md` |
| Adversarial eval coverage | codex | All four threat classes covered: prompt injection, data exfiltration, tool abuse, retrieval contamination | Cases must appear in release eval inventory | `utilities/skill-builder/references/evals.yaml` pressure cases |
| Regression escape rate | codex | 0 regressions past family gate | No decrease >1 point in any non-targeted analyzer subscore | `.harness/memory/LEARNINGS.md` operational notes or CI artifact upload |
| Analyzer score floor (skill-installer) | codex | Variation ≥ 8/15, Empowerment ≥ 3/5, Scope Focus ≥ 12/15 | No regression below floor | `docs/reference/skill-authoring-family-quality-baseline.md` |
| Analyzer score floor (plugin-creator) | codex | Variation ≥ 8/15, Empowerment ≥ 3/5, Scope Focus ≥ 12/15 | No regression below floor | `docs/reference/skill-authoring-family-quality-baseline.md` |
| Doc freshness (official guidance) | codex | Quarterly review against official platform docs | SLA: 90 days between official-doc alignment checks | `docs/reference/skill-authoring-family-gold-scorecard.md` next-review field |

## Failure Routing

| Failure condition | Immediate action | Escalation |
|---|---|---|
| Live eval non-pass | Retry-limited rerun; if still failing, open issue tagged `family-gate-blocker` | Block release-grade claim until resolved |
| OpenClaw warning | Root-cause and fix, or create time-bound risk-acceptance record | Block family gate until resolved or risk-accepted |
| Analyzer score regression | Fix SKILL.md content; do not mark P3 complete without floor checks passing | Escalate to maintainer if root cause is a tooling change |
| Official-doc drift | Update alignment notes in scorecard; flag if behavior contract must change | Open spec update issue before any contract changes |

## Governance Cadence

- **Family gate run**: every PR that touches family members or their validation scripts
- **Trusted live eval run**: required before any release-grade readiness claim
- **Official-doc alignment check**: quarterly (90 days from last review)
- **Scorecard review**: after any gate failure or quarterly

## Related Artifacts

- `docs/reference/skill-authoring-family-gold-scorecard.md` — single-view scorecard
- `docs/reference/skill-authoring-family-boundary-decision.md` — family membership authority
- `docs/reference/skill-authoring-family-quality-baseline.md` — analyzer baselines and thresholds
- `docs/reference/skill-authoring-family-risk-acceptance.md` — residual risk register (created when needed)
- `docs/reference/skill-authoring-validation-maturity-matrix.md` — readiness matrix (optional)
- `scripts/validate_skill_authoring_family.sh` — enforcement gate
