---
name: gh-issue-fix
description: "Analyze and resolve a GitHub issue from intake through fix, validation, and push using gh, local edits, and git. Use this skill when you need to analyze and fix a GitHub issue end-to-end using gh and local changes."
---

# GH Issue Fix Flow

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview
Resolve a GitHub issue from intake through fix, validation, and push using gh, local edits, and git.
See `references/contract.yaml` and `references/evals.yaml` for contract and eval expectations.

## When to use
- Fixing a GitHub issue end-to-end using gh and local changes.
- When a user provides an issue number to resolve.

## Inputs
- Issue number and repo (owner/name).
- Any reproduction steps or constraints.

## Outputs
- Code changes, tests, and a closing commit pushed to the repo.
- Summary with evidence and follow-ups.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs`

## Edge-case template (missing info)
Use this exact structure when key inputs are missing:

```md
## When to use
- This skill applies to GitHub issue fixes using gh and local edits.

## Inputs
- Missing: <issue number and repo>.

## Outputs
- None until inputs are provided.
```

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## When to use
- This skill applies to GitHub issue fixes using gh and local edits. The current request is out of scope.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

## Philosophy
- Fix the smallest surface area that resolves the issue.
- Prefer evidence-backed reproduction and verification.
- Preserve repo conventions and reviewer expectations.

## Guiding questions
- What is the minimal reproduction and expected behavior?
- Why is this the correct fix vs a workaround?
- What is the least risky change that solves the issue?
- How will the fix be verified (tests, builds, repro)?

## Workflow

### 1) Intake and issue context
1. Use `gh issue view <id> --repo <owner/repo> --comments` to get the full issue context.
2. If the repo is unclear, run `gh repo view --json nameWithOwner` to confirm.
3. Capture reproduction steps, expected behavior, and any maintainer notes.

### 2) Locate the code path
1. Use `rg -n` to locate likely files and entry points.
2. Read the relevant code paths with `sed -n` or `rg -n` context.
3. Follow repo-specific conventions (AGENTS/CLAUDE instructions).

### 3) Implement the fix
1. Edit the minimal set of files.
2. Keep changes aligned with existing architecture and style.
3. Add tests when behavior changes and test coverage is practical.

### 4) Build and test
1. Use repo-provided build/test scripts when available.
2. Prefer targeted test suites to reduce risk and runtime.
3. Report warnings or failures; do not hide them.

### 5) Commit and push
1. Check for unrelated changes with `git status --short`.
2. Stage only the fix (exclude unrelated files).
3. Commit with a closing message: `Fix … (closes #<issue>)`.
4. Push with `git push`.

### 6) Report back
1. Summarize what changed and where.
2. Provide test results (including failures).
3. Note any follow-ups or blocked items.

## Variation rules
- Vary depth by issue severity (typo vs crash vs data loss).
- Vary validation based on impact (unit tests vs full build).
- Use a different investigative path when the initial hypothesis fails.

## Empowerment principles
- Empower the user to approve the plan before code changes.
- Empower maintainers with clear trade-offs and rollback notes.
- Empower reviewers with evidence-linked summaries.

## Anti-patterns to avoid
- Fixing without a reproducible understanding of the issue.
- Broad refactors that are not required to close the issue.
- Hiding test failures or skipping validation without consent.

## Example prompts
- “Fix issue #123 in this repo and push the commit.”
- “Use gh to inspect issue #45, implement the fix, and run tests.”

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
