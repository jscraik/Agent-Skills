# PU-012 Breaker Review: Loop 3 Pass 2

## Findings

### Medium: A missing install receipt can still be classified as either fail or blocked

- Evidence:
  - The conformance rules still say that when installed SDK evidence exists but the lockfile is absent, conformance status must be fail or blocked. See .harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:263.
  - The acceptance matrix repeats the same ambiguity for the missing-receipt path: VAC-004 says a lockfile that references a missing install receipt should yield conformance status is fail or blocked. See .harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:436.
  - That is in tension with the deterministic status table, which classifies drift after a valid root is accepted as validation_failure / fail and reserves blocked for authority or runtime refusal before inspection. See .harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:272-281.
- Why it matters: implementation and test authors can legitimately pick different exit families for the same missing-receipt fixture. That makes the handoff non-deterministic and risks a spec-compliant implementation that still fails the later status-semantic tests.
- Concrete fix: pin this fixture to one exit family in every normative section. The simplest repair is to change both the conformance rule and VAC-004 to fail only, matching the deterministic status table and keeping blocked reserved for pre-inspection authority/runtime refusal.

## Accountability Receipt

- status: complete
- artifact_paths:
  - .harness/reviews/pu-012-breaker-loop-3-pass-2.md
- manifest_path: artifacts/agent-runs/adversarial-reviewer-019e9ded-9e94-7182-b781-72deda74ac98/manifest.json
- findings_count: 1
- failures_or_blockers: none
- improvement_opportunities:
  - Tighten the missing-receipt language so the conformance rules, acceptance matrix, and deterministic status table all name the same exit family.
- strengths:
  - The spec now has executable no-discovery coverage, broad-root refusal, moved-identity drift handling, cleanup-readiness classification, and capability-truth wiring.
  - The remaining issue is narrow and localized to one fixture class rather than a missing subsystem.
- validation_evidence:
  - Static review of the current spec text and prior breaker-loop reports; no source files were edited.
- next_action:
  - Update the spec wording before handing it to implementation, or explicitly justify why this one fixture should remain an exception to the deterministic status table.
- useful_findings:
  - The broad-root, no-project-root, and project_conformance gaps from earlier passes appear closed.
  - The last remaining ambiguity is the only blocker-grade inconsistency I found in the current text.
- avoided_false_positive:
  - I did not re-flag the validation-scope or mise-launch issues because the current spec already makes those executable and testable.
- evidence_quality: High
- followed_scope: reviewed only the PU-012 spec and the immediately relevant prior breaker reports needed to judge closure.
- reusable_learning: keep the status-class table and the acceptance matrix in one-to-one agreement; permissive wording in an earlier rule section can silently reopen exit-family drift.
- coordinator_score: 8/10

WROTE: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-3-pass-2.md
