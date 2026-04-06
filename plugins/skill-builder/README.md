# Skill Builder Plugin

Codex plugin package for the existing `skill-builder` workflow skill. It packages the skill as a plugin-owned skill bundle under `skills/skill-builder/` while keeping the current source skill at `.agents/skills/skill-builder/` as the upstream authoring path for now.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## Included Surfaces
- `.codex-plugin/plugin.json`
- `skills/skill-builder/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `templates/`
  - `workflows/`

## Source Of Truth
- Source skill: `.agents/skills/skill-builder/`
- Packaged skill: `plugins/skill-builder/skills/skill-builder/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating the skill logic, keep the packaged skill bundle aligned with the source skill until the plugin becomes the canonical maintenance path.

## Usage
The `skill-builder` plugin helps you:
- Improve existing skills' routing, workflow, and safety.
- Audit skills against validators and evals.
- Compare variants or fold overlapping skills into one.
- Package validated standalone skills.

## Validation
Validate the package:

```sh
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate plugins/skill-builder
```

Validate the packaged skill bundle:

```sh
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-builder/skills/skill-builder
```
