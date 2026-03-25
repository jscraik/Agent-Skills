# Findings and Todos

## Table of Contents
- [Purpose](#purpose)
- [When to create todo files](#when-to-create-todo-files)
- [When to act immediately instead](#when-to-act-immediately-instead)
- [Naming convention](#naming-convention)
- [Frontmatter contract](#frontmatter-contract)
- [Required sections](#required-sections)
- [Review-to-todo flow](#review-to-todo-flow)
- [Triage lifecycle](#triage-lifecycle)
- [Work log expectations](#work-log-expectations)

## Purpose
This note preserves the exact file-based todo follow-up lane supplied for review findings.

Use it when:
- `ce-review` is asked to capture findings into `todos/`
- the repo already uses the file-based `todos/` workflow
- review findings are substantial enough that they should become tracked work items

## When to create todo files
Create a todo when the finding:
- requires more than 15-20 minutes of work
- needs research, planning, or multiple approaches considered
- has dependencies on other work
- requires prioritization or explicit triage
- represents technical debt that should be documented and tracked

## When to act immediately instead
Do not force a todo when:
- the issue is trivial and can be addressed immediately
- the solution is obvious and complete context is already available
- the user explicitly asked for immediate action instead of follow-up tracking

## Naming convention
Todo files use:

`{issue_id}-{status}-{priority}-{description}.md`

Components:
- `issue_id`: sequential numeric identifier such as `001`, `002`, `003`; never reuse IDs
- `status`: `pending`, `ready`, or `complete`
- `priority`: `p1`, `p2`, or `p3`
- `description`: concise kebab-case summary

Examples:
- `001-pending-p1-mailer-test.md`
- `002-ready-p1-fix-n-plus-1.md`
- `005-complete-p2-refactor-csv.md`

## Frontmatter contract
Use this exact frontmatter shape:

```yaml
---
status: pending
priority: p2
issue_id: "003"
tags: [code-review]
dependencies: []
---
```

Guidance:
- add `code-review` to every review-created todo
- add domain tags such as `security`, `performance`, `architecture`, `rails`, `quality`, or `frontend` as appropriate
- use dependency issue IDs when a finding cannot be worked independently

## Required sections
Each review-created todo must include:
- `Problem Statement`
- `Findings`
- `Proposed Solutions`
- `Recommended Action`
- `Acceptance Criteria`
- `Work Log`

Optional but strongly useful:
- `Technical Details`
- `Resources`
- `Notes`

`Proposed Solutions` should normally include 2-3 options with:
- approach
- pros
- cons
- effort
- risk

## Review-to-todo flow
After `ce-review` synthesizes and deduplicates findings:
1. filter out protected-artifact cleanup findings
2. rank remaining findings as `P1`, `P2`, or `P3`
3. decide which findings deserve tracked todo files
4. determine the next issue ID from the existing `todos/` directory
5. create one todo file per finding using the naming convention and template structure
6. include evidence, affected files, resources, and a starter work log entry

Default review-created status:
- `pending`, unless the repo explicitly pre-approves review findings to land as `ready`

## Triage lifecycle
Status progression:
- `pending` -> needs triage or approval
- `ready` -> approved and actionable
- `complete` -> work finished

During triage:
- review the problem statement and findings
- compare proposed solutions
- fill `Recommended Action`
- rename the file and update frontmatter if the status changes

## Work log expectations
Every review-created todo should start with an initial discovery log entry that records:
- date
- reviewer identity
- actions taken
- evidence gathered
- notable learnings

Work logs are part of the handoff quality bar, not optional decoration.
