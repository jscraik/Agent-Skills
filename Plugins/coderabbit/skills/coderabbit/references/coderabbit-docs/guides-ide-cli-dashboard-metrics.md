---
source: https://docs.coderabbit.ai/guides/ide-cli-dashboard-metrics
---

# IDE/CLI Review Metrics

Detailed definitions for all CodeRabbit IDE and CLI review dashboard metrics.

## Summary

The Summary page provides a high-level overview of review activity across IDE extensions and the CLI. Use it to understand adoption, see whether Learnings carry over to local reviews, and track tool findings.

- **Active Repositories**: Total number of repositories where reviews were performed through IDE extensions or CLI.
- **Active Users**: Number of active users who have used CodeRabbit IDE extensions or CLI for reviews.
- **Reviews**: Total number of code reviews performed through IDE extensions or CLI.
- **Review Comments**: Total review comments posted for reviews done through IDE extensions or CLI.
- **Learnings Usage**: Percentage of IDE/CLI reviews that benefited from Learnings and total times applied.
- **Tool Findings**: Automated tool findings from SAST and linter tools surfaced during reviews.
- **Active Users by Extension Type**: Active users broken down by IDE extension or CLI.
- **Reviews by Extension Type**: Distribution of code reviews across IDE extensions and CLI.

---

## Organization Trends

Track week-over-week adoption of IDE and CLI reviews across your team.

- **Weekly Active Users**: Weekly trend of unique users performing reviews using each IDE extension or CLI.
- **Weekly Reviews**: Weekly trend of reviews performed using each IDE extension or CLI.
- **Weekly Avg Reviews per User**: Weekly trend of average number of reviews per active user.
- **Weekly Review Comments**: Weekly trend of review comments posted through IDE extensions and CLI.
- **Tool Findings by Tool Name**: Number of automated tool findings surfaced during reviews, grouped by individual tool.
- **Tool Findings by Severity**: Number of automated tool findings surfaced during reviews, grouped by severity.

---

## Data Metrics

Drill down into individual user activity to identify who's actively using local reviews and where to focus adoption efforts.

**Active User Details**: Per-user summary of IDE extension and CLI review activity.

Fields included:

- **Full Name**: Full name of the user
- **Username**: Username of the user
- **Extension Type**: IDE extension or CLI used
- **Installed**: When the extension or CLI was installed
- **Last Used**: Timestamp of the user's most recent review
- **Total Reviews**: Number of code reviews performed via CodeRabbit
- **Total Review Comments**: Number of review comments posted by CodeRabbit
