# He-Router Role Resolution Fallback

Preserved context moved from `skills/he-router/SKILL.md` during budget trimming:

- Resolve mapped roles from `~/.codex/agents/manifest.json` using the exact canonical role names from `Plugins/harness-engineering/references/routing-map.json`.
- Do not invent `he-*` role aliases; `he-*` identifies Harness Engineering stages, while subagent roles use manifest-backed role names.
