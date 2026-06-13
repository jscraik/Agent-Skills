# Docs Structure And Maintenance

Use this reference when auditing docs layout, docs freshness, or project execution state in a solo agent-native repository.

## Default Layout

Default folders:

- docs/architecture/
- docs/references/
- docs/projects/<project>/tasks.md
- docs/projects/archive/

Repos can add other folders when useful, such as docs/decisions, docs/setup, docs/quality, or docs/build-logs.

## Placement Rules

Use docs/architecture/ for system shape:

- boundaries
- layering
- data flow
- major tradeoffs
- dependency direction

Use docs/references/ for exact implementation facts:

- schemas
- API notes
- environment variables
- integration constraints
- command contracts
- field precedence rules

Use docs/projects/<project>/tasks.md for active execution state:

- current goal
- next steps
- decisions made during the work
- resume point
- validation state

Archive completed project folders once the scoped work is confidently done.

## Maintenance Policy

- Update architecture docs when boundaries or key flows change.
- Update references when operational facts change.
- Update project trackers during active work.
- Add mechanical checks when the same docs mismatch repeats.
- Keep AGENTS.md short and point it to the right durable docs.

If documentation cannot be kept current by habit, create a check, wrapper, or review gate that makes drift visible.
