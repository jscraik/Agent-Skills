---
name: ios_sim_interrogate
description: Analyze iOS Simulator behavior using simctl captures, Web Inspector,
  and Instruments. Use when you need evidence from iOS simulator runs.
---

Inputs:
- Simulator context (booted simulator), and either app bundle id or URL for web content.
- Goal + scenario.

Important:
- Safari Web Inspector inspects web content and WKWebView, not native Swift call stacks.
- Use Xcode/Instruments for native Swift/ObjC behavior.

Output:
- Annotate which evidence comes from media captures vs inspector exports vs Instruments traces.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

## Anti-patterns

- Applying this skill when a direct request is out of scope.
- Skipping validation/checks to save time.
- Assuming defaults without explicit user confirmation for risky actions.

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Prefer safe defaults and avoid irreversible changes without explicit confirmation.

## Inputs

- User task context and target environment.
- Relevant constraints, permissions, and preferences required to execute safely.

## Outputs

- A concrete next-step response with explicit, reproducible actions.
- A short verification checklist and caveats for the user.

## Philosophy

- Keep the workflow minimal, safe, and evidence-based.
- Load richer context only when needed; avoid unnecessary commands or overreach.

## Procedure

1. Verify scope and constraints before taking action.
2. Execute the minimal safe path first.
3. Validate intermediate state before making changes.

## Validation

- Fail fast: stop at the first failed check and do not continue.
- Re-run the required checks before proceeding to the next step.
- Report any failed check and requested follow-up actions clearly.

## When to use

- Use this skill when the request matches the skill's intent and scope.
- Do not use it when a different domain or higher-privilege workflow is required.

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Prefer safe defaults and avoid irreversible changes without explicit confirmation.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.
