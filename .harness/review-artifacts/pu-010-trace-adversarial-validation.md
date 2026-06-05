# PU-010 Trace Adversarial Review: Validation Proof

Artifact reconstructed by coordinator from completed adversarial-reviewer JSON response because the agent returned structured content instead of writing the requested file.

## Findings

### HIGH: One generic negative cleanup bucket can skip a required refusal case and still look complete

Why it matters: The trace plan can be marked covered while silently omitting one of the high-risk refusal paths that makes rollback and uninstall safe. That leaves room for a destructive cleanup bug to survive because the exact failing command was never forced to run.

Evidence:
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:104
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:402

Remediation: Replace the bucket with one row per refusal scenario, each with an exact command, expected envelope, and proof artifact. Keep the commands split by rollback versus uninstall so a missing case cannot hide inside a generic negative suite.
Confidence: 98

### HIGH: Wrapper and status parity are only exercised through ask-side preview paths, so bin/skills-sdk can diverge without being caught

Why it matters: The public wrapper can parse flags, format JSON, or label metadata differently from ask and still pass the current trace plan. That leaves the scripted surface inconsistent exactly where cleanup automation will depend on parity most.

Evidence:
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:102-103
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:108
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:391
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:383-384

Remediation: Add mirrored bin/skills-sdk commands for status, rollback apply, uninstall apply, and at least one blocked apply case. Assert identical JSON payloads and command metadata aside from wrapper identity fields.
Confidence: 92

### HIGH: Journal recovery is named, but the plan never recreates the interrupted state it is supposed to recover from

Why it matters: A test can prove that a journal file exists and still never prove that a subsequent cleanup command detects it, resumes safely, or blocks with recovery instructions. That leaves the half-mutated tree scenario unexercised.

Evidence:
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:59
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:105-107
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:379
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:315

Remediation: Add an explicit two-step repro: start apply, interrupt after the journal is written and before completion, then rerun the same cleanup command and assert the journal-aware resume or blocked recovery behavior.
Confidence: 90

### MEDIUM: Artifact truth is still a manual sidecar, so capability labels can drift without an executable proof step

Why it matters: A reviewer can update the matrix or status command while the HTML artifacts lag behind, or vice versa. That creates a local truth split where capability labels and rendered proof no longer say the same thing.

Evidence:
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:66
- .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:107
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:394
- .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:383-384

Remediation: Add deterministic artifact-update commands or checksum and diff assertions for both HTML files, and make the pass condition depend on those commands instead of a manual review note.
Confidence: 70

## Residual Risks

- PU-009 compatibility is at least called out with a dedicated install regression command at line 106, but the plan still does not isolate shared-helper regressions if cleanup work changes install internals.
- The trace plan is stronger on project-root scoping and receipt provenance than on end-to-end proof execution; the remaining risk is proof completeness, not scope creep.

## Testing Gaps

- No explicit two-step journal interruption-and-retry command sequence appears in the trace plan.
- No explicit ./bin/skills-sdk status --json --robot command appears in the trace plan.
- The negative-path matrix is bucketed rather than enumerated, so missing refusal cases can hide.

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-trace-adversarial-validation.md

