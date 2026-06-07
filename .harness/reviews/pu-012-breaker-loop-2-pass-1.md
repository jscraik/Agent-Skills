# PU-012 Breaker Loop 2, Pass 1 Review

## Findings

### 1. High: Cleanup readiness can still be overclaimed for invalid or stale receipts
**Evidence**
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:217-228` defines `install_status` values including `invalid_receipt`, `stale_receipt`, and `unknown`.
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:249-251` only forces false readiness for missing receipt proof, digest mismatch, and "unknown proof", but it never says `rollback_ready`/`uninstall_ready` must be false for `invalid_receipt` or `stale_receipt`.
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:357-365` enumerates missing receipt, receipt mismatch, missing file, and modified file cases, but again leaves invalid/stale receipt rows without an explicit readiness rule.

**Why it matters**
A project can carry a syntactically valid but semantically stale or invalid receipt and still be reported as rollback/uninstall ready if the implementation chooses the permissive path. That lets the adoption gate claim lifecycle proof that the cleanup commands do not actually have.

**Concrete fix**
Add an exhaustive readiness matrix that pins `rollback_ready` and `uninstall_ready` to `false` for every non-healthy receipt state, including `invalid_receipt`, `stale_receipt`, and `unknown`, and require blocker codes for each row.

### 2. Medium: Doctor is not validated on the unsafe and drift cases it claims to cover
**Evidence**
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:382-387` validates healthy status, missing-root refusal, and no-discovery behavior, but the doctor command only appears in the healthy and missing-root rows.
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:420-423` exercises broad-root refusal, moved-identity drift, and other high-risk conformance cases only with `project status`, not with `project doctor`.
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:141-141` and `234-236` promise schema-visible status/doctor differences, but the test matrix does not force those differences on failure-path fixtures.

**Why it matters**
A weaker `doctor` implementation can silently degrade into a `status` clone, or even accept a broad root, and still satisfy the current validation plan. That leaves the more diagnostic surface under-specified exactly where users need the extra evidence.

**Concrete fix**
Add doctor-specific acceptance and validation rows for broad roots, moved identity drift, unsupported/stale lockfiles, missing or mismatched receipts, and modified/missing files. The same no-read and no-mutation expectations should be asserted for `doctor` as for `status`.

### 3. Medium: Failure-state taxonomy is still ambiguous, so robot semantics can diverge
**Evidence**
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:197-198` allows `conformance_status` values `pass`, `warn`, `fail`, or `blocked`.
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:246-248` and `350-365` repeatedly permit `fail` or `blocked` for the same drift classes without pinning one deterministic outcome.
- `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:261-262` requires machine-readable evidence, but not machine-readable status semantics.

**Why it matters**
Two implementations can both comply with the current text while returning different robot states and exit behavior for the same project. That makes downstream automation brittle because it cannot reliably tell environmental refusal from project-state failure.

**Concrete fix**
Add a deterministic mapping table from each refusal/drift class to exactly one `conformance_status` and one exit-code family, and reserve `blocked` for a narrowly defined subset if that is the intended operator contract.

## Accountability Receipt
status: completed
artifact_paths:
- /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-2-pass-1.md
manifest_path: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/artifacts/agent-runs/adversarial-reviewer-2026-06-06T17-11-47-644Z/manifest.json
findings:
- high: cleanup readiness can be overclaimed for invalid or stale receipts
- medium: doctor is not validated on the unsafe and drift cases it claims to cover
- medium: failure-state taxonomy is still ambiguous, so robot semantics can diverge
failures_or_blockers: none
improvement_opportunities:
- pin a complete readiness matrix for all receipt states
- add doctor parity tests on failure fixtures, not just healthy and missing-root cases
- stabilize conformance status / exit-code mapping for drift and refusal classes
strengths:
- prior gaps around omitted-root no-discovery, mise launch env, broad-root identity, empty-project semantics, and capability-row visibility are all explicitly addressed in the spec text
- the spec already anticipates machine-readable schema, router, and validation-scope coverage
validation_evidence:
- review performed against the current spec text at the lines cited above
- no source files were modified
next_action:
- if the spec is revised, re-run the breaker pass against the new artifact and re-check the failure fixtures for doctor parity and readiness false positives

WROTE: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-loop-2-pass-1.md
