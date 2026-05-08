---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-08
origin: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
reviewed_artifact: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
traceability_required: true
linear_status: existing
linear_issue: JSC-246
linear_issue_url: https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Build repo surface contract and agent capability control-plane golden paths"
review_result: approved_with_residual_risks
---

# Agent Skills JSC-246 Agent First Golden Path Technical Review

## Review Verdict

Approved for `he-plan` handoff after remediation.

The spec is now strong enough to plan from. It defines the right execution
slice for `JSC-246`: harden the existing agent-first command loop without
pulling in neighboring proof-schema, command-handle, cleanup, or onboarding
tracks. The review found real loopholes in the first draft, but they have been
closed in the current spec.

No remaining blocking review finding is open against the spec artifact.

## Linear Work Item Contract

`linear_status: existing`

This review covers the existing Linear work item:

- Linear issue: `JSC-246`
- Linear team: `JSC`
- Linear workspace: `Jscraik`
- Linear project: `agent-skills`
- Linear milestone: `Command surface and ask reliability`
- Parent issue title: `Build repo surface contract and agent capability
  control-plane golden paths`

The review does not create or approve new Linear work. It only determines
whether the `JSC-246` spec is safe to pass to `he-plan`.

## Scope Reviewed

Reviewed artifact:

- `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`

Source context:

- `.harness/linear/agent-skills-linear-plan.md`
- `.harness/refactors/agent-first-golden-path.md`
- `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`

Live command probes:

- `./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot`
- `./bin/ask skills prove he-spec --json --robot`
- `./bin/ask repo closeout --changed --json --robot`

## Findings

No open blocking findings remain after the remediation pass.

### Remediated Finding 1: Proof Scope Could Swallow Neighboring Work

Severity: High  
Status: Fixed in spec

The earlier spec required proof-level behavior strongly enough that an
implementer could reasonably introduce new `skills prove` schema, promotion
states, or lifecycle gates. That would invade `JSC-230` / `JSC-234` style proof
and handle work, despite the slice claiming those tracks were out of scope.

Evidence:

- The spec now contains an explicit boundary clause in the proof-level
  contract: `JSC-246` may map existing `skills prove` output to proof taxonomy
  semantics, but must not introduce a new proof schema, promotion gate,
  command-handle proof artifact, or trusted/default-visible lifecycle state in
  this slice.
- Acceptance criterion `SA10` now requires proof taxonomy assertions against
  existing output and a plan scope check for no proof schema expansion.
- Acceptance criterion `SA16` keeps `JSC-230`, `JSC-167`, and `JSC-169`
  outside this slice unless a later delta gate admits them.

Why it matters:

Without this boundary, `he-plan` could turn a golden-path execution slice into a
cross-cutting schema migration. That would increase blast radius, make the
Linear slice hard to close, and weaken the repo's core discipline of bounded
HE phases.

### Remediated Finding 2: Diagnostic Debt Could Trap Agents In A Loop

Severity: High  
Status: Fixed in spec

The earlier spec made `repo surface` and diagnostic debt important, but did not
define when non-blocking diagnostic debt must stop steering the agent. In the
current repo, this matters because live closeout evidence shows non-blocking
surface debt can be large and persistent.

Evidence:

- The spec now includes a diagnostic debt continuation rule in the deterministic
  next-action contract.
- Acceptance criterion `SA6` requires a fresh-agent eval proving that
  non-blocking diagnostic debt does not create an endless loop and that the
  agent can continue into route, explain, prove, or closeout after
  acknowledging/capturing surfaced debt.
- Linear traceability maps `SA3` through `SA6` to repo truth, deterministic
  next-action ordering, repo surface, and continuation after diagnostic debt.

Why it matters:

If every diagnostic warning becomes the next blocking action, the command
surface stops being a golden path and becomes a diagnostic treadmill. The
correct behavior is blocking gates first, then advisory debt capture, then
task-continuation when the user's active goal can proceed.

### Remediated Finding 3: Routing Fixtures Could Encode Stale Handles

Severity: Medium  
Status: Fixed in spec

The earlier spec expected representative skill routing behavior but did not
protect the implementation from brittle exact-handle assertions. In this repo,
capability handles and runtime projections are generated surfaces and can drift
relative to canonical sources.

Evidence:

- The spec now includes a fixture stability rule requiring each exact expected
  handle to be resolved through `./bin/ask skills resolve <handle> --json
  --robot` or an equivalent registry snapshot.
- Acceptance criterion `SA8` requires route-family expectations to be separated
  from exact-handle expectations.
- The review probe successfully resolved `he-spec` and `he-code-review` through
  `./bin/ask skills resolve ... --json`, grounding the review in live registry
  behavior rather than assumed path names.

Why it matters:

Golden-path tests should fail when routing semantics regress, not when a handle
rename or projection refresh changes a generated surface. The spec now forces
the plan to separate those failure classes.

### Remediated Finding 4: Documentation Compression Could Become A Proxy Metric

Severity: Medium  
Status: Fixed in spec

The earlier spec required subtractive first-contact documentation, but the
metric could be gamed by deleting prose without improving agent behavior.

Evidence:

- Acceptance criterion `SA13` now pairs docs subtraction with fresh-agent
  behavior metrics.
- The spec names usable behavior metrics: commands required to reach
  ready-or-blocked, docs opened for basic navigation, misroute/ambiguity count,
  and whether the agent followed command-emitted next commands without manual
  repo browsing.
- Acceptance criterion `SA15` requires a fresh-agent eval that starts from
  `repo doctor`, follows command output, and reaches ready-or-blocked without
  reading docs for basic navigation.

Why it matters:

The project is trying to improve agent cognition, not win a prose-length
contest. Compression only helps if it reduces ambiguity and execution steps.

## Residual Risks

### Residual Risk 1: Live Closeout Is Not A Clean Fixture

Current live `./bin/ask repo closeout --changed --json --robot` reports
`sync_required` because unrelated canonical skill files and generated
`.skillsets/**` projections are already dirty in the worktree.

This is not a blocker for the spec, but it is a planning constraint. `he-plan`
must use controlled fixtures or isolate a clean validation branch when proving
blocked and clean closeout states. The plan must not treat the current dirty
worktree as the only source of truth for closeout behavior.

### Residual Risk 2: Fallback Routing Is Still A Known Behavior Gap

The live `skills improve` probe for `make agents better at fixing PR review
comments` returns `resolved_with_fallback` with unresolved goal decision state.
That is useful evidence, but it is not proof-grade routing.

The spec correctly treats this as work to plan and validate. It is not already
fixed by the spec.

### Residual Risk 3: Diagnostic Debt Volume Can Obscure Readiness

The repo has substantial non-blocking diagnostic debt. The spec now requires
non-loop continuation behavior, but the implementation phase must still define
how diagnostic debt is represented so agents can distinguish:

- blocking gates
- advisory debt
- freshness of diagnostic debt
- task-continuation commands

This is a design point for `he-plan`, not a reason to expand `JSC-246`.

## Validation Evidence

| Command | Result | Notes |
| --- | --- | --- |
| `./bin/ask skills resolve he-spec --json` | pass | Resolved to `Plugins/harness-engineering/skills/he-spec/SKILL.md`; source revision reported as `cec4b3a59`. |
| `./bin/ask skills resolve he-code-review --json` | pass | Resolved to `Plugins/harness-engineering/skills/he-code-review/SKILL.md`; source revision reported as `cec4b3a59`. |
| `./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot` | pass | Returned `resolved_with_fallback`; exposed routing ambiguity that the spec now covers. |
| `./bin/ask skills prove he-spec --json --robot` | pass | Returned `reachable_without_outcome_proof`; supports the spec's proof-boundary language. |
| `./bin/ask repo closeout --changed --json --robot` | blocked | Reported `sync_required` due current dirty generated/projection state; useful as closeout blocker evidence, not a clean fixture. |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` | pass | Spec artifact identity is valid. |
| `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` | pass | Spec Linear traceability is valid. |
| `git diff --check -- .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md .harness/linear/agent-skills-linear-plan.md` | pass | No whitespace errors in the edited planning artifacts. |

## Review Decision

Proceed to `he-plan`.

The next plan must preserve these constraints:

- Keep `JSC-246` bounded to the agent-first golden path.
- Do not add proof schemas, lifecycle states, or new promotion gates.
- Prove diagnostic debt continuation instead of allowing diagnostic loops.
- Ground route fixtures in a live capability registry snapshot.
- Pair documentation compression with fresh-agent behavior metrics.
- Treat current dirty closeout evidence as a blocker scenario, not as the clean
  completion fixture.

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Review coverage |
| --- | --- | --- |
| `JSC-246` | SA1-SA18 | Reviewed the HE spec for the approved agent-first golden path slice. |
| `JSC-246` | SA1, SA2 | Verified artifact identity and Linear traceability gates pass for the spec. |
| `JSC-246` | SA6, SA8, SA10, SA13, SA15, SA16 | Confirmed remediated scope boundary for proof, routing, diagnostic debt, and docs compression. |
| `JSC-246` | SA1-SA18 | Approved handoff to `he-plan` with residual risks documented for implementation planning. |

## Evidence & Traceability Matrix

| Conclusion | Evidence type | Files / commands | Confidence | Why it matters |
| --- | --- | --- | --- | --- |
| The spec is ready for `he-plan` after remediation. | review, validation | `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`; artifact identity lint; Linear traceability lint; `git diff --check` | High | The artifact is traceable, scope-bounded, and passes the required harness checks for planning handoff. |
| Proof work is bounded and must not expand into neighboring schema/lifecycle tracks. | spec, traceability | Spec proof boundary clause; `SA10`; `SA16`; `./bin/ask skills prove he-spec --json --robot` | High | Prevents a bounded golden-path slice from becoming a cross-cutting proof-system migration. |
| Diagnostic debt must not trap agents after blocking gates are green. | spec, runtime flow | Diagnostic debt continuation rule; `SA6`; live closeout blocker evidence | High | Protects the command surface from turning into a non-terminating repo-surface loop. |
| Routing tests must separate route semantics from handle/projection drift. | spec, command evidence | Fixture stability rule; `SA8`; `./bin/ask skills resolve he-spec --json`; `./bin/ask skills resolve he-code-review --json` | High | Keeps eval failures meaningful and avoids brittle tests against generated surfaces. |
| Documentation compression must be behavior-proven. | spec, eval requirements | `SA13`; `SA15`; fresh-agent metric requirements | Medium-high | Prevents cosmetic doc deletion from masquerading as agent-cognition improvement. |
| Live closeout cannot be used as a clean completion fixture today. | runtime evidence | `./bin/ask repo closeout --changed --json --robot`; `git status --short` | High | The dirty worktree includes unrelated generated/projection churn, so implementation planning needs controlled fixtures. |
