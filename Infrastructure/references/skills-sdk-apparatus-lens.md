---
schema_version: 1
artifact_type: sdk_apparatus_lens
status: implementation_ready
date: 2026-05-20
schema: Infrastructure/config/schemas/skill-doctor.v1.schema.json
extraction_contract: Infrastructure/config/skills-sdk.json
---

# Skill SDK Apparatus Lens

## Purpose

This lens defines what counts as proof for the first Skill SDK readiness seam.
It keeps the SDK agent-native: schema, command output, fixtures, evals, and
validation evidence outrank prose review.

## Boundary Safety Rule

`skills doctor` is agent-safe only after both halves of the deep module exist:
a stable public interface and executable seam proof. Until
`./bin/ask skills doctor <handle> --json --robot` dispatches and the RF-1
schema/action/fixture tests pass, the boundary remains risky even if the docs
and schema are coherent.

## Observability And Eval Feedback Rule

Skill improvement must be evidence-driven. A doctor/eval finding becomes a
SDK improvement only when it records the observed behavior, affected source
paths, rerun command, before/after evidence, and promotion or rollback
decision. RF-1 proves this through doctor output, fixtures, and eval closeout;
RF-2+ can add logs, metrics, traces, hook events, tool events, package events,
projection events, and subagent lifecycle events as first-class evidence.
The existing local `~/.agents/otel-collector` and `~/.agents/session-collector`
projects can be adapted as evidence providers for those later slices, but RF-1
must degrade cleanly when collector evidence is absent or stale.
`Infrastructure/config/skills-sdk.json` is the extraction contract for those
fields and provider surfaces.

## Project-Local Skill Root Rule

Agent Skills compatibility is a package-format claim, not a source-ownership
claim. A compliant skill has a `SKILL.md` manifest and optional supporting
directories such as `scripts/`, `references/`, and `assets/`; that does not
make every `.agents/skills/**` path editable source.

For SDK checks:

- `.agents/skills/` is the cross-client interoperable discovery convention.
- `.codex/skills/` is a Codex-native client-specific discovery root.
- In this repository, `.agents/skills/**` is generated runtime projection.
- In another owner repo, `.agents/skills/**` or `.codex/skills/**` is
  canonical only when the owner repo's `skills-sdk.json` declares the root as
  `canonical_project_source`.
- Project-local skills are evaluated in place and write evidence to the owner
  repo. Copying them into `agent-skills` is not proof and should be treated as
  drift unless an explicit migration says otherwise.

## Project-Local Lifecycle Rule

Project-local skills are created, installed, and updated by SDK lifecycle
commands. The SDK should save the skill source in the owner repo at
`<declared-root>/<skill-handle>/`, keep the portable Agent Skills eval suite at
`<declared-root>/<skill-handle>/evals/evals.json`, and write SDK eval
extensions plus run evidence under the owner repo's `.harness/` paths.

Lifecycle completion is eval-gated:

- Create: generate realistic starter evals, run the full gate, then promote or
  leave blocked.
- Install: verify provenance, namespace, manifest, permissions, and smoke
  behavior before enabling.
- Update: compare candidate behavior against the owner baseline, then record
  promote, rollback, or blocked with before/after evidence.

## Runtime Target Rule

The SDK must distinguish local skill discovery from hosted skill packaging:

- Local shell targets use `name`, `description`, and filesystem `path`.
- Hosted shell targets use uploaded, versioned `skill_reference` bundles.
- Sandbox agent targets may materialize skills into a workspace when file,
  shell, artifact, or resumable-state work is required.
- Codex runtime projection remains a generated exposure surface, not the
  default editable source.

## Codex Runtime Alignment Rule

Recent Codex runtime changes should be imported as SDK contracts, not copied as
implementation details. The apparatus should classify a skill boundary as
agent-native only when its package, runtime, permission, environment,
delegation, goal, async, and evidence claims can be checked.

Required post-RF-1 proof concepts:

- Package proof: build, inspect, validate, project/install, warm, and smoke.
- Enablement proof: available, installable, installed, projected, enabled,
  warmed, runnable, validated, and release-ready are separate states.
- Permission proof: declared permission profile, canonical `deny`, and observed
  action drift classification.
- Environment proof: local, optional-local, remote, CI, app-server, or unknown,
  with `remote_ready` false until proven.
- Async proof: approval and deferred-contributor states are explicit; pending
  or resumed work is not mislabeled as pass or fail.
- Goal proof: goal-managed work has a durable `goal_ref`; Linear issues, plan
  docs, and summaries remain linked context.
- Delegation proof: every `SubagentStart`-style event pairs with
  artifact-expected, artifact-written, reviewer-closed, and parent-integrated
  evidence.
- Evidence proof: command-backed claims include raw output references,
  parsed result, summary, redaction status, and blocker classification.
- Warmup proof: session-start skill/plugin warmup loads compact routing and
  execution boundaries only; deep references remain lazy.

## RF-1 Signoff Table

| Claim | Required proof |
| --- | --- |
| Command exists | `./bin/ask skills --help` lists `doctor`, and `./bin/ask skills doctor context7 --json --robot` dispatches. |
| Guidance is truthful | Parser actions, help text, command metadata, and unknown-action suggestions expose the same `ask skills` action set; `python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py::test_skills_action_metadata_matches_parser -q` passes. |
| Payload is stable | `data.skill_doctor` snapshots at `artifacts/skill-doctor/context7.after.json` and `artifacts/skill-doctor/<second-skill>.after.json` validate against `Infrastructure/config/schemas/skill-doctor.v1.schema.json` through `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py::test_skill_doctor_snapshots_validate_schema -q`. |
| Status is deterministic | Tests prove blocked outranks warning, warning outranks pass, and pass has no blockers or warnings. |
| Existing consumers are protected | `skills prove` and `skills proof` keep their current public semantics; doctor maps from them without replacing them. |
| Representative coverage exists | Fixtures cover `context7` and at least one additional non-`context7` skill class. |
| Package readiness is honest | Until package commands exist, doctor emits a schema-valid `not_run` package-readiness check with unavailable command-surface evidence instead of pass. |
| Source ownership is explicit | Doctor or later package-doctor output distinguishes canonical repo source, manifest-declared project-local source, generated projection, client runtime config, and unknown paths. |
| Project lifecycle is eval-gated | `skills create`, `skills install`, and `skills update` report target root, eval gate, lifecycle events, evidence path, and promote/rollback/blocked decision before claiming completion. |
| Eval baseline is portable | Skill evals remain compatible with Agent Skills `evals/evals.json`; SDK-only trace, event, provenance, permission, namespace, telemetry, and promotion fields are structured extensions. |
| Eval learning is bounded | Eval outcomes can create classified deltas only with affected paths, rerun commands, before/after evidence, and promotion or rollback decision. |
| Codex runtime alignment is bounded | RF-1 does not require package, permission, environment, goal, async, subagent, or raw-evidence implementations, but reserves field names and avoids contradictory readiness vocabulary. |
| Rollback is safe | After RF-1 acceptance, ordinary rollback preserves the `skills doctor` command with degraded/blocking output; command removal requires an emergency waiver and reopens RF-1. |

## Required Status Vocabulary

- Readiness status: `pass`, `warning`, `blocked`.
- Check status: `pass`, `warning`, `blocked`, `fail`, `not_run`.
- Blocker class: `blocked_runtime`, `blocked_missing_source`,
  `permission_gap`, `package_metadata_gap`, `runtime_projection_gap`,
  `outcome_proof_missing`, `telemetry_projection_unavailable`,
  `command_surface_gap`, `schema_contract_gap`.
- Post-RF-1 blocker classes to reserve: `permission_profile_drift`,
  `environment_mismatch`, `async_approval_pending`,
  `remote_compaction_timeout`, `subagent_artifact_missing`,
  `goal_ref_missing`, `raw_evidence_missing`, `redaction_status_missing`,
  `warmup_overload`, `runtime_capability_unknown`.
- Stable RF-1 check ids: `source_resolution`, `runtime_reachability`,
  `structural_audit`, `package_readiness`, `outcome_proof`,
  `command_surface_parity`, `schema_contract`.
- Package readiness before package seams exist: check id `package_readiness`
  with status `not_run`, an unavailable command-surface explanation, and never
  `pass`.

## Review Rule

AI review reports are advisory evidence. RF-1 is ready to proceed only when the
signoff table is encoded into implementation tasks, validation commands, and
the eval artifact.
