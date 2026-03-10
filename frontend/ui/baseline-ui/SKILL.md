---
name: baseline-ui
description: Validates animation durations, enforces typography scale, checks component accessibility, and prevents layout anti-patterns in Tailwind CSS projects. Use when building UI components, reviewing CSS utilities, styling React views, or enforcing design consistency.
---

# Baseline UI

Enforces an opinionated UI baseline to prevent AI-generated interface slop.

Current baseline markers:
- React 19 interaction guidance when the project uses React.
- Next.js 16 conventions when the target app is on Next.js.
- Tailwind CSS v4 utility patterns and token-safe usage.
- WCAG 2.2 accessibility expectations for review findings.

## How to use

- `/baseline-ui`
  Apply these constraints to any UI work in this conversation.

- `/baseline-ui <file>`
  Review the file against all constraints below and output:
  - violations (quote the exact line/snippet)
  - why it matters (1 short sentence)
  - a concrete fix (code-level suggestion)

## Stack

- MUST use Tailwind CSS defaults unless custom values already exist or are explicitly requested
- MUST use `motion/react` (formerly `framer-motion`) when JavaScript animation is required
- SHOULD use `tw-animate-css` for entrance and micro-animations in Tailwind CSS
- MUST use `cn` utility (`clsx` + `tailwind-merge`) for class logic

## Components

- MUST use accessible component primitives for anything with keyboard or focus behavior (`Base UI`, `React Aria`, `Radix`)
- MUST use the project’s existing component primitives first
- NEVER mix primitive systems within the same interaction surface
- SHOULD prefer [`Base UI`](https://base-ui.com/react/components) for new primitives if compatible with the stack
- MUST add an `aria-label` to icon-only buttons
- NEVER rebuild keyboard or focus behavior by hand unless explicitly requested

## Interaction

- MUST use an `AlertDialog` for destructive or irreversible actions
- SHOULD use structural skeletons for loading states
- NEVER use `h-screen`, use `h-dvh`
- MUST respect `safe-area-inset` for fixed elements
- MUST show errors next to where the action happens
- NEVER block paste in `input` or `textarea` elements

## Animation

- NEVER add animation unless it is explicitly requested
- MUST animate only compositor props (`transform`, `opacity`)
- NEVER animate layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`)
- SHOULD avoid animating paint properties (`background`, `color`) except for small, local UI (text, icons)
- SHOULD use `ease-out` on entrance
- NEVER exceed `200ms` for interaction feedback
- MUST pause looping animations when off-screen
- SHOULD respect `prefers-reduced-motion`
- NEVER introduce custom easing curves unless explicitly requested
- SHOULD avoid animating large images or full-screen surfaces

## Typography

- MUST use `text-balance` for headings and `text-pretty` for body/paragraphs
- MUST use `tabular-nums` for data
- SHOULD use `truncate` or `line-clamp` for dense UI
- NEVER modify `letter-spacing` (`tracking-*`) unless explicitly requested

## Layout

- MUST use a fixed `z-index` scale (no arbitrary `z-*`)
- SHOULD use `size-*` for square elements instead of `w-*` + `h-*`

## Performance

- NEVER animate large `blur()` or `backdrop-filter` surfaces
- NEVER apply `will-change` outside an active animation
- NEVER use `useEffect` for anything that can be expressed as render logic

## Design

- NEVER use gradients unless explicitly requested
- NEVER use purple or multicolor gradients
- NEVER use glow effects as primary affordances
- SHOULD use Tailwind CSS default shadow scale unless explicitly requested
- MUST give empty states one clear next action
- SHOULD limit accent color usage to one per view
- SHOULD use existing theme or Tailwind CSS color tokens before introducing new ones


## Philosophy
- Keep fixes minimal, targeted, and reversible.
- Prioritize accessibility, performance, and correctness over visual novelty.
- Respect the existing project stack and conventions before introducing changes.

## When to use
- Use this skill when the user asks to audit or fix the domain covered by this skill.
- Use during UI review passes when quick, concrete remediation is needed.

## Inputs
- Target file(s) or component scope to review.
- Current stack context (framework, styling, and component primitives) when known.
- Any explicit constraints from the user (for example: no refactors, minimal diff).

## Outputs
- Prioritized findings with exact snippets.
- Why each issue matters (brief rationale).
- Concrete code-level fix suggestions with minimal scope.

## Constraints / Safety
- Do not refactor unrelated code.
- Do not add dependencies or migrate frameworks unless explicitly requested.
- Default to safe, standards-aligned fixes and preserve existing behavior.

- Redact secrets, tokens, API keys, and PII by default.

## Procedure
1. Confirm target scope and constraints.
2. Audit against this skill rule set.
3. Prioritize critical issues first.
4. Provide minimal, concrete remediations.
5. Re-check modified snippets for regressions.

## Validation
- Verify fixes preserve intended UX behavior.
- Verify accessibility, performance, or metadata outcomes relevant to this skill.
- Confirm recommendations are scoped and actionable.
- Fail fast on ambiguous or unsafe changes and ask for clarification.

## Anti-patterns
- Large rewrites for small issues.
- Advice without concrete snippet-level fixes.
- Ignoring project conventions or introducing unrelated architecture changes.

## Variation
- Adapt enforcement depth for design-system implementation, component QA, or pre-release polish passes.
- Use different recommendation styles for new builds versus incremental refactors in existing UI code.
- Customize checks by surface area: typography-heavy pages, animation-heavy interactions, or dense dashboards.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes <notes>`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Examples
- Review one component and return only critical and high-impact fixes first.
- Suggest minimal edits that preserve current stack and behavior.

## Notes
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`

## Quality Uplift
- Philosophy and approach: apply a clear framework, explain why, consider tradeoff decisions, and use a practical mental model for execution.
- Guiding question: Why is this the right context-specific path?
- Guiding question: What tradeoff is being made and how is risk reduced?
- Guiding question: How do we verify behavior end-to-end before completion?
- Anti-pattern warning: avoid generic or repetitive output; DO NOT hide failures; NEVER skip validation; avoid common pitfall and mistake patterns.
- Anti-pattern warning: treat incorrect or wrong assumptions as blockers, and call out anti-pattern risks explicitly.
- Variation: vary recommendations by context-specific constraints; adapt, customize, and use different approaches when constraints differ.
- Variation: prefer diverse, unique alternatives and avoid repetition or cookie-cutter template convergence.
- Empowerment: enable users to explore options confidently, be capable and creative, unlock safe choices, and empower execution.
