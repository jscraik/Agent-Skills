# Harness Engineering Work Handoff And Shipping

Final handoff includes what changed, areas touched, validation run, Linear issue/status/comment result, governing spec/plan paths, branch/PR or blocker, completed IDs, drift updates, risks/deferrals, rollback or monitoring notes, and UI screenshots when relevant.

Every shipped change includes concrete monitoring notes or a justified no-impact note. Useful notes: logs/searches, metrics, healthy signals, failure signals, rollback triggers, validation window, and owner.

Default meaningful code changes to Tier 2: `he-code-review mode:autofix` with `plan:` when available. Tier 1 inline self-review is only for purely additive, single-concern, pattern-following, plan-faithful slices.

Use repo commit/PR conventions. Keep commits logical, avoid WIP commits, and link PR evidence back to Linear and the governing artifacts. GitHub is delivery evidence, not the tracker of record.
