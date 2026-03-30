# Audit Scorecard Template

Use this template when `baseline-ui` runs in `--audit` mode.

## Audit Health Score

| # | Dimension | Score | Key Finding |
|---|---|---|---|
| 1 | Accessibility | ?/4 | Most critical a11y issue or `--` |
| 2 | Performance | ?/4 | Most critical performance issue or `--` |
| 3 | Responsive Design | ?/4 | Most critical responsive issue or `--` |
| 4 | Theming | ?/4 | Most critical theming issue or `--` |
| 5 | Anti-Patterns | ?/4 | Most visible anti-pattern issue or `--` |
| **Total** |  | **?/20** | **Rating band** |

Rating bands:
- `18-20`: Excellent (minor polish)
- `14-17`: Good (address weak dimensions)
- `10-13`: Acceptable (significant work needed)
- `6-9`: Poor (major overhaul recommended)
- `0-5`: Critical (fundamental issues)

## Required Sections

1. Anti-pattern verdict (start here)
2. Executive summary
3. Detailed findings by severity (`P0` to `P3`)
4. Patterns and systemic issues
5. Positive findings
6. Prioritized next actions
7. Optional flow-friction note when the audited surface is a full user flow rather than a single isolated component

## Severity Rubric

- `P0`: Blocking issue that prevents key flows or release readiness
- `P1`: Major issue causing serious usability, accessibility, or performance risk
- `P2`: Minor issue with workaround; should be fixed in next pass
- `P3`: Polish-level improvement with low user impact

## Audit Mode Rules

- Audit mode is report-only by default.
- Do not apply code edits unless the user explicitly asks for fixes.
- Every finding must include location, impact, and concrete recommendation.
- If a flow-friction note is included, keep it short and tie it to visible overload or context switching.
