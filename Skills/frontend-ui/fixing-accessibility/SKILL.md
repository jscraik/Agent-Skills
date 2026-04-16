---
name: fixing-accessibility
description: Audit and fix HTML accessibility issues including ARIA labels, keyboard navigation, focus management, color contrast, and form errors. Use when adding interactive controls, forms, dialogs, or reviewing WCAG compliance.
metadata:
  skill-type: code_quality_review
---

# fixing-accessibility

Fix accessibility issues.

Current baseline markers:
- React 19 component behavior when the UI is React-based.
- Next.js 16 routing and rendering context when the app uses Next.js.
- WCAG 2.2 success criteria as the default accessibility bar.

## how to use

- `/fixing-accessibility`
  Apply these constraints to any UI work in this conversation.

- `/fixing-accessibility <file>`
  Review the file against all rules below and report:
  - violations (quote the exact line or snippet)
  - why it matters (one short sentence)
  - a concrete fix (code-level suggestion)

Do not rewrite large parts of the UI. Prefer minimal, targeted fixes.

## when to apply

Reference these guidelines when:
- adding or changing buttons, links, inputs, menus, dialogs, tabs, dropdowns
- building forms, validation, error states, helper text
- implementing keyboard shortcuts or custom interactions
- working on focus states, focus trapping, or modal behavior
- rendering icon-only controls
- adding hover-only interactions or hidden content

## rule categories by priority

| priority | category | impact |
|----------|----------|--------|
| 1 | accessible names | critical |
| 2 | keyboard access | critical |
| 3 | focus and dialogs | critical |
| 4 | semantics | high |
| 5 | forms and errors | high |
| 6 | announcements | medium-high |
| 7 | contrast and states | medium |
| 8 | media and motion | low-medium |
| 9 | tool boundaries | critical |

## quick reference

### 1. accessible names (critical)

- every interactive control must have an accessible name
- icon-only buttons must have aria-label or aria-labelledby
- every input, select, and textarea must be labeled
- links must have meaningful text (no “click here”)
- decorative icons must be aria-hidden

### 2. keyboard access (critical)

- do not use div or span as buttons without full keyboard support
- all interactive elements must be reachable by Tab
- focus must be visible for keyboard users
- do not use tabindex greater than 0
- Escape must close dialogs or overlays when applicable

### 3. focus and dialogs (critical)

- modals must trap focus while open
- restore focus to the trigger on close
- set initial focus inside dialogs
- opening a dialog should not scroll the page unexpectedly

### 4. semantics (high)

- prefer native elements (button, a, input) over role-based hacks
- if a role is used, required aria attributes must be present
- lists must use ul or ol with li
- do not skip heading levels
- tables must use th for headers when applicable

### 5. forms and errors (high)

- errors must be linked to fields using aria-describedby
- required fields must be announced
- invalid fields must set aria-invalid
- helper text must be associated with inputs
- disabled submit actions must explain why

### 6. announcements (medium-high)

- critical form errors should use aria-live
- loading states should use aria-busy or status text
- toasts must not be the only way to convey critical information
- expandable controls must use aria-expanded and aria-controls

### 7. contrast and states (medium)

- ensure sufficient contrast for text and icons
- hover-only interactions must have keyboard equivalents
- disabled states must not rely on color alone
- do not remove focus outlines without a visible replacement

### 8. media and motion (low-medium)

- images must have correct alt text (meaningful or empty)
- videos with speech should provide captions when relevant
- respect prefers-reduced-motion for non-essential motion
- avoid autoplaying media with sound

### 9. tool boundaries (critical)

- prefer minimal changes, do not refactor unrelated code
- do not add aria when native semantics already solve the problem
- do not migrate UI libraries unless requested

## common fixes

```html
<!-- icon-only button: add aria-label -->
<!-- before --> <button><svg>...</svg></button>
<!-- after -->  <button aria-label="Close"><svg aria-hidden="true">...</svg></button>

<!-- div as button: use native element -->
<!-- before --> <div onclick="save()">Save</div>
<!-- after -->  <button onclick="save()">Save</button>

<!-- form error: link with aria-describedby -->
<!-- before --> <input id="email" /> <span>Invalid email</span>
<!-- after -->  <input id="email" aria-describedby="email-err" aria-invalid="true" /> <span id="email-err">Invalid email</span>
```

## review guidance

- fix critical issues first (names, keyboard, focus, tool boundaries)
- prefer native HTML before adding aria
- quote the exact snippet, state the failure, propose a small fix
- for complex widgets (menu, dialog, combobox), prefer established accessible primitives over custom behavior


## Philosophy
- Keep fixes minimal, targeted, and reversible.
- Prioritize accessibility, performance, and correctness over visual novelty.
- Respect the existing project stack and conventions before introducing changes.

## When to use
- Use this skill when the user asks to audit or fix the domain covered by this skill.
- Use during UI review passes when quick, concrete remediation is needed.

## Required inputs
- Target file(s) or component scope to review.
- Current stack context (framework, styling, and component primitives) when known.
- Any explicit constraints from the user (for example: no refactors, minimal diff).

## Deliverables
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
- Adapt review depth for quick lint triage, focused component audits, or full-page accessibility sweeps.
- Use different fix strategies for static content, interactive widgets, and form-heavy screens.
- Customize recommendation detail to match whether the user wants patch-ready edits or prioritized findings only.

## See Also

| Skill | When to use together |
|---|---|
| [[baseline-ui]] | Validate passing accessibility alongside baseline UI checks |
| [[fixing-metadata]] | Fix semantic HTML and metadata alongside ARIA fixes |
| [[frontend-ui-design]] | Apply accessibility constraints during component design |
| [[playwright-interactive]] | Test keyboard and focus behaviour via Playwright |
| [[design-system]] | Ensure token changes don't reduce colour contrast |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes <notes>`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Examples
- Review one component and return only critical and high-impact fixes first.
- Suggest minimal edits that preserve current stack and behavior.

## Notes
- Contract: `Infrastructure/references/contract.yaml`
- Evals: `Infrastructure/references/evals.yaml`

## Execution quality
- Philosophy: use a practical framework that balances speed, safety, and tradeoff clarity.
- Approach: choose context-specific variation rather than generic cookie-cutter steps; adapt output to repository constraints.
- Guiding question: Why is this the smallest safe change?
- Guiding question: What tradeoff are we making and why?
- Guiding question: How do we verify the result end-to-end?
- Anti-patterns: DO NOT skip validation, NEVER hide failed checks, and avoid repetitive template-only output.
- Empowerment: be capable, creative, and enable users to explore options with confidence.

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
- If the affected UI, interaction path, or verification evidence is unclear, stop, report the missing context, and fall back to a scoped accessibility audit before making speculative fixes.
