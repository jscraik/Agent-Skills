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

## Required inputs

- explicit mention of `codex-plugin-builder` in the request or source document;
- plugin package path or source location (repo/path/ref) when implementation work is requested;
- desired validation depth (`smoke` or `full`) if the user already specified one.

## Deliverables

- routing acknowledgement that this alias is delegating to canonical `plugin-builder`;
- plugin-builder-aligned output (changes, checks, and safety notes) without alias drift;
- explicit blocker reporting when package hardening cannot proceed safely.

## Procedure

1. Acknowledge legacy alias usage.
2. Continue execution with `plugin-builder` contract, validation, and safety rules.
3. Keep output terminology canonical (`plugin-builder`) while noting alias compatibility.

## Validation

Run canonical plugin-builder checks:

```bash
python3 utilities/plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins
python3 utilities/plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-compat <path/to/plugin> --marketplace-path .agents/plugins/marketplace.json
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins
```

## Failure mode

- If the request is about pure install/provenance work, route to `plugin-installer`.
- If the request is standalone skill hardening, route to `skill-builder`.
- If plugin boundaries, source provenance, or destination paths are ambiguous, pause and clarify before editing.

## Gotchas

- Symptom: output keeps using `codex-plugin-builder` terminology end-to-end.
- Cause: alias handling skipped canonical handoff language.
- Do instead: treat this skill as a compatibility shim and execute with `plugin-builder` contract.
- Check: final output names `plugin-builder` as canonical owner and only mentions alias compatibility once.

## See Also

| Skill | When to use |
|---|---|
| [[plugin-builder]] | Canonical plugin hardening and conversion skill |
| [[plugin-installer]] | Install and verify third-party plugins from GitHub |
| [[plugin-creator]] | Scaffold a minimal plugin package before hardening |

codex-plugin-builder -> plugin-builder  
codex-plugin-builder -> plugin-installer  
codex-plugin-builder -> plugin-creator

**Topic map:** [[agent-ops]]
