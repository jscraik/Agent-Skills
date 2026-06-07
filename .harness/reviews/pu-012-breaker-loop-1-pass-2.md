# PU-012 Breaker Review: Loop 1 Pass 2

## Findings

### High: Missing lockfile drift states can still pass the gate
- Evidence: [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:146-147), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:218-219), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:369-370), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:350-354)
- Why it matters: FR-005 explicitly requires missing, invalid, unsupported, and stale lockfile states to be classified. The acceptance matrix only exercises invalid JSON and schema-invalid lockfiles, so an implementation can ignore unsupported schema versions or stale lockfiles and still satisfy the listed tests. That leaves the gate vulnerable to trusting outdated or incompatible project metadata.
- Concrete fix: Add explicit acceptance cases and temp-project tests for unsupported lockfile schema/version and stale lockfile state. The spec should also name the expected lockfile_status and issue codes for those cases so they cannot be folded into generic invalid-lockfile handling.
- Validation ownership: Spec gap
- Impacted behavior: Project status can still report a project as coherent when the lockfile version is unsupported or stale.
- Confidence: 92/100

### Medium: status and doctor are still defined by one shape, so compact vs expanded output is unenforceable
- Evidence: [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:136), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:183-198), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:371-374)
- Why it matters: The prose says status should be compact and doctor should expand issues/manual actions, but the schema gives both operations the same required top-level fields. A future implementation can make them identical and still satisfy the spec, which defeats the operator distinction the slice is trying to introduce.
- Concrete fix: Either split the schema by operation or define an operation-specific field matrix that makes status intentionally smaller and doctor intentionally richer. If the same fields are meant to appear in both, remove the compact/expanded distinction from the prose so the contract is honest.
- Validation ownership: Spec gap
- Impacted behavior: Downstream callers cannot rely on doctor providing more detail than status, or on status staying compact.
- Confidence: 84/100

### Medium: Missing-root refusal is still only output-tested, not guarded against cwd or parent reads
- Evidence: [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:114), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:348-349), [spec](.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:375-378)
- Why it matters: The spec correctly says the command must stop before reading cwd, parent directories, markers, lockfiles, receipts, or installed files. But the current validation plan only checks that the command returns an error when --project-root is omitted; it does not instrument or otherwise prove that no filesystem discovery happened before the refusal. A root-inference bug could still slip through.
- Concrete fix: Add a negative test that makes cwd/parent/project-marker access observable, or use a harness that fails the run if Path.cwd(), parent traversal, or project-marker reads occur before argument validation rejects the command.
- Validation ownership: Spec gap
- Impacted behavior: The most important safety guarantee, fail-closed root selection, can still be implemented with hidden cwd fallback behavior.
- Confidence: 78/100

## Accountability Receipt

- status: complete
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-1-pass-2.md
  - /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/artifacts/agent-runs/adversarial-reviewer-019e9ddf-3e9a-7ed1-b048-beaca8728a81/manifest.json
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/artifacts/agent-runs/adversarial-reviewer-019e9ddf-3e9a-7ed1-b048-beaca8728a81/manifest.json
- findings_count: 3
- failures_or_blockers: none
- improvement_opportunities:
  - Name the stale and unsupported lockfile states in acceptance and validation, not only in prose.
  - Make the status vs doctor distinction observable in the schema.
  - Instrument the omitted-root refusal so it proves no cwd or parent discovery happened.
- strengths:
  - The spec now clearly bakes in explicit --project-root refusal coverage.
  - The mise launch-time env block is now present in the validation section, which closes the earlier runtime-setup gap.
  - The project-conformance capability row is now named directly instead of relying on prose-only notes.
- validation_evidence:
  - Static review of the spec plus the referenced Skills SDK router, capability-status, validation-scope, and root-handling contracts.
  - No source files were edited; only the report artifact and run manifest were written.
- next_action: tighten the spec acceptance matrix so lockfile drift, operation-specific output shape, and missing-root refusal are all mechanically provable.
- useful_findings:
  - Lockfile freshness is still the easiest path to a false positive.
  - The compact/expanded distinction needs a schema-level discriminator to be enforceable.
  - Output-only missing-root tests are not enough for a safety-critical root-selection rule.
- avoided_false_positive: I did not re-flag the earlier mise env issue; the spec now includes an executable env block in the validation section.
- evidence_quality: High for the lockfile-state omission, medium-high for the operation-shape ambiguity, and medium for the missing-root instrumentation gap.
- followed_scope: Reviewed only the PU-012 spec and the directly relevant Skills SDK router, capability-status, validation, and root-handling contracts needed to judge it.
- reusable_learning: When a spec bans implicit cwd fallback, the validation plan should prove the refusal path before any discovery reads, not just after an error string appears.
- coordinator_score: 8/10

WROTE: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-1-pass-2.md

