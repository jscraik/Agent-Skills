# JSC-391 Plan Review Synthesis

STATUS: findings

## Subagent Runtime Coverage

Requested reviewers:

- agent-native-reviewer: invoked; completion notification received; required artifact was not written.
- adversarial-reviewer: invoked; completion notification received; required artifact was not written.
- api-contract-reviewer: invoked; completion notification received; required artifact was not written.
- architecture-strategist: invoked; completion notification received; required artifact was not written.

Artifact verification failed for all requested reviewer lanes. The first three lanes were retried with JSC-391-specific artifact paths and still produced no artifact. Because the repo swarm contract treats mailbox status as insufficient completion evidence, the role-specific review artifacts are coverage gaps rather than verified reviewer outputs.

Validation ownership: environment/tooling failure for subagent artifact persistence; not introduced by the JSC-391 plan content.

## Findings

### P1: Feature-planning gate can still be satisfied by non-durable evidence

Evidence:

- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:368 allows planning-gate proof via an he-plan dry-run/refusal artifact, repo-local routing check, or Linear dependency/status evidence.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:425 says feature implementation planning is forbidden until PU-006 proves no parent V1 crosswalk row remains blocked_parent_acceptance.

Why it matters: The plan correctly names the gate, but one accepted proof option is still an artifact or tracker-state claim rather than an executable repo-local guard. That can let future feature planning proceed after a one-off refusal artifact without a durable mechanism that agents or validation can re-run.

Remediation: Require a repo-local executable gate as mandatory evidence, such as a routing validator, plan validator rule, or focused test that fails when feature planning artifacts reference parent SA-024 through SA-029 while any JSC-391 crosswalk row remains blocked_parent_acceptance. Linear dependency/status evidence and dry-run refusal artifacts should be supplemental only.

Validation ownership: introduced by current plan.

### P1: Compatibility receipts omit Python SDK import/public-contract baselines

Evidence:

- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:237 defines the baseline compatibility matrix using repo status, repo doctor, skills list, skills explain, skills prove, and repo closeout.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:365 requires the same matrix for post-change receipts.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:117 identifies existing SDK modules under Infrastructure/scripts/lib/ask/skills_sdk/, but the receipt matrix does not include importability or public symbol checks for those modules.

Why it matters: JSC-391 is explicitly about SDK scaffold and module boundaries. CLI compatibility alone can pass while Python callers, tests, or future agents lose stable imports from contracts.py, package_contracts.py, package_verify.py, runtime_adapters.py, or conformance.py.

Remediation: Add a baseline/post-change Python SDK import contract receipt, for example importing every existing skills_sdk module, checking selected public symbols or __all__ where present, and classifying any changed import surface as preserved, wrapped, intentionally moved with compatibility shim, or blocked.

Validation ownership: introduced by current plan.

### P2: Agent-native module routing is not required to be machine-readable

Evidence:

- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:257 requires the ADR to select physical paths for logical landing zones.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:284 requires module boundary documentation for deep modules.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:338 through .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:343 require tests for scaffold structure, routing, dependency direction, path ownership, feature leakage, and discoverability.

Why it matters: The plan is agent-first in intent, but it permits the core module map to live only in prose ADR/docs. Future agents need a stable parseable ownership map to route work reliably and for tests to assert against without scraping narrative Markdown.

Remediation: Add a required parseable module routing artifact, such as JSON/YAML/TOML or a strictly table-shaped Markdown contract with stable columns for module, owns, collaborators, public_contract, forbidden_ownership, source_paths, and status. Make PU-005 tests consume that artifact rather than duplicating routing expectations in test code.

Validation ownership: introduced by current plan.

### P2: Fixture and placeholder validation is deferred too late

Evidence:

- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:315 adds parseable schema or Markdown placeholders in PU-004.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:318 defers focused fixture/parser tests to PU-005.
- .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md:324 says PU-004 can hand off after PU-003.

Why it matters: PU-004 can complete after adding placeholders that are not yet parsed or validated. That creates a temporary state where malformed or ambiguous placeholders become dependencies for PU-005, increasing repair cost and weakening the handoff boundary.

Remediation: Require PU-004 to run at least lightweight parser/schema checks for every placeholder it creates before handoff, while keeping the broader routing/dependency tests in PU-005.

Validation ownership: introduced by current plan.

## Coordinator Notes

No source implementation was reviewed because this request targeted the plan artifact only. No plan edits were made by this synthesis.

WROTE: artifacts/reviews/jsc391-plan-review-synthesis.md
