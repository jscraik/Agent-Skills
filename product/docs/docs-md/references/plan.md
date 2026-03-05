# Plan for docs-md

## Goal
Create a general-purpose progressive-disclosure documentation skill modeled after `agents-md`, but scoped to README, runbooks, specs, and internal Markdown docs for both humans and agents.

## Decisions
- Name: `docs-md`
- Location: `product/docs/docs-md`
- Structure: instruction-only skill with local references
- Response shape: reuse the `## When to use` / `## Outputs` / `## Inputs` pattern from `agents-md`
- Non-goals: dedicated md files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) and copyediting-only work

## Files
- `SKILL.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/doc-split-patterns.md`

## Validation plan
Run quick validation, gate checks, analyzer, OpenClaw guard, and skill evals. Fix the first failure before moving to the next gate.
