---
schema_version: 1
artifact_type: sdk_strategy
status: implementation_ready
date: 2026-05-20
repo: agent-skills
primary_contract: Infrastructure/config/schemas/skill-doctor.v1.schema.json
extraction_contract: Infrastructure/config/skills-sdk.json
---

# Agent Skills Kit SDK North Star

## BLUF

Agent Skills Kit should become a professional, agent-native SDK for Codex
skills. The first implementation boundary is additive: register
`./bin/ask skills doctor <handle> --json --robot` as the stable readiness
facade over existing `skills prove`, `skills proof`, `skills explain`,
audit, and future package signals. Do not move or deprecate existing
`prove`/`proof` semantics in RF-1.

## Source Of Truth

Implementation truth lives in executable surfaces, in this order:

1. `Infrastructure/config/skills-sdk.json`
2. `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
3. `./bin/ask skills doctor <handle> --json --robot`
4. focused command/parser/help/guided-error parity tests
5. doctor fixtures for `context7` and one non-`context7` skill class
6. `.harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md`
7. closeout evidence with exact commands and pass/fail/blocked outcomes

Markdown and HTML artifacts are maps over those surfaces. They are not allowed
to create parallel requirements.

## Operating Shape

- Thin surface: one small public doctor command for readiness.
- Strong guardrails: schema, fixtures, status precedence, and rollback rules.
- Durable memory: eval feedback becomes classified deltas with rerun evidence.
- Professional output: every readiness claim names evidence and a safe next
  command.

## Deep Module Contract

RF-1 is a deep-module move only if callers learn one interface and the
coordination stays behind it:

- Public interface: `./bin/ask skills doctor <handle> --json --robot` and the
  `skill-doctor.v1` payload.
- Owner module: the `ask skills` command surface delegates to a doctor service;
  callers do not compose readiness from skill source files, projections,
  package folders, audits, and eval artifacts themselves.
- Hidden implementation: source resolution, runtime reachability, structural
  audit, package-readiness availability, outcome proof, status precedence, and
  `next_command` selection live behind the doctor seam.
- Seam tests: action parity, schema snapshots, status precedence, and a second
  non-`context7` fixture must pass before the boundary is agent-safe.
- Safety classification: current state is `risky` because the interface is
  planned but unregistered; RF-1 is accepted only when the same boundary is
  executable and covered by seam tests.

## Layered Module Map

Use a layered domain map for the SDK so the repo is easier for humans and
agents to navigate:

- Types: schemas, status vocabulary, command metadata, package metadata, and
  compatibility rules.
- Config: permission profiles, validation policy, runtime profiles, and
  repository-owned execution defaults.
- Repo: canonical `Skills/**`, `Plugins/**`, `.harness/**`, and source
  artifacts.
- Providers: source/projection/package/eval readers that adapt repo state into
  typed inputs.
- Service: deep SDK modules such as doctor, package-doctor, profiles, events,
  routing, and compatibility checks.
- Runtime: `./bin/ask`, generated projections, plugin mirrors, and future
  app-server/CI execution contexts.
- UI: thin human-facing docs, browser visuals, and summaries over the
  machine-readable contract.
- Utils: shared parsing, filesystem, JSON/schema, command, and formatting
  helpers that do not own product rules.

Dependencies should flow through interfaces: repo/config/types feed providers;
providers feed services; services feed runtime; runtime feeds UI and harness
consumers. Cross-cutting observability and eval feedback may read all layers,
but must report through structured events, eval artifacts, and closeout
evidence rather than private module state.

## Project-Local Skill Roots

The SDK should support project-local skills without confusing source ownership:

- Agent Skills standard compatibility means a skill directory contains one
  `SKILL.md` manifest plus optional `scripts/`, `references/`, `assets/`,
  and eval files. The standard defines package contents, not a single
  mandatory filesystem root.
- `.agents/skills/` is the interoperable project/user discovery convention for
  cross-client skills.
- `.codex/skills/` is a Codex-native client root, not the generic Agent Skills
  standard path.
- In this repository, `.agents/skills/**` remains generated runtime projection.
  Do not hand-edit it.
- In another owner repo, `.agents/skills/**` or `.codex/skills/**` may be
  canonical only when that repo's `skills-sdk.json` declares the root as
  `canonical_project_source`.
- Project-local skills are evaluated in place. Evidence is written to the owner
  repo, for example `.harness/session-evidence/skills/<skill>/`, rather than
  copying the skill into `agent-skills`.

`Infrastructure/config/skills-sdk.json` is the machine-readable source for this
root-classification policy.

## Project-Local Lifecycle

The SDK should be the tool that creates, installs, and updates project-local
skills. A filesystem write is not enough. Each lifecycle command must finish
with eval evidence and an explicit promotion decision.

Project-local skills are saved in the owner repo, under the root declared by
that repo's `skills-sdk.json`:

- Skill source: `<owner-repo>/<declared-root>/<skill-handle>/`.
- Portable Agent Skills evals: `<owner-repo>/<declared-root>/<skill-handle>/evals/evals.json`.
- SDK eval extensions: `<owner-repo>/.harness/evals/skills/<skill-handle>/`.
- Run evidence: `<owner-repo>/.harness/session-evidence/skills/<skill-handle>/<eval-run-id>/`.
- Lifecycle events: `<owner-repo>/.harness/session-evidence/skills/<skill-handle>/<eval-run-id>/events.jsonl`.

The post-RF-1 reserved lifecycle surfaces are listed here so naming stays
consistent, but they are not required for RF-1 implementation or acceptance:

- `./bin/ask skills create <handle> --project <owner-repo> --root <declared-root> --eval-gate full --json --robot`
- `./bin/ask skills install <source> --project <owner-repo> --root <declared-root> --eval-gate install-smoke --json --robot`
- `./bin/ask skills update <handle> --project <owner-repo> --eval-gate regression --json --robot`

Create must generate a realistic eval suite before promotion. Install must prove
provenance, namespace, manifest, permission profile, and smoke behavior. Update
must compare the candidate against the owner baseline and record promote,
rollback, or blocked with exact before/after evidence.

RF-1 acceptance must not implement these lifecycle commands unless the Linear
issue is explicitly rescoped. RF-1 should only avoid vocabulary and schema
choices that would conflict with them later.

## Runtime Targets

Keep local and hosted skill execution targets separate:

- OpenAI local shell skills use local descriptors: `name`, `description`, and
  `path`.
- OpenAI hosted shell skills use uploaded, versioned `skill_reference` bundles.
- Sandbox Agents can materialize skills into a workspace when the agent needs
  files, commands, artifacts, or resumable state.
- Codex runtime projection exposes governed skills to local Codex sessions
  without turning generated handles into editable source.

The SDK may emit adapters for these targets later, but RF-1 remains limited to
the doctor facade and evidence contract.

## Codex Runtime Alignment

The adjacent `~/dev/codex` runtime is moving toward structured, inspectable
agent work: package layout detection, session-start skill/plugin warmup,
permission profile APIs, app-server enablement, durable goal storage, async
approval contributors, async turn item processing, turn-start metadata,
`SubagentStart` hooks, remote environment registration, remote compaction
timeouts, raw exec-output preservation, encrypted function output, and
namespaced/deferred subagent tools.

Agent Skills Kit should align to those behaviors as contracts, not by copying
Codex internals:

- Package contract: skills are buildable, inspectable, projected, warmed,
  smoke-tested packages, not loose Markdown folders.
- Enablement contract: `available`, `installable`, `installed`,
  `projected`, `enabled`, `warmed`, `runnable`, and `validated` are
  separate states.
- Permission contract: every operational skill declares a permission profile,
  uses canonical `deny`, and can be checked for declared-versus-observed
  drift.
- Environment contract: skills declare local, optional-local, remote, CI, and
  app-server compatibility instead of assuming Jamie's laptop.
- Async contract: approvals, deferred contributors, remote compaction, and
  resumed work use explicit states rather than being collapsed into generic
  pass/fail.
- Goal contract: goal-managed skills bind to a durable `goal_ref` or state
  that no durable goal is required; Linear issue, chat summary, and plan item
  are linked context, not goal truth.
- Delegation contract: every subagent start has a role, reason, expected
  artifact, parent run, timeout, artifact-written event, and parent
  integration status.
- Evidence contract: command-backed claims keep raw output references,
  redaction status, parsed result, summary, and blocker classification.
- Warmup contract: session-start warmup loads only routing metadata and compact
  execution boundaries; deep references stay lazy.

These are post-RF-1 SDK imports. RF-1 should not widen beyond the doctor seam,
but the doctor output should avoid names that conflict with these future
states.

## Eval Compatibility

Use the Agent Skills eval pattern as the portable baseline: `evals/evals.json`
with realistic prompts, expected outputs, optional files, assertions, and
with-skill versus without-skill or previous-skill comparisons. SDK-specific
extensions may add trace IDs, lifecycle events, tool calls, guardrails,
permission profiles, namespaces, provenance, telemetry confidence, and
promotion decisions, but only as structured evidence fields.

## Observability Feedback Loop

The SDK should improve through use. RF-1 starts the loop by making doctor
output and eval evidence structured; RF-2+ should add lifecycle events for
command runs, tool calls, package checks, projections, eval outcomes, and
subagent starts.

The loop is: run skill or doctor command, capture logs/metrics/traces/events,
query and correlate evidence, classify the failure or improvement opportunity,
apply the smallest source change, rerun the workload/eval, and promote or
roll back with before/after evidence.

Existing local adapters can supply this evidence without becoming the SDK core:

- `${HOME}/.agents/otel-collector` receives local OTLP HTTP logs,
  traces, and metrics on `127.0.0.1:4318`, writes raw NDJSON, and exposes
  `/health`, `/stats`, freshness, service contribution, and telemetry
  confidence signals.
- `${HOME}/.agents/session-collector` reads OTEL raw payloads plus
  Codex rollout sessions and emits privacy-safe session summaries, skill
  invocation analytics, proof candidates, and Harness Engineering evidence.
- Agent Skills Kit should consume those outputs through an evidence-provider
  seam. It should not require either collector to be running before the RF-1
  doctor contract can return schema-valid output.
- `Infrastructure/config/skills-sdk.json` names the specific fields to extract
  from doctor output, command surfaces, eval artifacts, Linear, and optional
  collector evidence.

## RF-1 Decision

RF-1 creates `skills doctor` as an additive facade. Existing `skills prove`
and `skills proof` remain valid comparison and compatibility surfaces.

RF-1 is green to implement only when the plan requires:

- parser/help/guided-error action parity;
- schema validation against `skill-doctor.v1`;
- phase A registration proof before phase B contract proof;
- `context7` plus one additional skill-class fixture;
- schema-valid package-readiness evidence as `not_run` with an unavailable
  command-surface explanation until a real package seam exists;
- rollback that preserves the doctor seam after acceptance unless an emergency
  waiver reopens RF-1.
