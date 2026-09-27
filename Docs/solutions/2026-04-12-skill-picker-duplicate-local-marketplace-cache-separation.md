---
title: Skill picker duplicate elimination via local marketplace cache separation
asset_family: skill discovery and runtime projection hygiene
owner: Agent Skills Team
source_artifact: Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh
freshness_reviewed_on: 2026-09-27
last_updated: 2026-09-27
review_after_days: 60
---

# Skill Picker Duplicate Elimination Via Local Marketplace Cache Separation

Historical solution, superseded for new installations. The 2026-09-27 review
compared the remaining sync implementation with the current OpenAI plugin
documentation and the approved repository-separation lifecycle. Do not apply
the old cache-flattening recipe to provider-managed or newly installed plugins.

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

The earlier transitional profile layout could hide plugins or show duplicate
plugin-lane skills such as `skill-builder` and `plugin-builder`. This note
originally attributed that behaviour to these conditions:

1. A mismatch between the then-used profile loader and nested cache variants
   accompanied `plugin is not installed` errors. That historical diagnosis is
   not a rule that all versioned directories are invalid.
2. Runtime homes such as `~/.codex-red` could still load both flat projection skills (`~/.codex-red/skills` -> `.agents/skills`) and plugin cache skills (`~/.codex-red/Plugins/cache/...`) simultaneously.
3. Independent curated plugins can legitimately ship the same skill directory name. Some are true homonyms, such as `cloudflare:agents-sdk` and `openai-developers:agents-sdk`; others are the same workflow exposed through two plugin families, such as `chatgpt-apps:build-chatgpt-app` and `openai-developers:build-chatgpt-app`.

Even after cache-path cleanup, duplicates persisted when stale nested cache variants remained in plugin-cache roots, or when cross-plugin collisions were merely baselined instead of classified by selection policy.

## Resolution

Retire the general flatten-and-prune instruction, not the inventory or working
consumer. Current OpenAI documentation describes installed plugin caches under
`~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`, including `local`
versions. A nested version directory alone is therefore not a defect. See
[Package your plugin](https://developers.openai.com/plugins/build/plugins).

Use the [approved lifecycle](/Docs/agents/14-path-ownership-boundaries.md#approved-lifecycle)
for new managed installations: SDK-checked private Tessl versions feed the
selected Codex runtime. Verified OpenAI plugins and system skills remain on
provider-managed routes. Do not flatten, prune, copy or relink them based on
this historical note.

For a specific existing-consumer failure, use
[Skill Management](/Docs/agents/17-skill-management.md), identify the actual
loader and installed candidate, and obtain the matching runtime/recovery
authority. Preserve complete plugin contents and the prior working state.
Do not infer a duplicate from two identical skill names alone; qualify their
provider/plugin identities before applying the active selection policy.

## Evidence

- Source inspection on 2026-09-27 found the old flattening behaviour still in
  `sync_local_marketplace_cache` and `materialize_plugin_cache_roots` in
  `Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh`. Its presence
  records a transitional dependency; it does not establish compatibility with
  current provider-managed caches.
- The current OpenAI documentation above distinguishes marketplace source paths
  from installed versioned cache paths. Compare the actual selected loader and
  installed version before diagnosing a path as stale.
- This review changed documentation only. It did not run sync, prune directories,
  modify provider files, or prove installed behaviour. Source-only validation
  cannot prove that every historical profile consumer has migrated.

## Follow-up

- Account for remaining sync/profile consumers during SDK adapter work; do not
  copy this historical implementation into the destination as a universal rule.
- Prove selected-package discovery, complete behaviour and recovery with
  Agent-Skills unavailable before retiring its runtime dependencies.
- Keep cache materialisation and cleanup separate from source edits and
  catalogue checks. This note grants no runtime mutation or deletion authority.
