# PU-011 Trace Plan Adversarial Review: Validation and Artifact Gaps

## Findings

### High: The plan proves a manual `skills-sdk` entrypoint but not the changed-file routing that would schedule it
- Evidence: Trace plan TR-012 only requires a recognized `skills-sdk` scope and an unknown-scope failure check (`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:66`), and S0 says it should freeze changed-file triggers without naming a proof artifact (`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:93-98`). The spec requires changed-file routing for SDK schema, contract, envelope/output, spec/plan/notes, and HTML edits (`.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:170-173`).
- Impacted behavior: A future implementation can make `./bin/ask repo validate --scope=skills-sdk --json --robot` pass manually while still failing to auto-schedule the new lane on relevant file edits. That leaves contract drift invisible unless someone remembers to invoke the scope by hand.
- Remediation: Add a trace row or acceptance case that proves changed-file routing for the exact SDK file families, not just scope recognition. The slice should fail if a touched schema, contract, notes, or HTML artifact does not schedule `skills-sdk`.
- Confidence: 95
- Validation ownership: plan gap

### Medium: The implementation-notes contract is weaker than the spec it is supposed to enforce
- Evidence: TR-009 only asks for a valid `.html` or `.mdx` fixture and an invalid missing-section/evidence fixture (`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:63`). The spec requires implementation notes to cover decisions, changed assumptions, tradeoffs, validation/evidence, and open follow-ups, and it defines a dedicated positive/negative notes fixture family (`.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:163-164`, `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:388-390`).
- Impacted behavior: A notes file can still pass if it has a notes section and some evidence but omits changed assumptions, tradeoffs, or open follow-ups. That weakens the handoff between slices because the next implementer loses the rationale the spec says must be preserved.
- Remediation: Expand the trace row and acceptance case so the invalid fixture fails on missing required notes content, not just a missing section or evidence field. The validator should assert all required note elements explicitly.
- Confidence: 91
- Validation ownership: plan gap

### Medium: Fixture provenance/freshness is mentioned, but not bound to the spec's required origin taxonomy or metadata
- Evidence: TR-007 says fixtures need provenance/freshness metadata but leaves that as generic "fixture family manifests or provenance fields" (`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:61`), and TR-016 only says the validator must avoid network access and live repo mutation (`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:70`). The spec is more specific: every typed artifact fixture family must declare one of the listed origins, and static fixtures must record schema version, source command or source artifact class, and why the static fixture is acceptable (`.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:340-350`).
- Impacted behavior: A stale or hand-authored fixture can still look "provenanced" if it carries any generic metadata, and different slices could invent incompatible provenance formats. That makes the fixture lane ambiguous for future updates and weakens the freshness guarantee.
- Remediation: Encode the exact origin taxonomy (`real_emitter`, `schema_positive`, `schema_negative`, `visual_projection`, `source_artifact`) plus the required freshness metadata in the trace row or a shared fixture contract, and make the invalid case fail when those fields are missing or stale.
- Confidence: 87
- Validation ownership: plan gap

## Residual Risks
- I did not execute the implementation tests, so these findings are about the trace plan's enforceability and handoff clarity, not runtime behavior.
- The plan is otherwise well-bounded on scope, and the remaining risk is mostly in whether the later execution plan turns these trace rows into concrete test fixtures instead of prose.

## Accountability Receipt
- status: complete
- artifact_paths: [/Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-validation-artifacts.md]
- manifest_path: /Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/adversarial-reviewer-20260606T131800Z/manifest.json
- findings: 3
- failures_or_blockers: none
- improvement_opportunities: add an explicit changed-file routing proof, tighten the implementation-notes contract, and bind fixture provenance to the spec's origin taxonomy.
- strengths: the plan already separates local proof from PR/CI truth, covers HTML runtime-vs-visual validation, and keeps network/live-mutation safety in view.
- validation_evidence: reviewed `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`, `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`, and the current validation runner in `scripts/validate_all_impl.sh`.
- next_action: fold these gaps into the execution plan before implementation starts.

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-validation-artifacts.md
