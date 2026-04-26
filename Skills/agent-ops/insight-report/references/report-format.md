# Report Format Specification

HTML report structure for Codex-authored insight reports.

## Table of Contents

- [File Location](#file-location)
- [Artifact Chain](#artifact-chain)
- [Report Sections](#report-sections)
- [Browser Launch](#browser-launch)

## File Location

```text
file://$HOME/dev/configs/codex/usage-data/report.html
```

## Artifact Chain

```text
insight-evidence.json -> INSIGHT_PROMPT.md -> insights.generated.json -> report.html
```

Codex writes `insights.generated.json`. Python renders `report.html`.

## Report Sections

### Header

```text
Codex Insights Report
Generated: {date}
Period: Last {N} days
Sessions: {count}
```

### At a Glance

- What's working.
- What's hindering you.
- Quick wins to try.
- Ambitious workflows.

### Charts

- Tool usage.
- Tool errors.
- Response-time distribution.
- Parallel Codex sessions.

### What You Work On

Project or workflow areas inferred by Codex from the evidence bundle.

### How You Use Codex

Narrative analysis of interaction style, written in second person.

### Impressive Things

Concrete wins and effective workflows supported by the evidence.

### Where Things Go Wrong

Friction categories with examples and consequences.

### Plain-English Prompting Help

Copyable prompts and small vocabulary bridges for moments where Jamie knows the desired outcome but not the technical term.

### AGENTS.md Suggestions

Repeated preferences or instructions that should be made durable.

### Features to Try

Codex features, skills, hooks, subagents, or browser workflows that fit the observed usage.

### Priority Fixes

Actionable improvements with impact, root cause, enforcement, and verification.

### On the Horizon

Future workflows Jamie can prepare for as Codex improves.

## Browser Launch

The runner prints:

```text
REPORT_URL=file://$HOME/dev/configs/codex/usage-data/report.html
```

When running inside Codex, open that URL with the Codex in-app browser. If Browser tooling is unavailable, disclose that and provide the URL.
