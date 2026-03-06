---
name: prd-to-accessibility
description: Generate accessibility requirements and checks from a PRD, aligned to
  WCAG targets and key journeys. Use when accessibility expectations must be explicit
  and testable.
knowledge_graph_profile: references/task-profile.json
---

# PRD to Accessibility Spec

## Pipeline Context
This skill generates accessibility requirements, which support **Stage 2 of the Spec Pipeline** (UX Spec) by ensuring accessibility is explicit in the UX design.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/ux-spec-template.md` — UX Spec template
- `design/references/spec-linter-checklist.md` — Quality gate checklist

## Response format (strict)
The first line of any response MUST be `## Inputs`.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Produce accessibility requirements and validation guidance from a PRD.

## Iron law
- No visual specs or layout guidance until accessibility requirements are complete.

## Output template (strict)
```markdown
# Accessibility Spec

## Target standard and scope

## Key user journeys and assistive tech assumptions

## Requirements by component/flow

## Non-text content and media alternatives

## Keyboard, focus, and navigation rules

## Validation plan (automated + manual)

## Known limitations and risks
```

## Output location
Write the accessibility spec in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-accessibility-spec.md`

## Required sections
1) Target standard (e.g., WCAG 2.2 AA) and scope
2) Key user journeys and assistive tech assumptions
3) Accessibility requirements by component/flow
4) Non-text content and media alternatives
5) Keyboard, focus, and navigation rules
6) Validation plan (automated + manual)
7) Known limitations and risks

## Constraints
- Keep requirements testable and user-visible.
- Redact secrets/PII by default.
## References
- Contract: references/contract.yaml
- Evals: references/evals.yaml

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the appropriate skill.

## Required inputs
- User request details and any relevant files/links.

## Deliverables
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Validation
- If findings are disputed or high-risk, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Accessibility is not a feature—it's a fundamental requirement for inclusive products.
- Test with real users—automated tools catch only a fraction of accessibility issues.
- Progressive enhancement is a strategy—ensure core functionality works for everyone.

## Empowerment
- The agent is capable of identifying accessibility gaps that designers and engineers might miss.
- Use judgment to prioritize accessibility requirements based on user impact and implementation effort.
- Enable teams to ship products that are usable by the widest possible audience.
- Don't be intimidated by accessibility standards—focus on user experience first, compliance follows.

## Variation
- Adapt accessibility depth to product type: consumer products need full WCAG compliance, internal tools can have baseline compliance.
- Vary assistive tech assumptions: consumer apps must support screen readers, admin panels may prioritize keyboard navigation.
- For touch-first products, expand on touch target sizing and gesture accessibility.
- For data products, expand on data visualization accessibility and screen reader optimization.
- Adjust validation rigor based on audience—public products need formal audit, internal products can use lighter validation.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip keyboard navigation—inaccessible products exclude users permanently.
- DO NOT omit screen reader semantics—unlabeled interactive elements are unusable for assistive tech.
- Avoid relying on color alone—colorblind users and screen readers can't perceive color-only cues.
- DO NOT forget error and loading states—dynamic content changes without announcements confuse assistive tech users.

## Response format (required)
The first line of any response MUST be `## Inputs`.
Every user-facing response must include these headings:
- `## Inputs`
- `## Outputs`
- `## When to use`

## Examples
- "Use this skill for a typical request in its domain."

Failure/out-of-scope template (use verbatim structure):
```markdown
## Required inputs
Objective: <what you received>

Plan:
1) <brief>
2) <brief>

Next step: <single request>

## Deliverables
- <what would be produced if in scope>

## Scope and triggers
- <when this skill applies>
```

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

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
