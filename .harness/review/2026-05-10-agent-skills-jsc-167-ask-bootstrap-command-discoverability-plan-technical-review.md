---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Plan Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-10
origin: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
reviewed_artifact: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
traceability_required: true
linear_status: existing
linear_issue: JSC-167
linear_issue_url: https://linear.app/jscraik/issue/JSC-167/harden-ask-bootstrap-and-command-discoverability
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Harden ask bootstrap and command discoverability"
review_result: approved_for_he_work_after_confidence_loop
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Plan Technical Review

## Review Verdict

Approved for `he-work` after the fresh confidence loop fixes.

The deepened plan is ready for implementation after review fixes and red-team
closure checks. It now treats bootstrap as the first-contact diagnostic, repo
doctor as post-bootstrap drift evidence, wrong-shim success as invalid without
both command provenance and parsed repo identity proof, docs drift as a
deterministic validator problem, and unknown fallback failures, unsafe entrypoint
paths, and subprocess timeouts as closure blockers rather than downstream
deferrals.

No known blocking findings remain after the second review pass. This is not a
claim of mathematical certainty; it means the plan has no unresolved factual,
scope, fixture, or closure-gate blocker found by this review loop.

## Reviewed Artifacts

- `.harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md`
- `.harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md`
- `.harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md`
- `.harness/linear/agent-skills-linear-plan.md`
- `bin/ask`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`
- `Infrastructure/tests/test_ask_repo_status_and_hub_stability.py`
- `Infrastructure/tests/test_ask_cli.py`
- `Infrastructure/tests/test_ask_helpers.py`
- `README.md`
- `AGENTS.md`
- `Docs/agents/5-minute-success-path.md`
- `Docs/agents/README.md`
- `Docs/agents/16-agent-operating-contract.md`
- `Docs/agents/04-validation.md`

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-167` |
| URL | https://linear.app/jscraik/issue/JSC-167/harden-ask-bootstrap-and-command-discoverability |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Milestone | `Command surface and ask reliability` |
| Parent issue title | `Harden ask bootstrap and command discoverability` |
| Reviewed artifact | `.harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md` |
| Review result | Approved for `he-work`; not approved for implementation closure |

## Fresh Confidence Loop

The second pass cross-checked the plan against repo evidence, an independent
red-team review, and primary documentation for the implementation mechanisms.

| Source | Verified fact | Plan effect |
| --- | --- | --- |
| Python subprocess documentation | `subprocess.run` supports argument-array execution, `cwd`, `capture_output`, `text`, and `timeout`, with `shell=False` as the default. | The plan now requires bounded subprocess probes with no shell and explicit timeouts. |
| Python pathlib documentation | `Path.chmod`, `Path.stat`, and `Path.is_symlink` expose the file-mode and symlink checks needed before mutation. | The plan now blocks chmod unless `bin/ask` is a regular repo-local non-symlink file. |
| Python shutil documentation | `shutil.which` resolves executables from a supplied path. | The plan now requires recorded command provenance for `ask` shim checks. |
| Python json documentation | `json.loads` parses JSON text into Python data structures. | The plan now requires structural JSON parsing for fallback and shim identity proof. |
| Pytest documentation | `tmp_path` provides isolated temporary directories per test invocation. | The plan now requires chmod/PATH fixtures to run against temporary roots. |
| GNU Bash set builtin documentation | `errexit`, `nounset`, and `pipefail` have explicit semantics and exceptions. | The plan now requires strict-mode launcher behavior with deliberate handling for expected non-zero probes. |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| `JSC-167` | SA1-SA12 | PLAN-JSC167-001 through PLAN-JSC167-005 | SA1-SA12 | Plan technical review approves `he-work`; PR evidence is not available because implementation has not started. |

## Findings

### Finding 1: Repo Doctor Was Too Load-Bearing For Broken Entrypoint Recovery

Severity: High
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The first plan draft made `repo doctor` the persistent owner for bootstrap
  health while still validating doctor through `./bin/ask`.
- In the target failure mode, `./bin/ask` may be non-executable, so doctor
  cannot be the first diagnostic surface.

Fix applied:

- The plan now states that bootstrap owns first contact and repo doctor owns
  persistent drift after bootstrap can run.
- Implementation must prove first-contact docs and validators route through
  `bash scripts/bootstrap-ask.sh --json` before any required `./bin/ask ...`
  command.

Review result:

Resolved. `he-work` must implement bootstrap as the recovery surface and doctor
as post-bootstrap visibility.

### Finding 2: JSC-168/JSC-169 Defer Routes Needed Deterministic Predicates

Severity: Medium
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The first plan draft allowed fallback failures to be deferred to `JSC-168` or
  `JSC-169`, but did not define classification predicates.
- That could mask a JSC-167 regression as downstream dependency or lazy-loading
  work.

Fix applied:

- The plan now defines deterministic classification rules for `JSC-167`,
  `JSC-168`, and `JSC-169`.
- It adds `unknown_unclassified` as a blocking classification.
- It adds CF10 to prove unknown fallback failures do not silently defer.

Review result:

Resolved. `he-work` must preserve raw failure evidence and block closure on
unknown fallback failures.

### Finding 3: Docs Drift Scope Was Too Narrow

Severity: Medium
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The first plan draft limited docs validation to `README.md`, `AGENTS.md`, and
  `Docs/agents/5-minute-success-path.md`.
- Current command-entry guidance also lives in the agent docs front door,
  operating contract, and validation docs.

Fix applied:

- The plan now makes normative first-contact docs explicit:
  `README.md`, `AGENTS.md`, `Docs/agents/5-minute-success-path.md`,
  `Docs/agents/README.md`, `Docs/agents/16-agent-operating-contract.md`, and
  `Docs/agents/04-validation.md`.
- It requires adding any newly discovered normative first-run `ask` doc to the
  deterministic validator rather than relying on manual review.

Review result:

Resolved. `he-work` must implement docs validation against the declared
normative first-contact surface.

### Finding 4: Safe-To-Close Gate Omitted CF10

Severity: High
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The prior gate text required CF1-CF9 even though CF10 was the explicit unknown
  fallback failure guard.
- A closure implementation could have passed without proving that
  `unknown_unclassified` blocks completion.

Fix applied:

- The plan now requires CF1-CF12 for `safe_to_close`, adding CF10, CF11, and CF12
  to the closure-grade fixture set.

Review result:

Resolved. Closure can no longer omit the unknown-fallback blocker fixture.

### Finding 5: Shim Identity Proof Was Spoofable

Severity: High
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The prior plan accepted either resolved-path proof or `repo_root_resolved` from
  output.
- A wrong shim could exit zero and emit forged JSON for the expected root.

Fix applied:

- The plan now requires both command provenance from controlled PATH resolution
  and structurally parsed `repo_root_resolved` matching the expected checkout.

Review result:

Resolved. Shim success now requires path proof and output identity proof.

### Finding 6: Chmod Repair Needed Symlink And File-Type Guards

Severity: Medium
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The prior plan allowed `chmod u+x bin/ask` for a non-executable path without
  requiring symlink or regular-file checks.
- That could mutate an unintended target if `bin/ask` were unexpectedly a
  symlink or non-regular file.

Fix applied:

- The plan now requires `path_type`, `safe_to_chmod`, and CF11 unsafe-entrypoint
  fixture proof. Bootstrap must refuse chmod on symlinks, missing files,
  non-regular files, or paths outside the repo root.

Review result:

Resolved. The plan now preserves the no-global-mutation boundary under unsafe
entrypoint shapes.

### Finding 7: Subprocess And PATH Fixtures Needed Tighter Bounds

Severity: Medium
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The prior plan said to run fallback and shim commands but did not require
  argument arrays, no-shell execution, `cwd`, timeouts, or structural JSON
  parsing.
- The PATH-less fixture could accidentally test absence of Python or Bash rather
  than absence of `ask`.

Fix applied:

- The plan now requires argument-array subprocess calls with `cwd`, timeout,
  captured text output, no shell, and `json.loads` parsing.
- CF12 covers hanging fallback/shim probes.
- CF3 now preserves enough interpreter/core utility access so the fixture tests
  `ask` discovery rather than interpreter absence.

Review result:

Resolved. Process execution and fixture semantics are now specific enough for
implementation and review.

### Finding 8: Scope Text Conflicted With Expanded Docs Validator Surface

Severity: Medium
Status: Fixed in plan
Finding tier: `safe_auto`

Evidence:

- The prior scope paragraph named only three docs while the implementation unit
  required six normative docs plus newly discovered active first-run docs.

Fix applied:

- The scope section now matches the docs validator contract and names the same
  normative first-contact surfaces.

Review result:

Resolved. Scope and validator obligations now align.

## Current Plan Strengths

### Bootstrap Proof Is Now Implementation-Grade

Severity: Informational
Status: Pass

Evidence:

- The plan defines the `ask-bootstrap.v1` output contract.
- The contract includes entrypoint executability, fallback command, PATH
  discovery, shim smoke, repo identity, safe chmod status, bounded subprocess
  timeouts, bounded raw excerpts, remediation, and downstream defer
  classification.

Operational impact:

Implementation can write tests from the plan without inventing a separate proof
schema.

### Fixture Coverage Targets The Actual Failure Modes

Severity: Informational
Status: Pass

Evidence:

- The plan maps CF1 through CF12 to plan units and concrete test surfaces.
- CF2, CF3, CF9, CF10, CF11, and CF12 specifically guard the most likely
  false-green paths: current checkout health, PATH assumptions, wrong global
  `ask`, unknown fallback failures, unsafe entrypoint mutation, and hanging
  probes.

Operational impact:

Closure should depend on falsifying the broken first-contact states, not on
happy-path `ask` behavior alone.

### Scope Remains Bounded To JSC-167

Severity: Informational
Status: Pass

Evidence:

- The plan excludes dependency setup, lazy loading, `ask start`, runtime
  projections, global shell mutation, and Linear mutation.
- It provides explicit defer behavior for `JSC-168` and `JSC-169` without
  implementing them.

Operational impact:

The next stage can start with PLAN-JSC167-001 without reopening milestone
selection or neighboring command-surface work.

## Residual Risks

- Implementation still needs to choose the exact helper API shape inside
  `Infrastructure/scripts/lib/ask/bootstrap.py`.
- The docs validator must avoid overmatching historical specs/plans while still
  catching active first-contact docs.
- Closeout can still report unrelated repo-surface diagnostic debt; closure
  evidence must separate that advisory debt from JSC-167 blockers.
- Source-spec CF numbering remains CF1-CF9; this plan deliberately extends the
  implementation fixture contract to CF12 after technical review.

## Handoff

```yaml
schema_version: 1
interactive_status: autonomous_assumption
selection_evidence:
  - .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
  - .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
  - .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
route: he-work
stage: he-code-review
scope: JSC-167 ask bootstrap and command discoverability plan review
traceability:
  linear_issue: JSC-167
  reviewed_artifact: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
  review_artifact: .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review.md
validation:
  required:
    - python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review.md
    - python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review.md
    - python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review.md
safe_to_continue: true
blocked_reason: null
blackboard_delta:
  current_slice: JSC-167 ready for he-work
  review_result: approved_for_he_work_after_confidence_loop
  first_unit: PLAN-JSC167-001
  closure_requires:
    - CF2 non-executable entrypoint proof
    - CF3 PATH-less fallback proof
    - CF9 wrong-shim identity proof
    - CF10 unknown fallback failure block proof
    - CF11 unsafe entrypoint no-chmod proof
    - CF12 bounded timeout proof
    - deterministic docs contract proof across normative first-contact docs
    - idempotence and no-global-mutation proof
```
