---
schema_version: 1
title: "feat: Agent Capability Control Plane and Repo Surface Contract Plan"
type: feat
status: active
date: 2026-05-01
origin: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
source_spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
linear_project: agent-skills
linear_issue: JSC-246
linear_parent: none
linear_children: []
linear_status: Open
linear_comment_required: true
branch: jscraik/jsc-246-build-repo-surface-contract-and-agent-capability-control
pr: pending
traceability_required: true
plan_route: fresh
plan_depth: deep
---

# feat: Agent Capability Control Plane and Repo Surface Contract Plan

## Table of Contents

- [Overview](#overview)
- [Problem Frame](#problem-frame)
- [Linear Work Item Contract](#linear-work-item-contract)
- [Requirements Trace](#requirements-trace)
- [Linear / Spec / Plan / PR Traceability](#linear--spec--plan--pr-traceability)
- [Scope Boundaries](#scope-boundaries)
- [Context & Research](#context--research)
- [Key Technical Decisions](#key-technical-decisions)
- [Open Questions](#open-questions)
- [High-Level Technical Design](#high-level-technical-design)
- [Deepening Addendum](#deepening-addendum)
- [Implementation Units](#implementation-units)
- [Execution Checkpoints](#execution-checkpoints)
- [System-Wide Impact](#system-wide-impact)
- [Risks & Dependencies](#risks--dependencies)
- [Documentation / Operational Notes](#documentation--operational-notes)
- [Execution Ledger (Planning Mode)](#execution-ledger-planning-mode)
- [Sources & References](#sources--references)
- [Next Stage Handoff](#next-stage-handoff)

## Overview

Implement the first delivery path for JSC-246 by turning the Agent Skills Kit
repo-surface cleanup idea into a safe, repeatable, software-backed workflow.
The plan treats the project as an agent capability control plane rather than a
prompt or skill library, and it starts with classification and policy before any
artifact cleanup.

Plan route: `fresh`.

Plan depth: `deep`.

Execution posture:

- policy-first;
- inventory-first;
- no destructive cleanup in the first slice;
- `ask` remains the public interface;
- generated and runtime surfaces must declare ownership before mutation;
- deferred context is preserved behind references, not trimmed away.

## Problem Frame

The repository already has strong operational machinery: canonical skill source,
generated command handles, runtime projection, sync, strict audits, runtime
budget checks, workouts, artifacts, and deferred context. The issue is that a
human or agent cannot yet ask the repo, mechanically, which tracked paths are
source, generated, archived evidence, runtime state, fixtures, or unknown.

That makes deadcode cleanup risky and makes the product harder to understand.
The first implementation must create a repo surface contract and inventory gate
before removing historical artifacts or adding broader product golden paths.

## Linear Work Item Contract

- Linear issue: `JSC-246`
- URL: `https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden`
- Parent / children: none yet
- Current Linear status: Open
- Branch: `jscraik/jsc-246-build-repo-surface-contract-and-agent-capability-control`
- PR: pending
- Linear comment required: true, because this plan creates the execution contract
  for a tracked issue and should be linked back to Linear before implementation
  starts.

## Requirements Trace

- R1. Define a repo surface ownership policy that separates source, fixtures,
  policy, references, intentional archives, vendored snapshots, generated output,
  runtime state, historical artifacts, and unknown paths.
- R2. Add a non-destructive surface inventory gate with stable JSON and concise
  human output through `./bin/ask`.
- R3. Detect tracked generated/historical artifacts under `artifacts/**` and
  `Infrastructure/artifacts/**` without deleting them in the first slice.
- R4. Flag suspicious nested infra paths such as `Infrastructure/Infrastructure/**`
  unless explicitly allowlisted with a reason.
- R5. Force explicit ownership decisions for `.skillsets/**`, `.harness/*.db`,
  `skills-system/**`, and `Plugins/cache/**`.
- R6. Preserve deferred context behind indexed references and keep it out of
  first-level runtime pressure.
- R7. Split cleanup into reference-scanned follow-on work after the inventory gate
  is trusted.
- R8. Define product golden paths for `ask` without expanding top-level command
  sprawl before namespace-first contracts are proven.
- R9. Keep runtime surface reporting visible in closeout and product health checks.
- R10. Reframe user-facing docs around the agent capability control plane promise
  and outcome proof.

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs       | Plan units | Acceptance IDs               | PR evidence |
| ------------ | ----------- | --------------------------- | ---------- | ---------------------------- | ----------- |
| JSC-246      | R1          | SA1                         | P0         | AC1, AC2                     | pending     |
| JSC-246      | R2          | SA2                         | P1, P2     | AC3, AC4, AC5                | pending     |
| JSC-246      | R3          | SA3                         | P1, P2     | AC6, AC7                     | pending     |
| JSC-246      | R4          | SA4                         | P1, P2     | AC8                          | pending     |
| JSC-246      | R5          | SA5                         | P0, P2     | AC9                          | pending     |
| JSC-246      | R6          | SA8                         | P0, P2     | AC10                         | pending     |
| JSC-246      | R7          | SA6, SA7                    | P3         | AC11, AC12                   | pending     |
| JSC-246      | R8          | SA9, SA10, SA11, SA12, SA13 | P4         | AC13, AC14, AC15, AC16, AC17 | pending     |
| JSC-246      | R9          | SA14                        | P4, P5     | AC18                         | pending     |
| JSC-246      | R10         | SA15                        | P5         | AC19                         | pending     |

## Scope Boundaries

In scope:

- repo surface ownership policy;
- inventory script and JSON report;
- `ask` route for surface reporting;
- validation tests and fixtures;
- first live report from the current tree;
- follow-on cleanup plan units after reference scan;
- namespace-first product command contracts;
- README/start-here framing after the inventory contract exists.

Out of scope for the first implementation unit:

- deleting tracked artifacts;
- changing runtime projection behavior;
- changing Codex desktop behavior;
- rewriting existing skill bodies;
- making every product golden path fully implemented before the inventory gate
  exists.

## Context & Research

### Relevant Code and Patterns

- `./bin/ask` is the public CLI entrypoint.
- `Infrastructure/bin/ask` contains command routing and alias behavior.
- `Infrastructure/scripts/lib/ask/**` contains command implementations.
- `Infrastructure/scripts/validation-and-linting/**` is the expected home for
  validation gates.
- `Infrastructure/scripts/lifecycle-and-sync/**` owns skill discovery, sync, and
  runtime projection behavior.
- `CONTEXT.md` defines runtime projection vocabulary.
- `UBIQUITOUS_LANGUAGE.md` defines Agent Skills Kit and generated command handle
  vocabulary.
- `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`
  is the governing source spec.

### Current Command Baseline

Current `ask` top-level topics are:

```text
repo, skills, reviewers, runtime, plugins, evals, workouts, graph, mcp, wiki
```

Current `repo` subcommands are:

```text
status, validate, check-stability, doctor-catalog, provider-audit
```

Current `skills` subcommands include:

```text
list, budget, handles, resolve, parse, proof, route, goal, starter, sync, audit,
install, fold, init
```

The plan therefore uses namespace-first commands and treats top-level golden
paths as optional aliases only after router compatibility is proven.

### Institutional Learnings

- Generated/runtime surfaces must not be hand-edited.
- Long context should move behind references and indexes, not be deleted for
  budget trimming.
- The first slice must prove the inventory classifier before cleanup work starts.

## Key Technical Decisions

### D1: Use `ask repo surface` As The Canonical Command

`ask repo surface` is the policy-grade interface. It classifies paths before
judging them. `ask repo bloat` may become a human-friendly alias later, but the
canonical JSON contract should use surface inventory language.

### D2: Keep The First Slice Non-Destructive

The first PR must not delete tracked artifacts. It creates the policy,
classifier, command route, tests, and live report. Cleanup starts only after
reference scanning and allowlist behavior are tested.

### D3: Classifier Owns Categories, Policy Owns Meaning

The script reports classifications and violations. A policy reference defines
what each classification means and which path patterns are allowed. This keeps
the script testable and the policy reviewable.

### D4: Generated Ownership Decisions Are Separate From Cleanup

`.skillsets/**`, `.harness/*.db`, `skills-system/**`, and `Plugins/cache/**` must
be classified and documented before any cleanup touches them. Ambiguous
ownership is a blocker, not a delete signal.

### D5: Product Golden Paths Follow Namespace-First Implementation

Use existing command namespaces first:

```text
ask repo doctor
ask repo onboard
ask skills improve
ask skills explain
ask skills prove
ask repo next
ask repo closeout
```

Top-level aliases can follow when they reduce friction without widening the
default command surface.

## Open Questions

### Resolved During Planning

- Canonical inventory command: use `ask repo surface`.
- Human-friendly cleanup wording: reserve `ask repo bloat` as a possible alias.
- First slice deletion policy: no destructive cleanup.

### Deferred to Implementation

- Whether `.skillsets/**` is a tracked canonical generated snapshot or a
  reproducible ignored output.
- Whether `.harness/context-compound.db` is runtime state, a fixture, or an
  accidental tracked file.
- Whether `skills-system/**` is a vendored snapshot, generated mirror, or legacy
  surface.
- Which historical artifact summaries deserve intentional archive status.
- Whether product golden paths should get top-level aliases after namespace-first
  behavior is working.

## High-Level Technical Design

The first delivery should create one policy document, one classifier, one command
route, and one test set.

```text
git tracked files
  -> surface inventory classifier
  -> path policy / allowlist
  -> JSON report
  -> human summary
  -> strict validation result
  -> next command recommendation
```

The classifier should not know every product decision. It should expose enough
structured evidence for humans and agents to resolve unknowns safely.

Suggested JSON shape:

```json
{
  "status": "warning",
  "summary": {
    "tracked_files": 1234,
    "violations": 12,
    "unknown": 3
  },
  "classifications": {
    "source": 100,
    "historical_artifact": 20,
    "runtime_state": 1,
    "unknown": 3
  },
  "findings": [
    {
      "path": "Infrastructure/Infrastructure/artifacts/example.json",
      "classification": "unknown",
      "status": "violation",
      "reason": "nested Infrastructure path is not allowlisted",
      "recommendation": "audit source and either remove, move to fixture, or allowlist with reason"
    }
  ],
  "next_command": "./bin/ask repo surface --strict --json"
}
```

This shape is directional guidance, not a final schema.

## Deepening Addendum

This plan is ready for `he-work` only for `P0-P2`. `P3-P5` are deliberately
sequenced after the inventory command exists and should not be bundled into the
first implementation pass.

### First-Slice Execution Rules

- Implement `P0-P2` as one vertical slice: policy, classifier, public `ask` route,
  focused tests, and live report.
- Do not implement artifact deletion, cleanup reports, product golden-path
  commands, or README reframing in the first slice.
- Treat live strict-mode failures as expected evidence when the current tree
  contains tracked historical artifacts or unknown ownership. Strict mode can
  fail while the implementation still succeeds, provided the failure is
  deterministic, non-mutating, and explained in the JSON envelope.
- Preserve any unrelated dirty HE symlink/reference work already present in the
  worktree.

### Test Location Decision

Use existing test conventions instead of inventing a new test root:

- classifier tests: `Infrastructure/scripts/testing/test_repo_surface_inventory.py`
- CLI route tests: `Infrastructure/tests/test_ask_repo_surface.py`

These names may be adjusted only if implementation finds an existing closer
test module. If adjusted, the plan closeout must state the selected path and why.

### Public Command Envelope Contract

`./bin/ask repo surface --json` must return the standard `ask` envelope shape:

```json
{
  "status": "success|warning|error",
  "trace_id": "<uuid-or-provided-trace-id>",
  "metadata": {
    "command": "repo surface --json",
    "next_steps": []
  },
  "data": {
    "summary": {},
    "classifications": {},
    "findings": []
  },
  "errors": []
}
```

Strict mode behavior:

- `./bin/ask repo surface --strict --json` exits non-zero when policy violations
  are present.
- The command must still print parseable JSON on strict failure.
- Strict failure is not a mutation and must not delete or move files.
- The `errors` or `findings` payload must identify at least one blocking
  violation and a recommended next action.

### Implementation Stop Conditions

Stop and return to planning if:

- the classifier needs to read or mutate generated runtime files to classify
  tracked paths;
- the command route requires broad `ask` router restructuring beyond adding a
  repo subcommand;
- live repo classification cannot distinguish active source from generated
  evidence for the first-slice policy categories;
- tests require deleting or rewriting existing artifacts to pass.

## Implementation Units

- [ ] **P0 / Unit 1: Surface Ownership Policy**

**Goal:** Create the reviewable policy contract for repo surface ownership.

**Requirements:** R1, R5, R6

**Dependencies:** None.

**Files:**

- Create: `Docs/agents/15-repo-surface-ownership.md`
- Modify: `AGENTS.md` or `README.md` only if needed to link the policy front
  door.
- Test: policy presence should be covered by P1/P2 inventory tests rather than a
  standalone prose test.

**Approach:**

- Define the classification categories from the spec.
- Define initial path policy for `Skills/**`, `Plugins/*/skills/**`,
  `.agents/skills/**`, `Plugins/cache/**`, `Infrastructure/artifacts/**`,
  `artifacts/**`, `.skillsets/**`, `.harness/*.db`, `skills-system/**`,
  deferred context, and `Infrastructure/Infrastructure/**`.
- Include the rule that unknown ownership is a blocker, not a delete signal.
- Include the rule that deferred context is preserved behind indexes.

**Test scenarios:**

- Policy contains every classification required by SA1.
- Policy contains explicit rows for the unresolved generated/runtime surfaces.

**Verification:**

- `rg 'source|fixture|historical_artifact|runtime_state|unknown' Docs/agents/15-repo-surface-ownership.md`
- `rg '.skillsets|.harness|skills-system|Plugins/cache|Infrastructure/Infrastructure' Docs/agents/15-repo-surface-ownership.md`

**Rollback:**

- Remove the policy doc and any link added to repo-facing docs.

**Exit criteria:**

- AC1: Policy exists and defines all surface classifications.
- AC2: Policy documents unresolved generated/runtime surfaces as explicit
  decision points.

- [ ] **P1 / Unit 2: Non-Destructive Inventory Classifier**

**Goal:** Add a script that classifies tracked paths and reports violations
without deleting or moving files.

**Requirements:** R2, R3, R4

**Dependencies:** P0 policy path can exist first, but the classifier can be built
in parallel if it imports policy constants locally.

**Files:**

- Create: `Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`
- Create: `Infrastructure/scripts/testing/test_repo_surface_inventory.py`

**Approach:**

- Use `git ls-files` from the repo root for tracked-file inventory.
- Classify by path pattern first, then by extension/pattern for generated
  evidence such as `.jsonl`, `.log`, timestamped validation dirs, and runtime DBs.
- Detect `Infrastructure/Infrastructure/**` as a violation unless allowlisted.
- Emit JSON and human summaries.
- Support a strict mode that exits non-zero on violations.
- Do not delete, move, or rewrite candidate files.

**Test scenarios:**

- A fake tracked `artifacts/.../events.jsonl` path is classified as
  `historical_artifact`.
- A fake `Infrastructure/Infrastructure/...` path is a violation.
- A fake source path under `Skills/**` is classified as `source`.
- A fake `.harness/context-compound.db` path is classified as `runtime_state` or
  unresolved ownership according to policy.
- JSON output includes `classification`, `status`, `reason`, `recommendation`,
  and `next_command`.

**Verification:**

- `python3 -m pytest Infrastructure/scripts/testing/test_repo_surface_inventory.py`
- Run the classifier against the live repository in report mode.

**Rollback:**

- Remove the script and focused tests; no tracked content cleanup is performed in
  this unit.

**Exit criteria:**

- AC3: Inventory script emits stable JSON.
- AC4: Inventory script emits useful human output.
- AC5: Strict mode fails on policy violations without mutating files.
- AC6: Historical artifact paths are detected.
- AC7: Generated JSONL/log/run-output paths are reported without deletion.
- AC8: Nested `Infrastructure/Infrastructure/**` paths are flagged.

- [ ] **P2 / Unit 3: Public `ask repo surface` Route**

**Goal:** Expose the inventory through the stable `ask` command surface.

**Requirements:** R2, R3, R4, R5, R6

**Dependencies:** P1.

**Files:**

- Modify: `Infrastructure/scripts/lib/ask/**` command routing for repo commands.
- Modify: `Infrastructure/bin/ask` only if routing registration requires it.
- Test: `Infrastructure/tests/test_ask_repo_surface.py`

**Approach:**

- Add `./bin/ask repo surface --json`.
- Add `./bin/ask repo surface --strict --json`.
- Return the standard ask envelope with `status`, `trace_id`, `metadata`,
  `data`, `telemetry`, and `errors`.
- Include `next_steps` or equivalent metadata pointing to the next safe command.
- Keep `ask repo bloat` out of the first implementation unless adding it as an
  alias is trivial and covered by tests.

**Test scenarios:**

- `./bin/ask repo surface --json` returns a parseable envelope.
- `./bin/ask repo surface --strict --json` reports violations consistently.
- Robot mode handles clear minor syntax only if existing router policy supports
  it.

**Verification:**

- `python3 -m pytest Infrastructure/tests/test_ask_repo_surface.py`
- `./bin/ask repo surface --json`
- `./bin/ask repo surface --strict --json` with expected non-zero behavior if
  the live tree has violations.

**Rollback:**

- Remove the repo subcommand route and command tests.

**Exit criteria:**

- AC9: Explicit ownership decisions are visible in the command output.
- AC10: Deferred context is classified as reference or preserved context, not
  treated as deletion-first bloat.

- [ ] **P3 / Unit 4: Reference-Scanned Cleanup Preparation**

**Goal:** Prepare cleanup follow-on work without deleting files prematurely.

**Requirements:** R7

**Dependencies:** P1 and P2.

**Files:**

- Create: a generated report artifact or documentation summary path selected by
  the implementation after policy confirms where reports belong.
- Modify: no cleanup deletions in this unit unless it is split into a later
  cleanup PR after review.

**Approach:**

- Run the live inventory report.
- Group cleanup candidates:
  - historical generated artifacts;
  - retired skill debris;
  - suspicious nested infra paths;
  - unresolved generated/runtime ownership surfaces.
- For each group, define the required reference scan command and retention
  decision.
- Record what can be safely deleted in a later PR and what needs ownership
  resolution first.

**Test scenarios:**

- Report includes candidate groups and required reference scans.
- No files are deleted by preparation mode.

**Verification:**

- `./bin/ask repo surface --json`
- Reference scans for retired skill names named by the spec.

**Rollback:**

- Remove the generated report or summary.

**Exit criteria:**

- AC11: Historical artifact cleanup has a reference-scanned candidate list.
- AC12: Retired skill debris cleanup has active/deferred/docs reference evidence.

- [ ] **P4 / Unit 5: Namespace-First Product Golden Path Contracts**

**Goal:** Specify or scaffold the product-facing `ask` workflows without
premature top-level command expansion.

**Requirements:** R8, R9

**Dependencies:** P2 for `repo surface`; can be planned in parallel but should not
ship before the surface report exists.

**Files:**

- Modify: `Docs/agents/15-repo-surface-ownership.md` or a companion command
  contract doc.
- Modify: `README.md` or start-here docs only after command names settle.
- Modify command code only for the smallest first product endpoint selected by
  implementation review.

**Approach:**

- Define the selected namespace-first commands:
  - `ask repo doctor`
  - `ask repo onboard`
  - `ask skills improve`
  - `ask skills explain`
  - `ask skills prove`
  - `ask repo next`
  - `ask repo closeout`
- Decide which one should be implemented first. Recommended: `ask repo doctor`
  consumes `repo status`, runtime budget, handles, and surface policy once
  `repo surface` exists.
- Keep top-level aliases as a later compatibility/product decision.

**Test scenarios:**

- Command contract doc lists expected inputs, outputs, and JSON fields.
- If the first endpoint is implemented, it returns standard ask envelope output.
- Runtime budget status remains visible in doctor/closeout contracts.

**Verification:**

- `./bin/ask runtime budget --json --robot`
- Focused command test for the first implemented endpoint, if any.

**Rollback:**

- Revert command docs or the first product endpoint route.

**Exit criteria:**

- AC13: `ask repo doctor` contract includes repo, sync, runtime budget, handles,
  surface policy, blockers, and next command.
- AC14: `ask repo onboard` contract explains current repo/runtime state and a
  next action.
- AC15: `ask skills improve` contract maps goals to candidate capabilities and
  validation/sync actions.
- AC16: `ask skills explain` contract distinguishes generated handle, canonical
  source, runtime projection, loaded references, and validation.
- AC17: `ask repo closeout --changed` contract includes changed files, sync needs,
  focused validation, and commit-readiness signal.
- AC18: Runtime surface reporting remains visible in health and closeout flows.

- [ ] **P5 / Unit 6: Product Framing and Outcome Proof Documentation**

**Goal:** Reframe repo-facing docs around the agent capability control plane
promise and define the minimum outcome-proof story.

**Requirements:** R10

**Dependencies:** P0-P4 should define enough concrete behavior to avoid a
marketing-only rewrite.

**Files:**

- Modify: `README.md`
- Modify or create: a start-here/product framing doc selected during
  implementation.

**Approach:**

- Lead with "Teach your coding agents how your work actually works, then prove
  they remembered."
- Describe the four outcomes:
  - remember workflows;
  - keep context small;
  - prevent drift;
  - prove quality.
- Link to `ask repo surface` and first health/onboarding command contracts.
- Define a minimum outcome proof format for later `ask skills prove` or
  `ask repo prove` work.

**Test scenarios:**

- README mentions Agent Skills Kit as a control plane, not only a skill repo.
- Docs link to the repo surface policy and selected first command.

**Verification:**

- Documentation grep for product thesis and command references.
- `./bin/ask repo validate` or the repo's narrower docs validation if available.

**Rollback:**

- Revert README/start-here docs.

**Exit criteria:**

- AC19: Repo-facing docs present Agent Skills Kit as an agent capability control
  plane with outcome proof.

## Execution Checkpoints

### Checkpoint A: Inventory Contract Proven Before Cleanup

**Exit criteria:**

- P0, P1, and P2 pass focused tests.
- `./bin/ask repo surface --json` works on the live repo.
- The report lists violations and unknowns without deleting files.

**Stop condition:**

- If classifier output cannot distinguish source from generated/runtime state
  confidently, stop and deepen the policy before cleanup planning.

### Checkpoint B: Cleanup Candidates Have Reference Evidence

**Exit criteria:**

- Historical artifacts are grouped by retention decision.
- Retired skill debris has active/deferred/docs reference scans attached.
- Unresolved generated/runtime surfaces are either classified or explicitly
  blocked.

**Stop condition:**

- If a candidate path is referenced by active source or deferred context, do not
  delete it in cleanup; reclassify or move it behind an indexed reference.

### Checkpoint C: Product Commands Do Not Expand Surface Accidentally

**Exit criteria:**

- Namespace-first contracts exist.
- Top-level aliases are either deferred or tested.
- Runtime budget reporting remains visible.

**Stop condition:**

- If a product command duplicates existing `ask` behavior without reducing user
  decisions, stop and consolidate it into an existing namespace instead.

## System-Wide Impact

- **Interaction graph:** `ask repo surface` becomes a repo-health input for
  doctor, onboarding, closeout, and cleanup planning.
- **Error propagation:** strict mode should return non-zero through `ask` while
  preserving standard JSON envelope details for agents.
- **State lifecycle risks:** no first-slice mutation of generated artifacts;
  later cleanup must be reversible through git and backed by reference scans.
- **API surface parity:** human and JSON outputs must report the same findings.
- **Integration coverage:** CLI tests must cover the public `ask` route, not only
  the lower-level classifier.

## Risks & Dependencies

- The live repo has existing dirty HE symlink/reference work; implementation must
  avoid mixing those changes with JSC-246 unless the branch intentionally absorbs
  them.
- `Infrastructure/Infrastructure/**` may turn out to be a generated artifact or
  historical import; classification should report it before removal.
- `.skillsets/**` and `skills-system/**` may be partially canonical. Treat them
  as ownership decisions, not cleanup candidates, until evidence is gathered.
- The command taxonomy already has `doctor-catalog`; avoid introducing a
  conflicting `doctor` shape without router tests.
- Historical artifacts may include useful fixtures. Require allowlist reasons and
  reference scans.

## Documentation / Operational Notes

- Keep the spec as the governing WHAT contract.
- Keep this plan as the HOW sequence.
- Before `he-work` starts, ensure Linear issue `JSC-246` includes links to this
  plan and the governing spec so the issue remains the coordination record.
- Do not trim deferred context; move important material to references and index
  it.
- Prefer wrapper commands through `./bin/ask` over direct script invocation in
  user-facing docs and closeout evidence.

## Execution Ledger (Planning Mode)

| Date       | Event                                              | Evidence                                                                                                                                                                           |
| ---------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-05-01 | Created JSC-246 Linear issue.                      | Linear URL in work item contract.                                                                                                                                                  |
| 2026-05-01 | Wrote governing spec.                              | `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`                                                                                      |
| 2026-05-01 | Ran HE traceability lint for the spec.             | `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md` |
| 2026-05-01 | Produced implementation plan.                      | This document.                                                                                                                                                                     |
| 2026-05-01 | Deepened plan for first-slice execution readiness. | Added first-slice rules, test paths, command envelope, strict-mode behavior, and stop conditions.                                                                                  |
| 2026-05-01 | Linked planning references back to Linear.         | Added JSC-246 comment `a19bbc38-1d89-4619-82f6-5c887a7a7fdd` with spec and plan paths.                                                                                             |

## Sources & References

- `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`
- `CONTEXT.md`
- `UBIQUITOUS_LANGUAGE.md`
- `AGENTS.md`
- `README.md`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/**`
- `Infrastructure/scripts/validation-and-linting/**`
- `Infrastructure/scripts/lifecycle-and-sync/**`

## Next Stage Handoff

Recommended first `he-work` handoff:

```text
Before editing code, confirm Linear issue JSC-246 includes the existing spec and
plan backlink comment.

Implement P0-P2 only: add repo surface ownership policy, a non-destructive
surface inventory classifier, and an `./bin/ask repo surface` route with focused
tests and a live JSON report. Do not delete tracked artifacts in this slice.
```

Required first passing validation ladder:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md
./bin/ask repo surface --json
./bin/ask runtime budget --json --robot
```

Required first diagnostic evidence:

```bash
./bin/ask repo surface --strict --json
```

Expected outcome: return success only when the live repository has no surface
policy violations. If violations exist, return non-zero while preserving the
standard JSON envelope with violation details and actionable next steps.
