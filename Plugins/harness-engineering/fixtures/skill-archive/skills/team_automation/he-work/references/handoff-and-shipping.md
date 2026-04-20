# CE Work Handoff And Shipping

## Table of Contents
- [Purpose](#purpose)
- [Required handoff package](#required-handoff-package)
- [Operational validation notes](#operational-validation-notes)
- [Review tiers](#review-tiers)
- [Commit and PR guidance](#commit-and-pr-guidance)
- [Status updates](#status-updates)

## Purpose
This note keeps the final execution handoff concrete while modernizing away from stale tool-vendor-specific commit and PR templates embedded in older prompts.

## Required handoff package
The final handoff should include:
- what changed
- files or areas touched
- tests, lint, type checks, and other validation run
- completed plan/checklist/acceptance IDs when the governing artifact exposes them
- any plan/spec updates made because execution discovered drift
- remaining risks, follow-up work, or explicit deferrals
- post-deploy monitoring and validation notes
- screenshot evidence for UI changes

## Operational validation notes
Every shipped change should include one of:
- concrete monitoring and validation notes:
  - logs or search terms
  - metrics or dashboards
  - expected healthy signals
  - failure signals and rollback triggers
  - validation window and owner
- or a justified no-impact note:
  - `No additional operational monitoring required` plus a one-line reason

## Review tiers
Every meaningful code change gets reviewed before handoff. Default to Tier 2.

Tier 2: full review
- default for almost all execution work
- run `he-review mode:autofix` and pass `plan:` when the governing plan path is available
- accept safe fixes automatically, then surface any remaining actionable work in the final handoff

Tier 1: inline self-review
- allowed only when all four are explicitly true:
  - purely additive
  - single concern
  - pattern-following
  - plan-faithful
- if any one of those is unclear, use Tier 2 instead

## Commit and PR guidance
- use the current repo's commit and PR conventions
- do not copy obsolete vendor-specific badge blocks or attribution templates from legacy prompts
- if the repo or harness requires an attribution trailer, follow that rule exactly
- keep commit boundaries logical and avoid `WIP` commits when a focused complete slice can land cleanly

## Status updates
- if the governing artifact has a status field and repo convention expects it to change, update it when execution is actually complete
- keep markdown checkboxes, task trackers, and the final handoff mutually consistent
