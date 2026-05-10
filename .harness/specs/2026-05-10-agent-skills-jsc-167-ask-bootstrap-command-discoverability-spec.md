---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec
artifact_type: he-spec
type: he-spec
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Spec
harness_stage: he-spec
status: ready_for_plan
date: 2026-05-10
origin: .harness/linear/agent-skills-linear-plan.md
risk: medium
depth: bounded-execution-slice
ui: false
traceability_required: true
linear_status: existing
linear_issue: JSC-167
linear_issue_url: https://linear.app/jscraik/issue/JSC-167/harden-ask-bootstrap-and-command-discoverability
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
linear_parent_initiative: Dev Portfolio
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Harden ask bootstrap and command discoverability"
linear_labels: "Roadmap: Now, Infra, Improvement"
linear_label_status: resolved_with_existing_labels
linear_priority: 2
linear_delta_status: pass_live_refresh_2026_05_10
review_status: approved_for_he_plan
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Spec

## Mode Decision

interactive_status: autonomous_assumption

This is a bounded HE spec for the live-verified next slice in
`.harness/linear/agent-skills-linear-plan.md`.

Selected slice:

- Linear issue: `JSC-167`
- Linear milestone: `Command surface and ask reliability`
- HE slice name: `Ask Bootstrap and Command Discoverability`
- Live status: `Backlog`
- Priority: `High`
- Labels: `Roadmap: Now`, `Infra`, `Improvement`
- Blocked by: none
- Blocks: `JSC-168`
- Related: `JSC-230`, `JSC-233`

The autonomous assumption is that the user request to retry Linear and route
through `$he-spec` authorizes this durable spec artifact after the live Linear
blocker cleared. The spec remains read-only with respect to Linear: no Linear
objects were created, closed, or updated.

## HE Gate Profile

```yaml
gate_profile:
  risk_class: agent_bootstrap_contract
  proven_risks:
    - A fresh user or agent can fail before reaching `./bin/ask` because the
      wrapper is not executable or the documented command path assumes PATH
      state that has not been established.
    - A bootstrap fix can accidentally become a global shell mutation or
      environment-management system instead of a repo-local entrypoint repair.
    - Preflight, repo doctor, and onboarding docs can report different first
      commands, leaving agents to infer which surface is authoritative.
    - JSC-168 dependency-contract work and JSC-169 lazy-loading architecture can
      be pulled into this slice unless failure boundaries are explicit.
  required_contracts:
    - Plugins/harness-engineering/references/stage-context-contract.md
    - Plugins/harness-engineering/references/linear-delta-capture-gate.md
    - Plugins/harness-engineering/references/first-principles-contract.md
    - Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md
  skipped_contracts:
    - contract: Plugins/harness-engineering/references/plugin-hook-capability-contract.md
      reason: JSC-167 does not introduce plugin hooks, hook-enforced lifecycle behavior, or bundled plugin guardrails.
    - contract: Plugins/harness-engineering/references/domain-model-production-contract.md
      reason: The slice changes repo command bootstrap behavior, not a product domain model.
    - contract: codex-security security scan
      reason: No credential handling, auth boundary, network side effect, or external mutation is admitted by this spec.
  minimum_proof_required:
    continue_to_next_stage: Artifact identity, live Linear traceability, current command baseline, explicit characterization fixtures, and technical review with no blocking findings.
    safe_to_close: Bootstrap/idempotence proof, executable-bit negative fixture, PATH-discovery fixture, fallback smoke, docs-contract evidence, focused repo validation, and closeout/eval artifact with exact command outcomes.
    block_next_stage: Any plan that mutates global shell config silently, folds in JSC-168/JSC-169, introduces an unapproved new first-contact command, or cannot prove a non-executable entrypoint fixture.
  evidence_basis: repo+linear+harness
  downstream_route: he-plan
```

## First-Principles Check

```yaml
first_principles_check:
  verified_failure: The repo has a strong `./bin/ask` control plane, but first contact can still fail before that control plane is reachable or discoverable.
  fundamental_constraint: Bootstrap must make the existing command contract reachable with the least repo-local mechanism, without becoming a dependency manager or global shell installer.
  assumption_being_challenged: More onboarding prose, a broader `ask start` flow, or a dependency refactor is required before fresh checkout usability improves.
  smallest_effective_mechanism: Add one canonical bootstrap path, characterize executable/PATH/fallback failures, and wire the same signals into docs and preflight/doctor evidence.
  analogy_or_template_rejected: Do not copy full installer or environment-manager patterns from other repos unless the repo-local entrypoint proof cannot solve the failure.
  proof_required: Non-executable wrapper fixture, fallback command smoke, PATH-discovery proof, idempotence rerun, docs-contract check, and explicit stop rules for dependency or lazy-loading failures.
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Problem

`ask` is the public command interface for humans and agents, but first-run
execution can still depend on checkout-local details that are easy to miss:
`bin/ask` may not be executable, `ask` may not be discoverable on `PATH`, and
the fallback command path can be scattered across docs instead of enforced by a
single bootstrap check.

The verified failure is not that the repo lacks command capability. The failure
is that a fresh human or agent can hit a low-level bootstrap problem before
reaching the intended repo control plane.

The current live checkout proves the happy path, not the failure boundary:

- `bin/ask` is executable in this worktree.
- `./bin/ask repo status --json --robot` returns a successful JSON envelope.
- `Docs/agents/5-minute-success-path.md` currently starts with
  `./bin/ask repo doctor --json --robot`, but does not name a bootstrap command
  or fallback path for a checkout where `bin/ask` is not executable.
- `README.md` names a Codex environment helper for PATH setup, but that helper
  is not a JSC-167 bootstrap contract for `ask` itself.

## Goals

- Provide one canonical bootstrap path for making `ask` usable from a fresh
  checkout.
- Detect non-executable `bin/ask` and missing command discovery in preflight or
  an equivalent repo wrapper.
- Preserve `python3 bin/ask ...` as the stable fallback path when a shell shim is
  not installed.
- Update onboarding and agent-facing docs so the 5-minute path uses the same
  command contract that validation checks.
- Keep output machine-readable where agents need pass/fail evidence.
- Make negative proof first-class: the implementation must prove what happens
  when `bin/ask` is not executable and when `ask` is not discoverable on PATH.

## Non-Goals

- Do not implement `JSC-169` lazy command import architecture.
- Do not implement `JSC-168` reproducible Python environment setup except for
  surfacing it as a dependency or follow-up when bootstrap cannot proceed.
- Do not create `ask start`, `ask doctor --fix`, or a broader command cockpit.
- Do not mutate runtime projections or generated command handles.
- Do not close or update Linear issues as part of the implementation plan.
- Do not silently modify shell startup files, global bin directories, or user
  runtime links.
- Do not treat the current checkout's executable `bin/ask` as sufficient proof
  for fresh-checkout behavior.

## Linear Work Item Contract

```yaml
linear_issue: JSC-167
linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
linear_project: agent-skills
linear_milestone: Command surface and ask reliability
linear_status: Backlog
linear_priority: High
linear_labels:
  - Roadmap: Now
  - Infra
  - Improvement
blocked_by: []
blocks:
  - JSC-168
related_to:
  - JSC-230
  - JSC-233
route: Agent-assisted; human-review required for public command/discoverability contract changes
```

This spec admits only `JSC-167`. `JSC-168` is treated as a downstream issue that
may become easier to validate after bootstrap hardening, not as in-scope
environment-management work.

## Boundary

In scope:

- Bootstrap script or wrapper route that verifies and, when safe, repairs the
  repo-local entrypoint executable bit.
- Detection that reports entrypoint executable status and PATH discoverability.
- Documentation updates for first-run usage, fallback behavior, and validation
  evidence.
- Focused tests or smoke scripts for bootstrap success and failure cases.
- One explicit fallback path for users who cannot or should not install a PATH
  shim.

Out of scope:

- Optional dependency lazy loading.
- Python dependency manifest redesign.
- Skill runtime projection sync.
- Broad cleanup of `./bin/ask` command modules.
- Cross-repo installation policy.
- Mutating `~/.zshrc`, `~/.bashrc`, shell profile files, global npm/pipx/uv
  environments, or Codex runtime projections.
- Making `ask` globally available on every machine without an explicit,
  reviewable install step.

## Baseline

Current baseline evidence:

- `./bin/ask skills resolve he-spec --json` resolves the `$he-spec` command
  handle to `Plugins/harness-engineering/skills/he-spec/SKILL.md`.
- `bin/ask` is currently `-rwxr-xr-x` in this checkout and is a thin Python
  wrapper that execs `Infrastructure/bin/ask`.
- `./bin/ask repo status --json --robot` currently returns `status: success`,
  `repo_root: "."`, `is_git: true`, and `skills_synced: true`.
- Live Linear milestone lookup for canonical project
  `791c2f12-5ffb-4644-8421-f4216ac6d805` returns
  `Command surface and ask reliability` with progress `37.5%`.
- Live Linear issue read for `JSC-167` returns `Backlog`, priority `High`,
  labels `Roadmap: Now`, `Infra`, and `Improvement`, with no blockers.
- Live Linear issue read for `JSC-169` returns `Backlog`, priority `High`, and
  `blockedBy: JSC-168`, so it must not precede `JSC-167` without re-approval.

Baseline gaps to characterize:

- There is no durable JSC-167 bootstrap artifact yet.
- The current happy path does not prove behavior when `bin/ask` is
  non-executable.
- The current docs do not prove that a PATH-less environment can recover using a
  single fallback path.
- Existing preflight scripts validate repo paths and binaries, but the spec has
  not yet proven that they expose `ask` entrypoint executable status and PATH
  discoverability as named signals.

## Domain Model

```yaml
ask_entrypoint:
  path: bin/ask
  required_property: executable or safely made executable by bootstrap
fallback_command:
  command: python3 bin/ask repo status --json
  role: stable repo-local command path when PATH shim is absent
path_discovery:
  target: ask
  required_property: shell can resolve the command after bootstrap or docs state the fallback
bootstrap_check:
  role: make first-run state explicit before deeper repo operations
preflight_signal:
  role: report executable and discoverability state with actionable remediation
docs_contract:
  role: keep README, AGENTS, and 5-minute path aligned on the same bootstrap and fallback commands
negative_fixture:
  role: prove first-run failure recovery without relying on this dirty checkout
```

## Lifecycle

1. Fresh checkout starts from repository root.
2. User or agent runs the canonical bootstrap path.
3. Bootstrap verifies or repairs `bin/ask` executability when safe.
4. Bootstrap runs the fallback smoke command.
5. Bootstrap reports whether `ask` is discoverable on `PATH`, and either proves
   the shim works or points to the fallback.
6. Preflight or repo doctor reports the same checks so drift is visible after
   setup.
7. Onboarding docs and agent guidance route to the same commands.
8. Closeout captures the bootstrap proof bundle and refuses closure if the
   negative fixture was skipped without a blocker reason.

## Interfaces

Required command surfaces:

```bash
bash scripts/bootstrap-ask.sh
python3 bin/ask repo status --json
ask repo status --json
```

The implementation may choose a different script name only if the name is
documented in the spec handoff and all docs/tests use that single command.

Recommended output shape for bootstrap proof:

```yaml
schema_version: 1
status: success|error
checks:
  entrypoint_executable:
    status: pass|fail|repaired
    path: bin/ask
  fallback_command:
    status: pass|fail
    command: python3 bin/ask repo status --json
  path_discovery:
    status: pass|warn|fail
    command: ask
  shim_smoke:
    status: pass|fail|skipped
    command: ask repo status --json
    resolved_path: <absolute path from command -v ask or null>
    repo_identity:
      status: pass|fail|skipped
      expected_repo_root: <current checkout path>
      observed_repo_root: <repo_root_resolved from ask repo status JSON>
remediation:
  applied:
    - chmod_bin_ask
  manual:
    - add_repo_bin_to_path_or_use_fallback
```

Expected machine-readable evidence should distinguish:

- entrypoint executable: pass/fail
- fallback command: pass/fail
- PATH discoverability: pass/fail/warn
- shim smoke: pass/fail/skipped
- shim repo identity: pass/fail/skipped
- remediation: applied/manual/not_available

## Invariants

- `./bin/ask` remains the repo command interface.
- `python3 bin/ask ...` remains a supported fallback.
- Bootstrap must be idempotent.
- Bootstrap must not silently mutate global shell configuration.
- If PATH shim installation is offered, it must be explicit or documented as a
  manual action unless the repo already has an approved safe installer pattern.
- Human-readable output may be concise, but JSON output must remain stable
  enough for agent proof.
- A failed dependency import during fallback smoke is a `JSC-168` signal unless
  the failure is caused by the bootstrap script itself.
- A failure caused by eager optional imports is a `JSC-169` signal unless it
  blocks the bootstrap's own minimal command path.
- The first-run docs must name the fallback command before introducing optional
  global `ask` discovery.
- A passing `ask repo status --json` shim smoke is insufficient unless it proves
  the resolved `ask` command is tied to this checkout, either through
  `command -v ask` path evidence or by asserting `repo_root_resolved` matches
  the intended repo root.

## Characterization Fixtures

| Fixture | Setup | Expected proof | Blocks closure? |
| --- | --- | --- | --- |
| CF1 executable happy path | Current checkout with executable `bin/ask` | Bootstrap reports `entrypoint_executable: pass` and fallback smoke passes | Yes |
| CF2 non-executable entrypoint | Temporary copy or controlled chmod fixture with `bin/ask` non-executable | Bootstrap reports repair or exact manual remediation, then fallback smoke passes | Yes |
| CF3 PATH-less shell | Shell with repo root available but `ask` not resolvable by name | Bootstrap reports `path_discovery: warn` or `fail` and gives `python3 bin/ask ...` fallback | Yes |
| CF4 PATH shim available | Environment where `ask` resolves to a command by name | `ask repo status --json` smoke passes and proves repo identity by resolved path and/or `repo_root_resolved` matching this checkout | Yes, if shim install is implemented |
| CF5 dependency failure | Fallback command fails because required Python dependencies are absent | Bootstrap preserves the raw failure text and returns a defer route to `JSC-168`; it does not implement dependency setup | Yes if encountered |
| CF6 eager optional import failure | Unrelated optional dependency breaks a minimal command | Bootstrap preserves the raw failure text and returns a defer route to `JSC-169`; it does not implement lazy-loading architecture | Yes if encountered |
| CF7 docs drift | First-run docs mention a different first command or no fallback | Docs check fails and names the mismatched path | Yes |
| CF8 idempotence rerun | Run bootstrap twice in the same checkout | Second run reports no unsafe extra mutation and fallback smoke still passes | Yes |
| CF9 wrong global shim | `ask` resolves to a command outside this checkout | Shim smoke fails or warns even if the command exits zero, because repo identity does not match | Yes |

## Failure And Recovery

| Failure | Required behavior | Recovery |
| --- | --- | --- |
| `bin/ask` is not executable | Detect clearly; repair only when scoped to the repo file and safe | Run bootstrap again and rerun fallback smoke |
| `python3 bin/ask repo status --json` fails | Surface the command, exit code, and shortest likely remediation | Defer dependency/environment repair to `JSC-168` if it exceeds bootstrap scope |
| `ask` is not on `PATH` | Report as discoverability failure or warning with fallback path | Provide documented shim/manual PATH step |
| Docs use a different first-run path | Treat as docs contract drift | Update docs to the canonical bootstrap path |
| Bootstrap wants to write shell startup files | Stop; do not silently mutate user shell state | Convert to explicit manual step or separate approved installer work |
| Implementation requires lazy import refactor | Stop; classify as `JSC-169` dependency | Return to Linear/spec gate before broadening scope |

## Observability

The implementation should produce one compact proof surface that can be cited by
`he-plan`, closeout, and future evals:

- command run
- exit code
- executable status
- fallback smoke result
- PATH discoverability result
- remediation action or manual instruction
- fixture ID when running characterization proof
- whether the failure belongs to JSC-167, JSC-168, JSC-169, or docs drift
- resolved `ask` path and repo identity match status when a PATH shim is tested

## Validation Plan

Minimum validation for `he-plan` handoff:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
```

Minimum validation for implementation closure:

```bash
bash <canonical-bootstrap-command>
python3 bin/ask repo status --json
./bin/ask repo status --json --robot
bash Infrastructure/scripts/validation-and-linting/verify-work.sh --fast
git diff --check -- <changed-files>
```

The implementation plan may substitute the repo's canonical focused validation
wrapper when it names the exact command and records why it covers the same
bootstrap, docs, and preflight surfaces.

Docs validation must be deterministic. A discretionary read-through is useful
review context, but closure requires a command, parser, or test that asserts the
documented bootstrap command and fallback command are the same across the
5-minute path and every modified onboarding surface.

## Acceptance Matrix

| ID | Acceptance criterion | Verification |
| --- | --- | --- |
| SA1 | A canonical bootstrap path exists and is documented in the first-run agent/human path. | Docs diff plus bootstrap smoke command. |
| SA2 | Fresh checkout flow can ensure `bin/ask` is executable without manual `chmod`. | Test or fixture that starts with non-executable entrypoint and proves repair. |
| SA3 | `python3 bin/ask repo status --json` passes after bootstrap in the documented environment. | Exact command outcome recorded. |
| SA4 | `ask repo status --json` passes when the documented PATH/shim path is available and proves the command targets this checkout, or the bootstrap emits a clear fallback when it is not. | PATH-discovery smoke with pass/fail/warn classification, resolved path evidence, and `repo_root_resolved` identity assertion. |
| SA5 | Preflight or equivalent repo wrapper reports entrypoint executable status and command discoverability. | Focused validation output includes both checks. |
| SA6 | The 5-minute docs path uses the same bootstrap and fallback commands as validation. | Deterministic docs contract check or executable docs smoke; manual review alone is not sufficient. |
| SA7 | Bootstrap remains idempotent and does not rewrite unrelated shell or runtime state. | Run bootstrap twice and inspect reported actions. |
| SA8 | `JSC-169`, `JSC-168`, `ask start`, and `ask doctor --fix` remain out of implementation scope unless later admitted. | Plan scope review before implementation. |
| SA9 | Negative fixtures prove non-executable entrypoint recovery and PATH-less fallback behavior. | CF2 and CF3 proof artifacts or blocked reasons. |
| SA10 | Dependency and optional-import failures, if encountered, preserve raw failure evidence and defer to JSC-168 or JSC-169 without implementing those fixes. | CF5 and CF6 fixture results when reproducible, or explicit not-encountered evidence. |
| SA11 | Bootstrap output includes stable machine-readable fields for executable status, fallback smoke, path discovery, shim smoke, repo identity, and remediation. | JSON/schema or snapshot assertion. |
| SA12 | No global shell config or runtime projection is mutated silently. | Diff/path ownership review and idempotence proof. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs |
| --- | --- |
| JSC-167: Fresh checkout can run `ask repo status` after bootstrap with no manual chmod. | SA1, SA2, SA3 |
| JSC-167: `python3 bin/ask repo status --json` and `ask repo status --json` both pass in documented environment. | SA3, SA4, SA11 |
| JSC-167: 5-minute docs path succeeds as written. | SA6, SA7 |
| JSC-167: Command contract smoke for bootstrap path. | SA1, SA3, SA4, SA7 |
| JSC-167: Preflight includes explicit pass/fail for entrypoint executable and discoverable. | SA5 |
| JSC-167: Current failures include missing PATH wiring and non-executable `bin/ask` in some checkouts. | SA2, SA9, SA11 |

## Stop Rules

Stop before implementation or closure when:

- the plan cannot name one canonical bootstrap command;
- the plan cannot prove CF2 without risking the real checkout;
- the plan cannot prove that `ask` resolves to this checkout when shim smoke is
  claimed;
- the docs validation is manual-only instead of deterministic;
- the bootstrap requires global shell profile edits to pass;
- the fallback command failure is actually a missing Python dependency contract
  requiring `JSC-168`;
- the failure is caused by eager optional imports and therefore belongs to
  `JSC-169`;
- docs and validation name different first-run commands;
- artifact identity or Linear traceability lint fails;
- the technical review has any open blocking finding.

## First Slice

The first implementation slice should add the smallest proof-producing
bootstrap mechanism and validation signal before broader docs cleanup:

1. Add or identify the canonical bootstrap command.
2. Add focused executable/discoverability detection.
3. Add targeted smoke coverage.
4. Update only the docs that present first-run command paths.

Recommended implementation units for `he-plan`:

| Unit | Purpose | Acceptance IDs |
| --- | --- | --- |
| PLAN-JSC167-001 | Select and add the canonical bootstrap command with JSON proof output. | SA1, SA3, SA11 |
| PLAN-JSC167-002 | Add executable-bit, PATH-discovery, wrong-shim, and repo-identity characterization fixtures. | SA2, SA4, SA9, SA11 |
| PLAN-JSC167-003 | Wire focused preflight or repo wrapper reporting for entrypoint/discoverability state and raw defer routes for JSC-168/JSC-169 failures. | SA5, SA10 |
| PLAN-JSC167-004 | Align README, AGENTS-linked guidance, and 5-minute path around bootstrap plus fallback with deterministic docs contract validation. | SA6 |
| PLAN-JSC167-005 | Add idempotence and no-global-mutation proof to closeout/eval evidence. | SA7, SA12 |

## Questions

- Should PATH shim installation be manual-only for this slice, or is there an
  existing approved installer pattern that can be reused? Default assumption for
  `he-plan`: manual-only unless source inspection finds an existing approved
  installer contract.
- Should the executable/discoverability signal live in preflight, repo doctor,
  or both? Default assumption for `he-plan`: put the focused detection in the
  smallest wrapper that is already part of first-run validation, then expose it
  through `repo doctor` only if the existing command architecture makes that
  additive and low-risk.

## Done

This spec is ready for `he-plan` when:

- Artifact identity and Linear traceability lint pass.
- The plan selects one bootstrap command name.
- The plan names the exact docs and validation scripts to update.
- The plan includes CF2 and CF3 proof without mutating the real checkout
  unsafely.
- The plan includes CF4/CF9 repo-identity proof for any claimed `ask` shim
  success.
- The plan includes deterministic docs contract proof rather than review-only
  docs confidence.
- The plan includes stop rules for JSC-168 and JSC-169 boundary failures.
- Technical review approves `he-plan` handoff with no blocking findings.
- The plan preserves `JSC-168` and `JSC-169` as separate Linear work.

## he-plan Handoff

```yaml
schema_version: 1
interactive_status: autonomous_assumption
selection_evidence:
  - .harness/linear/agent-skills-linear-plan.md
  - Linear JSC-167 live issue read
  - Linear Command surface and ask reliability milestone lookup
route: he-plan
stage: he-spec
scope: JSC-167 ask bootstrap and command discoverability
traceability:
  linear_issue: JSC-167
  linear_milestone: Command surface and ask reliability
  spec_artifact: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
validation:
  required:
    - python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
    - python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
    - python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
minimum_review:
  artifact: .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
  required_result: approved_for_he_plan
safe_to_continue: true
blocked_reason: null
blackboard_delta:
  current_slice: JSC-167 admitted for he-plan
  deferred:
    - JSC-168
    - JSC-169
    - JSC-172
    - JSC-174
```
