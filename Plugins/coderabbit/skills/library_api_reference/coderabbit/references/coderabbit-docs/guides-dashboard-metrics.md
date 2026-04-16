---
source: https://docs.coderabbit.ai/guides/dashboard-metrics
---

All metrics on this page that are derived from pull requests are calculated only for pull requests that were **reviewed by CodeRabbit and merged** within the selected timeframe. Metrics can be filtered by repository, username, team, or organization (self-hosted only).

## Summary

The Summary page provides a high-level overview of team performance in terms of delivery speed and review quality.
**Active Repositories**: Total repositories with CodeRabbit installed that had review activity.
**Merged Pull Requests**: Total pull requests reviewed by CodeRabbit and successfully merged, with the average number of PRs merged per active user.
**Active Users**: Total users whose pull requests were reviewed by CodeRabbit, split by assigned and unassigned seats.
**Chat Usage**: Number of chat sessions started and total messages exchanged with CodeRabbit.
**Median Time**: Median time from review readiness to merge and to last commit.

Medians of:

* `(pr_merge - ready_for_review)`
* `(last_commit - ready_for_review)`

where:

* `ready_for_review`: Timestamp when PR was marked ready for review (or creation date if never in draft)
* `pr_merge`: Timestamp when the PR was merged
* `last_commit`: Timestamp of the last non-merge, non-rebased commit (or merge date if no later commit)

**Reviewer Time Saved**: AI-estimated human reviewer time saved during pull request reviews.

Sum of estimated review effort displayed in the Walkthrough section of each
merged PR, representing the human review time saved since CodeRabbit’s
automated analysis handles the initial code review.

**CodeRabbit Review Comments**: Review comments posted by CodeRabbit on merged PRs.
**Acceptance Rate**: Percentage of CodeRabbit comments accepted by developers.
**Avg Review Comments Posted per PR**: Average review comments per pull request from CodeRabbit and human reviewers.
**Review Comments by Severity**: Distribution of CodeRabbit review comments grouped by severity.
**Severity Distribution**: Radar view of CodeRabbit comments by severity, showing posted vs accepted.
**Review Comments by Category**: Distribution of CodeRabbit review comments grouped by category.

Categories describe the type of issue identified:

* **Security & Privacy**: Vulnerabilities that enable exploitation or expose sensitive data (e.g., auth bypass, injection attacks, exposed secrets)
* **Data Integrity & Integration**: Problems that corrupt data or break API/schema contracts (e.g., transaction issues, schema mismatches, broken migrations)
* **Performance & Scalability**: Inefficiencies impacting speed or resource usage (e.g., N+1 queries, missing caching, unoptimized loops)
* **Stability & Availability**: Issues causing crashes, hangs, or resource leaks at runtime (e.g., null pointer errors, memory leaks, deadlocks)
* **Functional Correctness**: Logic errors producing wrong results (e.g., off-by-one errors, incorrect conditions, algorithm mistakes)
* **Maintainability & Code Quality**: Code hygiene affecting readability and future changes (e.g., unclear naming, duplication, poor structure)

Data captured from Nov 10, 2025 onwards.

**Category Distribution**: Radar view of CodeRabbit comments by category, showing posted vs accepted.

Categories describe the type of issue identified:

* **Security & Privacy**: Vulnerabilities that enable exploitation or expose sensitive data (e.g., auth bypass, injection attacks, exposed secrets)
* **Data Integrity & Integration**: Problems that corrupt data or break API/schema contracts (e.g., transaction issues, schema mismatches, broken migrations)
* **Performance & Scalability**: Inefficiencies impacting speed or resource usage (e.g., N+1 queries, missing caching, unoptimized loops)
* **Stability & Availability**: Issues causing crashes, hangs, or resource leaks at runtime (e.g., null pointer errors, memory leaks, deadlocks)
* **Functional Correctness**: Logic errors producing wrong results (e.g., off-by-one errors, incorrect conditions, algorithm mistakes)
* **Maintainability & Code Quality**: Code hygiene affecting readability and future changes (e.g., unclear naming, duplication, poor structure)

Data captured from Nov 10, 2025 onwards.

**Avg Review Iterations per PR**: Average number of review iterations per pull request.

Count of review events per PR.

**Tool Findings**: Automated tool findings surfaced during reviews.

* **SAST**: Security scanners like Semgrep, Betterleaks, Checkov
* **Linter**: Code quality tools like ESLint, RuboCop, Flake8
* **Other**: Unrecognized tools

**Pipeline Failures**: CI/CD pipeline failures detected during reviews (counted once per PR).

If either **Median Time (Merge)** or **Median Time (Last Commit)** spikes, it
may signal bottlenecks or overloaded reviewers.

---

## Quality Metrics

All charts on this page support drill-down into individual comments. Click any acceptance rate stat to view comments for that severity or category. On the bar charts, click a bar to reveal a tooltip, then click the **Posted** or **Accepted** count to list those comments and navigate to each one on the pull request.
**Acceptance Rate by Severity**: Percentage of CodeRabbit comments accepted, grouped by severity. Click any severity value to view all comments for that severity.

`(Accepted comments ÷ Posted comments) × 100` calculated per severity level.

**Review Comment Count by Severity**: Number of CodeRabbit comments posted and accepted, grouped by severity. Click a bar to open a tooltip, then click the Posted or Accepted count to drill down into individual comments.
**Acceptance Rate by Category**: Percentage of CodeRabbit comments accepted, grouped by category. Click any category value to view all comments for that category.

`(Accepted comments ÷ Posted comments) × 100` calculated per category.Data captured from Nov 10, 2025 onwards.

**Review Comment Count by Category**: Number of CodeRabbit comments posted and accepted, grouped by category. Click a bar to open a tooltip, then click the Posted or Accepted count to drill down into individual comments.

Data captured from Nov 10, 2025 onwards.

**Comment Details**: Paginated table of individual comments shown when drilling down from an acceptance rate stat or a bar chart count. Click the pull request number or comment link to navigate to the comment on the pull request.

* **Pull Request**: PR number
* **Comment**: Direct link to the comment on the pull request
* **Repository**: Repository name
* **Author**: PR author
* **Severity**: Severity of the comment
* **Category**: Category of the issue identified
* **Accepted**: Whether the comment was accepted (Yes/No)
* **Created At**: Timestamp of when the comment was posted

Categories describe the type of issue identified:

* **Security & Privacy**: Vulnerabilities that enable exploitation or expose sensitive data (e.g., auth bypass, injection attacks, exposed secrets)
* **Data Integrity & Integration**: Problems that corrupt data or break API/schema contracts (e.g., transaction issues, schema mismatches, broken migrations)
* **Performance & Scalability**: Inefficiencies impacting speed or resource usage (e.g., N+1 queries, missing caching, unoptimized loops)
* **Stability & Availability**: Issues causing crashes, hangs, or resource leaks at runtime (e.g., null pointer errors, memory leaks, deadlocks)
* **Functional Correctness**: Logic errors producing wrong results (e.g., off-by-one errors, incorrect conditions, algorithm mistakes)
* **Maintainability & Code Quality**: Code hygiene affecting readability and future changes (e.g., unclear naming, duplication, poor structure)

High acceptance for critical issues suggests CodeRabbit is catching
**meaningful defects** early.

---

## Time Metrics

**Time to Merge**: Duration from PR review-ready to merge. Shown as average, median, P75, and P90.

`(pr_merge - ready_for_review)` where:

* `ready_for_review`: Timestamp when PR was marked ready for review (or creation date if never in draft)
* `pr_merge`: Timestamp when the PR was merged

**Weekly Review-Ready → Merge Time**: Weekly trend of time from review-ready to merge.
**Time to Last Commit**: Duration from PR review-ready to final commit (or merge if no later commit). Shown as average, median, P75, and P90.

`(last_commit - ready_for_review)` where:

* `ready_for_review`: Timestamp when PR was marked ready for review (or creation date if never in draft)
* `last_commit`: Timestamp of the last non-merge, non-rebased commit (or merge date if no new commits)

**Weekly Review-Ready → Last Commit Time**: Weekly trend of time from review-ready to final commit.
**Time to First Human Review**: Duration from PR review-ready to the first human review activity. Shown as average, median, P75, and P90.

`(first_human_review - ready_for_review)` where:

* `ready_for_review`: Timestamp when PR was marked ready for review (or creation date if never in draft)
* `first_human_review`: Timestamp of the first review activity by a human reviewer

**Weekly Review-Ready → First Human Review Time**: Weekly trend of time from review-ready to the first human review activity.
**Time to Last Human Review**: Duration from PR review-ready to the last human review activity. Shown as average, median, P75, and P90.

`(last_human_review - ready_for_review)` where:

* `ready_for_review`: Timestamp when PR was marked ready for review (or creation date if never in draft)
* `last_human_review`: Timestamp of the last review activity by a human reviewer

**Weekly Review-Ready → Last Human Review Time**: Weekly trend of time from review-ready to the last human review activity.

### Understanding time metrics

* **Average**: Overall average duration across all PRs
* **Median**: Typical duration (less affected by outliers)
* **P75**: 75th percentile, helps identify PRs taking longer than usual
* **P90**: 90th percentile, highlights potential bottlenecks

If **Time to Last Commit** is short but **Time to Merge** is much longer, PRs
may be sitting idle—stalled by approvals, release gates, or unclear ownership.

---

## Knowledge Base

Track how your team’s accumulated knowledge — [Learnings](/knowledge-base/learnings) from review conversations and [MCP server](/integrations/mcp-servers) integrations — contributes to pull request reviews.
**Learnings Created**: Total Learnings created from chat interactions, showing both all-time and within the selected time period.
**Learnings Usage**: Percentage of PRs that benefited from Learnings and total times applied.
**Weekly Learnings Created**: Weekly count of Learnings created.
**Weekly Learnings Applied**: Weekly count of the number of times Learnings were applied.
**PR Coverage by MCP Server**: Percentage of PRs that used each of the MCP servers.
**MCP Tool Usage**: Total tool calls and insights generated per MCP server.
**Tool Findings by Tool Name**: Automated tool findings grouped by individual tool.
**Tool Findings by Severity**: Automated tool findings grouped by severity.

---

## Organization Trends

**Weekly Pull Requests: Created & Merged**: Weekly counts of pull requests created and merged.
**Weekly Avg Comments per PR: CodeRabbit & Human**: Weekly average review comments posted by CodeRabbit and human reviewers.
**Weekly Active Users**: Weekly count of distinct users whose PRs were reviewed by CodeRabbit.
**Weekly Avg Pull Requests per User**: Weekly average number of pull requests merged per user.
**Weekly Chat Sessions**: Weekly trend of chat interactions with CodeRabbit on pull requests.
**Weekly Pipeline Failures**: Weekly trend of CI/CD pipeline failures detected during reviews.
**Most Active Pull Request Authors**: Top 10 contributors ranked by number of merged PRs.
**Most Active Pull Request Reviewers**: Top 10 contributors ranked by number of PRs reviewed.

Slow **Time to First Human Review** combined with concentrated reviewer
activity may indicate review responsibilities are falling on too few people.

---

## Pre-merge Checks

Monitor how your built-in and [custom](/pr-reviews/custom-checks) quality gates are performing across repositories.
**Custom Pre-merge Checks Configured**: Number of unique custom Pre-merge Checks configured.
**Weekly Pre-Merge Check Runs**: Weekly trend of Pre-merge Check runs, broken down by result status.
**Pre-Merge Check Runs**: Number of Pre-merge Checks executed, split by built-in and custom checks.
**Pre-Merge Check Results**: Count of pass, fail, and inconclusive outcomes for each Pre-merge Check.

---

## Reporting

Track [scheduled](/guides/scheduled-reports) and on-demand report delivery across your organization.
**Scheduled Reports Delivered**: Total scheduled reports successfully delivered.
**Reports Delivered by Channel**: Distribution of reports delivered across delivery channels.
**Reports Configured**: Number of active reports configured, split by scheduled and on-demand.
**Weekly Reports Delivered**: Weekly count of scheduled reports successfully delivered.

---

## Data Metrics

**Active User Details**: Per-user summary of pull request activity and reviews.

* **PRs Created**: Number of PRs created by the user
* **PRs Merged**: Number of PRs merged by the user
* **Median Time to Last Commit**: Median time for PRs authored by the user
* **Total Review Comments**: CodeRabbit comments posted on their PRs
* **Overall Acceptance Rate**: Percentage of comments accepted
* **Critical Comments**: Posted vs accepted
* **Major Comments**: Posted vs accepted
* **Other Comments**: Posted vs accepted

**Pull Request Details**: Detailed review metrics for each merged pull request.

* **Repository**: Repository name
* **Author**: PR author
* **Created At**: PR creation timestamp
* **First Human Review**: Timestamp of first human review
* **Merged At**: PR merge timestamp
* **Estimated Complexity**: AI-estimated PR complexity
* **Estimated Review Time**: AI-estimated review effort
* **Number of Human Reviewers**: Count of human reviewers
* **Human Review Comment Count**: Comments from human reviewers
* **Total CodeRabbit Comments**: Posted vs accepted
* **Critical Comments**: Posted vs accepted
* **Major Comments**: Posted vs accepted
* **Other Comments**: Posted vs accepted
* **Tool Findings**: Automated tool issues found
* **Pipeline Failures**: CI/CD failures detected

**Tool Finding Details**: Automated tool findings surfaced during review for merged pull requests.

* **Tool Name**: Name of the tool (e.g., ESLint, Semgrep)
* **Category**: Rule type or issue category
* **Severity**: Warning, error, grammar, style, or unknown
* **Count**: Number of occurrences

---

## Data Export

The Data Export page provides CSV downloads of per-PR review metrics for offline analysis, reporting, or integration with other tools.
For export instructions and field definitions, see [Data Export](/guides/data-export).
