# Sub-Agent Map

Read when: the user explicitly requests delegation and `ce-tdd` needs specialist review lanes without uncontrolled fan-out.

## Table of Contents
- [Purpose](#purpose)
- [Selection contract](#selection-contract)
- [Baseline lanes](#baseline-lanes)
- [Risk-specific lanes](#risk-specific-lanes)
- [Execution order](#execution-order)

## Purpose
Map TDD weak spots to deterministic specialist lanes so verification quality improves without turning execution into reviewer sprawl.

## Selection contract
1. Use this map only when delegation is explicitly requested.
2. Start with baseline lanes.
3. Add only lanes justified by concrete risk signals in the current behavior slice.
4. Keep lane count minimal and bounded.

## Baseline lanes
Always include:
- `testing-reviewer`
- `correctness-reviewer`

## Risk-specific lanes
Add by signal:
- security-sensitive behavior or auth/session changes: `security-reviewer`
- migration, persistence, or state integrity behavior: `data-integrity-guardian`
- high-throughput or latency-sensitive behavior: `performance-reviewer`
- architecture-coupled boundary redesign while preserving behavior contracts: `architecture-strategist`
- final simplification pass after GREEN and refactor: `code-simplicity-reviewer`

## Execution order
1. baseline lanes
2. risk-specific lanes
3. integrate findings into the next RED -> GREEN slice
