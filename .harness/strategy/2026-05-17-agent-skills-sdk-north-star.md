---
schema_version: 1
title: Agent Skills Kit Professional Skill SDK North Star
status: draft-for-review
date: 2026-05-17
selected_mode: repo_intent
repo: agent-skills
primary_reader: Codex agents and Jamie as operator
decision_status: proposed
---

# Agent Skills Kit Professional Skill SDK North Star

## Command Summary

BLUF: This artifact defines the next product framing for Agent Skills Kit: it should behave like a professional SDK for Codex skills, not a folder of prompts or a broad archive of agent instructions. The reader is Jamie, future Codex agents, and harness operators who need one stable source for why the SDK direction matters, what it permits, and what implementation should prove first. The next action should be to make `./bin/ask skills doctor <handle> --json --robot` the trusted readiness contract because the main risk is adding SDK ceremony without increasing runtime trust, projection integrity, or evidence quality.

Decision Needed: Accept `doctor-driven trust` as the first proof point for the professional Skill SDK direction.

Top Risks: SDK language can add manifest ceremony without behavioral proof; harness control can drift into skill implementation ownership; stale memory or runtime projections can look authoritative until doctor, eval, package, and closeout gates classify them separately.

Next Action: Create a focused implementation slice that hardens `skills doctor` around source ownership, runtime projection, metadata, profiles, references, eval readiness, package readiness, and discoverability.

## Vision

Agent Skills Kit should become the professional SDK for reusable Codex capabilities.

In this framing, a skill is not just markdown. A skill is a productized capability module with a canonical source, a compact runtime surface, typed metadata, supported operation profiles, permission and root expectations, references, evals, package readiness, provenance, lifecycle status, and evidence-producing output.

The SDK promise is:

> Thin surface. Strong guardrails. Durable memory. Professional output.

That promise should stay operational, not poetic:

- Thin surface: Codex sees compact skill entrypoints, short handle descriptions, and machine-readable contracts instead of huge always-loaded workflow prose.
- Strong guardrails: source ownership, runtime projection, validation, permission roots, package readiness, and release claims fail closed.
- Durable memory: references, prior failures, examples, and freshness rules live in searchable memory/reference surfaces instead of bloating hot-path instructions.
- Professional output: skill runs report trace IDs, tools, references, artifacts, validations, confidence, and explicit passed, failed, blocked, and not-run buckets.

## Current Facts

- `README.md` and `Docs/product/agent-capability-control-plane.md` already frame Agent Skills Kit as an agent capability control plane rather than a prompt folder.
- `UBIQUITOUS_LANGUAGE.md` already defines the key operating terms: Agent Skills Kit, Canonical Skill Source, Runtime Projection, Generated Command Handle, User Runtime Links, Visible Runtime Surface, Strict Skill Audit, and Release-Readiness Claim.
- `Docs/agents/14-path-ownership-boundaries.md` already separates product, factory, and runtime planes, and says runtime/projection surfaces such as `.agents/**`, `.skillsets/**`, `skills-codex/**`, and `Plugins/cache/**` are not canonical edit targets.
- `./bin/ask skills --help` already exposes SDK-shaped verbs: `doctor`, `package`, `profiles`, `events`, `memory`, `route`, `prove`, `audit`, `validate-skill-gate`, `validate-openai-format`, `validate-boundaries`, `install`, `fold`, and `sync`.
- `./bin/ask skills profiles --json --robot` already describes operation profiles such as `authoring`, `package-review`, `plugin-share`, `eval`, and `live-mutation`.
- `./bin/ask skills events --json --robot` already declares lifecycle events including `skill_loaded`, `skill_doctor_completed`, `package_readiness_checked`, `eval_started`, `eval_blocked`, `eval_completed`, `projection_synced`, and `manifest_changed`.
- The May 2026 Codex Python SDK changes in `~/dev/codex` add useful SDK precedent: plain string turn input as a thin convenience over typed input, a public `TurnResult` object instead of raw app-server payloads, first-class login handles with `wait()` and `cancel()`, internal helper modules that keep the public facade small, public API signature tests, docs/examples/notebook parity, and validation commands that compile, lint, and smoke the changed SDK surface.

## Upstream Python SDK Lessons

The Codex Python SDK direction is directly relevant to Agent Skills Kit because it shows how a professional SDK can stay easy to use without hiding state.

Adopt these patterns:

- Public APIs should be small, friendly, and typed. A string shortcut can exist for the common case, but it should normalize immediately into the typed contract the rest of the system understands.
- Public run methods should return domain result objects, not raw transport payloads. Skill runs should return a `SkillRunResult`-style shape with status, error, timing, final response, artifacts, usage, evidence, and trace linkage.
- Long-running or setup workflows should return attempt-local handles. Login, install, projection sync, package, eval, and live-mutation workflows should expose `wait`, `cancel`, and status semantics on the handle instead of scattering root-level control methods.
- The public facade should remain thin. Environment discovery, login routing, input normalization, metadata validation, projection checks, and package comparison belong in focused internal modules.
- Public API signatures are product contracts. Agent Skills Kit should test exported commands, JSON fields, status enums, handle methods, and result fields the same way Codex tests Python SDK root exports and method annotations.
- Docs, examples, notebooks, fixtures, and tests must move together when public SDK behavior changes. A professional skill SDK cannot let examples teach stale workflows.
- Setup should be first-class. Agents should be able to enter a workspace, discover required roots/tools/auth, classify missing setup, and either perform an allowed setup flow or return a precise blocker without requiring Jamie to integrate the product by hand.

`openai/openai-python` should be used first as a reference architecture for Python SDK ergonomics, generated type stewardship, error taxonomy, pagination/streaming conventions, retry behavior, and docs discipline. It should become a runtime dependency only for surfaces that actually call OpenAI APIs or intentionally reuse OpenAI transport/types. The skill SDK should not depend on `openai-python` merely to validate local skill metadata, run doctor, manage projections, or execute filesystem/package checks.

The temporary design-reference clone of `openai/openai-python` reinforces this split:

- `src/openai/resources/skills` exposes generated skill verbs for create, retrieve, update default version, list, delete, content download, and versions. Agent Skills Kit should use that as distribution vocabulary pressure, not as proof that local skills are the same thing as hosted OpenAI skill resources.
- Skill upload accepts files or a zip bundle, while skill content download returns a binary bundle. Agent Skills Kit package/share gates should keep directory source, package archive, and downloaded/installable content as separate states.
- Version objects carry `id`, `created_at`, `description`, `name`, `skill_id`, and `version`; deleted version objects carry `deleted` and `version`. Agent Skills Kit should model version and deletion/provenance explicitly before claiming publish/share readiness.
- List APIs use cursor pagination with `after`, `limit`, `order`, `data`, and `has_more`. Agent Skills Kit registry, audit, lifecycle-event, and package-list surfaces should use similarly boring pagination when they become large.
- The normal path returns parsed typed models, while `with_raw_response` and `with_streaming_response` are explicit escape hatches. Agent Skills Kit should keep parsed JSON result contracts as the default and make raw logs/streams opt-in evidence channels.
- Error classes preserve status, request, response, body, code, param, type, and request ID when available. Skill SDK failures should likewise preserve operation context and original cause instead of collapsing auth, permission, runtime, validation, and transport failures into one generic failure.

## Interpretation

The repository already has the architecture of a skill SDK, but the product contract is still split across command help, docs, vocabulary, runtime projections, package gates, evals, and strategy artifacts.

The next useful strategic move is not to invent a second platform. It is to make the implicit SDK contract explicit and then prove it through the smallest high-leverage command: `skills doctor`.

The architecture pressure is ownership confusion plus readiness ambiguity:

- A skill can exist in canonical source but be missing or stale in runtime projection.
- A generated command handle can be reachable while richer package metadata is incomplete.
- Package readiness can pass while smoke evals remain blocked.
- Memory can preserve valuable learning while also carrying stale authority.
- Harness can observe, classify, and report skill behavior, but it should not become the place where skill internals are implemented.

## User Cases

### Jamie As Operator

Jamie needs to know whether a skill is safe, current, discoverable, and useful before relying on it in real Codex work.

The SDK should answer:

- What is the canonical source?
- Is the runtime projection current?
- What profile is safe to run?
- What can this skill read or mutate?
- What evidence proves it works?
- What failed, blocked, or was not run?

### Codex As Runtime

Codex needs short, precise, machine-readable capability surfaces.

The SDK should provide:

- compact `SKILL.md` instructions;
- stable handle descriptions;
- typed metadata;
- profile and mutation-policy declarations;
- reference and eval pointers;
- structured output contracts;
- traceable readiness and blocker reports.

### Skill Authors

Skill authors need a boring path from draft to reliable capability.

The SDK should provide:

- a small scaffold;
- a metadata contract;
- local audit and format checks;
- doctor output that names missing pieces;
- eval contracts that test behavior rather than prose polish;
- package readiness that separates install/share claims from draft authoring.

### Harness Operators

`coding-harness` needs a control surface it can trust without reimplementing skill logic.

The SDK should provide JSON outputs that harness can consume for:

- trace IDs;
- allowed roots and write policy;
- required tools and external systems;
- lifecycle events;
- artifact paths;
- validation outcomes;
- classified blockers;
- release-readiness status.

### Future Agents

Future agents need durable repo language so they do not rediscover source/projection/runtime boundaries every run.

The SDK should make the safe path obvious:

~~~bash
./bin/ask repo doctor --json --robot
./bin/ask skills doctor <handle> --json --robot
./bin/ask skills package <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
~~~

## North Star

Before Codex uses, promotes, shares, or publishes a skill, one command should be able to prove readiness:

~~~bash
./bin/ask skills doctor <handle> --json --robot
~~~

The command should classify:

- canonical source ownership;
- command-handle resolution;
- runtime projection reachability;
- metadata completeness;
- supported operation profiles;
- required tools and roots;
- mutation policy;
- reference availability;
- eval readiness;
- package readiness;
- provenance and lifecycle state;
- discoverability through Codex-visible surfaces;
- outcome proof availability;
- exact blockers and warnings.

Doctor should not replace evals, package checks, or strict audits. It should compose their readiness signals into one trusted operator view.

## Readiness Acceptance Criteria

The first implementation slice is complete only when these acceptance criteria
are machine-checkable:

| ID | Criterion | Proof |
| --- | --- | --- |
| SDK-AC1 | `skills doctor <handle> --json --robot` always returns `schema_version`, `status`, `target_summary`, `checks`, `blockers`, `warnings`, `operation_context`, `contract_schemas`, `agent_summary`, and `next_command`. `next_command` is required for every status and is `null` only when no safe next command exists. | Golden JSON fixture assertion for one passing skill, one warning skill, and one blocked skill, including required-vs-null field assertions. |
| SDK-AC2 | `status` is deterministic: `blocked` outranks `warning`, `warning` outranks `pass`, and `pass` requires no blockers or warnings. | Unit test that feeds mixed check outcomes and asserts the final status. |
| SDK-AC3 | Source, runtime projection, package readiness, eval readiness, and outcome proof are separate checks with separate blocker or warning classes. | Fixture matrix covering `blocked_missing_source`, `blocked_runtime`, `capability_contract_incomplete`, `outcome_proof_missing`, and `blocked_validation`. |
| SDK-AC4 | Doctor never turns package readiness into outcome proof. | Test where `skills package` passes but `skills prove` is missing or blocked; doctor must report package readiness separately from outcome proof. |
| SDK-AC5 | Doctor never hides package blockers behind runtime reachability or vice versa. | Test where runtime reachability fails and package metadata is incomplete; both are visible in the JSON. |
| SDK-AC6 | Harness consumers can use declared schemas without reading skill internals. | Contract test or lint that checks harness integration consumes `doctor`, `package`, `events`, and `profiles` outputs by schema fields, not by parsing `SKILL.md` bodies. |
| SDK-AC7 | Freshness-sensitive memory and references produce deterministic readiness outcomes. | Boundary tests use an injected evaluation time, UTC-normalized timestamps, and explicit stale/unknown/current fixtures. |
| SDK-AC8 | Review feedback that expresses a design principle is classified by intent radius before implementation. | Fixture where a line-level API comment is interpreted as an `api_design_rule`, triggers a bounded pattern sweep, classifies similar cases, and records a durable rule or explicit deferral. |

These are strategy-level criteria, not an implementation spec. A later plan can
choose the exact test files and helper APIs.

## Reconciliation Rules

`skills doctor` should compose readiness, not blur it.

- If resolver or canonical source fails, doctor is `blocked` even if package or eval data exists from stale artifacts.
- If runtime reachability fails, doctor is `blocked_runtime`, but package metadata warnings should still remain visible.
- If package readiness is blocked but structural audit passes, doctor should report package promotion as blocked while preserving the structural pass.
- If eval or outcome proof is missing, doctor should report readiness as warning in exploratory profiles and as blocked in promotion profiles. The profile response must say whether the warning is promotable or non-promotable so callers do not loop forever in an ambiguous warning state.
- If strict audit fails, doctor should report `blocked_validation` and should not claim release readiness.
- If memory evidence is stale, doctor should report freshness as warning or blocked according to the selected profile instead of treating memory as current proof.
- Freshness checks should use a canonical evaluation timestamp supplied by the runner, normalize all evidence timestamps to UTC, and classify missing timestamp or missing source as `freshness_unknown` rather than silently passing.
- Freshness thresholds belong to the declared profile or manifest contract, not to the local machine clock or an ad hoc caller default.

## Ownership Matrix

Agent Skills Kit owns the SDK contract and canonical skill source. Harness owns orchestration and evidence presentation. This split should be testable, not only aspirational.

| Surface | Agent Skills Kit owns | Coding-harness owns |
| --- | --- | --- |
| `doctor` contract | Schema, check classes, status precedence, profile semantics, and fixture corpus. | Invoking doctor, preserving raw JSON, displaying operator summary, and enforcing configured gates. |
| `package` contract | Package metadata schema, provenance rules, version rules, and package contents. | Running package checks and reporting package readiness alongside other evidence. |
| `profiles` contract | Profile names, required proof levels, mutation classes, and freshness thresholds. | Selecting an allowed profile for the current run and refusing undeclared profile escalation. |
| `events` contract | Event names, required fields, trace linkage, and lifecycle semantics. | Collecting events, correlating trace IDs, and surfacing audit reports. |
| `prove` / eval proof | Eval scenario contracts, expected behavior, fixtures, and proof classification. | Running approved proof workflows and preserving pass, warning, blocked, skipped, and not-run evidence. |
| Review feedback uptake | Feedback taxonomy, intent-radius rules, pattern-sweep contract, durable guidance admission, and eval fixtures. | Preserving review text, invoking the sweep, reporting fixed/deferred cases, and showing whether durable guidance was updated or intentionally skipped. |
| Schema stewardship | Versioned schema evolution and backward compatibility policy. | Consumer compatibility tests that fail when harness parses internals or depends on undocumented fields. |

## SDK Contract Shape

The first SDK contract should be intentionally small.

Recommended source layout for a mature skill:

~~~text
Skills/<cluster>/<skill>/
  SKILL.md
  skill.yaml
  references/
  evals/
  schemas/
~~~

Recommended contract fields:

~~~yaml
schema_version: skill-package.v1
name: context7
version: 0.1.0
owner: agent-ops
category: reference
maturity: validated
runtime_visibility: latent
command_visibility: target
supported_profiles:
  - authoring
  - package-review
  - eval
required_tools:
  - context7
required_roots:
  - repo
writable_roots:
  - artifacts
external_systems:
  - docs
mutation_policy: analysis_only
references:
  - references/examples.md
evals:
  - evals/routing.yaml
output_contract: references/output-contract.yaml
~~~

This contract can begin as YAML because it is author-readable. JSON schemas and JSON output should enforce it where machines consume it.

## File-Type Policy

Use the boring file types that match the job:

- `.md` for hot-path instructions, references, examples, decisions, human docs, and reports.
- `.yaml` or `.yml` for readable skill contracts, eval scenarios, and profile declarations.
- `.json` for machine contracts, package manifests, registry state, command output fixtures, and schema-validated surfaces.
- `.jsonl` for append-only lifecycle events, trace streams, audit history, and run evidence.
- `.py` for `ask` implementation, validators, sync/projection tooling, package checks, and eval runners.
- `pyproject.toml` and `uv.lock` for reproducible Python tooling when SDK enforcement becomes package-shaped.
- `.toml` for local environment or runtime configuration where the repo already uses TOML contracts.

## Roadmap

### Phase 1: Name The Contract

- Create or update the public SDK contract doc.
- Define skill maturity states: `draft`, `validated`, `packaged`, `published`, and `deprecated`.
- Define the minimum metadata fields for release-readiness claims.
- Align the contract language with `UBIQUITOUS_LANGUAGE.md`.
- State what belongs in `SKILL.md`, `references/**`, `evals/**`, generated handles, and package manifests.

### Phase 2: Make Doctor The Spine

- Harden `skills doctor` as the operator readiness command.
- Return `pass`, `warning`, or `blocked`.
- Compose resolver, source, projection, metadata, profile, reference, eval, package, and discoverability checks.
- Keep package readiness and eval blockers separate in the output.
- Emit or reference `skill_doctor_completed` lifecycle evidence.
- Satisfy SDK-AC1 through SDK-AC5 before treating doctor as the trusted readiness contract.

### Phase 2b: Make Review Feedback Transferable

- Classify reviewer feedback before fixing it as `local_bug`, `repeated_pattern`, `api_design_rule`, `architecture_boundary`, `naming_language`, `validation_gap`, `test_contract_gap`, or `documentation_drift`.
- Assign an intent radius: `line`, `function`, `file`, `package`, `repository`, `architecture_rule`, or `durable_memory`.
- Require a bounded pattern sweep when feedback expresses a design principle, such as "this API should return a named error instead of a bool."
- Report similar cases as `fixed_now`, `left_different_semantics`, `deferred_public_api`, `deferred_risk`, or `not_applicable`.
- Record the durable rule in the relevant guidance, eval, or memory surface when the rule should guide future work; otherwise state why it was intentionally not retained.
- Satisfy SDK-AC8 before claiming review-handling skills have professional uptake rather than patch compliance.

### Phase 2c: Make Python SDK Ergonomics Explicit

- Define public result objects for doctor, package, eval, projection sync, and skill run outcomes.
- Define attempt-local handles for workflows that can block, wait, cancel, or resume.
- Add public API signature tests for SDK command payloads, result fields, and handle methods.
- Keep string or markdown shortcuts as input conveniences only; normalize them into typed contracts at the boundary.
- Add docs/examples parity checks so public examples cannot drift from the supported SDK API.
- Treat `openai-python` as a reference first and add it as a dependency only behind a specific OpenAI API integration boundary.

### Phase 3: Prove The Contract On Top Skills

Start with a small representative set:

- `context7`;
- `skill-factory`;
- `plugin-factory`;
- `uv-python-project-setup`;
- `simplify`;
- `unslopify`;
- `improve-codebase-architecture`;
- `he-strategy`.

Use these to discover missing contract fields before migrating the whole catalog.

### Phase 4: Connect Harness As Control Plane

- Let `coding-harness` consume `doctor`, `package`, `profiles`, `events`, `memory`, `audit`, and `prove` outputs.
- Add trace IDs, profile selection, workspace roots, permission posture, artifact collection, and final report formatting in harness.
- Keep skill implementation, source ownership, package metadata, and projection mechanics in Agent Skills Kit.
- Satisfy SDK-AC6 before claiming harness integration is contract-safe.

### Phase 5: Add Release And Share Gates

- Treat install/share/publish claims as release-readiness claims.
- Block release on source/projection drift, incomplete metadata, missing package provenance, missing eval evidence, or unclassified blockers.
- Keep draft skills cheap to write, but make published skills strict.

## Guardrails

- Do not hand-edit runtime projections when canonical source exists.
- Do not let `coding-harness` become the skill implementation layer.
- Do not claim outcome proof from structural audit alone.
- Do not treat package readiness, smoke eval readiness, and merge readiness as one truth.
- Do not inject stale memory as if it were current evidence.
- Do not require full published-skill ceremony for draft skill exploration.
- Do not expand the SDK schema until at least one top-skill migration proves the field is needed.

## Gap Closure

| Gap | Close With | First Proof |
| --- | --- | --- |
| Skill readiness is spread across commands | Doctor-centered readiness contract | `skills doctor <handle> --json --robot` includes source, projection, metadata, profile, package, eval, and discoverability status |
| Metadata may become decorative | Doctor and eval gates outrank schema presence | Missing or stale behavioral proof is a warning or blocker |
| Projection drift can look like skill failure | Source/projection ownership checks | Doctor reports canonical source and runtime projection separately |
| Durable memory can go stale | Freshness and provenance fields | Memory entries include source, confidence, last verified, and recheck rules |
| Harness can duplicate SDK logic | Harness consumes SDK outputs | Harness reports skill readiness without parsing skill internals |
| Skill authoring can become heavy | Maturity states | Draft remains cheap; published is strict |

## Negative-Path Test Matrix

The SDK direction is not proven by happy-path output. The first doctor hardening
slice should include adversarial or contradictory states:

| Case | Setup | Expected Doctor Result |
| --- | --- | --- |
| Valid handle, missing source | Generated handle resolves to a source path that no longer exists. | `blocked_missing_source`; no release readiness claim. |
| Valid source, broken runtime projection | Canonical `SKILL.md` exists but runtime proof fails. | `blocked_runtime`; source metadata still visible. |
| Package metadata missing | Skill is structurally valid but lacks version, role compatibility, runtime needs, provenance, or share readiness. | Warning or package-promotion blocker; structural status remains separate. |
| Package ready, eval missing | Package gate passes but no outcome proof or workout exists. | Package readiness visible; outcome proof warning remains. |
| Stale memory evidence | Memory/reference entry is older than its freshness rule or has no source, using injected UTC evaluation time. | `freshness_stale` warning or blocker by profile; memory is not treated as current proof. |
| Unknown memory freshness | Memory/reference entry has no timestamp, no source path, or an unparsable timestamp. | `freshness_unknown`; non-promotable warning unless the profile explicitly allows exploratory use. |
| Harness parsing internals | Harness integration reads `SKILL.md` bodies instead of declared JSON schemas. | Contract violation in harness boundary test. |
| Cross-consumer schema drift | `./bin/ask` and coding-harness parse the same doctor JSON differently. | Contract test failure with the field path and consumer name. |
| Review comment implies API rule | Reviewer says a named function should return a named sentinel error instead of a success/failure bool. | `feedback_intent=api_design_rule`; intent radius is at least package; similar bool-return failure APIs are swept, classified, and either fixed or deferred with reasons. |
| Review comment is line-local only | Reviewer points to one typo, one missing import, or one isolated assertion. | `feedback_intent=local_bug`; no repo sweep required, but output states why the radius stayed local. |
| Pattern sweep finds unsafe public API changes | Similar cases exist but exported compatibility would be broken by immediate edits. | `deferred_public_api`; report affected symbols, caller impact, and required migration plan. |

Each case should assert both the status and the required JSON shape: `status`, `target_summary`, `checks`, `blockers`, `warnings`, `operation_context`, `contract_schemas`, `agent_summary`, and `next_command`. `next_command` is always present and may be `null` only when no safe command can be recommended.

## Authority Limits

This artifact proposes strategic direction. It does not authorize broad rewrites, package publication, runtime projection edits, external mutations, or validation policy changes.

Implementation should be routed through the appropriate execution skill or plan after a slice is selected.

## Stop Conditions

Revisit this strategy if any of these become true:

- `skills doctor` cannot provide useful readiness without duplicating most skill implementation logic.
- The SDK metadata contract grows faster than top-skill migrations prove real need.
- Published-skill gates block normal draft authoring.
- Harness begins owning skill internals instead of consuming skill contracts.
- Outcome proof remains unavailable even after doctor/package/profile surfaces are coherent.

## Future Agent Guidance

- Treat `doctor-driven trust` as the first SDK proof point.
- Keep the first implementation slice small and command-backed.
- Prefer strengthening existing `ask skills` verbs over adding new top-level commands.
- Use `UBIQUITOUS_LANGUAGE.md` terms exactly when naming source, projection, runtime, handle, package, and proof surfaces.
- When in doubt, separate facts from interpretation and report blocked checks instead of smoothing them into a polished success story.

## Validation Plan

- `rg -n "professional SDK|Skill SDK|skill doctor|doctor-driven|Agent Skills Kit" .harness Plugins Skills Docs`
- `git log --oneline -- .harness/strategy Docs/product UBIQUITOUS_LANGUAGE.md Docs/agents/14-path-ownership-boundaries.md`
- `python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md --json`
- `./bin/ask skills doctor context7 --json --robot` as a baseline readiness probe; if blocked, preserve exact blocker class as implementation input.
- `./bin/ask skills package context7 --json --robot` as a baseline package-readiness probe; preserve missing package metadata separately from runtime blockers.
- Future implementation validation should add fixture or unit tests for SDK-AC1 through SDK-AC8 before any release-readiness claim.
