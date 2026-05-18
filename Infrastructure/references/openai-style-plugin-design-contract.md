# OpenAI-Style Plugin Design Contract

Use this reference when creating, auditing, refactoring, or routing skills and
plugins. It adapts the official OpenAI Apps SDK design guidance to this
repository's skill/plugin system: small capability surfaces, precise
descriptors, structured contracts, bounded context, explicit side effects, and
user control around meaningful state changes.

This reference complements `Infrastructure/references/agent-native-skill-contract.md`.
That contract defines the local skill shape. This contract defines the
tool/plugin design pressure behind that shape.

## Source Basis

This is a local adaptation, not a claim that Codex skills are Apps SDK MCP
servers. The operating pressure comes from official OpenAI guidance:

- Apps SDK MCP tools must accurately describe potential impact with
  `readOnlyHint`, `openWorldHint`, and `destructiveHint` annotations:
  https://developers.openai.com/apps-sdk/build/mcp-server#tool-annotations-and-elicitation
- Tool results should keep `structuredContent`/`content` model-visible and
  `_meta` component-only:
  https://developers.openai.com/apps-sdk/reference#tool-results
- Data collection and response content should be minimized to what the tool
  actually needs:
  https://developers.openai.com/apps-sdk/app-submission-guidelines#data-collection
- UI-heavy Apps SDK tools should separate data-processing tools from render
  tools when that avoids unnecessary context or repeated UI rendering:
  https://developers.openai.com/apps-sdk/build/chatgpt-ui#decoupled-pattern

For this repository, translate those ideas into skill/plugin checks: precise
descriptions, explicit side-effect classes, minimized context, structured
outputs where useful, and confirmation before meaningful state changes.

## Core Rule

Design every skill, plugin, and routed lifecycle stage as a narrow,
self-describing capability with explicit inputs, outputs, side effects,
validation, and disclosure boundaries.

Do not use a large prompt, broad router, or plugin package as a substitute for a
clear capability contract.

## Capability Shape

Every new or changed skill/plugin surface must declare:

- primary user intent;
- when to use it and when not to use it;
- required inputs and optional evidence;
- expected output artifact or response shape;
- upstream and downstream routes, when applicable;
- validation or acceptance evidence;
- failure or blocker behavior;
- side-effect class;
- whether user steering is required for consequential ambiguity;
- how autonomous/headless mode records assumptions.

## Side-Effect Classes

Classify the strongest side effect a capability may perform:

- `read-only`: inspect, analyze, route, review, search, or summarize only.
- `artifact-write`: write repo-owned reports, specs, plans, evals, or generated
  artifacts without changing runtime or external state.
- `repo-write`: edit source, tests, scripts, configs, package manifests, or
  validation surfaces.
- `external-write`: update Linear, GitHub, PRs, comments, issues, calendars, or
  other systems outside the repository.
- `destructive`: delete, overwrite, close, archive, force-push, migrate,
  decommission, or irreversibly change state.
- `completion-gating`: recommend closure, readiness, merge, release, Linear
  completion, or other status transitions.

Use the class to decide whether the capability may proceed, must ask once, must
return a blocker, or must produce a ready-to-confirm payload.

## Progressive Disclosure

Route before loading deep context.

Load only the selected stage, lane, reference, script, or specialist skill
needed for the proven intent. Keep long examples, policy detail, prompt bodies,
schemas, and eval fixtures in references with clear `Read when:` signposts.

Avoid:

- always loading every child skill;
- exposing full prompt libraries before route selection;
- reading all `.harness` or session evidence when a narrower artifact set can
  prove the route;
- adding broad root skill descriptions to compensate for weak child contracts.

## Structured Inputs And Outputs

Prefer stable, machine-readable contracts over prose-only guidance.

When structured output is appropriate, include:

```yaml
schema_version: "1"
selected_capability: "<skill|plugin|stage|lane>"
side_effect_class: "<class>"
inputs_used: "<short evidence summary>"
outputs_expected: "<artifact or response shape>"
validation_evidence: "<pass|fail|blocked with command or method>"
interactive_status: "<not_needed|asked|autonomous_assumption|blocked>"
blocked_by: "<missing input or blocker, if any>"
```

Keep model-visible results relevant to the task. Do not surface internal traces,
raw session logs, secrets, credentials, telemetry payloads, or broad diagnostics
unless the user asked for them and they are safe to disclose.

## User Steering And Headless Mode

Ask once when one remaining decision materially changes route, scope, artifact
identity, side effects, external writes, destructive actions, validation gates,
or completion recommendation.

Do not ask when repo evidence can answer safely or the ambiguity is low impact.

In autonomous/headless mode:

- record the conservative assumption;
- include evidence and risk;
- do not perform external, destructive, broad, or completion-gating mutations
  from an assumption;
- return a blocker or ready-to-confirm payload when authority is missing.

## Retry Safety

Design capabilities so reruns are safe:

- deterministic filenames and artifact paths;
- no duplicate Linear/GitHub objects without lookup and dedupe;
- idempotent sync/projection/package behavior where possible;
- explicit append vs replace behavior;
- validation can be rerun without changing the result unless evidence changed;
- external writes are gated or previewed before mutation.

## Factory Application

`skill-factory` applies this contract to individual skills and modules.

It should reject or repair skills that have vague triggers, broad user intents,
unclear side effects, missing validation, hidden dependencies, or bloated
always-on context.

`plugin-factory` applies this contract to plugin packages.

It should reject or repair plugins with unclear package boundaries, too many
root-visible capabilities, overlapping child skill descriptions, mixed
read/write/destructive responsibilities, unsafe install or projection behavior,
or missing plugin-level evals.

`harness-engineering` applies this contract to lifecycle execution.

It should route to exactly one stage before loading stage detail, separate
analysis from artifact writes and external updates, use specialist skills only
when evidence proves the need, ask once at consequential ambiguity points, and
require eval proof before closure recommendations.

## Anti-Patterns

- One giant skill prompt instead of routed capabilities.
- Plugin packages that expose every child skill as always relevant.
- Ambiguous descriptions that overlap across skills.
- Mutating actions hidden inside read-only review or planning flows.
- External state updates without confirmation or proof.
- Prompt growth used instead of structured validation or evals.
- Specialist skills chosen from keyword overlap alone.
- Raw transcripts or session logs loaded as default context.
- Validation claimed from intent rather than command output or inspection
  evidence.
