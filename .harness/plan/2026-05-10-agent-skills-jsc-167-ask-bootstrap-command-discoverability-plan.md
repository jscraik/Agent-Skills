---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan
artifact_type: he-plan
type: he-plan
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Plan
harness_stage: he-plan
status: ready_for_he_work
date: 2026-05-10
origin: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
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
he_slice: Ask Bootstrap and Command Discoverability
linear_parent_issue_title: "Harden ask bootstrap and command discoverability"
linear_labels: "Roadmap: Now, Infra, Improvement"
linear_label_status: resolved_with_existing_labels
linear_priority: 2
linear_delta_status: pass_via_spec_live_refresh_2026_05_10
plan_deepening_status: deepened_with_fixture_schema_and_review_gate_2026_05_10
confidence_loop_status: reviewed_with_redteam_and_primary_sources_2026_05_10
source_spec: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
technical_review: .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Plan

## Mode Decision

interactive_status: autonomous_assumption

This is the durable `he-plan` artifact for the approved `JSC-167` slice only.
The user invoked `$he-plan` after the JSC-167 spec and technical review were
approved, so this plan writes the execution contract and stops before code
mutation.

Selected slice:

- Linear issue: `JSC-167`
- Linear project: `agent-skills`
- Linear project ID: `791c2f12-5ffb-4644-8421-f4216ac6d805`
- Linear milestone: `Command surface and ask reliability`
- HE slice: `Ask Bootstrap and Command Discoverability`
- Source spec:
  `.harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md`
- Technical review:
  `.harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md`

The plan admits only `JSC-167`. It does not implement `JSC-168` dependency
environment setup, `JSC-169` lazy command loading, `ask start`, `ask doctor
--fix`, runtime projection sync, global shell profile mutation, or broad
command-surface cleanup.

## Stage Context

```yaml
stage_context:
  selected_stage: he-plan
  selected_slice: JSC-167 ask bootstrap and command discoverability
  slice_status: resolved
  tracker_status: resolved
  artifact_identity_status: pass
  artifact_route_status: pass
  evidence_freshness: fresh
  session_trace_status: not_applicable
  linear_delta_status: pass_via_spec_live_refresh_2026_05_10
  domain_skill_status: not_applicable
  steering_status: assumed_headless
  coding_harness_status: not_applicable
  project_brain_status: not_checked
  validation_status: pass
  blocker: null
```

## HE Gate Profile

```yaml
gate_profile:
  risk_class: agent_bootstrap_contract
  proven_risks:
    - A fresh checkout can fail before the user or agent reaches the repo
      command control plane.
    - A global or unrelated `ask` shim can exit zero and still be the wrong
      command for this checkout.
    - Bootstrap fixes can drift into shell profile mutation, dependency
      management, or lazy-loading architecture.
    - README, AGENTS guidance, and the 5-minute path can diverge from
      validation.
  required_contracts:
    - Plugins/harness-engineering/references/stage-context-contract.md
    - Plugins/harness-engineering/references/first-principles-contract.md
    - Plugins/harness-engineering/references/artifact-classification-and-traceability.md
    - Plugins/harness-engineering/skills/he-plan/references/post-plan-handoff.md
  skipped_contracts:
    - contract: Plugins/harness-engineering/references/plugin-hook-capability-contract.md
      reason: The plan does not add, alter, or depend on plugin hooks.
    - contract: Plugins/harness-engineering/references/domain-model-production-contract.md
      reason: The slice changes command bootstrap proof, not a product domain model.
    - contract: codex-security security scan
      reason: The plan admits no credential handling, auth boundary, network mutation, or dependency trust change.
  minimum_proof_required:
    continue_to_next_stage: Plan artifact identity, Linear traceability, implementation units with SA/CF mapping, validation gates, rollback, and stop rules.
    safe_to_close: CF1-CF12 fixture evidence or explicit not-encountered/deferred evidence, deterministic docs contract proof, focused tests, live bootstrap output, closeout, and no open review findings.
    block_next_stage: Missing canonical bootstrap command, manual-only docs proof, no repo-identity assertion for shim success, or implementation pressure to solve JSC-168/JSC-169.
  evidence_basis: repo+linear+harness
  downstream_route: he-work
```

## First-Principles Planning Check

```yaml
first_principles_check:
  verified_failure: The repo has a working `./bin/ask` path in this checkout, but fresh users or agents can fail before reaching it when executability or command discovery is wrong.
  fundamental_constraint: Bootstrap must make the existing repo-local command reachable without becoming a global installer, dependency manager, or command architecture refactor.
  assumption_being_challenged: More onboarding prose or a broader first-contact command is needed before fresh-checkout usability improves.
  smallest_effective_mechanism: Add one repo-local bootstrap script with machine-readable proof, wire entrypoint/discovery signals into repo doctor, add focused fixtures, and assert docs command consistency.
  analogy_or_template_rejected: Do not copy full installer, shell-profile setup, or command cockpit patterns before the repo-local bootstrap proof fails.
  proof_required: Non-executable entrypoint fixture, PATH-less fallback fixture, wrong-shim fixture, idempotence rerun, deterministic docs assertion, focused repo-doctor tests, and closeout evidence.
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-167` |
| URL | https://linear.app/jscraik/issue/JSC-167/harden-ask-bootstrap-and-command-discoverability |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Project ID | `791c2f12-5ffb-4644-8421-f4216ac6d805` |
| Milestone | `Command surface and ask reliability` |
| HE slice | `Ask Bootstrap and Command Discoverability` |
| Parent initiative | `Dev Portfolio` |
| Priority | `2` |
| Status at planning time | `Backlog` |
| Labels | `Roadmap: Now`, `Infra`, `Improvement` |
| Execution route | Agent-assisted; human review required for public command/discoverability contract changes |
| Blocked by | None known |
| Blocks | `JSC-168` |
| Related | `JSC-230`, `JSC-233` |

## Linear Delta Capture

Captured by source spec: `2026-05-10`

The approved source spec records a live Linear refresh for canonical project
`791c2f12-5ffb-4644-8421-f4216ac6d805`. This plan consumes that gate and does
not create, close, or update Linear objects.

| Object | Live state from source spec | Classification | Plan handling |
| --- | --- | --- | --- |
| `JSC-167` | Existing issue, `Backlog`, priority `High`, labels `Roadmap: Now`, `Infra`, `Improvement`, no blockers | `approved_current_slice` | Use as the only implementation parent for this plan. |
| `JSC-168` | Blocked by this work according to the source spec | `downstream_dependency_contract` | Preserve as defer route only; do not implement Python environment setup here. |
| `JSC-169` | Backlog and blocked by `JSC-168` according to the source spec | `not_admitted` | Preserve as defer route only; do not implement lazy loading here. |
| `JSC-230`, `JSC-233` | Related neighboring work | `not_admitted` | Do not expand this plan into broader command-surface work. |

## Source Evidence

| Evidence | Path or source | Planning impact |
| --- | --- | --- |
| Approved spec | `.harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md` | Defines SA1-SA12, CF1-CF9, stop rules, and handoff. |
| Technical review | `.harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md` | Approves `he-plan` after requiring repo-identity proof, JSC-168/JSC-169 defer routes, and deterministic docs proof. |
| Linear plan snapshot | `.harness/linear/agent-skills-linear-plan.md` | Records JSC-167 as the current queue item after live Linear refresh. |
| Entry wrapper | `bin/ask` | Thin repo-local wrapper whose executable bit must be characterized. |
| Python entrypoint | `Infrastructure/bin/ask` | Stable fallback target reached by `python3 bin/ask ...`. |
| Repo command implementation | `Infrastructure/scripts/lib/ask/commands/repo.py` | Existing owner for `repo status`, `repo doctor`, and closeout signal composition. |
| Repo-doctor tests | `Infrastructure/tests/test_ask_repo_doctor.py` | Existing focused test surface for doctor signals and next-command behavior. |
| Repo-status tests | `Infrastructure/tests/test_ask_repo_status_and_hub_stability.py` | Existing focused test surface for `repo_status` data shape and `repo_root_resolved`. |
| CLI behavior tests | `Infrastructure/tests/test_ask_cli.py`, `Infrastructure/tests/test_ask_helpers.py` | Existing process-level and helper-level examples for JSON envelope and command parsing tests. |
| Onboarding docs | `README.md`, `AGENTS.md`, `Docs/agents/5-minute-success-path.md` | First-run command surfaces that must agree on bootstrap and fallback. |
| Validation wrapper | `Infrastructure/scripts/validation-and-linting/verify-work.sh` | Canonical closeout validation wrapper for implementation. |
| Script path reality | `scripts` is a symlink to `Infrastructure/scripts` | Adding `scripts/bootstrap-ask.sh` writes the canonical file at `Infrastructure/scripts/bootstrap-ask.sh`; the plan must not create a second divergent script tree. |
| Python subprocess docs | https://docs.python.org/3/library/subprocess.html | Confirms `subprocess.run` supports argument arrays, `cwd`, `capture_output`, `text`, and `timeout`; bootstrap process calls must use these bounded controls. |
| Python pathlib docs | https://docs.python.org/3/library/pathlib.html | Confirms `Path.chmod`, `Path.stat`, and `Path.is_symlink`; chmod repair must first prove `bin/ask` is a regular repo-local file, not a symlink or non-file. |
| Python shutil docs | https://docs.python.org/3/library/shutil.html#shutil.which | Confirms `shutil.which` can resolve executables from a supplied `PATH`; PATH discovery must record the exact resolved path. |
| Python json docs | https://docs.python.org/3/library/json.html | Confirms `json.loads` parses JSON strings; bootstrap identity proof must parse command output structurally instead of string-matching. |
| Pytest tmp_path docs | https://docs.pytest.org/en/stable/reference.html#tmp-path | Confirms `tmp_path` provides an isolated temporary directory; chmod/PATH fixtures must run against temporary roots, not the real checkout. |
| GNU Bash set builtin docs | https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html | Confirms `errexit`, `nounset`, and `pipefail` semantics; the shell launcher must use strict mode plus explicit failure handling around expected non-zero probes. |

## Scope

In scope:

- Add `scripts/bootstrap-ask.sh` as the canonical bootstrap command.
- Add `Infrastructure/scripts/lib/ask/bootstrap.py` or an equivalent internal
  helper module for reusable bootstrap checks when the shell script needs
  shared logic.
- Make bootstrap output machine-readable with fields for executable status,
  fallback smoke, PATH discovery, shim smoke, repo identity, and remediation.
- Add repo-doctor reporting for ask entrypoint executable status and command
  discoverability.
- Add focused tests and shell fixtures that cover CF1-CF12 where applicable.
- Add deterministic docs contract validation for the bootstrap and fallback
  commands.
- Update only normative first-contact command docs where they describe first-run
  command paths: `README.md`, `AGENTS.md`,
  `Docs/agents/5-minute-success-path.md`, `Docs/agents/README.md`,
  `Docs/agents/16-agent-operating-contract.md`, `Docs/agents/04-validation.md`,
  plus any newly discovered normative first-run `ask` doc linked from the active
  instruction map.

Out of scope:

- Optional dependency lazy loading.
- Python dependency manifest redesign or install automation.
- Runtime projection sync and generated handle edits.
- Broad `./bin/ask` module cleanup.
- Cross-repo installation policy.
- Global shell profile, global bin directory, pipx, npm, uv, or Codex runtime
  mutation.
- Linear issue mutation.

## Planning Decisions

### Decision 1: Canonical Bootstrap Command Is `bash scripts/bootstrap-ask.sh`

Use `bash scripts/bootstrap-ask.sh` as the first-contact command because it is
repo-local, explicit, shell-compatible with existing repo validation patterns,
and can repair a non-executable `bin/ask` without needing `./bin/ask` to run
first.

The script must support JSON output before closure. If human-friendly output is
added, it must not replace the stable machine-readable proof surface.

### Decision 2: Bootstrap Owns First Contact; Repo Doctor Owns Persistent Drift

The bootstrap script is the first diagnostic surface because it must work before
`./bin/ask` is executable. Add ask bootstrap health as a named `repo_doctor`
signal only after bootstrap can run, so ongoing drift remains visible through
the existing repo health surface.

The doctor signal should be advisory when PATH discovery is absent but fallback
passes, and blocking when the repo-local entrypoint or fallback smoke fails.
First-contact docs and validators must route users through bootstrap before any
required `./bin/ask ...` command.

### Decision 3: PATH Shim Success Requires Repo Identity

Any `ask repo status --json` success by command name must prove it is this
checkout. Success requires both a structurally parsed command result and
proven command provenance:

- Resolve `ask` from the controlled `PATH` using `shutil.which("ask",
  path=...)` or an equivalent non-shell resolver, and record the absolute path.
- Treat the shim as this checkout only when the resolved command path is the
  repo-local `bin/ask` or an allowed repo-local wrapper target, and the parsed
  JSON response reports the expected `repo_root_resolved`.
- Do not accept exit code alone, a forged-looking JSON body alone, or a
  `command -v`/string match alone.

### Decision 4: Dependency And Optional-Import Failures Are Deferred

If fallback smoke fails because dependencies are absent, preserve command,
exit code, stdout/stderr, and classify it as a `JSC-168` defer route. If an
eager optional import breaks a minimal command, preserve the same raw evidence
and classify it as a `JSC-169` defer route. Do not fix those failures in this
slice.

Classification must be deterministic:

- `JSC-168` is allowed only for missing interpreter/package/environment
  failures that prevent the minimal fallback command from importing required
  runtime modules.
- `JSC-169` is allowed only for optional topic/module imports that are not
  required by `repo status` but are loaded eagerly before the minimal command
  can execute.
- `JSC-167` remains the classification for wrapper, path, chmod, repo-root,
  subprocess, JSON parsing, or shim-identity failures.
- `unknown_unclassified` blocks closure and must not be silently deferred.

### Decision 5: Docs Proof Must Be Executable Or Parser-Based

Manual docs review is not closure-grade proof. Add a deterministic docs
contract check, preferably a small Python validator under
`Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py`
with focused tests under `Infrastructure/scripts/testing/`.

### Decision 6: Treat `scripts/` As The Public Symlink Surface

The public command is `bash scripts/bootstrap-ask.sh`, but `scripts` is a
repository symlink to `Infrastructure/scripts`. Implementation must add the file
through the canonical infrastructure tree and verify that the public symlink path
works. Do not create a physical replacement `scripts/` directory.

### Decision 7: Keep Bootstrap Logic Importable For Tests

The shell script may be the public entrypoint, but fixture-heavy behavior should
be implemented in a small Python helper when shell tests would otherwise copy
production logic. The helper should expose pure or injectable functions for:

- entrypoint executability classification;
- fallback command execution;
- PATH command resolution;
- shim repo identity verification;
- JSON result assembly.

The shell script should remain a thin launcher around those checks, similar in
spirit to `bin/ask` delegating to `Infrastructure/bin/ask`.

### Decision 8: File Repair And Process Execution Must Be Bounded

The bootstrap slice may repair only the repo-local `bin/ask` executable bit, and
only after the helper proves the path is a regular file inside the resolved repo
root and is not a symlink. If `bin/ask` is missing, symlinked, non-regular, or
resolves outside the checkout, bootstrap must report a JSC-167 blocker with
manual remediation and must not run chmod.

All process probes must use explicit argument arrays, `cwd=<resolved repo
root>`, bounded `timeout`, `capture_output=True`, `text=True`, and no
`shell=True`. Fallback and shim output must be parsed with `json.loads`; string
matching may only be used to classify bounded error excerpts after structured
parsing fails.

## Bootstrap Proof Contract

The implementation must treat this as the minimum stable output contract for
`bash scripts/bootstrap-ask.sh --json`:

```yaml
schema_version: ask-bootstrap.v1
status: success|warning|error
repo_root: <absolute path>
checks:
  entrypoint_executable:
    status: pass|repaired|fail
    path: bin/ask
    path_type: regular_file|symlink|missing|other
    safe_to_chmod: true|false
    mode_before: <octal or null>
    mode_after: <octal or null>
    remediation: none|chmod_user_execute|manual
  fallback_command:
    status: pass|fail
    command: [python3, bin/ask, repo, status, --json]
    exit_code: <integer>
    used_shell: false
    timeout_seconds: <integer>
    stdout_json_status: success|error|null
    raw_stdout_excerpt: <short string>
    raw_stderr_excerpt: <short string>
    defer_to: null|JSC-168|JSC-169
  path_discovery:
    status: pass|warn|fail
    command: ask
    resolution_method: shutil.which|equivalent
    resolved_path: <absolute path or null>
  shim_smoke:
    status: pass|fail|skipped
    command: [ask, repo, status, --json]
    exit_code: <integer or null>
    used_shell: false
    timeout_seconds: <integer or null>
    repo_identity_status: pass|fail|skipped
    observed_repo_root: <absolute path or null>
remediation:
  applied:
    - chmod_bin_ask
  manual:
    - use_python_fallback
```

Rules:

- `status: success` requires entrypoint executable and fallback command pass.
- `entrypoint_executable.status: repaired` is allowed only when `path_type:
  regular_file`, `safe_to_chmod: true`, and both before/after modes are recorded.
- PATH discovery absence may produce `status: warning` only when the fallback
  command passes and docs name the fallback.
- Shim smoke may pass only when resolved-path provenance and parsed
  `repo_root_resolved` both match the expected checkout.
- `defer_to` may be `JSC-168` or `JSC-169` only when the classification
  predicates in Decision 4 match; otherwise use `unknown_unclassified` and block
  closure.
- Subprocess timeouts are JSC-167 blockers unless deterministic evidence maps
  them to an existing downstream issue.
- `raw_stdout_excerpt` and `raw_stderr_excerpt` must be bounded so a failed
  dependency import does not flood agent context.
- The JSON contract should be asserted by snapshot or schema-like tests before
  docs are updated to depend on it.

## Fixture Matrix

| Fixture | Plan unit | Test surface | Required assertion |
| --- | --- | --- | --- |
| CF1 executable happy path | PLAN-JSC167-001 | `test_ask_bootstrap.py` plus live `bash scripts/bootstrap-ask.sh --json` | `entrypoint_executable.status == pass` and fallback command passes. |
| CF2 non-executable entrypoint | PLAN-JSC167-002 | Temporary fixture root copied from minimal wrapper files | Bootstrap repairs repo-local `bin/ask` or returns exact manual remediation; no real checkout chmod. |
| CF3 PATH-less shell | PLAN-JSC167-002 | Subprocess with controlled `PATH` | PATH discovery warns/fails and fallback command is present. |
| CF4 correct shim | PLAN-JSC167-002 | Temporary PATH shim pointing at this checkout | Shim smoke passes and repo identity matches current repo root. |
| CF5 dependency failure | PLAN-JSC167-003 | Mocked subprocess result or fixture command | Raw failure excerpt is preserved and `defer_to == JSC-168`; no dependency install is attempted. |
| CF6 optional import failure | PLAN-JSC167-003 | Mocked subprocess result or fixture command | Raw failure excerpt is preserved and `defer_to == JSC-169`; no lazy-loading implementation is attempted. |
| CF7 docs drift | PLAN-JSC167-004 | Docs validator fixture with mismatched command text | Validator fails and names the mismatched file and command. |
| CF8 idempotence rerun | PLAN-JSC167-005 | Two live bootstrap runs | Second run reports no additional mutation beyond stable pass state. |
| CF9 wrong global shim | PLAN-JSC167-002 | Temporary earlier `ask` command returning another repo root | Shim smoke fails or warns despite exit code zero. |
| CF10 unknown fallback failure | PLAN-JSC167-003 | Mocked subprocess result with no recognized dependency/import signature | Bootstrap reports `unknown_unclassified` and closure remains blocked. |
| CF11 unsafe entrypoint path | PLAN-JSC167-002 | Temporary fixture root with symlinked or non-regular `bin/ask` | Bootstrap refuses chmod, reports `safe_to_chmod == false`, and emits manual remediation. |
| CF12 hanging fallback or shim | PLAN-JSC167-003 | Mocked or fixture command that exceeds the configured timeout | Bootstrap records a bounded timeout failure and blocks closure as JSC-167 unless explicitly classified otherwise. |

## Implementation Units

### PLAN-JSC167-001 - Add Canonical Bootstrap Command

Linear mapping:

- Parent: `JSC-167`
- Acceptance: SA1, SA3, SA11
- Fixtures: CF1

Files:

- Add `Infrastructure/scripts/bootstrap-ask.sh`, reached publicly as
  `scripts/bootstrap-ask.sh` through the existing symlink.
- Add `Infrastructure/scripts/lib/ask/bootstrap.py` for importable check logic
  and JSON result assembly.
- Add `Infrastructure/scripts/testing/test_ask_bootstrap.py`.

Implementation:

- Resolve repo root from the script location, not the caller's current working
  directory.
- Check `bin/ask` existence and executable status.
- If `bin/ask` exists but is not executable, run chmod only after verifying it is
  a regular file, is not a symlink, and resolves inside the repo root; otherwise
  report `safe_to_chmod: false` and manual remediation.
- Run `python3 bin/ask repo status --json` as the fallback smoke using an
  argument-array subprocess call with `cwd`, `timeout`, `capture_output=True`,
  `text=True`, and no shell.
- Parse fallback and shim JSON with `json.loads`; do not rely on substring
  checks for success or identity.
- Support `--json`; optionally support human output, but JSON is the closure
  proof path.
- Emit the "Bootstrap Proof Contract" fields above.
- Preserve raw command failure data when fallback smoke fails.
- Use bounded output excerpts for subprocess failures.
- Keep the script free of shell-profile sourcing and global installer behavior.
- Ensure `bash scripts/bootstrap-ask.sh --json` is runnable before any required
  `./bin/ask ...` validation command in the first-contact sequence.

Validation:

```bash
bash scripts/bootstrap-ask.sh --json
test -x bin/ask
python3 bin/ask repo status --json
python3 -m pytest Infrastructure/scripts/testing/test_ask_bootstrap.py -q
```

Rollback:

- Remove `scripts/bootstrap-ask.sh`, the bootstrap helper if added, and focused
  tests. No runtime projection cleanup should be required.

Stop conditions:

- The script needs to source shell profiles, edit shell profiles, or install a
  global command to pass.
- The script cannot run before `./bin/ask` is executable.

### PLAN-JSC167-002 - Add Negative Fixture Coverage For Executability And Discovery

Linear mapping:

- Parent: `JSC-167`
- Acceptance: SA2, SA4, SA9, SA11
- Fixtures: CF2, CF3, CF4, CF9, CF11

Files:

- `Infrastructure/scripts/testing/test_ask_bootstrap.py`
- Optional shell fixture helpers under `Infrastructure/scripts/testing/fixtures/`
  only if they reduce unsafe chmod/PATH manipulation.

Implementation:

- Use temporary fixture roots for non-executable `bin/ask` rather than mutating
  the real checkout.
- Test PATH-less shells by controlling `PATH` in subprocess environment.
  Preserve enough interpreter/core utility access for the fixture to execute; the
  failure under test is absence of `ask` on PATH, not absence of Python or Bash.
- Test wrong global shim by creating a temporary earlier `ask` command on
  `PATH` that returns a successful-looking response for another repo.
- Test unsafe `bin/ask` repair with symlinked and non-regular entrypoint
  fixtures, and assert bootstrap does not chmod them.
- Assert wrong-shim cases warn or fail even when exit code is zero.
- Assert repo identity requires both resolved-path provenance and parsed
  `repo_root_resolved` evidence.
- Assert the public symlink path and canonical infrastructure path refer to the
  same script, rather than testing a duplicate script.

Validation:

```bash
python3 -m pytest Infrastructure/scripts/testing/test_ask_bootstrap.py -q
bash scripts/bootstrap-ask.sh --json
```

Rollback:

- Remove fixture tests and any temporary fixture helper files.

Stop conditions:

- Fixture design requires chmod or PATH mutation on the real checkout.
- Shim success cannot be tied to the current checkout.

### PLAN-JSC167-003 - Wire Ask Bootstrap Signals Into Repo Doctor

Linear mapping:

- Parent: `JSC-167`
- Acceptance: SA5, SA10, SA11
- Fixtures: CF5, CF6, CF10, CF12

Files:

- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`
- `Infrastructure/tests/test_ask_repo_status_and_hub_stability.py` only if
  `repo_status` data shape changes

Implementation:

- Add a focused doctor signal such as `ask_bootstrap`.
- Include entrypoint executable status and PATH discoverability details.
- Keep `repo_status` stable unless `repo_root_resolved` must be exposed through
  an additional helper for repo identity checks.
- Make fallback success the blocking threshold: missing PATH discovery is an
  advisory when fallback passes, but entrypoint/fallback failure blocks.
- Preserve raw dependency or optional-import failures and classify them as
  `JSC-168` or `JSC-169` defer routes without implementing fixes.
- Add an `unknown_unclassified` fallback-failure classification that blocks
  closure and points back to JSC-167 investigation.
- Add timeout handling for fallback and shim probes; timeout evidence must be
  bounded and must block closure unless a deterministic downstream classification
  exists.
- Add `ask_bootstrap` to `DOCTOR_SIGNAL_PRIORITY` only if doing so preserves the
  existing normal/advisory next-command behavior for unrelated repo-surface
  diagnostic debt.
- Update closeout expectations only when the new signal is blocking; do not let
  a PATH-only advisory block commit readiness.
- Do not rely on repo doctor as the only proof that a broken-entrypoint checkout
  can recover; repo doctor is post-bootstrap drift evidence.

Validation:

```bash
python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py Infrastructure/tests/test_ask_repo_status_and_hub_stability.py -q
./bin/ask repo doctor --json --robot
./bin/ask repo closeout --changed --json --robot
```

Rollback:

- Remove the `ask_bootstrap` signal and focused tests. Keep unrelated doctor
  signal behavior unchanged.

Stop conditions:

- Repo doctor changes require broad golden-path or command catalog redesign.
- JSC-168/JSC-169 handling becomes active repair work instead of classification.

### PLAN-JSC167-004 - Add Deterministic Docs Contract And Align First-Run Docs

Linear mapping:

- Parent: `JSC-167`
- Acceptance: SA1, SA6
- Fixtures: CF7

Files:

- `README.md`
- `AGENTS.md`
- `Docs/agents/5-minute-success-path.md`
- `Docs/agents/README.md`
- `Docs/agents/16-agent-operating-contract.md`
- `Docs/agents/04-validation.md`
- Add `Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py`
- Add `Infrastructure/scripts/testing/test_verify_ask_bootstrap_docs.py`

Implementation:

- Update first-run docs to name `bash scripts/bootstrap-ask.sh` before
  `./bin/ask repo doctor --json --robot`.
- Ensure docs name `python3 bin/ask repo status --json` as the fallback before
  any optional global `ask` discovery.
- Write a deterministic validator that asserts the same bootstrap and fallback
  commands appear in every normative first-contact surface named above.
- The validator should check command order where relevant: bootstrap first,
  fallback before optional PATH/global `ask` discovery, then normal
  `./bin/ask repo doctor --json --robot`.
- The validator should emit machine-readable JSON when passed `--json`, but a
  plain pass/fail CLI result is sufficient for local closure.
- If implementation discovers another doc that presents a first-run `ask`
  command as normative, add it to the validator input instead of leaving it to
  manual review. Historical specs and dated plans may mention older commands as
  evidence, but they must not be edited or treated as current first-contact
  authority unless they are linked from the active instruction map.
- Keep docs changes minimal; do not rewrite unrelated guidance.

Validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py
python3 Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py --json
python3 -m pytest Infrastructure/scripts/testing/test_verify_ask_bootstrap_docs.py -q
```

Rollback:

- Revert the docs edits and remove the focused docs validator/test.

Stop conditions:

- Docs require a different first command than validation.
- Closure proof depends on manual read-through instead of the validator.

### PLAN-JSC167-005 - Prove Idempotence, No Global Mutation, And Closeout Readiness

Linear mapping:

- Parent: `JSC-167`
- Acceptance: SA7, SA8, SA10, SA12
- Fixtures: CF8

Files:

- `.harness/evals/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md`
- Any test file touched by previous units

Implementation:

- Run bootstrap twice and record that the second run performs no unsafe extra
  mutation.
- Inspect changed paths and confirm no shell profile, global bin, runtime
  projection, or generated command handle was changed.
- Record CF5/CF6 as not encountered or deferred with raw evidence, as
  applicable.
- Record CF10 as not encountered, or block closure with raw evidence and the
  smallest JSC-167 investigation step.
- Record CF11 and CF12 as tested; unsafe path repair and timeout behavior cannot
  be inferred from happy-path bootstrap output.
- Write the eval/closure artifact only after implementation proof exists.

Validation:

```bash
bash scripts/bootstrap-ask.sh --json
bash scripts/bootstrap-ask.sh --json
python3 bin/ask repo status --json
./bin/ask repo status --json --robot
./bin/ask repo doctor --json --robot
python3 Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py
python3 -m pytest Infrastructure/scripts/testing/test_ask_bootstrap.py Infrastructure/scripts/testing/test_verify_ask_bootstrap_docs.py Infrastructure/tests/test_ask_repo_doctor.py Infrastructure/tests/test_ask_repo_status_and_hub_stability.py -q
bash Infrastructure/scripts/validation-and-linting/verify-work.sh --fast
./bin/ask repo closeout --changed --json --robot
git diff --check -- <changed-files>
```

Rollback:

- Remove the bootstrap script, focused validators/tests, repo-doctor signal
  changes, docs edits, and eval artifact as one bounded change set.

Stop conditions:

- Any changed path lands under `.agents/skills/`, `.skillsets/`, global shell
  files, or runtime projection output without a separate approved sync reason.
- Closeout cannot distinguish a real blocker from unrelated diagnostic debt.

## Acceptance Traceability

| Acceptance ID | Plan units | Closure evidence |
| --- | --- | --- |
| SA1 | PLAN-JSC167-001, PLAN-JSC167-004 | Bootstrap script exists; docs validator proves first-run docs use it. |
| SA2 | PLAN-JSC167-002 | CF2 temporary-root non-executable fixture passes; CF11 proves unsafe entrypoints are not chmodded. |
| SA3 | PLAN-JSC167-001, PLAN-JSC167-005 | `python3 bin/ask repo status --json` passes after bootstrap. |
| SA4 | PLAN-JSC167-002, PLAN-JSC167-003 | PATH/shim smoke requires resolved-path provenance and parsed `repo_root_resolved` identity proof. |
| SA5 | PLAN-JSC167-003 | Repo doctor reports entrypoint and discovery state. |
| SA6 | PLAN-JSC167-004 | Docs validator passes; manual review alone is insufficient. |
| SA7 | PLAN-JSC167-005 | Bootstrap rerun is idempotent. |
| SA8 | PLAN-JSC167-003, PLAN-JSC167-005 | Scope review confirms JSC-168/JSC-169/ask-start remain excluded. |
| SA9 | PLAN-JSC167-002 | CF2 and CF3 proof artifacts or explicit blockers exist. |
| SA10 | PLAN-JSC167-003, PLAN-JSC167-005 | Dependency/optional-import failures are not encountered or are deferred with raw evidence; unknown fallback failures and probe timeouts block closure. |
| SA11 | PLAN-JSC167-001, PLAN-JSC167-002, PLAN-JSC167-003 | JSON/schema or snapshot assertion covers executable, fallback, discovery, shim, identity, and remediation fields. |
| SA12 | PLAN-JSC167-005 | Diff/path review and idempotence evidence prove no silent global mutation. |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| `JSC-167` | SA1-SA12 | PLAN-JSC167-001 through PLAN-JSC167-005 | SA1-SA12 | Not available yet; implementation has not started. |

## Validation Gates

Plan-artifact validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
git diff --check -- .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
```

Implementation validation is listed per unit and consolidated in
PLAN-JSC167-005. Stop on the first failed required gate and record the blocker
in the eval artifact before attempting broader repairs.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Bootstrap becomes a hidden global installer | Script may only mutate repo-local regular-file `bin/ask` executability after symlink/non-file checks; global/PATH setup must be manual or separately approved. |
| Wrong global `ask` passes smoke | Require both resolved-path provenance and parsed `repo_root_resolved` identity proof for shim success. |
| Symlinked or non-regular `bin/ask` gets chmodded | Treat unsafe entrypoint paths as JSC-167 blockers with manual remediation; CF11 must prove no chmod occurs. |
| Fallback or shim probe hangs | Use bounded subprocess timeouts and classify unresolved timeouts as JSC-167 blockers; CF12 must prove bounded failure output. |
| Dependency setup sneaks into the slice | Preserve raw failure and defer to `JSC-168`. |
| Lazy-loading work sneaks into the slice | Preserve raw failure and defer to `JSC-169`. |
| Docs drift returns | Add parser/executable docs validation and include it in closure. |
| Current dirty worktree hides path ownership drift | Validate only touched JSC-167 files and explicitly inspect changed paths before closure. |
| First-contact guidance invokes `./bin/ask` before bootstrap | Docs validator enforces bootstrap-before-doctor ordering on normative first-contact docs. |
| Unknown fallback failure gets mislabeled as downstream work | `unknown_unclassified` blocks closure until JSC-167 ownership is resolved. |

## Out-Of-Scope Watchlist

- `JSC-168`: reproducible Python dependency/environment setup.
- `JSC-169`: lazy command import dependencies by topic.
- `JSC-174`: `ask start` or first-contact command cockpit.
- `JSC-246`: broader agent-first golden path.
- Runtime projections under `.agents/**` and `.skillsets/**`.
- Cross-repo bootstrap policy.

## Post-Plan Handoff

```yaml
post_plan_handoff:
  state: explicit_stop
  selected_next_stage: he-work
  evidence: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
  next_action: Invoke he-work only after the user authorizes implementation; start with PLAN-JSC167-001.
```

## Blackboard Delta

```yaml
schema_version: 1
interactive_status: autonomous_assumption
selection_evidence:
  - .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
  - .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
  - .harness/linear/agent-skills-linear-plan.md
route: he-work
stage: he-plan
scope: JSC-167 ask bootstrap and command discoverability
traceability:
  linear_issue: JSC-167
  linear_milestone: Command surface and ask reliability
  spec_artifact: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
  plan_artifact: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
  review_artifact: .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec-technical-review.md
validation:
  required_before_work:
    - python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
    - python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
    - python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
safe_to_continue: true
blocked_reason: null
blackboard_delta:
  current_slice: JSC-167 ready for he-work
  first_unit: PLAN-JSC167-001
  deferred:
    - JSC-168
    - JSC-169
    - JSC-174
    - JSC-246
```
