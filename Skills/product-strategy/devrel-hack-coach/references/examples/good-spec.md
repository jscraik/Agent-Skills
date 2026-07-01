# Good Spec Example: CacheScope

Track: Context Engineering.

## Goal

Show backend engineers exactly which line of their prompt is busting the
Anthropic cache, and what it costs each month.

## User

Backend engineers maintaining a production Anthropic integration with API
spend high enough that cache misses matter.

## Demo Moment

- Judge does: pastes two consecutive production API prompts into the CLI.
- Our system does: diffs the calls, highlights the cache-busting line, and
  multiplies by observed request volume.
- Judge sees: a red-highlighted line and "This line cost you $340 last month."

## Idea Pressure Test

- Prior attempt or obvious alternative: spend dashboards show totals after the
  fact.
- Why this path now: prompt caching makes one volatile line expensive enough to
  see.
- What would make this idea a false positive: if teams already know which line
  changed before they check cost.

## What's In

1. CLI that accepts two consecutive API requests and diffs prompts.
2. Cost estimator using observed request volume.
3. One fix suggestion for the volatile prompt line.

## What's Out

- Web dashboard.
- Auto-patching user code.
- Support for every provider.

## Timebox Success

- Working demo runs end-to-end on stage.
- No blocker in the golden path.
- Pitch dry-run completed with a timer.

## Fallback Path

- If the riskiest dependency fails: use two checked-in request fixtures.
- The smallest still-demoable version: static diff plus one cost calculation.

## Red Flags

- Prompt caching differs by model; pick one model and document it.
- Cost numbers must feel real enough to cite during the demo.

Spec locked. Moving to Phase 3.
