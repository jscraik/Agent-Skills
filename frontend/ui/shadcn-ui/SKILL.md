---
name: shadcn-ui
description: Integrate and customize shadcn/ui components in existing projects. Use when the user asks to set up, add, adapt, or troubleshoot shadcn/ui components, registry items, and implementation patterns.
allowed-tools:
  - "shadcn*:*"
  - "mcp_shadcn*"
  - "Read"
  - "Write"
  - "Bash"
  - "web_fetch"
metadata:
  skill-type: scaffolding_templates
---

# shadcn/ui Integration

Use shadcn/ui as a code-ownership workflow, not as a drop-in component dependency.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Design-system integration](#design-system-integration)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Variation](#variation)
- [Failure mode](#failure-mode)
- [Workflow](#workflow)
- [Antipatterns](#antipatterns)
- [Validation](#validation)
- [References](#references)

## Standards snapshot
- Treat shadcn/ui as source code copied into the repo, owned by the project team.
- Prefer the current shadcn CLI workflow and registry-aware install path over manual copy-paste unless the repo requires it.
- Keep Tailwind v4, design tokens, accessibility, and project-local component composition aligned with the host app.
- For React 19 and Next.js 16 projects, preserve WCAG 2.2 accessibility behaviors during every shadcn/ui integration step.
- Customize through project wrappers and token-aware variants rather than forking primitives blindly.

## Design-system integration
- Apply `frontend/ui/references/design-system-integration-contract.md` for typography, spacing, iconography, and semantic token alignment decisions.
- Route shared design-language changes to `design-system`; keep this skill focused on component integration and customization execution.
- Use `frontend/ui/references/skill-routing-matrix-2026.md` when shadcn component requests overlap with broader frontend routing or redesign asks.

## When to use
- The user wants to install, add, customize, or troubleshoot shadcn/ui components.
- A repo uses or plans to use `components.json`, registries, or copied component source under `components/ui/`.
- You need to compare registry options or integrate a block into an existing design system.
- A shadcn setup needs verification or migration guidance.

## Required inputs
- Target repo or project path.
- Framework and styling context:
  - React or Next.js;
  - Tailwind setup;
  - alias conventions;
  - server/client boundaries.
- The components or blocks the user wants.
- Any constraints on theming, accessibility, bundle size, or visual consistency.

## Deliverables
- Clear setup or integration guidance grounded in the existing project.
- The chosen shadcn components or registry items, plus customization notes.
- Any required dependency, config, or file-placement changes.
- A concise validation checklist covering install success and UI safety.

## Philosophy
- Treat shadcn/ui as owned source code, not a black-box dependency.
- Prefer the smallest install and customization path that matches the host repo.
- Keep accessibility and token alignment intact while adapting components.
- Ask: "Can this be solved with one component add plus wrapper adjustments?"
- Ask: "Will this customization still be maintainable after the next upstream update?"
- Ask: "Are we avoiding optional complexity and keeping this scope focused on one component lane?"

## Variation
- Adapt setup depth by project maturity:
  - existing production app: verify readiness and add only requested components;
  - new app bootstrap: initialize once, then establish wrapper conventions early.
- Vary customization strategy by ownership constraints:
  - strict design-system repo: use token-aware wrappers and minimal source edits;
  - exploratory prototype: allow faster iteration, then harden with accessibility and token checks.
- Keep package boundary explicit: prefer one component path and one validation lane before wider adoption.

## Failure mode
- If the task is a general design-system rewrite, route to a broader frontend or design-system skill.
- If the repo is not ready for shadcn/ui yet, stop at readiness guidance instead of forcing installation.
- If the user asks for opaque wrapper abstractions that weaken ownership, call out that tradeoff before proceeding.

## Constraints
- Redact secrets, local environment paths, and private registry details by default in outputs.
- Do not force shadcn/ui into repos that lack the prerequisite Tailwind or alias setup.
- Keep customization scoped to the requested component path and related config.

## Workflow
1. Check project readiness first:
   - framework support;
   - Tailwind presence;
   - path aliases;
   - `components.json` state.
2. Choose the smallest installation path that matches the repo:
   - `npx shadcn@latest init` for setup;
   - `npx shadcn@latest add <component>` for direct component install;
   - registry discovery only when the request needs it.
3. Prefer copied source in `components/ui/` and keep project-specific wrappers outside that folder.
4. Use the bundled references for setup, migration, and customization rather than re-explaining everything from memory.
5. Preserve accessibility and token alignment when editing variants or markup.
6. End with exact local checks the repo should pass next.

## Antipatterns
- Avoid treating copied components as if they were still vendor-owned and off-limits.
- Do not drop custom wrappers into `components/ui/`; keep wrappers in the project layer so ownership is explicit.
- Never hardcode visual values that bypass the repo token system. That is the wrong integration posture for long-term maintainability.
- Avoid installing many registry items before confirming the first component path compiles and matches host conventions.
- Do not bypass accessibility checks because the component "looked fine" in one viewport.
- Anti-pattern warning: incorrect import boundaries and ad hoc overrides create hidden upgrade debt.

## Validation
- Fail fast: stop at the first missing prerequisite or broken import before adding more components.
- Verify the component lands in the expected repo location and imports resolve cleanly.
- Confirm required dependencies and config changes are present, not implied.
- Check keyboard interaction, focus behavior, and semantic markup after customization.
- If the repo uses theme tokens, ensure the component respects them instead of hardcoded visual values.
- Confirm shadcn variants and overrides remain compliant with `frontend/ui/references/design-system-integration-contract.md`.

## Examples
- "Add shadcn dialog and command components to this Next.js app and keep the existing token system."
- "Check whether this repo is actually ready for shadcn/ui before we install anything."
- "Migrate this older component variant to the current shadcn pattern without breaking accessibility."

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Setup guide: `resources/setup-guide.md`
- Customization guide: `resources/customization-guide.md`
- Migration guide: `resources/migration-guide.md`
- Component catalog: `resources/component-catalog.md`
- Examples: `examples/auth-layout.tsx`, `examples/data-table.tsx`, `examples/form-pattern.tsx`
- Setup verifier: `scripts/verify-setup.sh`
- README: `README.md`

## See Also

| Skill | When to use together |
|---|---|
| [[react-ui-patterns]] | Apply React composition patterns to shadcn/ui components |
| [[design-system]] | Override shadcn/ui tokens with design-system aliases |
| [[baseline-ui]] | Validate shadcn/ui component usage against baseline rules |
| [[fixing-accessibility]] | Fix accessibility issues in shadcn/ui interactive components |
| [[figma]] | Use Figma designs as reference for shadcn/ui customisation |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
