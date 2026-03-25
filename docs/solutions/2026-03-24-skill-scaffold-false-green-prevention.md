---
title: Skill scaffold false-green prevention
asset_family: canonical skills and plugin packages
owner: Agent Skills Team
source_artifact: utilities/skill-builder/scripts/init_skill.py
freshness_reviewed_on: 2026-03-24
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

Require lifecycle metadata at scaffold time, include an initial review timestamp, and keep the generated copy explicitly incubating rather than silently production-shaped. Also include `## Gotchas` and `## See Also` by default so new skills participate in the local skill graph instead of starting as isolated stubs.

## Evidence

- [init_skill.py](/Users/jamiecraik/dev/Agent-Skills/utilities/skill-builder/scripts/init_skill.py)
- [create_basic_plugin.py](/Users/jamiecraik/dev/Agent-Skills/skills-system/plugin-creator/scripts/create_basic_plugin.py)
- [test_skill_creator_lifecycle_scaffold.py](/Users/jamiecraik/dev/Agent-Skills/scripts/test_skill_creator_lifecycle_scaffold.py)
- [test_plugin_creator_lifecycle_scaffold.py](/Users/jamiecraik/dev/Agent-Skills/scripts/test_plugin_creator_lifecycle_scaffold.py)
