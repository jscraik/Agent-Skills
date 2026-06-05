# PU-010 Traceability Coverage Review

## Findings

### 1. High: Filesystem safety is collapsed into one row, so the plan can miss a destructive edge case and still look complete
- **Evidence:** Spec FR-032 to FR-035 and the filesystem safety contract at `.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:276-289` require separate identity checks for canonicalization or `lstat`, symlink handling, hardlink refusal, case-collision ambiguity, and directory pruning. The plan only has TR-010 at `.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:58`, owned by "Cleanup filesystem guard," with a single validation string, "Path identity validator and directory prune planner."
- **Why it matters:** A generic filesystem-identity implementation can satisfy the row while still skipping one of the spec's destructive cases. That leaves rollback or uninstall able to delete through a symlink, mis-handle hardlinks, or prune a directory that contains user-added data, which is exactly the kind of failure PU-010 is meant to prevent.
- **Remediation:** Split TR-010 into discrete rows for symlink, hardlink, case-collision, and directory-prune behavior, and give each row a dedicated negative test plus a concrete proof output.
- **Confidence:** 96/100
- **Validation ownership:** human / implementation team

### 2. High: Cleanup receipt and journal ownership are too abstract, so the trace plan does not force the actual proof artifacts the spec requires
- **Evidence:** Spec lines 291-304 and 319-347 require a cleanup journal or staged marker with specific recovery semantics and a cleanup receipt schema that carries source receipt identity, target-root identity, lockfile digests, journal path, manual actions, and acceptance trace. The plan only has TR-011 "Cleanup journal module" and TR-012 "Cleanup receipt schemas and receipt writer" at `.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:59-60`, with outputs described as "Journal schema or staged state marker" and "Cleanup receipt schemas and receipt writer" rather than concrete file paths or schema names.
- **Why it matters:** Without naming the actual schema file(s), journal location, and recovery payloads, the implementation can produce a generic helper or a loosely shaped JSON blob that does not prove the spec's receipt or journal contract. That makes later implementation and review ambiguous and weakens traceability for AC-016, AC-027, and AC-030.
- **Remediation:** Add explicit owner surfaces for the journal path and the exact cleanup receipt schema file(s) chosen from the spec options, and add validation outputs that assert the required fields and recovery behavior.
- **Confidence:** 91/100
- **Validation ownership:** human / implementation team

### 3. Medium: Capability-truth and artifact-sync coverage is marked partial without a concrete cross-check, so status changes can drift from the HTML proof surfaces
- **Evidence:** Spec FR-026, FR-027, AC-018, AC-019, and AC-032 require capability truth to move only with executable evidence and keep the capability matrix, status output, and HTML artifacts aligned. In the plan, TR-018 at `.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:66` is only `partial`, and its artifact output says "Updated artifacts or explicit deferral note"; the validation matrix only checks `./bin/ask sdk status --json --robot` and a generic status or artifact test at lines 107-108, without a row that explicitly binds `Infrastructure/config/skills-sdk/capability-matrix.v1.json` to both HTML artifact files in the same proof step.
- **Why it matters:** The plan can land a status-only or artifact-only update and still satisfy the row, which allows the SDK to overstate cleanup readiness or leave the matrix and HTML surfaces contradictory. That undercuts the spec's honest-status requirement and makes PU-010 easy to misreport.
- **Remediation:** Add a dedicated trace row and validation step that compares the capability matrix, robot status output, and both HTML artifacts together, and only advances the status when all three agree.
- **Confidence:** 84/100
- **Validation ownership:** human / implementation team

## Residual Risks
- The plan does cover the broad command surface for rollback and uninstall, so the main risk is not omission of the top-level CLI routes.
- I did not run implementation tests because this pass was limited to traceability review of the plan versus the spec.
- The local-memory CLI probe did not yield usable output, so no durable memory evidence was added for this review.

## Testing Gaps
- No dedicated trace row names the exact journal file path or journal recovery artifact.
- No dedicated trace row names the exact cleanup receipt schema file(s) chosen from the spec's allowed designs.
- No trace row requires a single proof step that synchronizes capability status, capability matrix, and both HTML artifact surfaces.

## Accountability Receipt
- **status:** complete
- **artifact_paths:** ["/Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-trace-adversarial-coverage.md", "/Users/jamiecraik/dev/agent-skills/artifacts/reviews/adversarial-reviewer.md", "/Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/adversarial-reviewer-2026-06-05-pu-010-trace-adversarial-coverage/manifest.json"]
- **findings:** 3 traceability coverage gaps in PU-010 plan versus spec
- **failures_or_blockers:** blocked_local_memory_cli; the local-memory bootstrap/search attempt did not yield usable JSON output for this review
- **improvement_opportunities:** split broad safety rows, name concrete journal and schema artifacts, and add a synchronized capability-truth proof row
- **strengths:** the plan already covers the top-level CLI routes, wrapper parity, and local proof lanes for rollback/uninstall
- **validation_evidence:** `.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md:276-347,349-385`; `.harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md:45-68,93-110`
- **next_action:** update the trace plan before implementation so the row structure matches the spec's safety, journal, and truth-sync contracts
- **manifest_path:** /Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/adversarial-reviewer-2026-06-05-pu-010-trace-adversarial-coverage/manifest.json

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-trace-adversarial-coverage.md

