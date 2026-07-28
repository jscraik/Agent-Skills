---
title: Skill picker duplicate elimination via local marketplace cache separation
asset_family: skill discovery and runtime projection hygiene
owner: Agent Skills Team
source_artifact: Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh
freshness_reviewed_on: 2026-07-28
last_updated: 2026-07-28
review_after_days: 60
---

# Skill Picker Duplicate Elimination Via Local Marketplace Cache Separation

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

Skill picker surfaces could hide plugins entirely and/or show duplicate plugin-lane skills (for example `skill-builder` and `plugin-builder`) for two separate reasons:

1. Plugin caches were nested one level too deep (`.../local` or `.../<version|sha>`), while Codex runtime resolves plugin roots at `~/.codex-*/Plugins/cache/<marketplace>/<plugin>`. This produced runtime errors: `failed to load plugin: plugin is not installed`.
2. Runtime homes such as `~/.codex-red` could still load both flat projection skills (`~/.codex-red/skills` -> `.agents/skills`) and plugin cache skills (`~/.codex-red/Plugins/cache/...`) simultaneously.
3. Independent curated plugins can legitimately ship the same skill directory name. Some are true homonyms, such as `cloudflare:agents-sdk` and `openai-developers:agents-sdk`; others are the same workflow exposed through two plugin families, such as `chatgpt-apps:build-chatgpt-app` and `openai-developers:build-chatgpt-app`.

Even after cache-path cleanup, duplicates persisted when stale nested cache variants remained in plugin-cache roots, or when cross-plugin collisions were merely baselined instead of classified by selection policy.

## Resolution

Apply a runtime/cache separation rule plus runtime-compatible plugin-root materialization:

1. Keep local marketplace cache projection under hidden runtime cache path `.agents/plugins-runtime/cache/...`.
2. Materialize every plugin at cache root (`<cache>/<marketplace>/<plugin>/.codex-plugin/plugin.json`) by flattening stale nested `local`/version/hash variants.
3. Keep `Plugins/cache/agent-skills-local` as an ignored compatibility mirror
   for repository parity checks, generated from canonical plugin sources and
   never treated as authored source. The hidden
   `.agents/plugins-runtime/cache/agent-skills-local` tree remains the
   repository runtime cache.
4. Project repaired cache + marketplace manifest into profile homes (for example `~/.codex-red/Plugins/cache` and `~/.codex-red/Plugins/marketplace.json`).
5. For non-symlinked profile plugin directories (for example `~/.codex-red/plugins` as a real directory), also project plugin source mirrors at `~/.codex-red/Plugins/<plugin>` so marketplace `source.path` values like `./Plugins/<plugin>` resolve correctly.
6. Force-prune stale nested version/cache directories during rsync sync (`--delete --force`) so obsolete `0.1.0/` trees cannot survive cache refreshes and create loader ambiguity.
7. Keep the system bridge explicit and narrow: only `skill-creator`, `skill-installer`, `plugin-creator`, and `plugin-installer` are routed through `.agents/skills/.system/*`; all other plugin-family skills stay routed through canonical plugin paths.
8. Enforce plugin-owned skill gating during sync: only names explicitly allowlisted by `PLUGIN_VISIBLE_ROUTER_SKILL_NAMES` may project to flat `.agents/skills` (default is none), while the four `.system` bridge skills remain the only intentional flat/plugin overlap.
9. Classify cross-plugin same-name collisions in `PLUGIN_SKILL_COLLISION_POLICIES`:
   - `distinct_homonym` entries stay available only with qualified plugin names.
   - `same_capability` entries dedupe to a canonical plugin owner and list suppressed candidates in runtime-budget evidence.

This preserves canonical source ownership while keeping plugin runtime paths loadable.

## Evidence

- `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
  - emits cache-root flattening/removal lines for nested plugin variants and
    regenerates both the hidden runtime cache and ignored compatibility mirror.
- `bash Infrastructure/scripts/validation-and-linting/check_codex_home_skill_overlap.sh --codex-home ~/.codex-red --strict --show-overlap`
  - reports overlap counts after reading plugin skills from repaired cache roots.
- `python3 Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py --json`
  - reports `same_capability_scope_collisions` and `distinct_homonym_scope_collisions` from canonical selection policy, while unrelated same-scope collisions remain blocking.
- runtime log evidence:
  - inspect `~/.codex-red/logs_2.sqlite` for prior `failed to load plugin: plugin is not installed` entries under `Plugins/cache/<marketplace>/<plugin>`; post-fix runs should stop producing new instances for repaired plugins.

## Follow-up

- For one-time projection migrations that intentionally touch `Plugins/cache/**`, run validation with explicit projection intent (`PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1`) so path-ownership gates classify the lane correctly.
- Keep the hidden runtime cache authoritative for repository runtime use. If
  `Plugins/cache/agent-skills-local` is present, treat it only as an ignored,
  generated compatibility mirror and never edit or commit it as source.
- Keep rsync cache sync paths on `--delete --force` in both runtime projection and overlap-remediation scripts so stale nested version folders cannot persist.
- Keep `system_bridge_skill_names` scoped to the approved four skills only; do not add additional bridge skills without explicit policy approval.
- Keep plugin families sourced from plugin scope in Codex profiles; do not reintroduce broad plugin-family projection into flat `.agents/skills`.
- In profile homes where `Plugins/` is not symlinked, verify both `Plugins/marketplace.json` and `Plugins/<plugin>` source mirrors are present after sync.
- If a router-skill exception is needed, add it explicitly to `PLUGIN_VISIBLE_ROUTER_SKILL_NAMES`, rerun `bash Infrastructure/scripts/validation-and-linting/check_plugin_skill_shadowing.sh`, and record why overlap is acceptable.
- If a curated plugin adds another same-name skill, do not add it to an ad hoc allowlist. Classify it in `PLUGIN_SKILL_COLLISION_POLICIES` as either `same_capability` with a canonical owner or `distinct_homonym` with qualified display names, then rerun runtime-budget validation.
- Use `bash Infrastructure/scripts/validation-and-linting/check_codex_home_skill_overlap.sh --codex-home <home> --strict --show-overlap` as the one-command runtime audit for Codex profiles (`~/.codex`, `~/.codex-red`, and others); add `--remediate-cache-skills` to repair nested cache layouts before overlap checks.
