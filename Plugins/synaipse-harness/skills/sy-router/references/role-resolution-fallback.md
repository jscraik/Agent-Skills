# He-Router Role Resolution Fallback

Preserved context moved from `skills/sy-router/SKILL.md` during budget trimming:

- Resolve mapped roles from `~/.codex/agents/manifest.json` using the exact canonical role names from `Plugins/synaipse-harness/references/routing-map.json`.
- Do not invent `sy-*` role aliases; `sy-*` identifies SynAIpse Harness stages, while subagent roles use manifest-backed role names.
