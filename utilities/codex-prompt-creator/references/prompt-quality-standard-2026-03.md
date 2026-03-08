# Prompt Quality Standard (Validated March 3, 2026)

## Table of Contents
- [Purpose](#purpose)
- [Core rubric](#core-rubric)
- [Minimal-diff audit workflow](#minimal-diff-audit-workflow)
- [Patch patterns (preferred)](#patch-patterns-preferred)
- [Quality gates](#quality-gates)
- [Source baseline](#source-baseline)

## Purpose
Define a practical, current baseline for creating and improving prompts with minimal churn.

## Core rubric
1. **Task clarity**
   - State objective, scope, non-goals, and completion criteria.
2. **Context hygiene**
   - Delimit trusted instructions from user-provided text and references.
3. **Output contract**
   - Require explicit output sections/schema for deterministic review.
4. **Trigger boundaries**
   - Include positive triggers and near-miss non-triggers.
5. **Safety/uncertainty behavior**
   - Define fallback when data is missing, unsafe, or ambiguous.
6. **Evidence-first retrieval**
   - Require source-backed claims for time-sensitive or external facts.
7. **Eval readiness**
   - Wording must be testable in `references/evals.yaml`.
8. **Maintainability**
   - Prefer minimal patches over full rewrites unless rewrite mode is requested.

## Minimal-diff audit workflow
1. Inventory prompts in scope.
2. Score each prompt against the rubric.
3. Classify gaps:
   - **P0**: safety/risk/incorrectness
   - **P1**: reliability/routing/output consistency
   - **P2**: style/clarity/maintainability
4. Propose patch-sized edits first.
5. Escalate to rewrite only with explicit user approval.

## Patch patterns (preferred)
- Add one missing section instead of restructuring the whole file.
- Tighten a vague `description` line instead of replacing the body.
- Add a “do not trigger when …” bullet instead of introducing router complexity.
- Add explicit output headings instead of changing the entire workflow.

## Quality gates
- `quick_validate.py` passes.
- `skill_gate.py` passes.
- `analyze_skill.py` report reviewed.
- `openclaw_skill_guard.py --mode both` has no critical findings.
- At least one no-rewrite eval case passes for audit-mode tasks.

## Source baseline
- OpenAI prompt engineering guide: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic prompt engineering overview: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- Google Cloud prompt design strategies: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design
- Microsoft prompt engineering techniques: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/prompt-engineering
