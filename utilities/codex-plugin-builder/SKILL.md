---
name: codex-plugin-builder
description: Compatibility alias for `plugin-builder`. Use when legacy prompts reference `codex-plugin-builder`; this skill immediately routes work to `plugin-builder` without changing package behavior.
metadata:
  skill-type: scaffolding_templates
---

# Codex Plugin Builder (Compatibility Alias)

## When to use

Use this alias only when a user or document explicitly requests `codex-plugin-builder`.

Default behavior:
- treat `plugin-builder` as the canonical owner for plugin hardening and conversion;
- preserve backwards compatibility for older instructions and references.

## Procedure

1. Acknowledge legacy alias usage.
2. Continue execution with `plugin-builder` contract, validation, and safety rules.
3. Keep output terminology canonical (`plugin-builder`) while noting alias compatibility.

## Validation

Run canonical plugin-builder checks:

```bash
python3 utilities/plugin-builder/scripts/plugin_builder.py validate <path/to/plugin>
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-compat <path/to/plugin> --marketplace-path .agents/plugins/marketplace.json
```

## See Also

| Skill | When to use |
|---|---|
| [[plugin-builder]] | Canonical plugin hardening and conversion skill |
| [[plugin-installer]] | Install and verify third-party plugins from GitHub |
| [[plugin-creator]] | Scaffold a minimal plugin package before hardening |

**Topic map:** [[agent-ops]]
