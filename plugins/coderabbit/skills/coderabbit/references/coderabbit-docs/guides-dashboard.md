---
source: https://docs.coderabbit.ai/guides/dashboard
---

# Dashboard Overview

The CodeRabbit Dashboard provides visibility into your team's review speed, code quality, collaboration patterns, and the impact of AI-assisted reviews. Use the dashboard to track performance, identify bottlenecks, and measure the ROI of CodeRabbit across your organization.

## Filters

All dashboard metrics can be filtered by:

- **Timeframe**: Select a date range for analysis
- **Repository**: Focus on specific repositories
- **Username**: View individual contributor metrics

## Dashboard tabs

The dashboard is organized into six tabs, each designed for different analytical needs.

### Summary

The Summary tab provides a high-level overview of team performance in terms of delivery speed and review quality. It displays throughput metrics, time saved through AI-assisted reviews, comment volume and acceptance rates, and issues surfaced by automated tools.

For detailed metric definitions, see Summary metrics.

**Key questions this tab answers:**

- How much productivity is the team gaining from AI-assisted reviews?
- Is AI-generated feedback trustworthy and relevant?
- What types of review comments appear most frequently?

### Quality Metrics

The Quality Metrics tab shows what kinds of issues CodeRabbit flags, how often developers agree with the feedback, and where the largest opportunities for code quality improvements exist.

For detailed metric definitions, see Quality metrics.

**Key questions this tab answers:**

- Are we improving code quality across critical domains?
- Is CodeRabbit catching meaningful issues?
- Do developers trust and act on AI suggestions?
- Are certain teams or repositories seeing more severe problems?

### Time Metrics

A fast review cycle keeps engineering teams unblocked and deployments predictable. The Time Metrics tab highlights how quickly work moves through your review process.

For detailed metric definitions, see Time metrics.

**Key questions this tab answers:**

- Is our review process fast enough to support development velocity?
- Where do PRs wait the longest -- before, during, or after reviews?
- Are certain repositories or teams experiencing delays unrelated to reviews?

### Org Trends

The Org Trends tab visualizes how your team's activity and collaboration patterns evolve over time, helping you identify trends in throughput, review participation, and CI/CD health.

For detailed metric definitions, see Org Trends metrics.

**Key questions this tab answers:**

- Are we merging work consistently, or is a backlog forming?
- Is review participation evenly distributed across the team?
- Are weekly activity levels trending in a healthy direction?

### Data Metrics

The Data Metrics tab lets you drill down to individual pull requests and users. It's designed for auditability, coaching insights, and debugging review process issues.

For detailed metric definitions, see Data metrics.

**Key questions this tab answers:**

- Which developers need more support?
- Which PRs took unusually long to finalize, and why?
- Are certain contributors struggling with specific issue types?
- Which tools surface the most issues?

### Data Export

The Data Export tab provides data downloads for offline analysis, reporting, or integration with other tools.

**Currently available:**

- **Review Metrics**: Download per-pull request review metrics as a CSV file, including complexity scores, review times, and comment breakdowns by severity and category.

For export instructions and field definitions, see Data Export.
