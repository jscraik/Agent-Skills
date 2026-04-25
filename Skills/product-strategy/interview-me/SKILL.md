---
name: interview-me
description: Analyze underspecified requests with a short decision interview. Use this skill when guessing would risk the wrong plan.
metadata:
  skill-type: team_automation
---

# Interview Me

## Philosophy
Ask the smallest useful question, reduce uncertainty quickly, and preserve an explicit approval boundary.

## When To Use
- One or two decisions would materially change the work.
- The user needs assumptions, tradeoffs, or approval gates clarified.
- A downstream planning or implementation skill needs a compact handoff.

## Avoid
- Do not use when the request is already implementation-ready.
- Do not run a broad discovery workshop when one decision question will unblock the work.
- Do not prescribe implementation before unresolved decisions are closed or declared as assumptions.

## Inputs
- User request and target repo or artifact.
- Evidence source such as files, diffs, issues, releases, or existing workflow state.
- Any safety, privacy, compliance, or approval constraints.

## Outputs
- Schema-bound outputs include `schema_version`.
- Decision log with assumptions and constraints.
- Approval status.
- Compact handoff for the next skill.

## Workflow
1. Ask one high-impact question with 3-5 choices and one recommended default.
2. Explain briefly why the answer matters.
3. Ask a second question only if a material blocker remains.
4. Maintain a compact decision and assumption log.
5. End with approved, needs-input, or blocked plus the next route.

## Constraints
- Redact secrets and sensitive context by default.
- Do not ask broad exploratory questions without a decision payoff.
- Do not invent constraints or approval.
- Fail fast at the first missing input that would change the outcome.

## Validation
- Run Plugin Eval and strict skill audit after editing this skill.
- Report exact validation commands and pass/fail outcomes.
- Fail fast: stop at the first failed gate, fix it, and rerun before continuing.

## Anti-Patterns
- Do not use when the request is already implementation-ready.
- Do not run a broad discovery workshop when one decision question will unblock the work.
- Do not prescribe implementation before unresolved decisions are closed or declared as assumptions.

## Examples
- "This request is fuzzy; ask the one question that changes the plan."
- "I have no success metric yet; help me decide what to ask."

## Progressive Disclosure
- Archived full context: `Infrastructure/references/deferred-skill-context/product-strategy-interview-me/`.
- Load archived references only when the active workflow needs that exact detail.
- Keep the active path compact; do not remove important context for budget trimming.

## See Also

| Skill | When to use together |
|---|---|
| [[verification-before-completion]] | Confirm gate outcomes and report deterministic pass/fail evidence before closeout |
| [[project-brain]] | Capture durable repo learnings and route updates into the canonical memory surface |
