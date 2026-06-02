# Skills SDK Gap Analysis Report: Current Code Tree

Date: 2026-06-03

## Executive Recommendation

Recommendation: **Hybrid**.

Do not start a new project yet. Do not attempt a broad in-place refactor without
a boundary. The current tree is already a partial Skills SDK implementation and
contains hard-won substrate: the `ask` command surface, SDK-adjacent schemas,
project skill manifest support, skill/package readiness checks, conformance
evidence, Tessl staging rules, skill-factory eval tooling, plugin-factory
packaging patterns, governance docs, and projection ownership rules.

The next move should be:

1. Refactor in place around a clean internal SDK core.
2. Stabilize the public command/API contracts.
3. Add missing guardrails and lifecycle gates.
4. Extract to a separate project only after the internal boundary proves portable.

Short version:

```text
Incubate inside Agent Skills Kit.
Create a clean SDK core.
Make repo-specific behavior explicit adapters.
Extract later when portability is proven by fixtures and tests.
```

## Decision Frame

| Option | Verdict | Why |
| --- | --- | --- |
| Refactor in place | Good, but risky alone | The repo already owns the substrate, but a pure in-place refactor can keep repo-specific assumptions hidden. |
| Extract new module | Best immediate move | A bounded SDK core can clarify contracts while reusing current code and tests. |
| Create new project | Too early | It would look clean but would recreate unresolved questions around manifests, projections, runtime evidence, Tessl, skill roots, and plugin cache behavior. |
| Hybrid | Recommended | Use the current repo as the incubator, create an extractable SDK core, and define exit criteria for a later standalone project. |

## Evidence Reviewed

- `ARCHITECTURE.md`
- `UBIQUITOUS_LANGUAGE.md`
- `Infrastructure/config/skills-sdk.json`
- `Infrastructure/config/schemas/skills-sdk.project.v1.schema.json`
- `Infrastructure/scripts/lib/ask/skills_sdk/**`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/command_metadata.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/tests/**`
- `Plugins/skill-factory/scripts/skill-builder/**`
- `Plugins/plugin-factory/**`
- `Docs/agents/24-tessl-live-skill-eval-workflow.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`
- `artifacts/reviews/sdk-review-synthesis.md`
- `artifacts/reviews/sdk-api-contract-review.md`
- `artifacts/reviews/2026-05-26-skills-sdk-gap-audit-architecture-strategist.md`
- `artifacts/reviews/2026-05-26-skills-sdk-gap-audit-agent-native-reviewer.md`
- `artifacts/recommended-skills-sdk-pipeline.html`

Validation evidence for this report:

```text
./bin/ask repo status --json --robot
```

returned `status: success`.

## Current Tree Strengths

### 1. The Repo Already Has an SDK-Like Control Plane

The architecture file defines Agent Skills Kit as a governed control plane for
authoring, validating, discovering, packaging, projecting, and proving skills
and agent workflows.

Existing substrate:

- `./bin/ask` as the public interface.
- `Infrastructure/scripts/lib/ask/**` as command implementation.
- `Infrastructure/scripts/lib/ask/skills_sdk/**` as a nascent SDK module.
- `Infrastructure/config/schemas/**` as public-ish JSON schema contracts.
- `Infrastructure/tests/**` as command, schema, projection, runtime, package,
  plugin, and eval regression coverage.

This is not greenfield territory.

### 2. Skill Package Contracts Already Exist

The current SDK module has meaningful package-contract machinery:

- `contracts.py`
- `package_contracts.py`
- `package_verify.py`
- `runtime_adapters.py`
- `conformance.py`

It already models:

- skill metadata fields
- package readiness
- package verification
- conformance evidence
- Codex runtime preview/parity limitations
- doctor blocker taxonomy
- SDK layer attribution

Gap: these pieces are still a slice of the platform, not the full SDK pipeline.

### 3. Project-Local Skill Manifest Support Exists

`Infrastructure/config/skills-sdk.json` and
`Infrastructure/config/schemas/skills-sdk.project.v1.schema.json` already define
owner-repo skill-root concepts:

- canonical project source
- generated runtime projection
- client runtime config
- eval suite path
- evidence path
- trust policy
- precedence policy

This directly supports the design-map idea that skill roots need declared
ownership before create/install/update/eval behavior.

Gap: runtime use is weaker than the schema.

### 4. Eval and Tessl Support Are Real

The repo has:

- `./bin/ask evals prepare-tessl-scenarios`
- `./bin/ask evals run`
- `Docs/agents/24-tessl-live-skill-eval-workflow.md`
- skill-factory eval runners and tests
- pressure, smoke, release, and live-eval concepts

This is strong evidence for refactoring current machinery rather than
recreating it elsewhere.

Gap: eval ops are not yet unified under a portable SDK evaluation framework with
JSONL base dataset governance, Tessl setup blocker classification, context
attack evals, judge drift monitoring, and production eval feedback loops.

### 5. Deep Modules Are Already a Repo Concept

`ARCHITECTURE.md` explicitly defines deep modules and names major module regions:

- Skill Factory
- Plugin Factory
- Harness Engineering
- Ask CLI
- Projection and routing
- Validation and tests
- Governance memory

This is aligned with the visual map. The missing work is not inventing deep
modules; it is shaping a dedicated Skills SDK deep module that can eventually
stand alone.

## Critical Gaps

### Gap 1: Project Manifest Validation Is Not Strong Enough

Current state:

`_load_project_skills_sdk_manifest` in
`Infrastructure/scripts/lib/ask/commands/skills_impl.py` loads
`skills-sdk.json`, checks only `schema_version`, and manually rejects duplicate
roots. Invalid manifests can collapse into `None`, making invalid look like
absent.

Risk:

```text
invalid manifest -> silently treated like no manifest
```

That weakens the SDK's trust boundary. An external owner repo needs a hard
blocked state with exact reason.

Needed:

- manifest state: `absent | valid | invalid`
- schema validation through one canonical entrypoint
- blocker class such as `blocked_manifest_invalid`
- default root cardinality checks
- exact error path and remediation command

Decision classification: **Refactor in place first**.

### Gap 2: Lifecycle Defaults Are Ambiguous

Current schema requires:

- `default_for_create`
- `default_for_install`
- `default_for_update`

But it does not enforce exactly one default root per lifecycle action.

Risk:

Create/install/update commands can become nondeterministic or policy-dependent
when multiple roots, or no roots, are marked default.

Needed:

- exactly one default per lifecycle action, or an explicit `none` state that
  produces a blocked decision
- tests for ambiguous defaults
- owner-repo fixtures proving correct root targeting

Decision classification: **Refactor in place first**.

### Gap 3: Command Surface Authority Is Duplicated

Current state:

- argparse command registration lives in `Infrastructure/bin/ask`.
- valid action guidance lives in `Infrastructure/scripts/lib/ask/command_metadata.py`.
- skills handler implementation lives mostly in `skills_impl.py`.

Past reviews already flagged parser/help/metadata drift.

Risk:

A future `skills sdk` namespace, golden path, or install/publish flow can drift
between parser, help text, JSON error guidance, docs, and tests.

Needed:

- one command registry source
- generated parser/help/action metadata
- parity tests across parser, `--help`, `VALID_ACTIONS`, examples, and guided
  errors
- thin command principle to avoid surface sprawl

Decision classification: **Extract new internal module**.

### Gap 4: `skills init` Is Repo-Coupled

Current state:

The initializer defaults to internal repo paths and ownership assumptions.

Risk:

The SDK can appear to support owner-repo lifecycle operations while still
creating Agent Skills Kit-shaped packages with Agent Skills Kit defaults.

Needed:

- repo-internal scaffold mode
- owner-repo SDK mode
- manifest-driven root selection
- owner metadata from project manifest
- generated README contract
- install/update/eval evidence paths under the owner repo

Decision classification: **Refactor in place, then extract**.

### Gap 5: SDK Identity Is Still Tied to Current Branding

Current state:

Schema IDs and some trust/runtime names are anchored to `agent-skills.local`,
`Agent Skills Kit`, or `agent-skills` provenance names.

Risk:

Renaming or extracting the SDK becomes a protocol migration, not a cosmetic
change.

Needed:

- neutral canonical schema namespace
- compatibility aliases for existing IDs
- migration tests for old and new IDs
- provenance trust migration plan
- plugin/runtime selector migration plan

Decision classification: **Hybrid**.

### Gap 6: Runtime Enforcement Is Mostly Modeled, Not Enforced

The design map now requires a deny-by-default policy enforcement gateway.
The current code tree has previews, proof, conformance, package verification,
runtime adapters, and projection checks, but not a general runtime enforcement
gateway that checks every tool call, filesystem access, network egress, secret
request, MCP invocation, and state write at time of use.

Risk:

The SDK can produce receipts and readiness reports but still not be the runtime
authority that blocks unsafe actions.

Needed:

- explicit distinction between modeled enforcement and host-enforced runtime
- policy decision model
- egress ledger model
- state load gate model
- secret taint model
- MCP result taint model
- revocation feed model
- tests that prove fail-closed behavior at the SDK boundary

Decision classification: **New module inside repo first**.

### Gap 7: Eval Ops Are Strong but Fragmented

Current state:

The repo has many eval tools and Tessl guidance, but the SDK does not yet expose
one coherent eval operations layer.

Needed:

- JSONL base schema
- dataset governance
- train/dev/test lock policy
- leakage and dedupe checks
- context/reference evals
- adversarial case families
- judge calibration and drift monitor
- Tessl workspace identity checks
- Tessl setup blocker classification
- incident-to-eval loop
- memory quality evals

Decision classification: **Extract new internal module**.

### Gap 8: Knowledge Engineering Is Not Yet a Package Contract

The current repo has rich docs, references, skill graphs, and skill package
references, but the full design map asks for a formal `knowledge/` contract:

- sources
- canon
- non-canon
- glossary
- assumptions
- decision log
- freshness policy
- trust boundaries
- source cards
- claim maps
- distillation records

Risk:

Good skills can still perform poorly because reference/context quality is not
treated as first-class package state.

Needed:

- optional but validated `knowledge/` package shape
- promotion rules from raw sources to runtime context
- evidence debt ledger
- distillation loss check
- context attack evals
- freshness and ownership gates

Decision classification: **New module inside repo first**.

### Gap 9: Registry, Install, Publish, and Package Manager Are Not Yet Platform-Grade

Current state:

There is install tooling, package readiness, package verification, plugin cache
work, and plugin-factory behavior.

Missing platform-level contracts:

- registry search result card
- install preview screen
- permission/dependency/script/hook diff
- package manager resolver behavior
- native binary intake
- update/rollback/uninstall data disposition UX
- signed package lifecycle
- public/private registry distinction
- extension lifecycle and conformance report

Decision classification: **Hybrid**.

### Gap 10: Governance Is Strong but Not Yet SDK-State-Machine Strong

Current state:

The repo has substantial governance infrastructure under `.harness`, `Docs`,
and tests.

Missing for the SDK:

- lifecycle state machine
- expanded release gates
- accountability/RACI strip
- reattestation matrix
- archive disposition matrix
- decommission verification receipt
- insufficient-evidence blocked state

Decision classification: **Refactor in place using existing governance plane**.

## Domain-by-Domain Gap Matrix

| SDK Domain | Current Tree Status | Main Gap | Recommended Move |
| --- | --- | --- | --- |
| Authoring SDK | Partial | `skills init` is repo-coupled; README/knowledge contracts incomplete | Refactor in place |
| Package SDK | Partial/strong | Readiness exists, but signing/provenance/registry lifecycle incomplete | Internal SDK module |
| Skill IR/compiler | Weak/implicit | No clear typed Skill IR boundary independent of command handlers | New internal module |
| Security SDK | Partial | Verification exists, runtime enforcement missing | Internal module + host adapter |
| Runtime SDK | Partial/modelled | Conformance and preview exist; deny-by-default gateway absent | Internal module |
| Eval SDK | Strong but fragmented | No unified dataset governance and eval ops contract | Consolidate in module |
| Knowledge SDK | Mostly docs/reference behavior | No formal `knowledge/` package contract | New package contract |
| Registry SDK | Partial | Install/package exist; registry UX/publish/verify lifecycle incomplete | Hybrid |
| Governance SDK | Strong repo plane | Needs SDK state machine and release gates | Refactor in place |
| AX/DX | Partial | Command sprawl risk and unclear golden path | Internal module + product strip |

## Recommended Architecture Move

Create an internal SDK core with adapters:

```text
Infrastructure/scripts/lib/ask/skills_sdk/
  core/
    ir.py
    manifests.py
    diagnostics.py
    commands.py
    receipts.py
  authoring/
  package/
  security/
  runtime/
  evals/
  knowledge/
  registry/
  governance/
  adapters/
    agent_skills_kit_repo.py
    codex_runtime.py
    tessl.py
    plugin_host.py
```

This is illustrative, not a required exact folder layout. The key is the
boundary:

```text
SDK core = portable contracts and behavior
Adapters = Agent Skills Kit repo, Codex runtime, Tessl, plugin host, filesystem
```

## What Should Happen Next

### Phase 0: Stabilize Current Control Points

Highest leverage fixes:

1. Add a strict project manifest validator used by runtime loaders.
2. Classify manifest state as absent, valid, or invalid.
3. Enforce default root cardinality for create/install/update.
4. Add parser/help/metadata parity as one generated command registry.
5. Split repo-internal `skills init` defaults from owner-repo SDK mode.

Why this first:

These are boundary and trust issues. If they remain fuzzy, later platform
features will rest on sand.

### Phase 1: Define the SDK Core Contract

Create a small internal SDK core around:

- Skill IR
- manifest loading and validation
- diagnostics taxonomy
- receipts
- lifecycle state
- command protocol
- package source model
- eval dataset model

Do not build all platform features yet. Build the contracts and adapters first.

### Phase 2: Consolidate Existing Tooling Into Domains

Move or wrap existing code into the SDK domains:

- package contracts and verify -> Package SDK
- conformance/runtime preview -> Runtime SDK
- Tessl wrappers and skill-factory evals -> Eval SDK
- skill-factory init/analyze/upgrade -> Authoring SDK
- plugin-factory and package manager pieces -> Registry/Plugin Host SDK
- governance docs/receipts -> Governance SDK

### Phase 3: Run Owner-Repo Portability Fixtures

Before a new project exists, prove the SDK works outside this repo:

- tmp owner repo
- declared `skills-sdk.json`
- project-local skill root
- create/install/update flow
- eval gate
- evidence output
- blocked invalid manifest
- rollback/decommission receipt

This is the extraction gate.

### Phase 4: Decide Whether to Extract

Extract only when:

- SDK core imports no repo-specific constants except through adapters.
- Schema IDs have neutral namespace plus compatibility aliases.
- Public commands are generated from one registry.
- Owner-repo fixtures pass.
- Tessl staging works without live repo source.
- Skill/package/eval/registry contracts have schema-backed fixtures.
- Agent Skills Kit itself consumes the SDK as a client, not as the hidden owner.

## Final Recommendation

Choose: **Hybrid**.

The current repo should become the incubation host for the Skills SDK, but the
implementation should be reshaped around a portable internal SDK core. Starting
from scratch would discard the hard parts this repo already learned. A pure
in-place refactor would preserve too many hidden repo assumptions.

The right move is:

```text
Refactor in place around an extractable SDK core,
then create a standalone project only after portability is proven.
```

The first concrete implementation slice should be:

```text
Project manifest hardening + command registry unification + owner-repo init mode
```

That slice directly reduces the highest-risk ambiguity before larger platform
work begins.
