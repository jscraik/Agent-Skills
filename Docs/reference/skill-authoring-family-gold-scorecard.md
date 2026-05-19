---
title: Skill Authoring Family — Gold Standard Scorecard
type: reference
status: active
date: 2026-05-15
next_review: 2026-07-05
plan: Docs/plans/2026-04-05-feat-skill-authoring-family-gold-standard-upgrade-plan.md
---

# Skill Authoring Family — Gold Standard Scorecard

## Table of Contents
- [Readiness Summary](#readiness-summary)
- [Gate Evidence Links](#gate-evidence-links)
- [Metric Scorecard](#metric-scorecard)
- [Official-Doc Alignment](#official-doc-alignment)
- [Blocker Routing](#blocker-routing)
- [May 2026 Audit Freshness](#may-2026-audit-freshness)
- [Recent Changes](#recent-changes)

## Readiness Summary

| Status | Meaning |
|---|---|
| `gold` | All AC1–AC8 satisfied; trusted live evidence archived; no unresolved warnings |
| `structural-pass` | Structural gate passes; live evidence not yet captured for release-grade claim |
| `blocked` | One or more gate failures; not release-grade |

**Governance Requirement:** Any PR modifying skill authoring family behavior must run and pass the `authoring-family-gate` CI job before claiming `gold` status. The check must execute:
```bash
SKILL_FAMILY_RELEASE_READY=1 SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 SKILL_FAMILY_CODEX_PROFILE=fast SKILL_EVAL_TIMEOUT_SEC=300 bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```
PR approval is conditional on this job passing.

**Current status: `structural-pass`**  
Structural family gate passes for all 4 members. Trusted live evidence attempted 2026-04-05 — partial evidence captured (quota-limited); quota resets at 11:58 PM UTC. Re-run required before gold claim.

**Live eval attempt summary (2026-04-05):**
- Run command: `SKILL_FAMILY_RELEASE_READY=1 SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 SKILL_FAMILY_CODEX_PROFILE=fast SKILL_EVAL_TIMEOUT_SEC=300 bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
- Model: gpt-5.3-codex-spark (`[profiles.fast]`)
- Evidence dir: `Infrastructure/artifacts/validation/family-gate/20260405T182450Z/` (partial; evidence-index.json not written)
- Confirmed passes: 8/19 smoke cases for skill-builder
- Blocking issues: 2 behavioral gaps (cases 8, 10); 1 quota exhaustion (remaining skills not reached)
- Eval calibration applied: regexes widened for cases 7, 11; case 12 upgraded to discovery-heavy

Active family:
- `Skills/skill-builder` — structural pass ✓
- `Skills/skill-creator` — structural pass ✓
- `Skills/skill-installer` — structural pass ✓; quality uplifted (P3)
- `Skills/plugin-creator` — structural pass ✓; quality uplifted (P3)

## Gate Evidence Links

| Gate | Artifact | Status |
|---|---|---|
| Boundary reconciliation (P0) | `docs/reference/skill-authoring-family-boundary-decision.md` | complete |
| Trusted live eval evidence (P1) | `docs/evidence/skill-authoring-family/gold-evidence-index.json` (committed) or release asset | pending trusted run |
| Security hardening (P2) | OpenClaw output in gate run — 0 warnings | complete |
| Quality uplift (P3) | `docs/reference/skill-authoring-family-quality-baseline.md` | complete |
| Governance scorecard (P4) | `docs/reference/skill-authoring-family-gold-scorecard.md` | complete |

**To advance to `gold` status:** run with `SKILL_FAMILY_RELEASE_READY=1 SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1` and commit the resulting `evidence-index.json` to `docs/evidence/skill-authoring-family/gold-evidence-index.json`, or upload it as a release asset and link it in this scorecard.

## Metric Scorecard

| Metric | Value | Threshold | Pass? |
|---|---|---|---|
| OpenClaw warnings | 0 | 0 | ✓ |
| Adversarial eval threat classes | 4 (PI, exfiltration, tool abuse, retrieval contamination) | 4 | ✓ |
| skill-installer Variation | 10/15 | ≥ 8/15 | ✓ |
| skill-installer Empowerment | 5/5 | ≥ 3/5 | ✓ |
| skill-installer Scope Focus | 12/15 | ≥ 12/15 | ✓ |
| plugin-creator Variation | 13/15 | ≥ 8/15 | ✓ |
| plugin-creator Empowerment | 5/5 | ≥ 3/5 | ✓ |
| plugin-creator Scope Focus | 15/15 | ≥ 12/15 | ✓ |
| Family boundary consistency | Canonical (script=spec=matrix) | Non-contradictory | ✓ |
| Trusted live evidence | Partial (quota-limited 2026-04-05) | Required for gold | ✗ (pending midnight rerun) |
| Official-doc alignment | Checked 2026-04-05 | Quarterly | ✓ (next: 2026-07-05) |

## Official-Doc Alignment

Last checked: 2026-04-05

Sources verified:
- OpenAI Codex skills guidance: structure, `SKILL.md` conventions, discovery mechanism
- OpenAI tools and skills guidance: routing contracts and eval best practices
- OpenAI evaluation best practices: eval case design, acceptance patterns
- OpenAI shell/tool safety: risk categories for deterministic command guards
- OpenAI Codex plugin build guidance: plugin.json contract, marketplace entry schema
- OWASP Top 10 for LLM Applications (2025): adversarial threat classes verified against eval set
- NIST AI RMF 1.0: risk management posture review

Findings (2026-04-05): No breaking changes observed in official guidance versus current family contract. The adversarial eval additions (exfiltration, tool abuse, retrieval contamination) align with OWASP LLM Top 10 threat taxonomy.

Next review due: **2026-07-05**

## May 2026 Audit Freshness

Checked: **2026-05-15**

The stricter local audit flags are still intentional, but they are local gold
requirements rather than Tessl registry requirements:

- `references/contract.yaml` and `references/evals.yaml` remain required for a
  gold claim. Tessl reviews, local review dashboards, and run artifacts are
  evidence outputs; they do not replace the per-skill source contract and eval
  definitions.
- A short description can still be flagged even if Tessl validation passes.
  The local gate keeps a stricter activation bar because discovery quality is
  driven by concrete WHAT + WHEN wording and trigger terms.
- Safety, execution-boundary, failure-mode, gotcha, validation, and anti-pattern
  headings remain required for local gold because this repo uses skills as
  executable operating contracts, not only registry-readable documentation.
- `references/evals.yaml` may now include local signal-grading fields used by
  the May 2026 runner calibration: `expected_signals.required_terms`,
  `expected_signals.required_output_fields`,
  `expected_signals.required_source_reads`, `expected_signals.forbidden_terms`,
  `expected_signals.forbidden_actions`, `expected_signals.flow_steps`, and
  `budgets.min_expected_signal_score`.

The May 2026 audit language should therefore refer to skill-local `references/`
and `scripts/` directories. Historical `Infrastructure/references/` examples in
old evidence remain historical only and must not be used as the current contract.

### How to Perform Alignment Check

1. Review each official source for guidance updates (new conventions, deprecated patterns, new risk categories).
2. Compare against:
   - family SKILL.md routing and eval contracts
   - skill-local `references/evals.yaml` adversarial case set
   - `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py` benchmark contract
3. Record findings and update this scorecard.
4. If changes are required, open a spec update issue before modifying contracts.

## Blocker Routing

| Condition | Routing |
|---|---|
| Live eval pass rate < 100% | Retry-limited rerun; if still blocked, tag `family-gate-blocker` in issue tracker |
| New OpenClaw warning | Fix or create time-bound risk-acceptance record in `docs/reference/skill-authoring-family-risk-acceptance.md` |
| Analyzer score regression | Fix SKILL.md; do not accept PR that drops a dimension below its floor |
| Official-doc drift | Update alignment notes here; open spec issue if contract must change |
| Boundary drift reappears | Consult `docs/reference/skill-authoring-family-boundary-decision.md`; gate script is authoritative |

## Recent Changes

### 2026-04-05 — Gold Standard Upgrade (P0–P4)

**Changes:**
- P0: Reconciled active family boundary across spec, maturity matrix, and decision record. `plugin-creator` is now the canonical gate member; `plugin-builder` is adjacent handoff surface.
- P1: Added `SKILL_FAMILY_RELEASE_READY=1` mode to `validate_skill_authoring_family.sh` with evidence artifact capture, freshness constraints, branch-lineage metadata, and degraded-mode policy.
- P2: Fixed OpenClaw false positives by tightening `potential_exfiltration` context pattern (requires actual HTTP method calls, not bare string mentions). Added 3 new adversarial pressure cases: data exfiltration, tool abuse, retrieval contamination.
- P3: Uplifted `skill-installer` (Variation +10, Empowerment +5) and `plugin-creator` (Variation +13, Empowerment +5, Scope Focus +9). Frozen baseline documented.
- P4: Created this scorecard, `.harness/quality/criteria.md`, and official-doc alignment record.

**Plan:** `Docs/plans/2026-04-05-feat-skill-authoring-family-gold-standard-upgrade-plan.md`
