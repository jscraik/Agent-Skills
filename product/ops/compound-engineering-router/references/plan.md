# Plan for Compound Engineering Router

## Table of Contents
- [Goal](#goal)
- [Design choices](#design-choices)
- [Included routes](#included-routes)
- [Included meta-modes](#included-meta-modes)
- [NotebookLM role](#notebooklm-role)
- [Validation plan](#validation-plan)

## Goal
Create a narrow router-style skill that selects the correct compound-engineering prompt, specialist review path, or workflow-support meta-mode for the Codex config repository.

## Design choices
- Keep the skill repo-light and instruction-first.
- Reuse the existing prompt pack and agent registry instead of copying instructions.
- Treat `technical-review` as a first-class route, separate from `review`.
- Keep NotebookLM optional and evidence-oriented.
- Add meta-modes only where there is real value and no prompt-backed equivalent exists.

## Included routes
- brainstorm
- spec
- deepen-spec
- plan
- deepen-plan
- work
- review
- technical-review
- compound

## Included meta-modes
- context-compaction
- guardrail-extract

## NotebookLM role
NotebookLM is included as an optional enrichment layer for:
- spec-writing and orchestration patterns
- planning-mode and hook patterns
- Codex operating patterns, review loops, and eval ideas
- context-compaction and guardrail-extraction heuristics

## Validation plan
1. Run skill structure validators.
2. Fix the first failing gate.
3. Re-run validators.
4. Improve analyzer quality where it reveals clear gaps.
5. Summarize final readiness and any follow-up work.
