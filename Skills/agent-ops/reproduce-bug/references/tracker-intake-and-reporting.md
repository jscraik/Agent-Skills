# Tracker Intake And Reporting

Read when: the bug report comes from Linear or GitHub and the reproduction workflow needs tracker-driven intake, structured investigation, and optional tracker follow-up.

Imported from the upstream `reproduce-bug` skill in `EveryInc/compound-engineering-plugin` commit `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`, adapted for a Linear-first repo that still supports GitHub issues.

## Purpose

Systematically reproduce and investigate bugs from tracker issues rather than relying on ad hoc bug descriptions.

## Issue intake

### Preferred path: Linear

In this repo, prefer Linear when the user provides:
- a Linear issue identifier such as `ENG-123`
- a Linear issue URL
- a request that clearly points to Linear as the source of truth

Read the issue ID, description, comments, link attachments, and linked context before touching the codebase.

Extract:
- reported symptoms
- expected behavior
- reproduction steps
- environment clues
- frequency

### Supported secondary path: GitHub

Keep the upstream GitHub flow available when the user provides:
- a GitHub issue number
- a GitHub issue URL
- a request to reproduce directly from a GitHub issue thread

The upstream core call shape was:

```bash
gh issue view <issue> --json title,body,comments,labels,assignees
```

That path remains valid when GitHub is the actual issue source.

### Manual-context fallback

If no tracker issue exists, gather the same fields from the user's prose report and mark the run as `manual-context`.

## Hypothesis-driven investigation

Before reproducing:
1. search the repo for code paths, strings, routes, or services related to the report
2. form 2-3 ranked hypotheses
3. tie each hypothesis to:
   - what might be wrong
   - where in the codebase
   - why it would produce the symptoms

## Reproduction routes

### Route A: test-based

Use for backend, data, logic, or deterministic code-path bugs.

Approach:
- find existing tests
- run the most relevant ones
- add or sketch a minimal failing test when needed
- use the failing test as reproduction evidence

### Route B: browser-based

Use for UI, interaction, or visual bugs.

Prefer `agent-browser` for the browser path.

Core flow:
- confirm the dev server and port
- navigate to the affected route
- execute the issue's reproduction steps
- capture screenshots and visible error state

### Route C: manual or environment-specific

Use when the bug depends on:
- special data
- user roles
- external services
- OS or browser conditions
- state that cannot be safely automated

Document the missing conditions and what the user would need to provide for confirmation.

## Investigation

Once the bug reproduces or partially reproduces:
- inspect logs
- inspect browser console for UI bugs
- inspect relevant data state when needed
- trace the code path from the likely entry point
- check recent changes in the affected files

## Findings report

Organize the result into:
1. root cause
2. reproduction steps
3. evidence
4. suggested fix, if apparent
5. open questions

Present the report to the user before any external write.

## Tracker follow-up options

In this repo, the preferred write-back order is:
1. Linear comment or issue update
2. GitHub issue comment when GitHub is the active issue source or the user explicitly wants GitHub updated
3. no external action

Offer next-step choices such as:
1. post findings to Linear
2. post findings to GitHub
3. start working on a fix
4. just review findings

## Local adaptation notes

- Linear is the default source of truth for bug intake here.
- GitHub support is intentionally preserved, not removed.
- The local wrapper keeps the tracker-source choice explicit so the workflow does not assume GitHub-only issue management.
- External tracker mutation still requires explicit user approval.
