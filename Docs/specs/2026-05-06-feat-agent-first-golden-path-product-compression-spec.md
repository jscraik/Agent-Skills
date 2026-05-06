---
schema_version: 1
title: Agent-First Golden Path Product Compression
type: feat
status: ready_for_plan
date: 2026-05-06
origin: conversation: blunt product critique of Agent Skills Kit usefulness and agent ergonomics
parent_spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
linear_project: agent-skills
linear_issue: JSC-246
linear_status: Open
traceability_required: true
risk: medium
spec_depth: full
ui_required: false
---

# Agent-First Golden Path Product Compression

## Table of Contents

- [Spec Mode Decision](#spec-mode-decision)
- [Problem Statement](#problem-statement)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Linear Work Item Contract](#linear-work-item-contract)
- [System Boundary](#system-boundary)
- [Current-State Baseline](#current-state-baseline)
- [Core Domain Model](#core-domain-model)
- [Skill Analytics Evidence Pipeline](#skill-analytics-evidence-pipeline)
- [Evidence Contracts](#evidence-contracts)
- [Agent Decision Contract](#agent-decision-contract)
- [Implementation Slices](#implementation-slices)
- [Main Flow / Lifecycle](#main-flow--lifecycle)
- [Interfaces and Dependencies](#interfaces-and-dependencies)
- [Command Naming Compatibility](#command-naming-compatibility)
- [Invariants / Safety Requirements](#invariants--safety-requirements)
- [Failure Model and Recovery](#failure-model-and-recovery)
- [Observability](#observability)
- [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [Linear Acceptance Traceability](#linear-acceptance-traceability)
- [Technical Review Checklist](#technical-review-checklist)
- [Planning-Ready First Slice](#planning-ready-first-slice)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)
- [Handoff to `he-plan`](#handoff-to-he-plan)

## Spec Mode Decision

Use `standard-spec` with `spec_depth: full`.

This is a product and command-contract spec for Agent Skills Kit. It narrows the
active JSC-246 control-plane work to the agent-facing golden path that turns the
repo from "powerful machinery" into a small set of obvious next actions for AI
coding agents.

This is not a UI spec, so `ui_required: false`.

## Problem Statement

Agent Skills Kit has sound control-plane architecture: canonical skill sources,
generated command handles, rooted runtime projection, audit gates, runtime
budget checks, and repo surface ownership policy. The remaining product problem
is compression.

An AI coding agent can currently discover many true facts about the repository,
but it must already know which command to run, how to interpret large diagnostic
JSON, and which warnings are safe to continue past. That makes the project more
impressive than intuitive. The product should instead answer one agent-native
question at each stage:

```text
What is the next safe, evidence-backed action?
```

The user critique identified the desired product shape:

```text
doctor -> improve -> explain/prove -> closeout
```

The project already has contracts for these commands in the parent JSC-246
spec and product command contract docs. This spec makes the narrowed behavior
testable and planning-ready.

## Goals

- Make `ask repo doctor` the default agent health entrypoint before repo work.
- Make `ask skills improve "<goal>"` the default goal-to-capability entrypoint.
- Make `ask skills explain <skill-or-handle>` a concise capability explanation
  surface that hides source/projection complexity until needed.
- Make `ask skills prove <skill-or-goal>` separate reachability proof, quality
  proof, and outcome proof.
- Make `ask repo closeout --changed` the default completion-readiness command
  for agents before claiming work is done.
- Add a concise `agent_summary`, machine-readable `blocking` state, and exactly
  one primary `next_command` to each golden-path command.
- Keep existing detailed JSON reports available without requiring agents to
  inspect them before receiving a recommended action.
- Preserve namespace-first command design under `repo` and `skills`; do not add
  top-level aliases in the first slice.
- Treat catalog parity, runtime budget, command-handle health, and repo surface
  warnings as composed product signals rather than disconnected diagnostics.

## Non-Goals

- Do not implement a broad UI or dashboard.
- Do not add new skills solely to make the catalog larger.
- Do not rewrite the whole README or all product docs in the first slice.
- Do not remove repo surface diagnostic debt as part of this golden-path slice.
- Do not weaken existing validation, path ownership, or projection rules.
- Do not make structural validation count as outcome proof.
- Do not introduce top-level aliases such as `ask doctor` until telemetry or
  repeated usage evidence proves they reduce friction.
- Do not include external session metadata roots beyond the supported Codex
  source contract in the first skill-analytics evidence pipeline.

## Linear Work Item Contract

Linear issue: `JSC-246`

Title: Build repo surface contract and agent capability control-plane golden
paths.

Status: Open.

Project: `agent-skills`.

Team: `Jscraik`.

Priority: High.

Labels: `Roadmap: Next`, `Agent`, `Infra`, `Feature`, `Improvement`.

This spec is a child contract under the active JSC-246 work. It should not
create a separate tracker unless planning decides the golden-path implementation
must split from repo-surface delivery.

## System Boundary

### Owned Surfaces

- `./bin/ask` public command surface.
- `Infrastructure/scripts/lib/ask/**` command implementation and shared
  envelope helpers.
- `Infrastructure/scripts/lifecycle-and-sync/**` route, goal, proof, command
  surface, and catalog parity helpers reused by the golden path.
- `Infrastructure/scripts/validation-and-linting/**` checks used by doctor and
  closeout.
- `Docs/cli-specs/**`, `Docs/product/**`, `Docs/specs/**`, and README sections
  that describe the golden path.
- Generated Agent Skills Kit telemetry projections under `.skill-telemetry/**`,
  if planning chooses a local cache for normalized collector output.

### Companion Collector Surfaces

The golden-path proof work spans three local projects, but ownership must stay
separated:

- `$HOME/dev/agent-skills` owns product commands, proof decisions,
  command envelopes, docs, and generated ASK-local projections.
- `$HOME/.agents/session-collector` owns privacy-safe normalized
  session and skill evidence derived from supported local telemetry sources.
- `$HOME/.agents/otel-collector` owns raw OTLP ingest, raw NDJSON,
  and low-cardinality aggregate telemetry health stats.

The collector source contract for this slice is intentionally narrow:

- Include `~/.agents/otel-collector/data/raw/*.ndjson`.
- Include `~/.codex/sessions`.
- Exclude all other session metadata roots.

### Referenced Surfaces

- `Skills/**`
- `Plugins/**/skills/**`
- `.agents/skills/**`
- `.skillsets/**`
- `Docs/agents/14-path-ownership-boundaries.md`
- `Docs/agents/15-repo-surface-ownership.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`
- `Docs/product/agent-capability-control-plane.md`
- `$HOME/.agents/session-collector/README.md`
- `$HOME/.agents/otel-collector/README.md`

### Out of Scope

- Codex desktop runtime behavior.
- Provider plugin marketplace internals.
- Non-Agent Skills Kit repositories except the explicitly named local collector
  companion changes in this spec.
- Destructive cleanup of historical artifacts.
- Skill body rewrites unrelated to the golden-path command experience.
- Deep OTel collector proof logic, dashboards, or high-cardinality per-thread
  stats in `/stats`.

## Current-State Baseline

Baseline from the 2026-05-06 critique and live command evidence:

- `./bin/ask repo status --json` passed and reported `skills_synced: true`.
- `./bin/ask runtime budget --json --robot` passed with no violations while
  reporting `advanced_visible_count: 157`, advisory threshold `60`,
  `first_level_default_count: 103`, `default_visible_count: 10`, and
  `root_skill_set_count: 10`.
- `./bin/ask skills handles --check --json` passed with `handle_count: 93`,
  `generated_command_handle_count: 93`, and no violations.
- `./bin/ask repo surface --json` reported `status: warning` with
  `blocking_findings: 4515`, including tracked historical artifacts and unknown
  ownership debt.
- `./bin/ask skills goal "make the project more useful and compelling and
intuitive to AI coding agents" --json --robot` failed with
  `blocked_catalog_parity`.
- `./bin/ask repo doctor-catalog --json --robot` showed canonical count `21`
  while `README.md` observed count was `20`.
- Local Codex commits `3ad7cf099` and `7e71d0261` expanded skill invocation
  analytics so `skill_invocation` events include `plugin_id` and `turn_id` in
  addition to existing skill name, skill ID, scope, repo URL, thread ID, invoke
  type, model slug, and product client ID.

Collector-backed baseline from `$HOME/.agents/session-collector`
on 2026-05-06:

- The session collector is the code project, while the actual raw telemetry
  input root is `$HOME/.agents/otel-collector/data/raw`.
- A narrowed run using only `$HOME/.codex/sessions` plus OTel raw
  files wrote `/tmp/ask-session-collector-spec-evidence.json` and
  `/tmp/ask-session-collector-spec-bundle`.
- That run kept `391942` records across `596` source files, including
  `391759` Codex rollout lines and `183` OTel log lines.
- The rendered artifact reported `200` sessions, source type counts of
  `192` `codex_rollout` sessions and `8` `codex_conversation` sessions, and no
  parser warnings.
- Existing collector evidence layers already emit `skillify-candidates.json`,
  `skill-refactor-evidence.json`, `harness-engineering-evidence.json`,
  `insight-evidence-extension.json`, `solved-problems.json`,
  `redaction-report.json`, `index.json`, and `aggregate.json`.
- Existing skill evidence is currently text-derived mention evidence, not
  native Codex `skill_invocation` analytics. The run reported `simplify: 140`
  and `skill-refactor: 2` as skill mentions, plus `harness-engineering: 3287`
  as plugin mentions.
- Current collector code still defines default rollout roots for
  `~/.codex-red/sessions` and `~/.codex-main/sessions`, and still accepts
  legacy Claude session metadata flags. That conflicts with this spec's narrow
  supported-source contract and must be cleaned up in the collector slice.

Interpretation:

- Core mechanics are healthy enough to build on.
- Diagnostic surfaces are too fragmented for first-contact agent usability.
- Catalog parity drift can block goal routing, so doctor must surface it before
  agents attempt broad goal resolution.
- Surface inventory warnings are useful, but they need a short agent summary
  that distinguishes "known diagnostic debt" from "stop now."
- Native Codex skill analytics can become the strongest low-level signal for
  skill proof because invocation evidence no longer has to be inferred only
  from markdown transcripts or shell history.
- Session collector already provides the right privacy-safe evidence bundle
  shape for downstream consumers, so the implementation should extend the
  existing bundle rather than inventing a parallel ASK-only collector output.
- The first analytics implementation must migrate from mention-derived evidence
  to native invocation-derived evidence without breaking existing
  `skillify`, `skill-refactor`, `insight-report`, and
  `harness-engineering` consumers.

## Core Domain Model

### Golden Path Command

A namespace-first `ask` command that gives an agent a concise decision,
blocker state, and next command while preserving access to deeper evidence.

### Agent Summary

A short field in the standard JSON envelope that states the current decision in
plain language. It is for agents and humans skimming output, not a replacement
for detailed evidence.

### Blocking State

A boolean plus reason list indicating whether progress should stop before the
next stage.

### Next Command

The single primary command the agent should run next. This must not conflict
with `metadata.next_steps`; when both exist, `next_command` is the primary
recommendation and `metadata.next_steps` contains supporting actions.

### Diagnostic Debt

Known warning-level repo state that should stay visible but should not block
unrelated work unless the current change worsens it or strict mode is enabled.

### Product Compression

The behavior of reducing multiple low-level checks into one agent-facing
decision without hiding evidence or weakening validation.

### Skill Invocation Analytics

Native Codex analytics emitted when a skill is explicitly loaded or implicitly
detected during command execution. For this spec, useful attribution fields are:

- `skill_name`
- `skill_id`
- `skill_scope`
- `plugin_id`
- `thread_id`
- `turn_id`
- `invoke_type`
- `model_slug`
- `repo_url`
- `product_client_id`

These fields are observational evidence. They prove that a skill was invoked in
a specific thread and turn; they do not by themselves prove the skill improved
the outcome. Raw identifiers from these events must be hashed or redacted before
they reach normalized collector artifacts or ASK projections.

### Normalized Skill Evidence

Privacy-safe collector output that converts raw local telemetry into a stable
artifact Agent Skills Kit can consume. It may include hashed thread and turn
identifiers, hashed product-client identifiers, skill identity, scope, plugin
attribution, invoke type, model, and source availability status. It must not
expose raw account, email, transcript, or full prompt content.

### Low-Cardinality Telemetry Health

OTel collector aggregate stats that prove whether skill analytics appear in the
raw stream without storing per-thread or per-skill proof detail in `/stats`.
Examples include event counts, last-seen timestamps, invoke-type totals, and
scope totals.

## Skill Analytics Evidence Pipeline

The skill analytics feature must use a three-layer pipeline.

### 1. OTel Collector Layer

`$HOME/.agents/otel-collector` remains the raw telemetry receiver.
It should store raw OTLP payloads in `data/raw/*.ndjson` and may expose only
low-cardinality skill analytics health fields in `/stats`, such as:

- `skill_invocation_event_count`
- `codex_skill_injected_metric_count`
- `skill_invocation_last_seen_at`
- `skill_invocation_by_invoke_type`
- `skill_invocation_by_scope`
- `plugin_backed_skill_invocation_count`

It must not become the proof engine and must not emit high-cardinality
per-thread, per-turn, per-repo, or per-skill proof details in aggregate stats.

### 2. Session Collector Layer

`$HOME/.agents/session-collector` is the canonical normalizer for
this feature. It should read the supported local sources, extract native Codex
`skill_invocation` events when present, preserve legacy skill-mention fallback
signals, and emit privacy-safe normalized evidence.

Supported sources for this slice:

- `~/.agents/otel-collector/data/raw/logs.ndjson`
- `~/.agents/otel-collector/data/raw/traces.ndjson`
- `~/.agents/otel-collector/data/raw/metrics.ndjson`
- `~/.codex/sessions`

Explicitly unsupported sources for this slice:

- Any session metadata root other than `~/.codex/sessions`.

The session collector implementation must remove this feature's default
dependence on:

- `~/.codex-red/sessions`
- `~/.codex-main/sessions`
- Claude session metadata flags or readers

If compatibility for old scripts must remain temporarily, it must be explicit
opt-in, marked deprecated in help text, excluded from the skill-analytics
default path, and covered by a validation test proving those roots are not used
for this feature.

Required normalized evidence fields:

- `analytics_status`
- `evidence_class`
- `thread_id_hash`
- `turn_id_hash`
- `skill_id`
- `skill_name`
- `skill_scope`
- `plugin_id`
- `repo_url_hash`
- `invoke_type`
- `model_slug`
- `product_client_id_hash`
- `source`
- `last_seen_at`
- `source_event_count`
- `collector_artifact_id`

### 3. Agent Skills Kit Layer

Agent Skills Kit consumes normalized collector evidence and turns it into
agent-facing decisions. The default integration path is a generated ASK-local
projection under `.skill-telemetry/**` that is refreshed from a
session-collector artifact. Direct reads from the session-collector project are
allowed only for an explicit developer command or `--collector-artifact` style
override. Canonical parsing of raw telemetry remains in the session collector.

ASK commands must classify analytics evidence separately from validation and
outcome evidence:

- `analytics_status: available`
- `analytics_status: unavailable_or_legacy`
- `evidence_class: reachability_attribution`
- `outcome_proof: missing|stale|present`

ASK must not parse raw telemetry as the default path once a session-collector
artifact is available.

## Evidence Contracts

### Normalized Artifact Shape

The session collector must emit a versioned normalized artifact for Agent
Skills Kit rather than requiring ASK to understand raw telemetry shape. The
artifact may be NDJSON or JSON, but the schema must include:

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-06T00:00:00Z",
  "collector_version": "string",
  "redaction_policy_version": "string",
  "source_file_fingerprints": [],
  "source_status": {},
  "skill_invocations": [],
  "summary": {}
}
```

The canonical artifact names for the first slice are:

- `skill-invocations.json`
- `skill-invocation-summary.json`
- `skill-proof-candidates.json`

`skill-invocations.json` is the detailed normalized record set.
`skill-invocation-summary.json` is the low-detail aggregate an agent can skim.
`skill-proof-candidates.json` is the ASK-oriented projection that maps skill
identity to proof candidates without claiming outcome proof.

These artifacts must be added to the existing session-collector bundle rather
than replacing the current bundle. The bundle must continue to include existing
consumer artifacts:

- `aggregate.json`
- `index.json`
- `skillify-candidates.json`
- `skill-refactor-evidence.json`
- `harness-engineering-evidence.json`
- `insight-evidence-extension.json`
- `solved-problems.json`
- `redaction-report.json`
- `manifest.json`

The bundle `manifest.json` must list the new skill-invocation artifacts, the
collector confidence, limitations, and schema version. Existing consumers must
not need to parse `skill-invocations.json` unless they opt into the new
analytics-backed proof path.

### Field Semantics

Normalized records must use these enum values:

| Field              | Values                                                                         | Meaning                                                                                                |
| ------------------ | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `analytics_status` | `available`, `unavailable_or_legacy`, `source_missing`, `parse_error`, `stale` | Whether native Codex skill analytics are usable for the record or artifact.                            |
| `evidence_class`   | `reachability_attribution`, `legacy_mention`, `collector_health`               | What the evidence can safely prove.                                                                    |
| `source`           | `otel_logs`, `otel_traces`, `otel_metrics`, `codex_session`                    | Which supported source produced the evidence.                                                          |
| `invoke_type`      | `explicit`, `implicit`, `unknown`                                              | Whether Codex loaded the skill explicitly, inferred it from tool use, or could not determine the type. |
| `outcome_proof`    | `missing`, `stale`, `present`                                                  | Whether separate task outcome evidence exists.                                                         |

Missing `turn_id` or `plugin_id` must not make the whole artifact unusable.
Records without those newer Codex fields should be preserved with
`analytics_status: unavailable_or_legacy` or a field-level `null`, and the
summary must count how many records lack each field.

### Privacy and Stability

Raw thread IDs, turn IDs, repo URLs, account identifiers, email addresses, and
prompt text must not appear in normalized artifacts or ASK projections. Hashes
must be deterministic within one artifact generation and stable enough for
de-duplication, but they should not be treated as permanent user identifiers.

The collector must preserve enough provenance for audit:

- `generated_at`
- `collector_version`
- `redaction_policy_version`
- `source_file_fingerprints`
- `source_status`
- `source_record_count`
- `normalized_record_count`
- `parse_error_count`
- `legacy_fallback_count`

### De-Duplication

The collector must de-duplicate duplicate invocation records by the strongest
available tuple:

```text
source + thread_id_hash + turn_id_hash + skill_id + skill_name + invoke_type
```

When `turn_id_hash` is missing, the collector may fall back to source path,
timestamp bucket, skill identity, and invoke type, but it must report that
weaker de-duplication mode in the summary.

### Freshness

The artifact must report freshness with `generated_at`, `last_seen_at`, and
`age_seconds`. Agent Skills Kit decides whether evidence is stale for a command
using command-level thresholds. The session collector should not silently drop
old evidence just because it is stale.

## Agent Decision Contract

Golden-path commands must use the same small state vocabulary so coding agents
can branch without reading command-specific prose.

### Command State

| Field                  | Values                                                 | Contract                                                                                                                                               |
| ---------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `status`               | `success`, `warning`, `error`                          | Existing `ask` envelope status. `warning` means usable with visible non-blocking debt. `error` means the command itself failed or progress is blocked. |
| `blocking`             | `true`, `false`                                        | Whether the agent should stop the current workflow before the next stage.                                                                              |
| `signals.<name>.state` | `pass`, `warn`, `block`, `error`, `unknown`, `skipped` | Machine-readable state for each composed lower-level signal.                                                                                           |
| `blockers[].severity`  | `blocker`, `warning`, `info`                           | Severity used for deterministic ordering and human output.                                                                                             |

`blocking: true` must always have at least one blocker with
`severity: blocker`. `blocking: false` may still include warning or info entries
inside `diagnostic_debt`, but not inside primary blockers unless the command
contract explicitly marks them non-blocking.

### Stable Blocker IDs

The first slice must use stable IDs for the composed doctor signals:

- `repo_status`
- `catalog_parity`
- `runtime_budget`
- `command_handles`
- `repo_surface`
- `projection_sync`
- `unknown_signal_error`

Future golden-path commands may add IDs, but they must not rename these without
a compatibility note and regression test.

### Primary Next Command Selection

Each command must return exactly one primary `next_command`, or `null` only when
there is deliberately no follow-up action. Selection must be deterministic for
the same inputs:

1. Choose the first blocking item by severity priority, then stable blocker ID.
2. If there is no blocker, choose the highest-priority warning that has a
   concrete repair or inspection command.
3. If there is no blocker or actionable warning, choose the command's normal
   continuation command.
4. Put alternate commands in `metadata.next_steps` or command-specific detail,
   not in `next_command`.

For `ask repo doctor`, the normal continuation command after a clean or
warning-only state is:

```bash
./bin/ask skills improve "<goal>" --json --robot
```

If the user has not supplied a goal, doctor should use a concrete inspection
command instead of inventing a goal:

```bash
./bin/ask repo status --json --robot
```

## Implementation Slices

The golden path and analytics evidence work should be sliced so each project can
ship independently without corrupting ownership boundaries.

### Slice A: Evidence Discovery

- Confirm where native Codex `skill_invocation` events and
  `codex.skill.injected` metrics appear in the local telemetry stream.
- Add fixtures for the current Codex event shape, including records with
  `plugin_id`, `turn_id`, both fields missing, and malformed payloads.
- Do not change ASK proof behavior in this slice except to document source
  availability.

### Slice B: Session Collector Normalization

- Add normalized skill invocation artifact generation.
- Extend the existing evidence bundle with `skill-invocations.json`,
  `skill-invocation-summary.json`, and `skill-proof-candidates.json` instead of
  replacing existing bundle artifacts.
- Preserve legacy mention extraction as `evidence_class: legacy_mention`.
- Enforce the narrow supported-source contract.
- Remove default scanning of `~/.codex-red/sessions` and
  `~/.codex-main/sessions` from the skill-analytics path.
- Remove or deprecate Claude session metadata flags so they cannot participate
  in this feature by accident.
- Add tests for native analytics, legacy-only sessions, source-missing state,
  parse errors, duplicate records, and stale artifacts.
- Add regression tests that existing bundle consumers still receive
  `skillify-candidates.json`, `skill-refactor-evidence.json`,
  `harness-engineering-evidence.json`, `insight-evidence-extension.json`, and
  `solved-problems.json`.

### Slice C: OTel Collector Health

- Preserve raw NDJSON capture.
- Add low-cardinality skill analytics health in `/stats` only when native
  events or metrics are present.
- Add tests that reject raw thread, turn, repo, prompt, account, and email
  values from `/stats`.

### Slice D: Agent Skills Kit Analytics Projection

- Add an ASK-local generated projection under `.skill-telemetry/**`.
- Refresh it from the session-collector artifact rather than parsing raw
  telemetry.
- Make `ask skills prove` consume the projection as reachability attribution
  evidence only.
- Report stale, missing, and unavailable analytics without failing structural
  proof.

### Slice E: Golden Path Commands

- Implement `ask repo doctor` and shared envelope fields first.
- Implement `ask skills improve`, `ask skills explain`, `ask skills prove`, and
  `ask repo closeout --changed` incrementally after the envelope is stable.
- Keep each command backed by lower-level helpers so detailed diagnostics remain
  available.

## Main Flow / Lifecycle

### 1. Doctor

Before work, an agent runs:

```bash
./bin/ask repo doctor --json --robot
```

The command composes repo status, catalog parity, runtime budget, handle health,
surface policy, and known blockers into one envelope.

### 2. Improve

When the user gives a goal, an agent runs:

```bash
./bin/ask skills improve "<goal>" --json --robot
```

The command maps the goal to candidate capabilities, required validation,
possible sync actions, and one next command.

### 3. Explain

Before loading a target capability body or changing source, an agent runs:

```bash
./bin/ask skills explain <skill-or-handle> --json --robot
```

The command explains what the capability does, when to use it, when not to use
it, canonical source, generated handle, runtime visibility, and validation.

### 4. Prove

Before claiming a capability is reliable, an agent runs:

```bash
./bin/ask skills prove <skill-or-goal> --json --robot
```

The command separates reachability, structural quality, and outcome proof.

### 5. Closeout

Before claiming work is done, an agent runs:

```bash
./bin/ask repo closeout --changed --json --robot
```

The command infers changed files, sync needs, focused validation, diagnostic
debt, and commit readiness.

## Interfaces and Dependencies

### Shared Golden-Path Envelope

Each golden-path command must use the standard `ask` envelope and include:

```json
{
  "status": "success|warning|error",
  "metadata": {
    "next_steps": []
  },
  "data": {
    "<command_key>": {
      "agent_summary": "string",
      "blocking": false,
      "blockers": [],
      "next_command": "string|null"
    }
  },
  "errors": []
}
```

Command-specific data may be richer, but these fields are required.

### `ask repo doctor`

Required composed signals:

- repo status
- dirty state when available
- skills sync status
- catalog parity status
- runtime budget status and advisories
- command-handle status
- repo surface status and diagnostic debt summary
- strict-mode distinction between blocking failures and known warnings

### `ask skills improve`

Required composed signals:

- original goal
- interpreted goal summary
- candidate capabilities with confidence and rationale
- catalog parity prerequisite status
- required validation commands
- sync actions, if any
- next command, usually `ask skills explain <candidate>`

### `ask skills explain`

Required composed signals:

- query
- canonical source path
- generated command handle path, if present
- runtime visibility
- owner/root router
- when to use
- when not to use
- validation commands
- overlap or ambiguity notes

### `ask skills prove`

Required composed signals:

- reachability proof
- structural audit or strict audit status
- invocation evidence by hashed thread ID, hashed turn ID, `skill_name`,
  `skill_scope`, `plugin_id`, and `invoke_type`, when normalized collector
  evidence is available
- workout/eval/outcome proof status
- stale or missing proof classification
- next command to obtain missing proof

### ASK Skill Telemetry Projection

Required generated projection behavior in `$HOME/dev/agent-skills`:

- Projection path: `.skill-telemetry/**`.
- Projection ownership: generated runtime evidence, not canonical source.
- Inputs: session-collector normalized artifacts only, unless an explicit
  developer override supplies a one-off artifact path.
- Outputs: proof-oriented summaries keyed by skill identity, canonical path when
  resolvable, generated handle when present, and analytics status.
- Staleness: report artifact age and source `last_seen_at`; do not delete stale
  evidence automatically.
- Privacy: preserve only hashed identifiers and aggregate counts.

### Session Collector Skill Evidence

Required changes in `$HOME/.agents/session-collector`:

- Parse native Codex `skill_invocation` events from supported local telemetry
  sources when present.
- Preserve existing text-level `skill_mentions` as a legacy fallback, not as
  equivalent proof.
- Emit normalized privacy-safe skill invocation evidence and summary counts.
- Add the new skill-invocation artifacts to the existing bundle writer and
  manifest.
- Keep current downstream bundle artifacts stable for `skillify`,
  `skill-refactor`, `insight-report`, and `harness-engineering`.
- Include source availability and legacy/unavailable status in the output.
- Keep the first slice limited to `~/.agents/otel-collector/data/raw/*.ndjson`
  and `~/.codex/sessions`.
- Remove default source resolution for `~/.codex-red/sessions` and
  `~/.codex-main/sessions` from this feature.
- Remove, or keep as explicitly deprecated opt-in only, legacy Claude session
  metadata CLI flags. If retained, validation must prove those flags do not
  affect the default skill-analytics output.
- Expose input-window counts for `logs`, `traces`, `metrics`, and
  `codex_rollout`, mirroring the current rendered artifact shape.

### OTel Collector Skill Health

Required changes in `$HOME/.agents/otel-collector`:

- Preserve raw NDJSON capture of any native Codex analytics payloads.
- Add only low-cardinality aggregate visibility for skill analytics if the raw
  stream contains those events or metrics.
- Keep `/stats` privacy-safe and avoid per-thread, per-turn, per-repo, or
  per-skill high-cardinality detail.
- Keep detailed analytics extraction delegated to the session collector.

### `ask repo closeout --changed`

Required composed signals:

- changed files
- generated surfaces requiring sync
- focused validation commands
- diagnostic debt summary
- commit readiness
- next command

## Command Naming Compatibility

The product command in this spec is `ask skills prove`, matching the parent
golden-path contract. Implementation must verify the live `./bin/ask` parser
before changing docs or command behavior, because the code may contain internal
variables or legacy names such as "proof" even when the public command is
"prove".

If both `prove` and `proof` exist or are introduced for compatibility, exactly
one must be documented as canonical. The non-canonical form must either:

- return a correction through the existing `ask` command-correction behavior, or
- act as a compatibility shim that emits the canonical command in
  `next_command` and docs metadata.

The two forms must not diverge in output shape, proof classification, or
validation behavior.

## Invariants / Safety Requirements

- Golden-path commands must not hide blockers in long JSON.
- `next_command` must be deterministic for the same repo state and inputs.
- Known diagnostic repo-surface debt must remain visible.
- Catalog parity drift must block goal routing and closeout until resolved or
  explicitly classified as non-blocking by a command contract.
- Runtime projection and generated command handles must remain regenerate-only.
- `ask skills prove` must never label structural audit as outcome proof.
- `ask skills prove` must never label skill invocation analytics as outcome
  proof. Invocation analytics are reachability and attribution evidence unless
  joined to task outcome, validation, or review evidence.
- Session collector normalized analytics must hash or redact raw thread IDs,
  turn IDs, repo URLs, account identifiers, email addresses, and prompt content
  before exposing downstream artifacts.
- OTel collector `/stats` must remain low-cardinality and must not expose raw
  thread, turn, repo, prompt, account, or email values.
- This slice must not read or depend on session metadata roots outside the
  supported Codex source contract.
- ASK must not parse raw telemetry as the default path once a session-collector
  normalized artifact exists.
- ASK-local `.skill-telemetry/**` files are generated projections and must not
  become the canonical source of truth.
- `ask skills prove` must tolerate older Codex analytics that lack `turn_id` or
  `plugin_id` and classify them without crashing or dropping all evidence.
- `ask repo closeout --changed` must not create commits or edit files.
- Human-readable output and JSON output must agree on blocker state.

## Failure Model and Recovery

| Failure                                                                 | Required Recovery                                                                                                                                                                  |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Catalog parity drift blocks goal routing                                | `./bin/ask repo doctor --json --robot` reports exact drift and recommends `./bin/ask repo doctor-catalog --json --robot` or the precise sync/source-doc repair command.            |
| Runtime budget advisory exceeds threshold                               | Command returns warning with visible advisory and continues unless strict mode is enabled.                                                                                         |
| Handle collisions or unresolved handles exist                           | Doctor blocks and recommends `./bin/ask skills handles --check --json --robot`.                                                                                                    |
| Repo surface warning has many findings                                  | Doctor summarizes counts and recommends `./bin/ask repo surface --json --robot`; unrelated work may continue unless strict mode or changed files touch the debt.                   |
| Goal is too broad                                                       | `./bin/ask skills improve "<goal>" --json --robot` asks for narrower goal context and returns no fake candidate.                                                                   |
| Capability proof is missing                                             | `./bin/ask skills prove <skill-or-goal> --json --robot` returns `proof_status: missing` and a concrete audit/workout/eval command.                                                 |
| Codex analytics are unavailable or do not contain `turn_id`/`plugin_id` | `./bin/ask skills prove <skill-or-goal> --json --robot` falls back to reachability, audit, workout, and transcript evidence and reports `analytics_status: unavailable_or_legacy`. |
| Native skill analytics exist only in raw OTel payloads                  | Session collector normalizes them into privacy-safe skill evidence before Agent Skills Kit consumes them.                                                                          |
| Native skill analytics are absent from local telemetry                  | Session collector reports `analytics_status: unavailable_or_legacy`; Agent Skills Kit does not claim invocation evidence.                                                          |
| Raw telemetry record is malformed                                       | Session collector records a parse warning, increments `parse_error_count`, preserves other valid records, and emits `analytics_status: parse_error` at artifact or record level.   |
| Collector artifact is stale                                             | ASK reports stale evidence, keeps proof classification conservative, and recommends the refresh command rather than silently ignoring the artifact.                                |
| Duplicate events exist for the same skill and turn                      | Session collector de-duplicates by source, hashed thread, hashed turn, skill identity, and invoke type, then reports duplicate counts.                                             |
| Multiple collector artifacts are available                              | ASK selects the newest artifact by `generated_at` unless an explicit artifact path is provided, and reports the selected path.                                                     |
| OTel stats receive high-cardinality skill data                          | Implementation is rejected; detailed proof belongs in session collector artifacts, not `/stats`.                                                                                   |
| Unsupported source roots are configured for this feature                | Validation fails if the skill-analytics pipeline depends on any session metadata root outside the supported Codex source contract.                                                 |
| Changed files require projection sync                                   | Closeout blocks commit readiness and returns the required sync command.                                                                                                            |

## Observability

Every golden-path command must expose:

- `trace_id`
- command name
- latency
- `agent_summary`
- `blocking`
- blocker codes
- `next_command`
- source commands or helper checks used to compose the result
- analytics availability for skill proof and improvement ranking
- collector source availability for supported OTel raw files and
  `~/.codex/sessions`
- explicit unsupported-source exclusion status for session metadata roots outside
  the supported Codex source contract
- selected collector artifact path, when proof uses normalized analytics
- collector artifact `generated_at`, `collector_version`, and
  `redaction_policy_version`
- normalized evidence counts, duplicate counts, parse error counts, and legacy
  fallback counts

Telemetry must not include secrets, raw transcripts, or full user prompts beyond
the command input needed for local routing.

## Acceptance and Test Matrix

| ID   | Acceptance Criteria                                                                                                                                                                | Validation                                                                                                       |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| SA1  | `ask repo doctor --json --robot` composes repo status, catalog parity, runtime budget, handle health, and surface policy into one envelope.                                        | Unit or integration test asserts required fields and one `next_command`.                                         |
| SA2  | Doctor reports README/catalog count drift as a blocker with exact affected surface when parity is broken.                                                                          | Fixture or live test with mismatched catalog count.                                                              |
| SA3  | Doctor distinguishes warning-level diagnostic debt from strict-mode blockers.                                                                                                      | Test default mode and strict mode against repo surface warning fixture.                                          |
| SA4  | `ask skills improve "<goal>" --json --robot` returns candidate capabilities only after catalog parity is healthy.                                                                  | Test blocked parity and healthy routing paths.                                                                   |
| SA5  | `ask skills improve` returns one primary next command and separates validation from sync actions.                                                                                  | JSON schema/envelope test.                                                                                       |
| SA6  | `ask skills explain <handle>` resolves generated handles to canonical source and states runtime visibility.                                                                        | Test against `he-spec` or another known command handle.                                                          |
| SA7  | `ask skills prove <skill-or-goal>` separates reachability, structural quality, and outcome proof.                                                                                  | Test missing, stale, and present proof states.                                                                   |
| SA8  | `ask skills prove` uses normalized collector-backed native Codex skill invocation analytics as attribution evidence when available and reports legacy/unavailable status when not. | Fixture with normalized `skill_invocation` evidence containing hashed turn/thread IDs and `plugin_id`.           |
| SA9  | Session collector emits privacy-safe normalized skill invocation evidence from supported sources and preserves legacy skill mentions as fallback only.                             | Session-collector tests with native analytics, legacy mention-only, and unavailable-source fixtures.             |
| SA10 | Skill analytics source coverage is limited to OTel raw NDJSON and `~/.codex/sessions`; other session metadata roots are not used for this slice.                                   | Session-collector config/source-resolution test asserts unsupported roots are absent.                            |
| SA11 | OTel collector exposes only low-cardinality skill analytics health counts when native events or metrics are present.                                                               | OTel collector stats test asserts counts/last-seen fields and rejects raw thread/turn/repo values.               |
| SA12 | `ask repo closeout --changed --json --robot` reports changed files, sync needs, focused validation, diagnostic debt, and commit readiness without editing or committing.           | Integration test in temporary worktree with controlled changes.                                                  |
| SA13 | All golden-path commands include `agent_summary`, `blocking`, `blockers`, and `next_command`.                                                                                      | Shared envelope test across command keys.                                                                        |
| SA14 | README or product docs show the golden-path command sequence before deeper command inventory.                                                                                      | Docs lint plus content assertion.                                                                                |
| SA15 | Skill analytics normalization tolerates older Codex events without `turn_id` or `plugin_id` and malformed records without dropping valid evidence.                                 | Session-collector compatibility and parse-error fixtures.                                                        |
| SA16 | ASK consumes generated `.skill-telemetry/**` projections by default and does not parse raw telemetry when a normalized artifact exists.                                            | ASK proof test with raw source present and projection fixture selected.                                          |
| SA17 | `ask skills prove` and any compatibility spelling such as `proof` cannot diverge in envelope, proof classification, or documented canonical command.                               | CLI parser and command-correction tests.                                                                         |
| SA18 | Normalized analytics artifacts and OTel `/stats` never expose raw thread IDs, turn IDs, repo URLs, account identifiers, email addresses, or prompt text.                           | Privacy/redaction tests across collector artifacts and stats output.                                             |
| SA19 | Session collector keeps existing bundle artifacts stable while adding skill-invocation artifacts and manifest entries.                                                             | Session-collector bundle regression test asserts old and new artifact filenames are present.                     |
| SA20 | Session collector default source resolution excludes `~/.codex-red/sessions`, `~/.codex-main/sessions`, and Claude session metadata from this feature.                             | Session-collector CLI/config tests assert default source list and help text match the supported-source contract. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs         | Traceability note                                                                                                                                                             |
| ------------ | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JSC-246      | SA1, SA2, SA3          | Implements composed product health, catalog-parity blocker surfacing, and strict/default diagnostic behavior promised by the parent spec.                                     |
| JSC-246      | SA4, SA5               | Makes goal-to-capability routing reliable only when prerequisites are healthy and returns one primary next action.                                                            |
| JSC-246      | SA6, SA7, SA8          | Makes generated handles understandable, preserves the reachability/quality/outcome proof distinction, and uses normalized Codex invocation analytics as attribution evidence. |
| JSC-246      | SA9, SA10, SA11        | Adds the companion collector contracts for normalized session evidence, narrow source scope, and low-cardinality OTel health.                                                 |
| JSC-246      | SA12, SA13             | Creates the agent-native closeout contract and standardizes the command envelope agents can depend on.                                                                        |
| JSC-246      | SA14                   | Makes the product front door match the intended golden path.                                                                                                                  |
| JSC-246      | SA15, SA16, SA17, SA18 | Hardens analytics compatibility, ASK projection ownership, command naming, and privacy guarantees.                                                                            |
| JSC-246      | SA19, SA20             | Keeps collector-backed evidence backward-compatible while removing unsupported default source roots.                                                                          |

## Technical Review Checklist

Before planning or implementing this spec, review the resulting plan and diffs
against these checks:

- Source ownership: raw telemetry parsing stays in session collector; ASK owns
  product decisions and generated projections only; OTel owns raw ingest and
  low-cardinality health only.
- Privacy: no raw IDs, repo URLs, accounts, emails, prompt text, or transcripts
  are exposed in ASK projections or `/stats`.
- Cardinality: OTel `/stats` remains aggregate-only and cannot grow per thread,
  per turn, per repo, or per skill.
- Compatibility: older Codex analytics without `turn_id` or `plugin_id` remain
  parseable and are classified as partial or legacy evidence.
- Proof semantics: invocation analytics are reachability attribution, not
  outcome proof.
- Determinism: every golden-path command returns one deterministic
  `next_command` for the same input state.
- Command contract: `prove` is canonical unless implementation discovers a
  stronger existing public contract; any compatibility spelling is tested.
- Failure behavior: malformed records, missing sources, stale artifacts, and
  duplicate events produce conservative summaries instead of crashes.
- Testing: each project gets focused tests at its ownership boundary before any
  cross-project integration claim is made.
- Collector compatibility: existing bundle consumers still receive their current
  artifact files after skill-invocation artifacts are added.
- Source scope: session-collector defaults do not include Codex Red, Codex Main,
  or Claude metadata roots for this feature.
- Rollback: disabling analytics proof must leave doctor, improve, explain,
  closeout, structural audit, and legacy proof behavior usable.

## Planning-Ready First Slice

First implementation should target `ask repo doctor` and the shared
golden-path envelope fields.

Minimum first slice:

- Compose existing `repo status`, `repo doctor-catalog`, `runtime budget`,
  `skills handles --check`, and `repo surface` helpers.
- Return `agent_summary`, `blocking`, `blockers`, and `next_command`.
- Preserve strict-mode behavior.
- Add tests for healthy state, catalog parity drift, and surface warning debt.
- Update the smallest README/product-doc section needed to advertise doctor as
  the first agent command.
- Defer collector implementation to a separate slice unless planning chooses to
  start with analytics proof before doctor.

Do not implement all five golden-path commands in one slice unless planning
proves the shared envelope can be added safely without widening behavior. The
collector analytics slices may proceed independently, but they must not require
ASK to claim analytics-backed proof before normalized artifacts and privacy
tests exist.

## Open Questions

- Should `ask repo doctor` automatically run `repo doctor-catalog`, or should
  catalog parity become a reusable helper called by both commands?
- Should README hardcoded skill counts be generated, removed, or linted against
  canonical count during closeout?
- What proof artifact path should become canonical for `ask skills prove`:
  workouts, evals, generated proof summaries, or a combined index?
- Should `ask repo closeout --changed` treat existing repo surface debt as
  warning by default even when changed files are under `Docs/**`?
- What telemetry is enough to justify later top-level aliases?

## Definition of Done

- A planning artifact exists that sequences the first implementation slice.
- `ask repo doctor --json --robot` exists and satisfies SA1-SA3 for the
  first slice.
- Shared envelope behavior satisfies SA13 for every implemented golden-path
  command.
- The catalog parity drift class from the critique is surfaced as a precise
  doctor blocker.
- The command output gives agents one primary next command.
- README or product docs show the golden path before lower-level diagnostics.
- Companion collector responsibilities are documented with the narrow source
  contract and unsupported-source exclusions.
- Session collector bundle compatibility is preserved while native
  skill-invocation artifacts are added.
- Unsupported default roots are removed from the skill-analytics source path.
- Analytics proof work documents the `.skill-telemetry/**` generated projection
  boundary before implementation.
- Focused tests pass for the implemented command behavior.
- Technical review finds no unresolved P1 issues against the checklist above.
- Validation evidence records exact commands and outcomes.

## Handoff to `he-plan`

Use `he-plan` to produce an implementation plan for the first slice only:

```text
Implement ask repo doctor and the shared golden-path envelope fields for
Agent-First Golden Path Product Compression, preserving existing lower-level
diagnostic commands and using JSC-246 for traceability.
```

Planning must begin by confirming the current catalog parity state and deciding
whether the README count drift is fixed inside the first slice or treated as a
precondition blocker.
