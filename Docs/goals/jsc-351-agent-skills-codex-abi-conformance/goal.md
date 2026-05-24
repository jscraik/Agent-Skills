# JSC-351 Agent Skills Codex ABI Conformance Goal

## Execution Mode

Mode: GOVERNED_IMPLEMENTATION

Jamie explicitly authorized governed execution for the JSC-351 Codex ABI
conformance plan and specification. This board is the repo-visible control
plane for that execution. The native Codex goal remains the conversational
objective; this board supplies scoped tasks, receipts, validation gates,
review-stack evidence, and stop conditions.

## Kickoff Command

/goal Follow Docs/goals/jsc-351-agent-skills-codex-abi-conformance/goal.md

That command is a prompt convention. It is not a native file binding.

## Objective

Fully implement the JSC-351 Agent Skills Codex ABI Conformance plan and spec
through bounded, independently validated slices that make Agent Skills Kit prove
Codex-native runtime readiness before broader Skills SDK work expands.

The implementation must converge toward deterministic enforcement, lower human
steering cost, stronger runtime truth, stronger architectural coherence,
stronger validation, lower stale-state risk, and safer autonomous operation.

## Canonical Sources

- .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md
- .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
- .harness/research/audits/2026-05-22-evidence-led-codebase-gap-audit.md
- .harness/research/deep/2026-05-22-skills-sdk-oagen-analysis.md

## Target Repository

<REPO_ROOT>

## Implementation Notes

.harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html

The notes file is a runtime reasoning ledger, architecture decision journal,
implementation delta tracker, operational-risk log, and future-agent handoff
artifact. It must be updated during execution, not only at closeout.

## Completion Contract

Outcome:

- The plan and spec are fully implemented through operationally complete,
  independently validated slices.
- ask can prove Codex ABI conformance at the intended runtime boundary without
  confusing .agents readiness, generated projections, advisory warnings, or
  documentation-only claims with Codex-native truth.
- The final state has no unresolved blockers, no unapproved unfinished
  placeholders, no silent stale-state contradictions, and no deferred critical
  correctness work.

Verification surface:

- Goal board validator.
- Plan/spec artifact identity, traceability, BLUF, and generated-shape
  validators.
- Slice-specific focused tests and command smoke checks.
- Mandatory review-stack findings normalized as blocker, high, medium, low, or
  informational.
- Implementation notes with validation evidence and runtime discoveries.
- Linear issue state, PR state, CI state, CodeRabbit/Codex review state, and
  mergeability once a PR exists.
- Final Judge or PM completion receipt.

Constraints:

- No partial slices, speculative refactors, placeholder scaffolds, or unapproved
  future-work handoffs.
- Every slice must be operationally complete, independently validated, and leave
  the repository buildable.
- Trust runtime truth over docs, specs, plans, review assumptions, or summaries.
- Do not edit generated runtime projections, plugin caches, user/global runtime
  config, or unrelated repos.
- Do not proceed past unresolved blockers, stale validation, unclear blast
  radius, merge-safety ambiguity, or deterministic verification failure.

Boundaries:

- Canonical implementation surfaces are Infrastructure/bin/ask,
  Infrastructure/scripts/lib/ask/**, Infrastructure/config/schemas/**, and
  focused tests under Infrastructure/tests/\*\*.
- Planning, governance, and evidence surfaces are .harness/\*\*, this goal board,
  and implementation notes.
- Runtime projections such as .agents/**, .skillsets/**, Plugins/cache/**, and
  runtime/** are not implementation targets for this goal unless a later
  reviewed slice proves the canonical source requires projection regeneration.
- External writes to Linear, GitHub, CircleCI, or CodeRabbit require the relevant
  lane evidence and must preserve runtime truth.

Target Skills SDK layout:

- The goal must converge toward a Python-native Skills SDK service package under
  Infrastructure/scripts/lib/ask/skills_sdk/\*\* or the closest existing ask
  package boundary approved by the governor.
- Expected service areas are contracts, catalog, validation, packaging,
  runtime_adapters/codex, runtime_adapters/agents, evidence, and governance.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py must become a thin CLI
  facade by JSC-355 acceptance: parse arguments, call service modules, format
  command output, and return exit status.
- This is not a repo-wide codex-rs-style workspace migration. The Python-native
  equivalent is modular package boundaries plus import-boundary tests.
- JSC-355 may not close if SDK/domain behavior touched by JSC-352 through
  JSC-354 remains concentrated in commands/skills_impl.py without a governor
  disposition and validation-backed reason.
- Import-boundary validation must prove ask.skills_sdk does not depend on
  ask.commands, and runtime adapters do not depend on command presentation code.

Iteration policy:

- Govern one bounded slice at a time.
- Declare allowed files, verification commands, and stop conditions before any
  Worker implementation.
- Implement only inside the active slice boundary.
- Validate locally before review-stack synthesis.
- Run architecture, simplification, unused-code, language, testing, docs, and
  code review checks before progression.
- Hand off to git triage only after a validated slice reaches a safe state.
- Continue only after the governor confirms no blocker, stale-state, or
  merge-safety contradiction remains.

Blocked stop condition:

- Stop immediately on unverifiable runtime safety, unclear merge safety,
  increased architecture drift, stale validation, deterministic verification
  failure, unresolved blockers, unclear blast radius, ambiguous governance,
  repeated retry-without-progress, review churn, or user steering that changes
  the objective.

## Four Lanes

1. Governor lane: owns sequencing, blast-radius control, runtime safety,
   convergence, escalation, stopping conditions, implementation priority, and
   architectural coherence.
2. Implementation lane: implements only the active slice within declared
   allowed files and validation boundaries.
3. Review/validation lane: runs deterministic checks and the mandatory review
   stack, then normalizes findings.
4. Merge/remediation lane: tracks PR, CI, review, branch, Linear, and merge
   safety after a validated slice has a delivery branch or PR surface.

## Mandatory Slice Lifecycle

Every slice follows this lifecycle exactly:

1. GOVERN
2. IMPLEMENT
3. VALIDATE
4. ARCHITECTURE REVIEW
5. SIMPLIFY
6. UNSLOPIFY
7. UBIQUITOUS LANGUAGE REVIEW
8. TEST
9. DOCS UPDATE
10. CODE REVIEW
11. IMPLEMENTATION NOTES UPDATE
12. GIT TRIAGE HANDOFF
13. CONTINUE ONLY AFTER SAFE STATE CONFIRMED

If a step cannot run, record blocked with evidence and stop progression until
the governor resolves the blocker.

## Mandatory Review Stack

- $improve-codebase-architecture
- $simplify
- $unslopify
- $ubiquitous-language
- $testing
- $docs-expert

Findings are normalized into blocker, high, medium, low, and informational. The
governor disposition is fix_immediately, defer_safely, reject, or escalate. No
unresolved blocker may proceed.

## Continuous Git Triage Lane

After every validated slice, the merge/remediation lane tracks:

- GitHub PR lifecycle, mergeability, branch drift, stale state, merge conflicts,
  and review status.
- CircleCI validation freshness, failure classification, retry loops, and flaky
  failure evidence.
- CodeRabbit/Codex review comments, classified as valid, stale, hallucinated,
  already_resolved, architectural_disagreement, or low_signal_noise.
- Linear issue progress, blockers, implementation state, review state,
  unresolved risks, and operational traceability.

If no PR or CI surface exists yet, record that state as
not_applicable_pre_delivery_surface rather than pretending the triage lane is
green.

## First Governed Slice

Slice: PU-001 / JSC-352 runtime-targeted proof and doctor Codex parity entry

Operational objective:

- Implement runtime-targeted proof and ask skills doctor --codex-parity behavior
  so .agents readiness cannot satisfy Codex-targeted conformance.

Initial allowed implementation files:

- Infrastructure/bin/ask
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/fixtures/\*\*
- .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html
- Docs/goals/jsc-351-agent-skills-codex-abi-conformance/\*\*

Initial verification:

- python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-351-agent-skills-codex-abi-conformance
- python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
- python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
- python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md --json
- python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md --kind plan --json
- python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md --kind spec --json
- Focused PU-001 tests added or updated during implementation.

Stop if:

- The plan/spec validators fail.
- Runtime parser or doctor behavior has drifted enough to invalidate PU-001.
- --runtime-target codex cannot be made to fail closed without a broader service
  extraction.
- Codex parity would require editing generated projections or plugin caches.
- Live Linear, PR, CI, or review truth contradicts the slice state.

## Definition Of Done

The goal is complete only when a final Judge or PM receipt records
decision=complete and confirms:

- Implementation is operational.
- Validation passes.
- Review stack passes or all non-blocking findings have governor disposition.
- Documentation and implementation notes are updated.
- CI is green for the delivery surface.
- Review blockers are resolved.
- Runtime truth is verified.
- PR state is healthy and mergeability is confirmed where applicable.
- Linear state matches actual implementation state.
- No stale-state contradictions remain.
