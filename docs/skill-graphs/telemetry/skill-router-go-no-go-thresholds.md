# Skill Router Go/No-Go Thresholds (v1)

## Table of Contents
- [Decision window](#decision-window)
- [Go criteria](#go-criteria)
- [Auto-downgrade triggers](#auto-downgrade-triggers)

## Decision window
- Fixed rolling 7-day window.
- Evaluate once per window; no intra-window mode upgrades.

## Go criteria
To move from `observe_only` to broader active usage:
- first-hit rate improves by at least `+0.03` over baseline.
- override regret rate is `<= 0.10`.
- repeat misroute prompt count is non-increasing versus prior window.
- telemetry redaction violations remain `0`.
- rollback drill passes in current window.

## Auto-downgrade triggers
Force immediate downgrade to `observe_only` when any trigger is true:
- rollback drill fails.
- kill-switch is active.
- redaction violation count > 0.
- repeat misroute prompt count rises by >20% window-over-window.
- low-confidence auto-run is observed in agent mode.
