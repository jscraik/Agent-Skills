---
name: baseline-ui
description: Check Tailwind UI work for accessibility, performance, theming, responsive behavior, and anti-patterns. Use when the user wants guardrail-style UI validation, scored technical audits, or targeted cleanup, not a full redesign.
metadata:
  skill-type: code_quality_review
---

# Baseline UI

Enforces an opinionated UI baseline to prevent AI-generated interface slop.

Current baseline markers:
- React 19 interaction guidance when the project uses React.
- Next.js 16 conventions when the target app is on Next.js.
- Tailwind CSS v4 utility patterns and token-safe usage.
- WCAG 2.2 accessibility expectations for review findings.
- Use `frontend/ui/references/skill-routing-matrix-2026.md` when deciding whether this skill should audit or route to a narrower frontend owner.

Design-system integration contract:
- Apply `frontend/ui/references/design-system-integration-contract.md` when auditing typography, spacing, iconography, and token usage.
- Treat drift from semantic token and icon governance as a first-class finding, not optional polish.

## How to use

- `/baseline-ui`
  Apply these constraints to any UI work in this conversation.

- `/baseline-ui <file>`
  Review the file against all constraints below and output:
  - violations (quote the exact line/snippet)
  - why it matters (1 short sentence)
  - a concrete fix (code-level suggestion)

- `/baseline-ui --audit <area>`
  Run score-first technical audit mode and output:
  - 5-dimension scorecard (0-4 each, total `/20`)
  - P0-P3 prioritized findings with impact and location
  - systemic patterns and positive findings
  - recommended follow-up skill sequence

In `--audit` mode, do not apply code fixes unless the user explicitly asks for edits.

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
- NEVER leave production-intent actions wired to `href="#"` or equivalent dead links unless placeholders were explicitly requested
- MUST show an explicit active state for current page/location in navigation surfaces

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
- SHOULD align CTA/button baselines in comparable card rows (for example pricing/features) when cards are presented side-by-side

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

## Flow Friction Overlay

Use this overlay in `--audit` mode when the target is a user flow, decision surface, or dense UI rather than a single isolated component.

- Check whether the user faces more than 4 meaningful visible choices at once without grouping or recommendation support.
- Check whether key information needed for an action is hidden in another screen, tab, modal, or side panel.
- Check whether the interface forces reading, deciding, and navigating at the same time.
- If these issues appear, report them under anti-patterns or systemic patterns instead of inventing a second score axis.

## Audit report mode

Use this mode when the user asks for a technical quality audit, quality score, or release-readiness review.

1. Score these dimensions from 0 to 4: Accessibility, Performance, Theming, Responsive Design, and Anti-Patterns.
2. Report total score as `/20` with rating band.
3. Classify issues by severity:
   - `P0`: blocking
   - `P1`: major
   - `P2`: minor
   - `P3`: polish
4. Include anti-pattern verdict first, then executive summary, detailed findings by severity, systemic patterns, positive findings, and prioritized follow-up actions.
5. When the audit scope is a real user flow, add a short flow-friction note if cognitive overload or context switching materially increases error risk.

Reference template: `references/audit-scorecard.md`.

## Philosophy
- Keep fixes minimal, targeted, and reversible.
- Prioritize accessibility, performance, and correctness over visual novelty.
- Respect the existing project stack and conventions before introducing changes.

## When to use
- Use this skill when the user asks to audit or fix the domain covered by this skill.
- Use during UI review passes when quick, concrete remediation is needed.
- Keep scope to audit and targeted cleanup only; route broad redesign direction work to `frontend-ui-design` or `frontend-design`.

## Required inputs
- Target file(s) or component scope to review.
- Current stack context (framework, styling, and component primitives) when known.
- Any explicit constraints from the user (for example: no refactors, minimal diff).

## Deliverables
- Prioritized findings with exact snippets.
- Why each issue matters (brief rationale).
- Concrete code-level fix suggestions with minimal scope.
- Optional score-first technical audit report (`/20`, P0-P3, patterns, positive findings) when audit mode is requested.
- Output contract note: when returning structured audit payloads, include `schema_version: 1.0`.

## Constraints / Safety
- Do not refactor unrelated code.
- Do not add dependencies or migrate frameworks unless explicitly requested.
- Default to safe, standards-aligned fixes and preserve existing behavior.

- Redact secrets, tokens, API keys, and PII by default.

## Procedure
1. Confirm target scope and constraints.
2. Determine execution mode:
   - audit-only scorecard mode (`--audit`)
   - remediation mode (default)
3. Audit against this skill rule set.
4. Prioritize critical issues first.
5. Provide minimal, concrete remediations in remediation mode, or report-only output in audit mode.
6. Re-check modified snippets for regressions when edits are made.

## Validation
- Verify fixes preserve intended UX behavior.
- Verify accessibility, performance, or metadata outcomes relevant to this skill.
- Confirm recommendations are scoped and actionable.
- Confirm typography, spacing, iconography, and token findings align with `frontend/ui/references/design-system-integration-contract.md`.
- Fail fast on ambiguous or unsafe changes and ask for clarification.

## Anti-patterns
- Large rewrites for small issues.
- Advice without concrete snippet-level fixes.
- Ignoring project conventions or introducing unrelated architecture changes.
- Polishing visuals while leaving dead interactions, missing active navigation context, or misaligned comparison actions unfixed.

## Variation
- Adapt enforcement depth for design-system implementation, component QA, or pre-release polish passes.
- Use different recommendation styles for new builds versus incremental refactors in existing UI code.
- Customize checks by surface area: typography-heavy pages, animation-heavy interactions, or dense dashboards.
- Switch between audit-only scorecard mode and targeted remediation mode based on user intent.

## See Also

| Skill | When to use together |
|---|---|
| [[design-system]] | Apply design tokens that baseline-ui validates |
| [[fixing-accessibility]] | Fix accessibility issues found during baseline-ui checks |
| [[frontend-ui-design]] | Implement UI components that baseline-ui governs |
| [[ui-visual-regression]] | Combine with visual regression to catch visual drift |
| [[shadcn-ui]] | Validate shadcn/ui components against baseline rules |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes <notes>`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Examples
- User says: "Review one component and return only critical and high-impact fixes first."
- User says: "Suggest minimal edits that preserve current stack and behavior."
- User says: "Can you audit this checkout modal for a11y/perf and give me a `/20` score plus top P1 fixes?"
- User says: "Please inspect and validate `src/components/NavBar.tsx`, then suggest minimal fixes only. No refactor."

## Notes
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Audit template: `references/audit-scorecard.md`

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

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the target component, design constraints, or accessibility expectations are unclear, stop, identify the missing context, and fall back to a narrower UI audit before changing styles.
