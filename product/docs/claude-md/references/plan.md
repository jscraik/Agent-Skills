# Plan - claude-md skill

## Goal
Create a CLAUDE.md-focused version of the existing agents-md skill with the same operating shape (scope, workflow, contracts, evals) but tuned for Claude-specific file behavior and brevity rules.

## Steps
1. Analyze `product/docs/agents-md/` structure and reuse its proven sections.
2. Author `product/docs/claude-md/SKILL.md` with CLAUDE-specific triggers, include/exclude guidance, and layered file behavior.
3. Define `references/contract.yaml` for outputs and guardrails.
4. Add `references/evals.yaml` with in-scope, out-of-scope, layering, and contradiction cases.
5. Run skill validation gates and fix any failures.

## Notes
- Default compatibility posture remains canonical-only unless explicitly requested otherwise.
- Keep CLAUDE guidance concise and move deep workflows to imports/skills.
