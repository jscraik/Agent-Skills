---
name: gh-pr-local
description: "Fetch, preview, test, and merge GitHub PRs locally. Use when the user wants to evaluate a PR before merge."
---

# GitHub PR Tool

Fetch and merge GitHub pull requests into your local branch. Perfect for:
- Trying upstream PRs before they're merged
- Incorporating features from open PRs into your fork
- Testing PR compatibility locally

## Links

- https://cli.github.com

## Prerequisites

- `gh` CLI authenticated (`gh auth login`)
- Git repository with remotes configured

## Commands

### Preview a PR
```bash
github-pr preview <owner/repo> <pr-number>
```
Shows PR title, author, status, files changed, CI status, and recent comments.

### Fetch PR branch locally
```bash
github-pr fetch <owner/repo> <pr-number> [--branch <name>]
```
Fetches the PR head into a local branch (default: `pr/<number>`).

### Merge PR into current branch
```bash
github-pr merge <owner/repo> <pr-number> [--no-install]
```
Fetches and merges the PR. Optionally runs install after merge.

### Full test cycle
```bash
github-pr test <owner/repo> <pr-number>
```
Fetches, merges, installs dependencies, and runs build + tests.

## Examples

```bash
# Preview MS Teams PR from clawdbot
github-pr preview clawdbot/clawdbot 404

# Fetch it locally
github-pr fetch clawdbot/clawdbot 404

# Merge into your current branch
github-pr merge clawdbot/clawdbot 404

# Or do the full test cycle
github-pr test clawdbot/clawdbot 404
```

## Notes

- PRs are fetched from the `upstream` remote by default
- Use `--remote <name>` to specify a different remote
- Merge conflicts must be resolved manually
- The `test` command auto-detects package manager (npm/pnpm/yarn/bun)

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.

- Encourage variation: adapt steps for different contexts and enable creative exploration.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.
- If context differs, customize steps to fit the situation.

## Antipatterns
- Do not add features outside the agreed scope.
