---
schema_version: 1
plan_id: JSC-246-GP-20260506
title: "feat: Agent-First Golden Path Product Compression Plan"
type: feat
status: active
date: 2026-05-06
origin: Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md
spec: Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md
source_spec: Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md
parent_spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
parent_plan: Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md
linear_project: agent-skills
linear_issue: JSC-246
linear_parent: none
linear_children: []
linear_status: Open
linear_comment_required: true
branch: feature/jscraik-agent-first-golden-path-spec-plan
pr: https://github.com/jscraik/Agent-Skills/pull/152
traceability_required: true
plan_route: child
plan_depth: deep
---

# feat: Agent-First Golden Path Product Compression Plan

## Table of Contents

- [Overview](#overview)
- [Planning Status](#planning-status)
- [Linear Work Item Contract](#linear-work-item-contract)
- [Linear / Spec / Plan / PR Traceability](#linear--spec--plan--pr-traceability)
- [Requirements Trace](#requirements-trace)
- [Coding Harness Gate Status](#coding-harness-gate-status)
- [Current Repo Evidence](#current-repo-evidence)
- [Scope Boundaries](#scope-boundaries)
- [Key Decisions](#key-decisions)
- [Task Graph](#task-graph)
- [Implementation Units](#implementation-units)
- [First-Slice Technical Design](#first-slice-technical-design)
- [Acceptance and Traceability](#acceptance-and-traceability)
- [Validation Plan](#validation-plan)
- [Rollback Plan](#rollback-plan)
- [Follow-On Work](#follow-on-work)
- [Technical Review](#technical-review)
- [Risks and Blockers](#risks-and-blockers)
- [Sources and References](#sources-and-references)
- [Next Stage Handoff](#next-stage-handoff)

## Overview

Implement the first executable slice of the agent-first golden path for
JSC-246. This plan converts the product-compression spec into an implementation
contract that makes Agent Skills Kit easier for AI coding agents to use without
weakening the existing control plane.

The first slice is intentionally narrow:

- add `ask repo doctor` as the agent-facing health entrypoint;
- compose existing repo status, catalog parity, runtime budget, handle, and
  surface signals;
- return a compact golden-path envelope with `agent_summary`, `blocking`,
  `blockers`, `next_command`, and `signals`;
- add focused tests and documentation for this first command;
- leave `ask skills improve`, `ask skills explain`, `ask skills prove`,
  `ask repo closeout --changed`, and cross-project analytics wiring as
  follow-on work.

This keeps the next implementation PR useful on its own: a cold agent can ask
the repo whether it is safe to work and receive one evidence-backed next action.

## Planning Status

Plan status: `active`.

The implementation shape is ready once the prerequisite repository-health repair
set is present on the implementation branch. In the current working tree those
repairs are staged as sibling changes, not contained in this spec/plan artifact:

- catalog parity now resolves across README, root `SKILL.md`,
  `ask skills list`, and route considered metadata after the README count repair
  is included;
- the coding-harness plan gate now passes with no findings after assigning
  stable `plan_id` frontmatter to historical plans and making the repo wrapper
  apply a long-lived default max age for plan artifacts.

Do not treat this plan artifact alone as the baseline repair commit. Before
implementation handoff, either commit the sibling repair files
(`README.md`, `Infrastructure/scripts/harness-cli.sh`, and the historical
`Docs/plans/*.md` frontmatter updates) or re-run the gates and mark this plan
blocked if those repairs are absent.

This plan includes its own `plan_id` and traceability fields.

## Linear Work Item Contract

- Linear issue: `JSC-246`
- URL: `https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden`
- Project: `agent-skills`
- Team: `Jscraik`
- Priority: High
- Labels: `Roadmap: Next`, `Agent`, `Infra`, `Improvement`
- Current status: Open
- Branch: `feature/jscraik-agent-first-golden-path-spec-plan`
- PR: https://github.com/jscraik/Agent-Skills/pull/152 (draft)
- Linear comment required: true

Implementation should add a Linear workpad comment before code changes start,
linking the spec, this plan, and the intended first-slice scope.

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs          | Plan units                     | Acceptance IDs                    | PR evidence |
| ------------ | ------------------------------ | ------------------------------ | --------------------------------- | ----------- |
| JSC-246      | R1, R2, R3, R4, R5, R6, R7, R8 | P0, P1, P2, P3, P4, P5, P6     | AC1, AC2, AC3, AC4, AC5, AC6, AC7 | https://github.com/jscraik/Agent-Skills/pull/152 (draft) |
| JSC-246      | R9, R10, R11, R12              | F1, F2, F3, F4, F5, F6, F7, F8 | deferred follow-on acceptance     | https://github.com/jscraik/Agent-Skills/pull/152 (draft) |

## Requirements Trace

| Requirement                                                                                                  | Source                                                                    | Plan unit  | First-slice status |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | ---------- | ------------------ |
| R1. Give agents one repo health entrypoint.                                                                  | Product-compression spec goals                                            | P2, P3     | in scope           |
| R2. Preserve detailed diagnostics while adding a compact agent summary.                                      | Product-compression spec goals                                            | P1, P3     | in scope           |
| R3. Compose catalog parity, runtime budget, handle health, and repo surface signals.                         | Product-compression spec current-state baseline                           | P3         | in scope           |
| R4. Return exactly one primary next command.                                                                 | Product-compression spec problem statement                                | P1, P3     | in scope           |
| R5. Keep namespace-first command design.                                                                     | Product-compression spec goals                                            | P2         | in scope           |
| R6. Avoid weakening validation, path ownership, and projection rules.                                        | Product-compression spec invariants                                       | P3, P6     | in scope           |
| R7. Add tests for the new command contract.                                                                  | Product-compression spec acceptance matrix                                | P4         | in scope           |
| R8. Add concise docs for the new golden-path entrypoint.                                                     | Product-compression spec definition of done                               | P5         | in scope           |
| R9. Use expanded Codex skill analytics as future proof evidence.                                             | Product-compression spec analytics pipeline                               | F3, F4, F5 | deferred           |
| R10. Include agent-skills, session-collector, and otel-collector in the full feature arc.                    | Product-compression spec companion collector surfaces                     | F3, F4, F5 | deferred           |
| R11. Extend the existing session-collector bundle rather than creating a parallel ASK-only collector output. | Product-compression spec collector-backed baseline and evidence contracts | F5         | deferred           |
| R12. Remove unsupported default roots from this feature's collector source path.                             | Product-compression spec session collector layer and SA20                 | F5         | deferred           |

## Coding Harness Gate Status

```yaml
coding_harness:
  mode: coding-harness-managed
  linear_state: S0_TRIAGE
  blocked_overlay: false
  transition_event: passed
  transition_command: "./Infrastructure/scripts/harness-cli.sh plan-gate --require-plan-id --require-traceability --json -> pass"
  project_brain_status: not_checked
  north_star_evidence_status: not_checked
  harness_commands_run:
    - "./Infrastructure/scripts/harness-cli.sh plan-gate --require-plan-id --require-traceability --json -> pass"
  harness_commands_blocked: []
```

The next implementation run can start from a passing plan-gate baseline only
after the prerequisite baseline repair set described above is present in the
branch under implementation.

## Current Repo Evidence

Command evidence gathered before this plan:

- `./bin/ask repo status --json` passed and reported `skills_synced: true`.
- `./bin/ask skills --help` passed and showed the current `skills` namespace
  includes `proof`; it does not yet include `prove`, `improve`, or `explain`.
- `./bin/ask repo doctor-catalog --json --robot` passes with
  `decision_status: resolved`; canonical count is `21`, README observed count
  is `21`, and all required surfaces report parity.
- `./Infrastructure/scripts/harness-cli.sh --help` passed and confirmed the
  `plan-gate` command exists.
- `./Infrastructure/scripts/harness-cli.sh plan-gate --require-plan-id --require-traceability --json`
  passes with zero findings.
- `rg` evidence from `Infrastructure/bin/ask` shows current `repo` subcommands
  include `status`, `validate`, `check-stability`, `doctor-catalog`,
  `provider-audit`, and `surface`; there is no `repo doctor` route yet.
- `fd` evidence shows existing tests for `repo doctor-catalog`, `repo surface`,
  `repo status`, and the `ask` CLI, but no dedicated `repo doctor` test yet.
- `$HOME/.agents/session-collector` is the collector code project;
  its raw telemetry input root is
  `$HOME/.agents/otel-collector/data/raw`.
- A narrowed session-collector run using OTel raw files and
  `$HOME/.codex/sessions` wrote
  `/tmp/ask-session-collector-spec-evidence.json` and
  `/tmp/ask-session-collector-spec-bundle`.
- That collector run kept `391942` records across `596` source files:
  `391759` Codex rollout lines and `183` OTel log lines.
- Current collector output already includes bundle files consumed by downstream
  workflows: `aggregate.json`, `index.json`, `skillify-candidates.json`,
  `skill-refactor-evidence.json`, `harness-engineering-evidence.json`,
  `insight-evidence-extension.json`, `solved-problems.json`,
  `redaction-report.json`, and `manifest.json`.
- Current collector skill evidence is mention-derived, not native
  `skill_invocation` analytics. The sampled run reported `simplify: 140`,
  `skill-refactor: 2`, and `harness-engineering: 3287`.

## Scope Boundaries

In scope for the first implementation:

- `Infrastructure/bin/ask` parser and dispatch updates for `repo doctor`;
- `Infrastructure/scripts/lib/ask/**` helper code for the golden-path envelope;
- `Infrastructure/scripts/lib/ask/commands/repo.py` doctor composition logic;
- focused tests under `Infrastructure/tests/**`;
- concise docs that introduce `ask repo doctor` as the first agent command;
- focused command metadata or help text needed to expose `repo doctor`.

Out of scope for the first implementation:

- deleting historical repo-surface artifacts;
- changing generated skill projections;
- changing current `ask skills proof` behavior;
- implementing `ask skills improve`, `ask skills explain`, `ask skills prove`,
  or `ask repo closeout --changed`;
- modifying `$HOME/.agents/session-collector`;
- modifying `$HOME/.agents/otel-collector`;
- ingesting or storing high-cardinality per-turn analytics in Agent Skills Kit.

## Key Decisions

### D1: Start With `ask repo doctor`

`ask repo doctor` is the smallest useful golden-path command because it answers
the first question every coding agent has before touching the repo:

```text
Can I work safely, and what should I do next?
```

This command can be implemented by composing existing repo signals. It does not
require new skill semantics or collector ingestion.

### D2: Add A Shared Golden-Path Envelope

The first command should establish a reusable response shape:

```json
{
  "agent_summary": "Usable, but blocked by catalog parity drift.",
  "blocking": true,
  "blockers": [
    {
      "id": "catalog_parity",
      "severity": "blocker",
      "summary": "Canonical skill count is 21 but README reports 20.",
      "next_command": "./bin/ask repo doctor-catalog --json --robot"
    }
  ],
  "next_command": "./bin/ask repo doctor-catalog --json --robot",
  "signals": {},
  "diagnostic_debt": []
}
```

Existing `--json` and `--robot` wrappers should continue to use the repo's
standard result envelope. The golden-path fields should live inside the command
payload rather than replacing lower-level diagnostics.

### D3: Compose Existing Helpers, Do Not Shell Out

The implementation should call existing Python helpers or command functions
where possible. It should not invoke `./bin/ask` subprocesses and parse their
stdout from inside the `ask` implementation.

If a lower-level command currently only exposes CLI-oriented behavior, extract a
small pure helper before composing it into doctor.

### D4: Keep Current `skills proof` Stable

The current CLI already has `ask skills proof`. The spec's desired
`ask skills prove` command should be handled in a later compatibility unit.
The first slice must not rename, remove, or silently change the existing
`proof` command.

### D5: Preserve Catalog Parity As A First-Class Blocker

Catalog parity drift has been repaired in the current tree, but it remains the
first-class drift condition that blocks broad goal routing. The new doctor
command should surface any future catalog parity drift as a blocker with one
clear next command.

Implementation may fix catalog parity before adding doctor, but the doctor tests
should still include a fixture that proves catalog parity drift is presented as
a blocking signal.

### D6: Treat Runtime Budget Differently In Default And Strict Modes

Runtime budget over advisory threshold should be a warning by default and a
blocker in strict mode, unless the lower-level runtime budget check already
reports policy violations.

The command should support a strict flag only if it matches existing `ask`
style. If no shared strict pattern exists, strict behavior can be deferred.

## Task Graph

```text
P0 -> P1 -> P2 -> P3 -> P4 -> P5 -> P6
```

- P0 confirms the repaired baseline.
- P1 creates the response contract.
- P2 exposes the command route.
- P3 composes repo signals.
- P4 proves the behavior with tests.
- P5 documents the new entrypoint.
- P6 runs validation and writes handoff evidence.

Follow-on units F1-F8 depend on P6 unless explicitly split into separate
tracked implementation work.

## Implementation Units

### P0: Handoff Cleanup And Baseline Confirmation

Owner: implementation agent.

Actions:

- Confirm current branch and uncommitted files.
- Confirm new spec and plan files are reported under canonical `Docs/**` paths
  by using exact uppercase pathspecs.
- Rerun `./bin/ask repo doctor-catalog --json --robot`.
- Preserve a catalog parity drift fixture even though the live README/catalog
  drift has been repaired.
- Add a Linear workpad comment linking JSC-246, the product-compression spec,
  and this plan.

Exit criteria:

- implementation branch is known;
- unrelated dirty files are identified and left untouched;
- catalog parity pass state is recorded with exact command output;
- Linear has a workpad note or the lack of Linear write access is recorded.

### P1: Shared Golden-Path Envelope

Owner: `Infrastructure/scripts/lib/ask/**`.

Actions:

- Add a small helper for agent-facing command summaries.
- Keep fields stable: `agent_summary`, `blocking`, `blockers`,
  `next_command`, `signals`, `diagnostic_debt`.
- Make blockers deterministic and sorted by severity, then stable ID.
- Use the state vocabulary from the spec: `pass`, `warn`, `block`, `error`,
  `unknown`, and `skipped` for `signals.<name>.state`.
- Require `blocking: true` to include at least one `severity: blocker` entry.
- Return exactly one primary `next_command`; put alternates in
  `metadata.next_steps` or signal-specific detail.
- Support concise human output and full JSON output through existing result
  conventions.

Exit criteria:

- helper is unit-testable without command-line parsing;
- at least one test covers blocker ordering and primary next-command selection.

### P2: `ask repo doctor` Parser And Dispatch

Owner: `Infrastructure/bin/ask`.

Actions:

- Add `doctor` to the `repo` subparser.
- Wire dispatch to a `repo_doctor` implementation.
- Preserve current `doctor-catalog`, `surface`, `status`, and `validate`
  behavior.
- Update help text so `repo doctor` reads as the agent health entrypoint.

Exit criteria:

- `./bin/ask repo doctor --help` works;
- invalid command correction behavior remains unchanged for nearby commands.

### P3: Doctor Signal Composition

Owner: `Infrastructure/scripts/lib/ask/commands/repo.py` and extracted helpers.

Actions:

- Compose these signals:
  - repo status and sync state;
  - catalog parity via the same logic as `doctor-catalog`;
  - runtime budget health;
  - generated command handle health;
  - repo surface status and diagnostic debt.
- Extract pure helper functions for any signal that currently exists only as a
  CLI-oriented command path; do not call `./bin/ask` from inside `ask`.
- Map signals into blocker, warning, or informational classes.
- Pick one primary `next_command`.
- Include enough signal detail for robot callers to act without reading lower
  level reports first.

Default severity rules:

- catalog parity drift: blocker;
- unresolved handle collision or handle check failure: blocker;
- runtime budget policy violation: blocker;
- runtime budget advisory threshold only: warning;
- repo surface warning: warning unless strict mode is implemented and enabled;
- repo status failure: blocker;
- synced skills: informational pass.

Exit criteria:

- current live repo returns a compact summary;
- catalog parity drift, if still present, is the primary blocker;
- surface debt is present as diagnostic debt rather than hiding the catalog
  blocker.
- each signal includes `state`, `summary`, `source`, and, when actionable,
  `next_command`.

### P4: Focused Tests And Fixtures

Owner: `Infrastructure/tests/**`.

Actions:

- Add tests for:
  - parser route exists;
  - JSON payload includes golden-path fields;
  - catalog parity drift blocks and selects the catalog doctor next command;
  - non-blocking surface warning appears as diagnostic debt;
  - all-pass fixture returns `blocking: false` and selects the existing
    `./bin/ask repo status --json --robot` inspection command as
    `next_command` until `skills improve` or `repo closeout --changed` exists;
  - help output includes `repo doctor`.
- Reuse existing fixture style from `test_ask_repo_doctor_catalog.py` and
  `test_ask_repo_surface.py`.

Exit criteria:

- focused tests pass locally;
- no unrelated broad fixture churn.

### P5: Minimal Docs Front Door

Owner: README and focused docs only.

Actions:

- Add a concise golden-path snippet:

```bash
./bin/ask repo doctor --json --robot
./bin/ask repo doctor-catalog --json --robot
./bin/ask repo surface --json --robot
```

- Avoid broad README rewrite in this first PR.
- Link to the spec and this plan from any implementation note.

Exit criteria:

- docs describe `repo doctor` as the first agent command;
- docs do not claim `skills improve`, `skills explain`, `skills prove`, or
  `repo closeout --changed` are implemented until they exist.

### P6: Validation And Handoff

Owner: implementation agent.

Actions:

- Run focused tests for the new command.
- Run the repo's relevant validation wrapper.
- Rerun harness plan-gate and record the pass/fail state.
- Capture exact command outcomes in the final handoff and Linear workpad.

Exit criteria:

- new command behavior is validated or blockers are explicit;
- no new plan-gate issue is introduced by this plan;
- final handoff records pass, fail, and blocked results with exact commands.

## First-Slice Technical Design

### Command Shape

```bash
./bin/ask repo doctor
./bin/ask repo doctor --json
./bin/ask repo doctor --json --robot
```

Optional flags may include `--strict` only if the existing parser has a
compatible pattern.

### JSON Payload

The command payload should use the existing `ask` result envelope and include a
doctor object shaped like this:

```json
{
  "repo_doctor": {
    "agent_summary": "Usable, but blocked by catalog parity drift.",
    "blocking": true,
    "blockers": [
      {
        "id": "catalog_parity",
        "severity": "blocker",
        "summary": "Canonical skill count is 21 but README reports 20.",
        "next_command": "./bin/ask repo doctor-catalog --json --robot",
        "source": "repo.doctor_catalog"
      }
    ],
    "next_command": "./bin/ask repo doctor-catalog --json --robot",
    "signals": {
      "repo_status": { "state": "pass" },
      "catalog_parity": { "state": "block" },
      "runtime_budget": { "state": "warn" },
      "handles": { "state": "pass" },
      "surface": { "state": "warn" }
    },
    "diagnostic_debt": [
      {
        "id": "repo_surface_findings",
        "severity": "warning",
        "summary": "Repo surface inventory has historical blocking findings."
      }
    ]
  }
}
```

Exact nesting can adapt to existing command conventions, but the field names
above are the first-slice contract.

### Human Output

Human output should prefer compact action language:

```text
Repo doctor: blocked
Summary: Usable, but blocked by catalog parity drift.
Next: ./bin/ask repo doctor-catalog --json --robot
```

Do not print thousands of repo-surface findings in the first screen.

### Integration Points

Likely files:

- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/scripts/lib/ask/commands/runtime.py`, if runtime budget logic
  needs extraction
- `Infrastructure/scripts/lib/ask/commands/skills.py`, if handles check logic
  needs extraction
- `Infrastructure/tests/test_ask_cli.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`

Implementation should verify exact helper boundaries before editing.

## Acceptance and Traceability

| Acceptance ID | Requirement                                                                                                                               | Evidence                                       |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| AC1           | `./bin/ask repo doctor --help` documents the command.                                                                                     | CLI help output                                |
| AC2           | `./bin/ask repo doctor --json --robot` returns `agent_summary`, `blocking`, `blockers`, `next_command`, `signals`, and `diagnostic_debt`. | focused test and live command                  |
| AC3           | Catalog parity drift is reported as a blocker.                                                                                            | fixture test and live command if drift remains |
| AC4           | Repo surface warning is summarized without flooding the first response.                                                                   | fixture test                                   |
| AC5           | Existing `repo doctor-catalog`, `repo surface`, and `skills proof` behavior remains compatible.                                           | regression tests                               |
| AC6           | The README or command docs point agents at `repo doctor` first.                                                                           | docs diff                                      |
| AC7           | Harness plan-gate state is recorded and this new plan carries `plan_id`.                                                                  | plan-gate output                               |

## Validation Plan

Planning validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json
./Infrastructure/scripts/harness-cli.sh plan-gate --require-plan-id --require-traceability --json
git status --short -- Docs/specs Docs/plans
```

First implementation validation:

```bash
./bin/ask repo doctor --help
./bin/ask repo doctor --json --robot
python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py Infrastructure/tests/test_ask_cli.py
./bin/ask repo validate --json --robot
./Infrastructure/scripts/harness-cli.sh plan-gate --require-plan-id --require-traceability --json
```

Run broader validation only after implementation discovers the repo's current
wrapper expectations and confirms the changed files.

## Rollback Plan

- Revert the `repo doctor` parser route and implementation helper.
- Leave existing `repo doctor-catalog`, `repo surface`, and `skills proof`
  untouched.
- Remove only tests and docs added for `repo doctor`.
- If catalog parity is fixed as a prerequisite, keep that fix unless it is
  proven incorrect, because it repairs a live blocker outside the new command.

## Follow-On Work

### F1: `ask skills improve "<goal>"`

Route a user goal to the best capability, using existing goal routing and
catalog parity checks. Output one recommended skill or handle, why it matched,
reachability status, proof status, and one next command.

### F2: `ask skills explain <skill-or-handle>`

Return concise capability guidance: what it is for, when to use it, canonical
source path, runtime projection path, command handles, required validation, and
known limitations.

### F3: `ask skills prove <skill-or-goal>`

Add `prove` as the user-facing verb while preserving `proof` compatibility.
Separate reachability proof, structural audit proof, and outcome proof.

### F4: Agent Skills Kit Analytics Projection

Use expanded Codex skill analytics as evidence input. Agent Skills Kit should
own ASK-local projections and proof decisions, not raw telemetry ingest.

Candidate projection:

```text
.skill-telemetry/skill-invocations.jsonl
.skill-telemetry/skill-scorecards/*.json
```

Projection fields should include `skill_id`, `plugin_id`, `turn_id_hash`,
`thread_id_hash`, `invoke_type`, `scope`, `model_slug`,
`product_client_id_hash`, timestamp, and privacy-safe repository attribution
when available.

### F5: Session Collector Changes

Update `$HOME/.agents/session-collector` to normalize supported
skill invocation events from:

- `~/.agents/otel-collector/data/raw/*.ndjson`;
- `~/.codex/sessions`.

Add these new artifact files to the existing bundle writer and manifest:

- `skill-invocations.json`;
- `skill-invocation-summary.json`;
- `skill-proof-candidates.json`.

Keep these existing bundle artifacts stable for current downstream consumers:

- `aggregate.json`;
- `index.json`;
- `skillify-candidates.json`;
- `skill-refactor-evidence.json`;
- `harness-engineering-evidence.json`;
- `insight-evidence-extension.json`;
- `solved-problems.json`;
- `redaction-report.json`;
- `manifest.json`.

The collector should remove these roots from the default skill-analytics source
path:

- `~/.codex-red/sessions`;
- `~/.codex-main/sessions`;
- optional Claude session metadata.

If backward compatibility requires retaining old CLI flags, keep them explicit
opt-in, mark them deprecated in help text, and prove they do not affect the
default skill-analytics output.

Required normalized record semantics:

- native Codex `skill_invocation` events are
  `evidence_class: reachability_attribution`;
- text-derived skill mentions remain `evidence_class: legacy_mention`;
- missing native analytics are reported as
  `analytics_status: unavailable_or_legacy`;
- raw thread IDs, turn IDs, repo URLs, account markers, prompt text, and email
  addresses are redacted or hashed before they reach bundle artifacts.

Validation for this unit:

```bash
cd $HOME/.agents/session-collector
UV_CACHE_DIR=/tmp/session-collector-uv-cache uv run --python 3.12 ruff check .
UV_CACHE_DIR=/tmp/session-collector-uv-cache uv run --python 3.12 python -m py_compile main.py evidence.py renderer.py tests/test_session_collector.py
UV_CACHE_DIR=/tmp/session-collector-uv-cache uv run --python 3.12 python -m unittest discover -s tests -v
UV_CACHE_DIR=/tmp/session-collector-uv-cache uv run --python 3.12 python main.py --days 7 --max-sessions 200 --codex-sessions-dir $HOME/.codex/sessions --output /tmp/session-collector-skill-analytics.json --bundle-dir /tmp/session-collector-skill-analytics-bundle --verbose
```

Exit criteria:

- existing bundle filenames and the three new skill-invocation filenames are
  present in `manifest.json`;
- default source resolution includes OTel raw files and `~/.codex/sessions`;
- default source resolution excludes Codex Red, Codex Main, and Claude metadata;
- tests cover native analytics, legacy mentions, malformed records, duplicate
  records, missing `turn_id`, missing `plugin_id`, source-missing state, and
  stale artifact classification.

### F6: OTel Collector Changes

Update `$HOME/.agents/otel-collector` to preserve raw skill
invocation attribution metadata and expose low-cardinality aggregate health:

- seen skill invocation event count;
- seen plugin ID count;
- seen turn ID coverage;
- malformed or dropped event counts;
- source freshness.

Do not expose high-cardinality per-thread or per-turn breakdowns in `/stats`.

### F7: `ask repo closeout --changed`

Compose changed-file awareness, validation recommendations, repo doctor state,
and required closeout checks into one completion-readiness command.

### F8: README Golden Path Rewrite

After the commands exist, rewrite the README first screen around:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

Do not publish this as the live first screen until the commands are implemented.

## Technical Review

Review status: passed with prior blockers repaired.

### Finding TR-1: Spec Uses `prove`, Current CLI Uses `proof`

Severity: medium.

Evidence:

- `./bin/ask skills --help` shows `proof`.
- `Infrastructure/bin/ask` contains parser support for `proof`.
- No current `prove` route was found.

Resolution:

- First implementation must keep `proof` stable.
- `prove` is deferred to F3 as a compatibility addition or alias.

### Finding TR-2: Harness Plan Gate Historical Debt

Severity: resolved.

Evidence:

- `./Infrastructure/scripts/harness-cli.sh plan-gate --require-plan-id --require-traceability --json`
  previously failed with stale-plan and missing-`plan_id` findings in existing
  plans.

Resolution:

- Historical plans now carry `plan_id` frontmatter.
- `Infrastructure/scripts/harness-cli.sh` now applies a repo-local default
  `--max-age` for `plan-gate` unless the caller supplies one explicitly.
- The gate now passes with zero findings.

### Finding TR-3: Catalog Parity Drift

Severity: resolved.

Evidence:

- `./bin/ask repo doctor-catalog --json --robot` previously reported canonical
  skill count `21` and README observed count `20`.

Resolution:

- README now reports `21` canonical skills.
- `./bin/ask repo doctor-catalog --json --robot` passes with
  `decision_status: resolved`.
- Preserve a fixture that proves blocked behavior for future drift.

### Finding TR-4: Path Casing Needs Exact Pathspecs

Severity: low.

Evidence:

- `git ls-files` shows tracked plan and spec paths under canonical `Docs/**`.
- `git status --short -- Docs/plans Docs/specs` reports the new files under
  uppercase `Docs/**`; mixed uppercase/lowercase pathspecs can still echo the
  caller's lowercase spelling on macOS because `core.ignorecase` is true.

Resolution:

- Use exact uppercase `Docs/**` pathspecs for status, staging, and review.
- Do not create a second lowercase tree.

### Finding TR-5: First Slice Must Avoid Three-Project Coupling

Severity: medium.

Evidence:

- The spec correctly includes Agent Skills Kit, session-collector, and
  otel-collector, but the first command does not need collector changes.

Resolution:

- Keep collector changes in F5 and F6.
- Implement `repo doctor` first using existing local signals.

### Finding TR-6: Collector Follow-On Must Preserve Existing Evidence Bundle

Severity: medium.

Evidence:

- The live session collector already emits bundle artifacts consumed by
  `skillify`, `skill-refactor`, `insight-report`, and `harness-engineering`.
- The spec adds native skill-invocation artifacts, but those artifacts should
  extend the bundle rather than replacing it.

Resolution:

- F5 requires the existing bundle filenames to remain present.
- F5 requires `manifest.json` to list both the existing artifacts and the new
  skill-invocation artifacts.

### Finding TR-7: Collector Source Defaults Conflict With The Narrow Feature Scope

Severity: medium.

Evidence:

- Current collector defaults still include Codex Red and Codex Main rollout
  directories, and the CLI still exposes legacy Claude metadata flags.
- The skill-analytics source contract for this feature is intentionally limited
  to OTel raw files and `~/.codex/sessions`.

Resolution:

- F5 requires Codex Red, Codex Main, and Claude metadata to be removed from the
  default skill-analytics source path.
- Any retained compatibility flags must be explicit opt-in, deprecated in help
  text, and covered by tests proving they do not affect default output.

## Risks and Blockers

- Future catalog parity drift can block `skills improve` and broad goal routing.
- Future plan-gate failures should now indicate new debt, not inherited
  historical plan metadata.
- Mixed-case pathspecs can create confusing status output on macOS; use
  canonical `Docs/**` pathspecs.
- Shelling out from `ask` into `ask` would make doctor brittle and slow; extract
  helper functions instead.
- Surfacing thousands of repo-surface findings in doctor would reproduce the
  product problem this work is meant to solve.
- Replacing the session-collector bundle would break existing downstream
  evidence consumers; extend it instead.
- Leaving unsupported collector roots in the default skill-analytics path would
  reintroduce the exact source-scope ambiguity this spec is trying to remove.

## Sources and References

- `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md`
- `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`
- `Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`
- `Docs/product/agent-capability-control-plane.md`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/tests/test_ask_repo_doctor_catalog.py`
- `Infrastructure/tests/test_ask_repo_surface.py`
- `Infrastructure/tests/test_ask_cli.py`
- `$HOME/.agents/session-collector`
- `$HOME/.agents/otel-collector`

## Next Stage Handoff

Start implementation with P0. The recommended first code change is not a broad
README rewrite or collector update; it is the smallest executable golden-path
contract:

```bash
./bin/ask repo doctor --json --robot
```

The command should make repo state legible to a cold AI coding agent in one
screen. For a future catalog drift case, it should be this compact:

```text
Status: blocked
Reason: catalog parity drift
Next: ./bin/ask repo doctor-catalog --json --robot
```

Once that works, continue through P4 and P5 before starting any deferred
analytics or collector work.
