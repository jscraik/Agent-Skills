# PU-010 Trace Adversarial Review: Implementation Slicing

Artifact reconstructed by coordinator from completed adversarial-reviewer JSON response because the agent returned structured content instead of writing the requested file.

## Findings

### HIGH: Filesystem mutation is scheduled before the journal exists, so interrupted cleanup cannot recover from the first apply path

Why it matters: This makes the first destructive cleanup slice impossible to prove safe: happy-path cleanup can pass while crash/retry semantics remain undefined and unrecoverable.

Evidence:
- The plan places "Filesystem safety executor" in S3 and "Journal and partial recovery" in S4: /Users/jamiecraik/dev/agent-skills/.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:88-89.
- The spec requires apply mode to create a cleanup journal or staged marker before the first filesystem mutation and to detect unresolved journals on the next cleanup attempt: /Users/jamiecraik/dev/agent-skills/.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:293-305.
- If S3 is implemented literally, a crash or timeout after the first delete/restore but before S4 leaves a half-mutated tree with no journal evidence to resume or block from.

Remediation: Move journal design and staged-state creation ahead of any filesystem mutation work, or split the apply path so no destructive action can occur until journaling is in place.
Confidence: 97

### HIGH: Implementation starts before the spec's unresolved design decisions are frozen, so later slices can hard-code the wrong authority model

Why it matters: A provisional schema or authority rule can get baked into preview and lockfile code before the real contract is decided, forcing rework or inconsistent behavior when the true shape lands.

Evidence:
- S1 and S2 begin with preview, receipt, and lockfile work: /Users/jamiecraik/dev/agent-skills/.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:86-87.
- The spec still marks several required decisions as blocked inputs: separate vs discriminated cleanup schemas, before-state support for overwritten files, the exact receipt identity field, duplicate-install policy, and cleanup journal location: /Users/jamiecraik/dev/agent-skills/.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:437-444.
- Those decisions directly affect the receipt authority model, duplicate-instance handling, and recovery layout that the later cleanup slices depend on.

Remediation: Insert a prerequisite decision-gate slice before S1 that freezes schema shape, receipt identity binding, before-state policy, duplicate-install policy, and journal location before implementation slices proceed.
Confidence: 93

### MEDIUM: The status/artifact slice can overclaim cleanup readiness before the full refusal and recovery matrix is proven

Why it matters: This creates a local truth-plane mismatch where the repo can claim implemented or partial cleanup status before the high-risk refusal and recovery obligations are actually satisfied.

Evidence:
- S5 bundles CLI parity, status, artifacts, and regression proof, with the stop condition "Tests, status, wrappers, and artifacts agree without overclaiming": /Users/jamiecraik/dev/agent-skills/.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:90.
- The validation matrix for that slice only checks status output, wrapper parity, and the artifact tests: /Users/jamiecraik/dev/agent-skills/.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:107-108.
- The spec says parser-only routes, status-only matrix edits, or receipt schema changes alone must not move rollback/uninstall above deferred or preview, and implemented status requires preview, apply, refusal, modified-file preservation, lockfile update, wrapper parity, journal recovery, artifact truth, and status truth: /Users/jamiecraik/dev/agent-skills/.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:306-317.
- If S5 is reached while the negative matrix or journal recovery is still incomplete, the capability matrix and HTML artifacts can drift ahead of the actual cleanup contract.

Remediation: Gate S5 on an explicit proof checklist that includes the full refusal and recovery matrix, not just wrapper and status parity, and freeze capability labels until that checklist is complete.
Confidence: 82

## Residual Risks

- I only reviewed the plan/spec pair; I did not inspect the implementation or run runtime cleanup scenarios.
- The plan may have external notes or coordinator context that narrow these slices further, but that context was not present in the reviewed files.

## Testing Gaps

- No temp-project execution trace was available to prove the journal-before-mutation contract.
- No proof was available that receipt identity, duplicate-install policy, and journal location were resolved before implementation sequencing.
- No evidence showed the capability-status/artifact slice being gated on the full refusal and recovery matrix.

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-trace-adversarial-slicing.md

