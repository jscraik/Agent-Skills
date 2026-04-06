---
name: plugin-creator
description: Scaffold local Codex plugins with a contract-valid `.codex-plugin/plugin.json`, optional companion folders, and marketplace entries. Use when the user asks to create a new plugin skeleton, generate plugin.json, or add marketplace entries.
metadata:
  short-description: Scaffold plugin skeletons and marketplace entries
---

# Plugin Creator

## When to use

Use this skill when the user asks to:
- create a new local plugin skeleton;
- generate `.codex-plugin/plugin.json` with valid baseline fields;
- add or update local marketplace entries.

Do not use this skill as primary owner for:
- skill lifecycle hardening and eval upgrades;
- full plugin packaging beyond scaffold scope.

Handoffs:
- to `skill-builder` when bundled skills need quality hardening;
- to `codex-plugin-builder` for full plugin package assembly and governance checks.

## Inputs

Minimum inputs:
- plugin name (will be normalized to lowercase hyphen-case);
- optional companion folder flags (`--with-<type>`);
- marketplace intent (`--with-marketplace`).

## Outputs

Expected outputs (schema_version: 1):
- `<plugin-root>/<plugin-name>/.codex-plugin/plugin.json`;
- optional companion folders selected by flags;
- marketplace entry at `.agents/plugins/marketplace.json` when requested.

## Resources

- **scripts/**: Contains `create_basic_plugin.py` for deterministic scaffold generation.
- **references/**: Contains contract definitions (`contract.yaml`), evaluation spec (`evals.yaml`), plugin JSON spec (`plugin-json-spec.md`), and task profile (`task-profile.json`).
- **assets/**: Contains plugin icons and visual assets (`plugin-creator.png`, `plugin-creator-small.svg`).

## Philosophy

Plugin scaffolding should be deterministic and policy-forward:
- normalize names once and reuse consistently;
- keep defaults explicit so downstream automation is stable;
- separate scaffold creation from deeper packaging lifecycle decisions.

## Constraints

- Keep `.codex-plugin/plugin.json` present in every generated plugin.
- Never output secrets, tokens, or private credentials in generated manifests.
- Redact sensitive values in any shared logs or snippets by default.

## Procedure

1. Normalize plugin name.
2. Run scaffold via the unified CLI (`ask plugins init`).
3. Add optional folders only when requested.
4. Generate or update marketplace entry with explicit policy defaults.
5. Validate generated outputs before handoff.

Core command:

```bash
# Initialize a new plugin scaffold with marketplace entry
bin/ask plugins init <plugin-name> --with-marketplace --with-scripts --with-assets
```

## Anti-Patterns

Avoid these failures:
- mixing plugin scaffold scope with full package governance work;
- silently overwriting existing entries without explicit intent;
- writing absolute repo paths into marketplace `source.path` values.

## Examples

- When the user asks: "Can you create a repo-local plugin scaffold named `incident-tools` and add marketplace entry?"
- When the user says: "Help me set up a new plugin skeleton with scripts and assets folders."

## Validation

Run checks in order and fail fast: stop at first failure, fix it, then rerun from the failed gate.

Validate the generated plugin artifacts (not this authoring skill):

```bash
# Validate the created plugin scaffold
python3 utilities/skill-builder/scripts/openclaw_skill_guard.py .codex-plugin --mode both

# Run family benchmark validation
python3 scripts/validate_skill_authoring_family_benchmarks.py .codex-plugin

# Full Repository Health
bin/ask repo validate --ephemeral
```

## See Also

| Skill | When to use together |
|---|---|
| [[codex-plugin-builder]] | Promote scaffold into a full plugin package with governance checks |
| [[skill-builder]] | Improve bundled skill quality before plugin release |
| [[cli-spec]] | Consult the technical contract for the ask CLI |

**Topic map:** [[agent-ops]]
