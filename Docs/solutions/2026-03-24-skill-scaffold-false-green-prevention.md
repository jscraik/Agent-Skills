---
title: Skill scaffold false-green prevention
asset_family: canonical skills and plugin packages
owner: Agent Skills Team
source_artifact: skills-system/skill-creator/scripts/init_skill.py
freshness_reviewed_on: 2026-09-26
review_after_days: 90
---

# Skill Scaffold False-Green Prevention

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)

## Problem

New skill and plugin scaffolds were producing outputs that looked mature enough to ship while still missing lifecycle governance data or adjacent-skill navigation sections.

## Resolution

Require lifecycle metadata at scaffold time and include an initial review
timestamp. The current skill scaffold declares `lifecycle_state: active` with
`maturity: experimental`; the plugin scaffold declares `incubating` with
`experimental` maturity. Neither label proves release readiness.

The skill scaffold uses the compact SDK heading contract, including `## Gotchas`
and `## References`, rather than the historical `## See Also` heading. It also
creates adjacent contract, eval, task-profile, source-context, and agent files.
Validate the resulting package and its behavior before making readiness claims.

## Evidence

- [init_skill.py](/skills-system/skill-creator/scripts/init_skill.py)
- [create_basic_plugin.py](/Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.py)
- [test_skill_creator_lifecycle_scaffold.py](/Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py)
- [test_plugin_creator_lifecycle_scaffold.py](/Infrastructure/scripts/testing/test_plugin_creator_lifecycle_scaffold.py)
