# JSC-364 Governed Implementation Prompt

Use this prompt to start the governed implementation lane for JSC-364 without
reopening scope, sequencing, or proof boundaries.

## Mode Gate

Current mode is `GOVERNED_IMPLEMENTATION`.

Jamie approved the switch from `PROMPT_REVIEW_ONLY` to
`GOVERNED_IMPLEMENTATION` on 2026-05-24. This grants authority to create the
Goal Governor board, seed execution notes, validate the governed state, and
begin the slice lifecycle below.

This does not grant blanket authority to mutate PR state, update Linear, merge
work, or perform unsafe external operations outside the bounded slice lifecycle.
Those actions remain gated by the relevant slice, review stack, validation
evidence, and explicit stop conditions.

Before any implementation code starts, the Goal Governor continuation must
record:

- `prompt_readiness`: `pass | revise | blocked`
- `interpreted_objective`
- `target_repository`
- `source_plan`
- `source_spec`
- `proposed_first_slice`
- `required_permissions`
- `external_systems_that_would_be_touched`
- `expected_artifacts`
- `review_stack`
- `slice_delivery_model`
- `stop_conditions`
- `questions_or_contradictions`
- `governor_start_command`

The review-only launch contract is now satisfied. This prompt is the active
governed execution contract.

## Execution Trigger

Jamie has authorized the switch from `PROMPT_REVIEW_ONLY` to
`GOVERNED_IMPLEMENTATION`.

Create the governed board, validate it, and begin the first governed slice only
after the board is valid.

## Objective

Implement JSC-364: add a Codex Runtime Proof Plane to Agent Skills Kit.

The implementation must make `./bin/ask` able to produce durable,
machine-readable runtime proof or durable `blocked_runtime` evidence for
Codex-targeted skill/runtime checks. The central trust boundary is that modeled
Codex compatibility, generated projection readiness, docs, plans, and local
intent must never masquerade as live runtime proof.

## Canonical Sources

- Plan:
  `.harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md`
- Spec:
  `.harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md`
- Audit:
  `.harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md`
- Evidence extraction:
  `.harness/research/deep/2026-05-24-jamie-craik-evidence.md`
- Codex integration analysis:
  `/Users/jamiecraik/dev/codex/.harness/research/deep/2026-05-24-codex-skills-sdk-native-integration-analysis.md`
- Linear:
  `JSC-364`, child of `JSC-351`

## Target Repository

`/Users/jamiecraik/dev/agent-skills`

## Kickoff Command

After execution approval, use:

```text
/goal Follow Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/goal.md
```

That command is a prompt convention. It is not a native file binding.

## Goal Board To Create After Approval

Create the governed board under:

`Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/`

Minimum files:

- `goal.md`
- `state.yaml`
- `receipts.jsonl`
- `notes/`

Before implementation starts, validate the board with:

```bash
python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane
```

## Completion Contract

Outcome:

- JSC-364 is implemented through bounded, independently validated slices.
- `./bin/ask` exposes a reachable Codex Runtime Proof Plane path that emits
  schema-valid runtime proof or schema-valid `blocked_runtime` evidence.
- `repo doctor`, proof commands, conformance output, capability discovery,
  and closeout output do not confuse modeled conformance with live runtime
  parity.
- Agents can discover, invoke, validate, and hand off proof artifacts from the
  shared workspace without private session context.
- Every implemented slice is committed, pushed, opened or updated as a GitHub
  PR, and handed to a PR green-sweep lane until faults are fixed or a concrete
  blocker is recorded.
- Final cleanup is not announced until docs and AGENTS-facing instructions have
  been checked for accuracy.

Verification surface:

- Goal board validator.
- Plan/spec traceability and current source identity.
- Slice-specific focused tests and command smoke checks.
- RuntimeCard, EvidenceReceipt, ArtifactRecord, RuntimeSessionSummary, and
  RecoveryPlanSummary schema validation.
- `./bin/ask` proof/conformance/capability/doctor command output.
- Mandatory review-stack artifacts and reviewer dispositions.
- GitHub PR state, CI state, review state, mergeability, and branch freshness.
- Live Linear JSC-364 tracker truth, reported separately from local validation.
- Final Judge or PM completion receipt.

Constraints:

- Do not mutate `/Users/jamiecraik/dev/codex`; it is read-only source context.
- Do not claim live Codex parity from source inspection, modeled conformance,
  generated projection visibility, or documentation.
- Do not create prose-only schemas, validators, or evidence artifacts. Every
  new proof surface must be reachable from a command or test.
- Do not silently downgrade runtime absence into success.
- Do not edit generated runtime projections, plugin caches, user/global runtime
  config, or external service state unless a slice explicitly authorizes it.
- Do not broaden into P1 telemetry schemas before P0 proof-plane acceptance.
- Do not merge without explicit authority in the current turn.

## Architecture Direction

Use `$improve-codebase-architecture` as the structural lens for every slice.

Architectural priorities:

- Small, reversible changes.
- Deep modules over scattered proof logic.
- Stable public JSON contracts.
- Schema-backed runtime boundaries.
- Agent-safe command surfaces with focused tracer tests.
- Separation between command proof, schema proof, runtime proof, PR truth,
  tracker truth, and documentation truth.
- Source-of-truth discipline: canonical implementation before projections,
  runtime truth before stated intent, current branch truth before memory.

The default design choice is to extend existing ask surfaces in place unless
fresh evidence proves a new module boundary is needed.

## Slice Delivery Model

Govern one bounded slice at a time.

Each slice has a dedicated implementation branch and PR unless the governor
records a safer reason to batch slices. A slice is ready for PR only when local
validation and the mandatory review stack have no unresolved blockers.

After the slice PR exists:

1. Launch a dedicated subagent with `$pr-green-sweep`.
2. The subagent must triage that PR from live GitHub truth until all faults are
   fixed, the PR is merged, or a concrete blocker requires owner input.
3. The subagent must write a deterministic triage artifact under
   `artifacts/reviews/jsc-364-runtime-proof-plane/<slice>/pr-green-sweep.md`
   or the board must record a blocked handoff health report.
4. The coordinator may continue to the next implementation slice while the PR
   green-sweep subagent runs only after the current slice has:
   - a pushed branch,
   - a PR URL,
   - a verified head SHA,
   - a non-empty triage artifact or deterministic handoff health report,
   - no local unstaged work from that slice,
   - no unresolved blocker that changes the next slice's safe patch path.

Do not treat spawn success, mailbox text, elapsed wait time, or a prose summary
as PR triage completion evidence.

## Mandatory Slice Lifecycle

Every implementation slice follows this lifecycle exactly:

1. GOVERN
2. IMPLEMENT
3. FOCUSED VALIDATION
4. SIMPLIFY REVIEW
5. UNSLOPIFY REVIEW
6. HE CODE REVIEW
7. TESTING REVIEW
8. FIX ACCEPTED FINDINGS
9. ADVERSARIAL REVIEW
10. AGENT-NATIVE REVIEW
11. FIX BLOCKING REVIEW FINDINGS
12. UPDATE IMPLEMENTATION NOTES AND RECEIPTS
13. FINAL LOCAL VALIDATION FOR THE SLICE
14. GIT ADD AND COMMIT
15. PUSH BRANCH
16. OPEN OR UPDATE GITHUB PR
17. LAUNCH PR GREEN-SWEEP SUBAGENT
18. RECORD TRIAGE HANDOFF ARTIFACT
19. CONTINUE ONLY AFTER GOVERNOR CONFIRMS SAFE NEXT-SLICE STATE

If any step cannot run, record `blocked` or `not_applicable` with exact
evidence. Do not fabricate completion.

## Mandatory Slice Review Stack

After implementation and before marking a slice task done, run or explicitly
record a blocked/not-applicable result for:

- `$simplify`
- `$unslopify`
- `$he-code-review`
- `$testing`

Before a slice task is considered done, request and disposition independent
review from:

- `@adversarial-reviewer`
- `@agent-native-reviewer`

Review outputs must identify findings as:

- `blocker`
- `high`
- `medium`
- `low`
- `informational`

Governor dispositions are:

- `fix_now`
- `defer_safely`
- `reject_with_reason`
- `escalate_to_owner`

No unresolved `blocker` or accepted `high` finding may proceed to commit.

## Documentation And Cleanup Gate

Before cleanup can be announced, run documentation accuracy review with:

- `$docs-expert`
- `$agents-md`

The documentation gate must verify:

- AGENTS-facing instructions still match live repo behavior.
- README or command docs do not advertise non-reachable proof commands.
- RuntimeCard/EvidenceReceipt schema docs match implementation.
- Validation commands in docs match actual wrapper behavior.
- Any generated or projected surfaces are either regenerated from canonical
  source or explicitly out of scope.
- No cleanup claim hides active PR, CI, review, Linear, or validation blockers.

If docs or AGENTS instructions are stale, fix them before closeout or record a
blocked cleanup state.

## Continuous PR Green-Sweep Lane

For each slice PR, the green-sweep agent must inspect live GitHub truth:

- PR head SHA and branch identity.
- Mergeability and merge conflicts.
- Required GitHub Actions and CircleCI checks.
- CodeRabbit and GitHub review state.
- Active inline review comments.
- Linear gate status where applicable.
- Branch drift from `main`.
- Required conversation resolution.
- Stale or old-head comments separated from active blockers.

The green-sweep agent may make safe scoped fixes only when branch/worktree
ownership is clear. Otherwise it records the blocker and exact next action.

The coordinator must not mark the slice PR green from local validation alone.

## Work Units

Implement the plan's work units in order unless the governor records a concrete
dependency reason to change sequencing.

### PU-001: Command-Handle Drift Repair And Repo Doctor Baseline

Objective:

Make command-handle drift mechanically visible and blocking before runtime proof
features expand.

Allowed initial files:

- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/commands/repo_impl.py`
- `Infrastructure/tests/test_ask_skills_doctor.py`
- `Infrastructure/tests/test_ask_cli_impl.py`
- Existing generated command-handle fixtures only through repo-owned generators.

Validation:

```bash
./bin/ask skills handles --check --check-command-handles --no-handles --json --robot
./bin/ask repo doctor --json --robot
python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q
python3 -m pytest Infrastructure/tests/test_ask_cli_impl.py -q
```

Stop if generator ownership is unclear or repo doctor cannot report command
handle drift separately from unrelated failures.

### PU-002: P0 Runtime Evidence Schemas And Validator

Objective:

Create the smallest schema and validation layer that proves runtime evidence
without dragging P1 telemetry into P0.

Allowed initial files:

- `Infrastructure/config/schemas/**`
- `Infrastructure/scripts/validation-and-linting/**`
- `Infrastructure/tests/**`
- `Infrastructure/scripts/lib/ask/skills_sdk/**`
- test fixtures under repo-owned paths.

Validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py <fixture-or-evidence-path> --json
python3 -m pytest Infrastructure/tests -q -k 'runtime_card or evidence_receipt or runtime_proof'
```

Stop if schema dependencies require network install or if P1 schema concepts
become necessary for P0 acceptance.

### PU-003: Codex Parity Conformance Status Split

Objective:

Make conformance output distinguish `modeled_conformance`,
`live_runtime_parity`, and `blocked_runtime`.

Allowed initial files:

- `Infrastructure/scripts/lib/ask/skills_sdk/conformance.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- focused conformance tests.

Validation:

```bash
./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/jsc-364-codex-parity --json --robot
python3 -m pytest Infrastructure/tests -q -k 'conformance or codex_parity'
```

Stop if source-modeled checks are about to be reported as live runtime parity.

### PU-004: Capability Discovery And Wrapper Fixture Coverage

Objective:

Expose runtime target capability/limitation discovery and prove public wrapper
reachability.

Allowed initial files:

- `Infrastructure/scripts/lib/ask/commands/**`
- `Infrastructure/scripts/lib/ask/skills_sdk/**`
- `Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py`
- focused tests and fixtures.

Validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation
./bin/ask skills capabilities --runtime-target codex --json --robot
```

Stop if capability discovery can only be proven through private implementation
imports instead of the public wrapper.

### PU-005: Codex Preview Source Identity And Truncation Hardening

Objective:

Harden preview source identity, unavailable-source behavior, partial-depth
reporting, and truncation warnings.

Allowed initial files:

- `Infrastructure/scripts/lib/ask/services/codex_preview.py`
- `Infrastructure/tests/test_ask_skills_codex_preview.py`
- related command wiring only if the public output must change.

Validation:

```bash
python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q
```

Stop if implementation would mutate `/Users/jamiecraik/dev/codex` or global
Codex runtime state.

### PU-006: Runtime Proof Command And Blocked Runtime Evidence

Objective:

Implement the core proof command that emits RuntimeCard, EvidenceReceipt,
ArtifactRecord data, and RecoveryPlanSummary.

Allowed initial files:

- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/contracts.py`
- `Infrastructure/config/schemas/**`
- focused tests.

Validation:

```bash
./bin/ask skills proof testing --runtime-target codex --json --robot
python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py <proof-artifact-path> --json
python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q
```

Stop if proof cannot produce either schema-valid runtime evidence or
schema-valid `blocked_runtime` evidence.

### PU-007: Shared Workspace Evidence And Agent-Operable Closeout

Objective:

Make proof artifacts usable by another agent without private session context.

Allowed initial files:

- `Infrastructure/scripts/lib/ask/skills_sdk/**`
- `Infrastructure/scripts/lib/ask/commands/**`
- `Infrastructure/tests/**`
- `.harness/evidence/**`
- implementation notes or receipts for this goal.

Validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py <proof-artifact-path> --require-shared-workspace --json
./bin/ask repo doctor --json --robot
python3 -m pytest Infrastructure/tests -q -k 'shared_workspace or closeout or runtime_card'
```

Stop if artifacts depend on ephemeral session-only state or private prompt
content.

### PU-008: Final Integration, Review, And Tracker Evidence

Objective:

Prove the complete implementation through local validation, review, docs, PR
truth, and live tracker evidence without conflating those proof sources.

Validation:

```bash
./bin/ask repo closeout --changed --json --robot
./bin/ask repo doctor --json --robot
python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation
python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py Infrastructure/tests/test_ask_skills_codex_preview.py Infrastructure/tests/test_ask_cli_impl.py -q
```

Also refresh:

- GitHub PR state.
- CircleCI/GitHub required checks.
- CodeRabbit/GitHub review state.
- Linear JSC-364 state.

Stop if a critical validator fails, review identifies a false-success path, or
live tracker state contradicts claimed delivery.

## Validation Rules

Use the smallest relevant verifier first. Broaden only after the focused gate
passes or when the focused gate proves the implementation risk is wider.

Always record exact command text and result:

```text
Command: <exact command> -> pass|fail|blocked (<reason>)
```

Required common gates:

```bash
python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane
./bin/ask skills handles --check --check-command-handles --no-handles --json --robot
./bin/ask repo doctor --json --robot
./bin/ask repo validate --scope=check --json --robot
./bin/ask repo validate --scope=audit --json --robot
```

Run `./bin/ask repo validate --scope=check --json --robot` before a slice PR
only when focused validation is green and the slice is ready for broader proof.

## Source And Projection Boundaries

Canonical implementation surfaces:

- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/**`
- `Infrastructure/config/schemas/**`
- `Infrastructure/scripts/validation-and-linting/**`
- `Infrastructure/tests/**`
- `Skills/agent-ops/goal-governor/**` only if the board or validator contract
  must change.
- `.harness/evidence/**`, `.harness/implementation-notes/**`, and this goal
  board for delivery evidence.

Do not hand-edit:

- `.agents/**`
- `.skillsets/**`
- `Plugins/cache/**`
- global Codex config
- user home runtime state
- generated runtime projections

If projection regeneration is required, use the repo-owned generator, stage only
the intended generated files, and record the command.

## Implementation Notes

Create and update this implementation ledger during execution:

`.harness/implementation-notes/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-execution-notes.html`

The notes file must contain:

- slice name,
- allowed files,
- commands run,
- validation outcomes,
- review findings,
- PR URL and head SHA,
- green-sweep artifact path,
- blockers and dispositions,
- rollback notes,
- next-slice safety decision.

## Required Receipts

Append a JSONL receipt to the goal board after every material step.

Receipt types:

- `governed_slice_selected`
- `implementation_started`
- `validation_run`
- `review_requested`
- `review_dispositioned`
- `slice_committed`
- `pr_opened_or_updated`
- `pr_green_sweep_launched`
- `pr_green_sweep_artifact_verified`
- `slice_safe_to_continue`
- `docs_accuracy_checked`
- `cleanup_ready`
- `completion_receipt`

A receipt without exact verifier, outcome, command, artifact path, or scope is
not completion evidence.

## Stop Conditions

Stop immediately and report `blocked` when:

- Goal board validation fails.
- Plan/spec traceability is stale or contradicted by live repo evidence.
- A proof command can only return prose, not schema-valid evidence.
- Runtime absence is being treated as success.
- The current slice needs files outside its allowed boundary.
- Validation fails and the next fix is outside the active slice.
- Reviewers identify a false-success path, unsafe command surface, or
  agent-native reachability gap.
- PR green-sweep cannot produce a deterministic artifact or handoff health
  report.
- GitHub, CI, review, or Linear state contradicts the claimed slice status.
- Documentation or AGENTS guidance is inaccurate at cleanup time.
- Owner approval is needed for external mutation, destructive commands, or
  changing tracker/project ownership.

## Rollback Rules

Rollback only the active slice unless the governor proves a wider dependency
requires it.

Preserve:

- failing validation output,
- proof artifacts,
- review artifacts,
- PR state evidence,
- receipts,
- implementation notes.

Do not revert unrelated dirty worktree changes, untracked research, or
artifacts created outside the active slice.

## Definition Of Done

The goal is complete only when a final Judge or PM receipt records
`decision=complete` and confirms:

- All PU-001 through PU-008 acceptance conditions are satisfied or explicitly
  superseded with owner-approved evidence.
- Runtime proof commands emit schema-valid proof or schema-valid
  `blocked_runtime` evidence.
- Modeled conformance, live runtime parity, preview identity, PR truth, tracker
  truth, and documentation truth are reported separately.
- Every slice PR is merged or explicitly escalated with a concrete blocker.
- CI and review state are current for every PR surface.
- `$simplify`, `$unslopify`, `$he-code-review`, and `$testing` have no
  unresolved blockers for each slice.
- `@adversarial-reviewer` and `@agent-native-reviewer` have no unresolved
  blockers before each slice is marked done.
- `$docs-expert` and `$agents-md` confirm documentation and instruction
  accuracy before cleanup is announced.
- Linear JSC-364 state is refreshed and not confused with local validation.
- No stale-state, false-success, blocked-runtime, review, merge-safety, or
  documentation contradiction remains.

## First Governor Action After Approval

1. Create `Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/`.
2. Write `goal.md`, `state.yaml`, and `receipts.jsonl` from this prompt and
   the source plan.
3. Validate the board.
4. Select PU-001 as the first slice.
5. Record allowed files, validation commands, and stop conditions in
   `state.yaml`.
6. Start implementation only after the board is valid.

## Prompt Readiness Criteria

This prompt is ready only if the reviewing agent can answer `pass` to all of:

- Does it preserve JSC-364 as a runtime proof plane rather than prose
  governance?
- Does it keep `PROMPT_REVIEW_ONLY` separate from implementation authority?
- Does it prevent modeled conformance from being claimed as live runtime parity?
- Does it require per-slice validation, review, commit, PR, and green-sweep
  handoff?
- Does it allow next-slice work while PR triage runs only after deterministic
  handoff evidence exists?
- Does it require adversarial and agent-native review before slice completion?
- Does it require docs and AGENTS accuracy before cleanup?
- Does it name concrete stop conditions and validation commands?
- Does it avoid editing generated projections or external runtime state as a
  default implementation path?
