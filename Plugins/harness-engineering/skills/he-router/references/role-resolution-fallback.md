# He-Router Role Resolution Fallback

Preserved context moved from `skills/he-router/SKILL.md` during budget trimming:

- Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
- When a selected stage has no `he-*` mapping, fall back to the manifest-mapped role to keep reviewer routing deterministic.
