# Risk Scoring Methodology

## Overview

The PR architecture impact analysis uses a differentiated risk scoring system that weighs different types of changes based on their potential architectural impact.

## Scoring Factors

| Factor | Weight | Trigger |
|--------|-------|---------|
| Auth component changed | +3 | Changes to files matching `**/auth/**`, `**/*auth*`, `**/*credential*`, `**/*identity*`, `**/session*`, `**/token*` |
| Security boundary touched | +3 | Changes to files matching `**/security/**`, `**/*security*`, `**/*permission*`, `**/*authorization*`, `**/*access-control*`, `**/middleware/*auth*` |
| Database path touched | +2 | Changes to files matching `**/database/**`, `**/db/**`, `**/migrations/**`, `**/*repository*`, `**/models/**`, `**/schema/**`, `**/prisma/**`, `**/sequelize/**` |
| Blast radius >= 5 nodes | +1 | When transitive impact reaches 5+ components |
| Edge delta >= 10 edges | +1 | When 10+ dependency edges are added/removed |

## Severity Levels

| Score | Level | Description |
|-------|-------|-------------|
| 0 | none | No architectural risk detected |
| 1-2 | low | Minor changes, localized impact |
| 3-5 | medium | Moderate changes, some cross-cutting concerns |
| 6+ | high | Significant changes affecting critical components |

## Blast Radius Calculation

Blast radius represents components potentially impacted through transitive dependencies:

1. **Direct Impact**: Files changed in the diff
2. **Transitive Impact**: Components that depend on changed components (BFS traversal)
3. **Depth Bounding**: Default max 2 hops from changed components
4. **Node Cap**: Default max 50 components in report (truncates if exceeded)

### Truncation Indicators

When node cap is hit:
- `blastRadius.truncated: true` in JSON output
- `blastRadius.omittedCount` shows number of cut components

## Risk Gate Usage

### Threshold-based Gating

```bash
# Fail if risk meets or exceeds "high" threshold
diagram workflow pr . --risk-threshold high --fail-on-risk

# Fail if risk meets or exceeds "medium" threshold (includes high)
diagram workflow pr . --risk-threshold medium --fail-on-risk

# Fail if any risk detected (includes low, medium, high)
diagram workflow pr . --risk-threshold low --fail-on-risk
```

### Override Mechanism

When a risk gate would fail but the change is approved:

```bash
diagram workflow pr . --risk-threshold high --fail-on-risk \
  --risk-override-reason "Approved by security review per SEC-123"
```

The override reason is recorded in the output artifacts for audit purposes.

### Exit Codes with Risk Gate

| Code | Meaning |
|------|---------|
| 0 | Risk below threshold OR override applied |
| 1 | Risk meets/exceeds threshold AND no override |
| 2 | Git/configuration error |

## Best Practices

1. **Set appropriate thresholds**: Use `high` for production branches, `medium` for development
2. **Document overrides**: Always include a ticket/PR reference in override reasons
3. **Review blast radius**: Even with overrides, review the blast radius for awareness
4. **CI separation**: Run analysis and risk gate as separate jobs for better visibility
