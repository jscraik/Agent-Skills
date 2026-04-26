# `/he-improve` Usage Guide

## What This Stage Is For
`he-improve` runs controlled optimization loops when one-shot implementation is not enough.

Use it when:
- you can evaluate variants with the same measurement command,
- "better" can be scored using hard metrics, judge scoring, or both,
- you want evidence-backed keep/revert decisions.

## Good fits
- latency/throughput/memory tuning with explicit gates,
- ranking/search/clustering quality where hard metrics alone can be gamed,
- prompt or workflow tuning with quality and cost tradeoffs.

## Usually not a fit
- obvious single-fix bugs,
- no repeatable measurement harness,
- requests that are really first-pass planning or direct implementation.

## First-run defaults
- use serial mode,
- cap iterations and max run hours,
- keep judge sample size small and capped in cost,
- avoid adding new dependencies until baseline trust is established.

## Core pattern
1. Define target and constraints.
2. Capture baseline.
3. Generate hypotheses.
4. Run bounded experiments.
5. Keep only validated improvements.
6. Handoff best result to `he-work` when implementation delivery is needed.
