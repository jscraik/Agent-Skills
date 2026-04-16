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
  - `Infrastructure/references/`
- `skills/code-review/`
  - `SKILL.md`
  - `Infrastructure/references/`
  - `Infrastructure/scripts/`
- `skills/autofix/`
  - `SKILL.md`
  - `github.md`
  - `Infrastructure/references/`
  - `Infrastructure/scripts/`
- `skills/simplify/`
  - `SKILL.md`
  - `Infrastructure/references/`

## Source Of Truth
- Source family:
  - `Plugins/coderabbit/skills/library_api_reference/coderabbit/`
  - `Plugins/coderabbit/skills/code_quality_review/code-review/`
  - `Plugins/coderabbit/skills/code_quality_review/autofix/`
  - `Plugins/coderabbit/skills/code_quality_review/simplify/`
- Packaged cache mirror:
  - `.agents/plugins-runtime/cache/agent-skills-local/coderabbit/local/`

When updating this plugin, keep source and packaged mirror behaviorally aligned.

## Quickstart Modes
Use these modes to reduce setup friction for humans and AI agents:

- `run` (recommended front door): classify intent and execute the safest mode automatically (`setup`, `review-only`, `autofix-safe`, or `pre-merge-simplify`) with one confirmation checkpoint before edits.
- `setup`: configure baseline `.coderabbit.yaml`, then validate schema and first PR run.
- `review-only`: run `code-review` and output blocker-first findings without edits.
- `autofix-safe`: run `autofix` in manual approval mode, one unresolved thread at a time.
- `pre-merge-simplify`: run `simplify` against current diff and apply behavior-preserving cleanup.

### Run mode routing policy
- If `.coderabbit.yaml` is missing or clearly invalid, route to `setup`.
- If the user requests findings-only output, route to `review-only`.
- If unresolved CodeRabbit PR threads exist and user asks to apply fixes, route to `autofix-safe`.
- If user asks for behavior-preserving cleanup on an existing diff, route to `pre-merge-simplify`.
- When scope is ambiguous, start with `review-only` and ask one clarifying question.

### Example prompts
- "Run CodeRabbit in `run` mode for this branch and choose the safest lane."
- "Use CodeRabbit setup mode for a TypeScript repo and produce a minimal config."
- "Run review-only mode against uncommitted changes and list critical/warning findings."
- "Run autofix-safe mode and ask before each patch."
- "Run pre-merge-simplify mode and keep behavior unchanged."

## Linear-First Defaults
For Linear-first repositories:

- Keep `reviews.sequence_diagrams: true` explicit in `.coderabbit.yaml`.
- Keep GitHub issue auto-enrichment disabled by default unless explicitly requested.
- Validate required-check naming (`pr-pipeline`) through repo contracts before CI topology changes.

## Response Envelope
All operational modes should emit the same top-level handoff keys so humans and agents can parse outcomes consistently:

- `schema_version`
- `summary`
- `actions`
- `validation`
- `risk_note`
- `next_step`

Reference mode should also include a trust banner:

- `freshness_checked_at`
- `confidence` (`high|medium|low`)
- `live_verification_needed` (`true|false`)

## Skill Visibility UX
- Default catalog surfaces should prioritize the router (`coderabbit`) and hide lane skills (`code-review`, `autofix`, `simplify`) unless advanced mode is requested.
- Power users and agents can still invoke lane skills directly by name even when hidden from default lists.
- For CLI catalog checks, use:
  - `python3 bin/ask skills list --json` (default view)
  - `python3 bin/ask skills list --advanced --json` (full view)

## Validation
Validate lifecycle and discoverability:

```sh
source Infrastructure/scripts/codex_env_common.sh && codex_apply_env
ask plugins status coderabbit
ask plugins doctor
```

Validate plugin state tests:

```sh
python3 -m unittest Infrastructure/tests/test_ask_plugins_state.py
```
