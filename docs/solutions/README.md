---
title: Governed Solutions
owner: Agent Skills Team
freshness_reviewed_on: 2026-03-24
review_after_days: 90
source_artifact: docs/reference/managed-asset-lifecycle.md
asset_family: managed assets
---

# Governed Solutions

## Table of Contents
- [Purpose](#purpose)
- [What Belongs Here](#what-belongs-here)
- [Required Metadata](#required-metadata)
- [Required Content Sections](#required-content-sections)
- [Freshness and Ownership](#freshness-and-ownership)
- [How To Add An Entry](#how-to-add-an-entry)

## Purpose

`docs/solutions/` stores durable, reusable problem-resolution patterns for governed assets in this repo. It is not a task journal, scratchpad, or transient debugging log.

## What Belongs Here

Add an entry only when the result is likely to help future work beyond a single session. Good candidates include:

- lifecycle representation decisions that affect multiple assets
- recurring scaffold or validation failure patterns with a stable fix
- repeatable repo operations that now have a proven safe path

Keep one-off execution notes, raw investigation logs, and per-session status elsewhere.

## Required Metadata

Each solution entry must include frontmatter with:

- `title`
- either `governed_asset` or `asset_family`
- `owner`
- `source_artifact`
- `freshness_reviewed_on`
- `review_after_days`

## Required Content Sections

Each solution entry must contain:

- `## Problem`
- `## Resolution`
- `## Evidence`

Optional sections such as `## Tradeoffs` or `## Follow-up` are fine when they add durable context.

## Freshness and Ownership

- `owner` is the curator responsible for keeping the solution useful.
- `freshness_reviewed_on` records the last date the solution was re-checked.
- `review_after_days` determines when the entry becomes stale for validator purposes.
- If a linked asset changes meaningfully, refresh the solution entry rather than letting it drift silently.

## How To Add An Entry

1. Start from [solution-entry-template.md](/Users/jamiecraik/dev/Agent-Skills/docs/solutions/solution-entry-template.md).
2. Link the entry to a governed asset or clear asset family.
3. Cite at least one concrete source artifact.
4. Keep the problem and resolution concise enough to scan quickly.
