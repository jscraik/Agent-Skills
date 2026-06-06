# PU-011 Trace Plan Adversarial Review: Validation and Artifact Gaps, Pass 2

## Findings

### Medium: The plan leaves fixture provenance storage undecided, so different slices can encode incompatible validation metadata
- Evidence: The patched plan now correctly names the required provenance taxonomy in TR-007 and requires freshness metadata for accepted fixture origins (\`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:65\`). It also says static fixtures must carry schema version, source command or source artifact class, and rationale (\`.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:342-350\`). But the same plan still defers the actual provenance format decision to the pre-work gap list, allowing provenance to be embedded, split into adjacent manifest files, or inferred from directory convention plus test metadata (\`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:177-188\`).
- Impacted behavior: If one execution slice embeds provenance inside fixtures while another uses sidecar manifests or convention-based inference, the validator has to support multiple incompatible representations. That makes freshness checks brittle, weakens fixture provenance as an artifact contract, and lets stale fixtures look valid under one representation but not another.
- Remediation: Pick one canonical provenance storage model in the trace plan itself, then make the alternative representations explicit non-goals. If sidecar manifests are required, say so and name the exact fields that must be present; if embedded metadata is required, say so and forbid inference-only provenance.
- Confidence: 89
- Validation ownership: plan gap

## Residual Risks
- I did not run the implementation validation commands; this review only checks whether the trace plan is sufficiently actionable and artifact-safe.
- The earlier findings about changed-file routing proof, implementation-notes fixture strength, and fixture provenance taxonomy are mostly closed by TR-021, TR-009, and TR-007 respectively, but the provenance storage format is still left open.

## Accountability Receipt
- status: complete
- artifact_paths: [/Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-validation-artifacts-pass2.md]
- manifest_path: /Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/adversarial-reviewer-20260606T132732Z/manifest.json
- findings: 1
- failures_or_blockers: none
- improvement_opportunities: lock the provenance storage format, then carry that decision into the implementation-plan slice and fixture generator tests.
- strengths: the patch closes the prior changed-file-routing, implementation-notes, and provenance-taxonomy gaps on paper, and it keeps no-network/no-live-mutation boundaries explicit.
- validation_evidence: reviewed \`.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md\`, \`.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md\`, the prior review artifact, and \`Infrastructure/scripts/validate_all_impl.sh\`.
- next_action: freeze the provenance format before the implementation slice starts so fixture metadata cannot fork across families.

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-validation-artifacts-pass2.md
