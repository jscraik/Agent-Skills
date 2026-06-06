# PU-011 Adversarial Review: Artifact Validation
## Findings
### High: The spec names a skills-sdk validation lane that the repo does not currently recognize
- Evidence: spec Acceptance Criteria and Validation Plan at lines 141-142 and 309-310, plus the current scope table in scripts/validate_all_impl.sh at lines 14-16 and scope dispatch at lines 97-105.
- Problem: the spec tells implementation to use ./bin/ask repo validate --scope=skills-sdk, but the current validation runner only accepts all, lint, typecheck, test, audit, check, consistency-advisory, and consistency-health. As written, the named gate is invalid today unless the implementation also changes the repo validation contract.
- Impact: the focused typed-artifact lane is either un-runnable or forced to pick an undocumented fallback, which makes the spec hard to execute and easy to misread during closeout.
- Recommended fix: choose one existing scope name and make it the contract, or explicitly add skills-sdk to the validation runner and update the scope table, acceptance criteria, and validation plan together.
- Confidence: 96
- Validation ownership: spec gap

### High: Implementation-notes validation is in scope, but nothing in the acceptance criteria proves it
- Evidence: approved scope at lines 50-55, FR-015 at line 135, Markdown contract boundaries at lines 209-218, and the acceptance criteria at lines 267-283.
- Problem: the spec explicitly says implementation notes are part of the contract surface, but there is no positive or negative acceptance case for .harness/implementation-notes/*skills-sdk*.mdx or .html, and no validation command that proves the parser works on that family.
- Impact: an implementation can ship with broken or stale implementation-note parsing while still satisfying every listed acceptance case, leaving one of the declared artifact families effectively unprotected.
- Recommended fix: add at least one valid and one invalid implementation-notes fixture, then wire a dedicated acceptance case or validation command for that family.
- Confidence: 92
- Validation ownership: spec gap

### Medium: The HTML truth rule is incomplete for the status classes that already exist in runtime output
- Evidence: current runtime status distribution in Current Evidence lines 71-81, HTML contract rules at lines 137-140, and HTML contract details at lines 222-240.
- Problem: the spec says runtime status is authoritative, but it never defines the exact allow/deny mapping for preview-only, deferred, optional-placeholder, blocked-adapter, or out-of-scope rows, and it never says how to treat a runtime row that is missing from one HTML artifact but present in the other.
- Impact: the validator can become brittle in either direction: it may falsely fail on intentionally non-implemented rows, or it may falsely pass if it ignores rows that should have been rendered and compared.
- Recommended fix: add an explicit status matrix and missing-row policy for each runtime class, including what counts as a tolerated omission versus a real drift.
- Confidence: 88
- Validation ownership: spec gap

### Medium: The package-manager boundary is described, but not structurally enforced
- Evidence: out-of-scope package-manager language at lines 61-67, the package-boundary requirement at line 144, the AC-015 boundary claim at line 283, and the validation plan at lines 289-312.
- Problem: the spec says the root remains wrapper-only and that validation commands should use uv run --project Infrastructure, but it never requires a negative filesystem assertion that root package manifests or lockfiles stay absent, nor does it pin a command that would fail if the root package-manager boundary regressed.
- Impact: a future change could reintroduce root package-manager state while the current validation flow still looks green, which weakens the boundary the spec is trying to preserve.
- Recommended fix: add an explicit absence check for root package metadata and make it part of the validation receipt, not just the prose.
- Confidence: 84
- Validation ownership: spec gap

### Medium: Fixture strategy can go stale and hide drift between local truth and PR/CI truth
- Evidence: fixture allowance at lines 54 and 96, JSON/YAML/Markdown/HTML contract coverage at line 130, helper flexibility at line 207, local-vs-PR/CI limits at lines 317-320, and the handoff note to update artifacts only when drift is proven at line 368.
- Problem: the spec allows both real and fixture inputs, but it never requires a freshness stamp, provenance note, or regeneration rule that ties fixtures back to the current emitters. That makes it possible for stale snapshots to keep tests green long after command output or visual truth has changed.
- Impact: local validation can quietly drift away from the actual runtime and visual artifacts, and the spec's boundary between local evidence and PR/CI evidence stays prose-only instead of being encoded in the artifact contract.
- Recommended fix: require either real-emitter goldens or a documented freshness/provenance field for each fixture family, and make the validation receipt say which lanes were checked locally versus left to PR/CI.
- Confidence: 86
- Validation ownership: spec gap

## Residual Risks
- The spec is already better bounded than a broad refactor would be, so the remaining risk is mostly in how aggressively the typed validators are wired into existing scopes.
- I did not run implementation tests; this review only checked the spec against current repo wiring and the repository's validation contract.

## Verdict
changes_requested

## Accountability Receipt
- status: complete
- artifact_paths: [.harness/review-artifacts/pu-011-adversarial-artifact-validation.md]
- manifest_path: artifacts/agent-runs/adversarial-reviewer-20260606T130437Z/manifest.json
- findings: 5
- failures_or_blockers: none
- improvement_opportunities: define the validation scope contract precisely, add implementation-notes fixtures, pin HTML status-class handling, and turn the package-manager boundary plus fixture freshness into explicit checks.
- strengths: the spec already keeps runtime truth above visual truth, keeps mutation authority bounded, and makes the package-manager boundary visible in prose.
- validation_evidence: reviewed the spec at .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md, the current validation scope contract in scripts/validate_all_impl.sh, and the repo validation guidance in Docs/agents/04-validation.md.
- next_action: feed the spec back into planning with a tighter validation-scope contract and explicit coverage for implementation notes, fixture freshness, and status-class mapping.

WROTE: .harness/review-artifacts/pu-011-adversarial-artifact-validation.md
