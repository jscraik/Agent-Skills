# CodeRabbit Plugin

Codex plugin package for CodeRabbit review operations: reference guidance, CLI review triage, unresolved-thread autofix workflows, and behavior-preserving simplify passes.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Quickstart Modes](#quickstart-modes)
- [Linear-First Defaults](#linear-first-defaults)
- [Validation](#validation)

## Included Surfaces
- `.codex-plugin/plugin.json`
- `skills/coderabbit/`
  - `SKILL.md`
  - `references/`
- `skills/code-review/`
  - `SKILL.md`
  - `references/`
  - `scripts/`
- `skills/autofix/`
  - `SKILL.md`
  - `github.md`
  - `references/`
  - `scripts/`
- `skills/simplify/`
  - `SKILL.md`
  - `references/`

## Source Of Truth
- Source family:
  - `plugins/coderabbit/skills/coderabbit/`
  - `plugins/coderabbit/skills/code-review/`
  - `plugins/coderabbit/skills/autofix/`
  - `plugins/coderabbit/skills/simplify/`
- Packaged cache mirror:
  - `plugins/cache/agent-skills-local/coderabbit/local/`

When updating this plugin, keep source and packaged mirror behaviorally aligned.

## Quickstart Modes
Use these modes to reduce setup friction for humans and AI agents:

- `setup`: configure baseline `.coderabbit.yaml`, then validate schema and first PR run.
- `review-only`: run `code-review` and output blocker-first findings without edits.
- `autofix-safe`: run `autofix` in manual approval mode, one unresolved thread at a time.
- `pre-merge-simplify`: run `simplify` against current diff and apply behavior-preserving cleanup.

### Example prompts
- "Use CodeRabbit setup mode for a TypeScript repo and produce a minimal config."
- "Run review-only mode against uncommitted changes and list critical/warning findings."
- "Run autofix-safe mode and ask before each patch."
- "Run pre-merge-simplify mode and keep behavior unchanged."

## Linear-First Defaults
For Linear-first repositories:

- Keep `reviews.sequence_diagrams: true` explicit in `.coderabbit.yaml`.
- Keep GitHub issue auto-enrichment disabled by default unless explicitly requested.
- Validate required-check naming (`pr-pipeline`) through repo contracts before CI topology changes.

## Validation
Validate lifecycle and discoverability:

```sh
source scripts/codex_env_common.sh && codex_apply_env
ask plugins status coderabbit
ask plugins doctor
```

Validate plugin state tests:

```sh
python3 -m unittest tests/test_ask_plugins_state.py
```
