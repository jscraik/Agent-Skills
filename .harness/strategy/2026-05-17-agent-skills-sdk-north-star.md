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

- `/Users/jamiecraik/.agents/otel-collector` receives local OTLP HTTP logs,
  traces, and metrics on `127.0.0.1:4318`, writes raw NDJSON, and exposes
  `/health`, `/stats`, freshness, service contribution, and telemetry
  confidence signals.
- `/Users/jamiecraik/.agents/session-collector` reads OTEL raw payloads plus
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
