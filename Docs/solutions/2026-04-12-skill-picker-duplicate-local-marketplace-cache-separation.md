---
title: Skill picker duplicate elimination through cache ownership and selection policy
asset_family: plugin cache ownership and skill discovery policy
owner: Agent Skills Team
source_artifact: Infrastructure/scripts/lib/ask/services/plugin_cache.py
freshness_reviewed_on: 2026-07-26
last_updated: 2026-07-26
review_after_days: 90
---

# Skill Picker Duplicate Elimination Through Cache Ownership And Selection Policy

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

The runtime and picker use different derived plugin-cache surfaces. The canonical
source remains `Plugins/<plugin>`, while the workspace runtime cache is
`.agents/plugins-runtime/cache/<marketplace>/<plugin>` and the versioned picker
cache is `Plugins/cache/<marketplace>/<plugin>/<version>`. Treating either
derived cache as source, or deleting the picker cache to resolve an apparent
duplicate, conflates their consumer contracts.

Duplicate-looking skills have two distinct causes: a plugin can be visible both
through a flat skill route and its plugin route, or independently curated
plugins can own the same directory name. The latter is either a qualified
`distinct_homonym` or a `same_capability` collision; it is not safely resolved
by an unscoped cache cleanup.

## Resolution

Apply the cache-ownership and selection-policy contract:

1. Keep `Plugins/<plugin>` as the canonical source. `plugin_cache.py` produces
   the ignored runtime cache and the versioned picker cache from that source;
   neither cache receives hand edits.
2. Materialize runtime plugins at
   `.agents/plugins-runtime/cache/<marketplace>/<plugin>` and picker plugins at
   `Plugins/cache/<marketplace>/<plugin>/<version>`. Both locations are
   supported because they serve different consumers.
3. Use the owning sync/refresh route to prune stale derived entries. Its
   `rsync --delete --force` behavior applies to the derived destination; it is
   not authority to delete canonical sources or arbitrary profile directories.
4. Keep flat-skill promotion opt-in. The default
   `PLUGIN_VISIBLE_ROUTER_SKILL_NAMES` is empty, and only `skill-creator`,
   `skill-installer`, `plugin-creator`, and `plugin-installer` are intentional
   `.system` bridge overlaps.
5. Resolve cross-plugin same-name cases through
   `PLUGIN_SKILL_COLLISION_POLICIES`: show `distinct_homonym` entries with a
   qualified plugin identity, and choose one canonical owner for
   `same_capability` entries.

This preserves a single source writer while making cache and picker visibility
an explicit selection-policy decision rather than a filesystem accident.

## Evidence

- `Infrastructure/scripts/lib/ask/services/plugin_cache.py` owns the runtime
  cache root and the versioned `Plugins/cache/<marketplace>` picker root.
- `Infrastructure/scripts/lib/ask/commands/plugins.py` defines the local
  `agent-skills-local` marketplace and its repository-owned cache paths.
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py` declares
  the empty default flat-promotion list, four system bridges, and collision
  classifications.
- `Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh` owns
  materialisation and pruning of derived projections.
- `Infrastructure/tests/test_projection_integrity_plugin_cache.py`,
  `Infrastructure/tests/test_local_plugin_picker_surface.py`, and
  `Infrastructure/tests/test_skill_scope_precedence.py` cover the relevant
  cache and selection seams.

## Follow-up

- Do not delete `Plugins/cache/agent-skills-local` as a general duplicate fix:
  it is a supported versioned picker surface.
- Do not edit generated runtime or picker cache entries directly. Use the owning
  cache refresh/sync command only in a separately authorised runtime lane.
- A new flat-router exception requires an explicit
  `PLUGIN_VISIBLE_ROUTER_SKILL_NAMES` policy change and focused shadowing
  validation.
- A new same-name plugin skill requires an explicit collision classification;
  it must not be resolved by an ad hoc allowlist.
- This entry documents source/cache ownership and policy only. It does not
  prove current installed runtime behavior or authorize cache refresh, profile
  projection, or plugin activation.
