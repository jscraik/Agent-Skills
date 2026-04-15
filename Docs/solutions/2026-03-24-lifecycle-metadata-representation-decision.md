---
title: Lifecycle metadata representation decision
asset_family: phase-one managed assets
owner: Agent Skills Team
source_artifact: docs/reference/managed-asset-lifecycle.md
freshness_reviewed_on: 2026-03-24
review_after_days: 90
---

# Lifecycle Metadata Representation Decision

## Table of Contents
- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)

## Problem

The repo needed one inspectable source of lifecycle truth for governed assets without introducing a shadow registry that could drift from the files contributors actually edit.

## Resolution

Keep lifecycle metadata in-file on the canonical asset, use frontmatter for Markdown-governed skills, use the native plugin manifest for plugin packages, and let packaged skills inherit from their one-to-one canonical source when that mapping is lossless enough for governance use.

## Evidence

- [managed-asset-lifecycle.md](/Users/jamiecraik/dev/Agent-Skills/docs/reference/managed-asset-lifecycle.md)
- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md](/Users/jamiecraik/dev/Agent-Skills/Docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md)
- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md](/Users/jamiecraik/dev/Agent-Skills/Docs/plans/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md)
