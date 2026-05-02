# Skill Factory

Skill Factory is the Codex plugin for skill lifecycle work: route requests, create or capture skill packages, harden existing packages, analyze reliability evidence, and verify runtime installation. The plugin manifest is [`.codex-plugin/plugin.json`](./.codex-plugin/plugin.json); bundled skills live in [`skills/`](./skills/).

| Lane | Canonical path | Use when |
|---|---|---|
| `skill-factory-router` | [`skills/skill-factory-router/`](./skills/skill-factory-router/) | A request needs classification before execution. |
| `skill-creator` | [`skills/scaffolding_templates/skill-creator/`](./skills/scaffolding_templates/skill-creator/) | A new skill or draft package needs its first usable shape. |
| `skill-builder` | [`skills/code_quality_review/skill-builder/`](./skills/code_quality_review/skill-builder/) | An existing skill or plugin needs evidence-backed hardening, budget reduction, eval coverage, safety checks, or release readiness. |
| `skill-refactor` | [`skills/data_fetch_analysis/skill-refactor/`](./skills/data_fetch_analysis/skill-refactor/) | Session or portfolio evidence should drive keep, improve, merge, split, retire, or redirect decisions. |
| `skillify` | [`skills/scaffolding_templates/skillify/`](./skills/scaffolding_templates/skillify/) | A completed repeatable workflow should become a durable skill package. |
| `skill-installer` | [`skills/infrastructure_ops/skill-installer/`](./skills/infrastructure_ops/skill-installer/) | An already valid skill needs listing, install, sync, or runtime visibility checks. |

The flat paths [`skills/skill-builder/`](./skills/skill-builder/), [`skills/skill-refactor/`](./skills/skill-refactor/), and [`skills/skillify/`](./skills/skillify/) are compatibility links to the category-owned paths above. Prefer the category path when changing source.

## Skill Builder Boundary

- Creator designs the first usable shape.
- Builder hardens an existing skill with concrete edits, validation evidence, residual risks, and the next smallest hardening step.
- Installer proves runtime visibility for an already valid skill.
- Refactor decides keep, merge, split, retire, or redirect from usage evidence.

Use Skill Builder for builder-style output: `builder_result`, `diff_summary`, severity-ranked findings, exact validation outcomes, security notes, a handoff lane only when another skill should take over, and one evidence-backed next step.

## Source Boundaries

Edit canonical plugin source under [`Plugins/skill-factory/`](../skill-factory/). Do not hand-edit generated runtime projections or copied plugin mirrors. Some active skill files resolve through symlinks into [`fixtures/budget-archive/`](./fixtures/budget-archive/); verify with `readlink` or `find -L` before choosing an edit target.

## Validation

```sh
python3 Infrastructure/scripts/lifecycle-and-sync/route_skillset.py --skill-set skill-factory --task "<request>" --json
Infrastructure/bin/plugin-eval analyze Plugins/skill-factory --format markdown
Infrastructure/bin/plugin-eval analyze Plugins/skill-factory/skills/code_quality_review/skill-builder --format markdown
PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python ./bin/ask skills audit Plugins/skill-factory/skills/code_quality_review/skill-builder --level strict --json
bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict
bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn
```

Run the focused lane gate first, then the smallest broader package gate. A package-level deferred budget warning can remain even when an individual lane is clean; evaluate important lanes directly before making release-readiness claims. `./bin/ask evals run ... --mode smoke --json` depends on the local Codex runner environment, so report runner startup failures separately from content validation.
