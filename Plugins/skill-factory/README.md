# Skill Factory

Skill Factory is the Codex plugin for skill lifecycle work. It routes skill requests, creates first drafts, captures repeatable workflows as skills, hardens existing packages, analyzes reliability evidence, installs valid packages, and proves runtime visibility.

The plugin manifest is [`.codex-plugin/plugin.json`](./.codex-plugin/plugin.json). Bundled skill sources live in [`skills/`](./skills/).

## Reader Map

- [Command-Facing Lanes](#command-facing-lanes): which skill handles which job.
- [Factory Lifecycle](#factory-lifecycle): how ideas move from draft to runtime proof.
- [Routing Boundaries](#routing-boundaries): where each lane stops.
- [Context Lifecycle](#context-lifecycle): the shared generate/test/distribute/observe/adapt frame.
- [Tessl And KnowledgeOS](#tessl-and-knowledgeos): current plugin-first Tessl layout and evidence boundaries.
- [Source Boundaries](#source-boundaries): which paths are canonical and which paths are compatibility links.
- [Validation](#validation): commands to prove docs and plugin metadata still match the live package.

## Command-Facing Lanes

| Lane | Canonical path | Use when |
|---|---|---|
| `skill-factory-router` | [`skills/skill-factory-router/`](./skills/skill-factory-router/) | A request needs classification before execution. |
| `skill-creator` | [`skills/scaffolding_templates/skill-creator/`](./skills/scaffolding_templates/skill-creator/) | A new skill or draft package needs its first usable shape. |
| `skill-factory-router` | [`skills/skill-factory-router/`](./skills/skill-factory-router/) | Existing skill hardening, budget, eval, safety, or release-readiness work needs routing to the current repair workflow. |
| `skill-refactor` | [`skills/data_fetch_analysis/skill-refactor/`](./skills/data_fetch_analysis/skill-refactor/) | Session or portfolio evidence should drive keep, improve, merge, split, retire, or redirect decisions. |
| `skillify` | [`skills/scaffolding_templates/skillify/`](./skills/scaffolding_templates/skillify/) | A completed repeatable workflow should become a durable skill package. |
| `skill-installer` | [`skills/infrastructure_ops/skill-installer/`](./skills/infrastructure_ops/skill-installer/) | An already valid skill needs listing, install, sync, or runtime visibility checks. |

The flat paths [`skills/skill-refactor/`](./skills/skill-refactor/) and [`skills/skillify/`](./skills/skillify/) are compatibility links to the category-owned paths above. Prefer the category path when changing source.

## Factory Lifecycle

```mermaid
flowchart LR
  Idea["Idea, repeated workflow, or observed failure"] --> Router["skill-factory-router"]
  Router --> Creator["skill-creator<br/>Create first usable skill shape"]
  Router --> Skillify["skillify<br/>Capture completed repeatable workflow"]
  Router --> Refactor["skill-refactor<br/>Analyze evidence and recommend direction"]
  Creator --> Builder["skill-factory-router<br/>Route repair until pass or blocked"]
  Skillify --> Builder
  Refactor --> Builder
  Builder --> Installer["skill-installer<br/>Install, sync, and prove visibility"]
  Installer --> Runtime["Runtime-visible skill"]
```

Use this flow as the default handoff path. A lane may stop early only when it records a concrete blocker, a read-only verdict, or a user-requested pause.

## Routing Boundaries

| Request shape | Use | Stop before |
|---|---|---|
| Create a new skill or evolve a draft package into a usable first shape. | `skill-creator` | Release hardening, install proof, or portfolio analysis. |
| Convert a completed repeated workflow into a durable skill package. | `skillify` | Capturing exploratory or one-off work as if it were repeatable. |
| Improve, tighten, test, or release-harden an existing skill or plugin. | `skill-factory-router` | First-draft creation, install/sync operations, or read-only portfolio decisions. |
| Analyze session, review, validation, or Plugin Eval evidence for keep/improve/merge/split/retire direction. | `skill-refactor` | Editing source unless the user explicitly approves the recommended repair lane. |
| List, install, sync, or prove runtime visibility for an already valid skill. | `skill-installer` | Source creation or hardening. |

`skill-factory-router` is the factory front door for repair requests. It selects the current hardening workflow, then the selected lane patches canonical source until its gate passes or a blocker is explicit.

Use the routed hardening workflow for builder-style output: `builder_result`, `diff_summary`, severity-ranked findings, exact validation outcomes, security notes, a handoff lane only when another skill should take over, and one evidence-backed next step.

## Context Lifecycle

Skills are context packages. Durable changes should move through generate, test, distribute, observe, and adapt instead of ending at template completion. Use [`references/context-development-lifecycle.md`](./references/context-development-lifecycle.md) when repeated review feedback, session evidence, or validation drift should become a skill, eval, or routing improvement.

## Tessl And KnowledgeOS

Use [`references/tessl-knowledgeos-capsule.md`](./references/tessl-knowledgeos-capsule.md) when Skill Factory work depends on Tessl plugin layout, registry/install behavior, review/eval lanes, MCP packaging, workspace/project setup, security policy, or the KnowledgeOS-to-Skills-SDK handoff.

The reference is plugin-first: `.tessl-plugin/plugin.json` is the Tessl package manifest, `tessl.json` is the project manifest, plugin-bundled `.mcp.json` differs from project `.mcp.json`, and `tile.json` is legacy/migration terminology. Keep KnowledgeOS source evidence, Skill Factory package validation, Tessl review/eval proof, registry publish state, security policy, hosted PR state, and runtime visibility as separate evidence lanes.
## Source Boundaries

Edit canonical plugin source under [`Plugins/skill-factory/`](../skill-factory/). Do not hand-edit generated runtime projections or copied plugin mirrors.

Category paths are source-owned. Flat compatibility links are runtime conveniences. Confirm the real path with `readlink` or `find -L` before patching.

Runtime cache paths under `Plugins/cache/**` are projections and should not be edited as source. Keep examples, scripts, and references with the skill package that owns them, and do not move user-facing skills between categories without updating discovery metadata and validation.

## Validation

```sh
jq empty Plugins/skill-factory/.codex-plugin/plugin.json
./bin/ask plugins status skill-factory --json --robot
python3 Infrastructure/scripts/lifecycle-and-sync/route_skillset.py --skill-set skill-factory --task "<request>" --json
Infrastructure/bin/plugin-eval analyze Plugins/skill-factory --format markdown
Infrastructure/bin/plugin-eval analyze Plugins/skill-factory/skills/skill-factory-router --format markdown
PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python ./bin/ask skills audit Plugins/skill-factory/skills/skill-factory-router --level strict --json
bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict
bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn
```

Run the focused lane gate first, then the smallest broader package gate. A package-level deferred budget warning can remain even when an individual lane is clean; evaluate important lanes directly before making release-readiness claims. `./bin/ask evals run ... --mode smoke --json` depends on the local Codex runner environment, so report runner startup failures separately from content validation.
