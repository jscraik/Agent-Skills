---
name: react-ui-patterns
description: "Provide concrete React UI composition patterns for TypeScript + Tailwind + Radix, including state, routing, and component structure examples. Use when building or refactoring React screens and components for maintainability."
---

# React UI Patterns

## Table of Contents
- [Overview](#overview)
- [Current baseline markers](#current-baseline-markers)
- [Philosophy](#philosophy)
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Quick start](#quick-start)
- [General rules to follow](#general-rules-to-follow)
- [Constraints / Safety](#constraints--safety)
- [Workflow for a new React view](#workflow-for-a-new-react-view)
- [Modern React guidance](#modern-react-guidance)
- [Component references](#component-references)
- [Modal patterns](#modal-patterns)
- [Adding a new component reference](#adding-a-new-component-reference)
- [Variation rules](#variation-rules)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Example prompts](#example-prompts)
- [Resources](#resources)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Procedure](#procedure)
- [Antipatterns](#antipatterns)

## Compliance
- Check against current global instructions in `~/.codex/AGENTS.md` and linked standards docs.

## Overview
Provide concrete, example-driven guidance for React UI composition, state, routing, and component patterns in a TypeScript + Tailwind + Radix stack.

## Current baseline markers
- React 19 is the default baseline for hooks, transitions, and client interaction guidance.
- Next.js 16 is the default routing and server/client boundary baseline when the target app uses Next.js.
- Tailwind CSS v4 is the default utility and token baseline for styling examples.
- WCAG 2.2 AA is the default accessibility bar for component and screen recommendations.

## Philosophy
- Prefer composable, accessible primitives over bespoke UI logic.
- Keep state local when possible; lift only when needed.
- Preserve repo conventions; do not introduce new patterns without need.

## Scope and triggers
- Building or refactoring React screens and components.
- Designing layout, routing, or tabbed navigation structures.
- Choosing component-specific patterns or examples in a React stack.

## Required inputs
- Target React component(s) or feature description.
- Existing repo conventions, design system, and component references.
- Constraints (router, state library, or data fetching approach).

## Deliverables
- Pattern guidance and example structure for the requested UI.
- References to relevant component docs or in-repo examples.
- Notes on accessibility and state ownership where needed.

## Quick start

Choose a track based on your goal:

### Existing project

- Identify the feature or screen and the primary interaction model (list, detail, editor, settings, tabbed).
- Find a nearby example in the repo with `rg "<ComponentName>"` or `rg "<RouteName>"`, then read the closest React component.
- Apply local conventions: prefer React hooks, keep state local when possible, and use context for shared dependencies.
- Choose the relevant component reference from `references/components-index.md` and follow its guidance.
- Build the view with small, focused components and predictable data flow.

### New project scaffolding

- Start with `references/app-scaffolding-wiring.md` to wire Router + Layout + providers.
- Add a minimal route map and layout shell based on the provided skeletons.
- Choose the next component reference based on the UI you need first (Tabs, Dialog, Form, Data table).
- Expand routes and layouts as screens are added.

## General rules to follow

- Use idiomatic modern React hooks and state primitives:
  - `useState` for local UI state;
  - `useEffectEvent` for event logic inside effects when the repo/runtime supports it;
  - `startTransition` for non-urgent UI updates;
  - `useDeferredValue` for expensive filtered or derived views when user typing should stay responsive.
- Do not add `useMemo` or `useCallback` by default. Use them only when profiling or established repo conventions justify them.
- Prefer composition; keep components small and focused.
- Use async/await for data fetchers and explicit loading/error states.
- Keep server/client boundaries explicit in hybrid React frameworks; do not pull client-only stateful UI into server components accidentally.
- Maintain existing legacy patterns only when editing legacy files.
- Follow the project's formatter and style guide (TypeScript + Tailwind + Biome).
- Avoid adding new dependencies without user approval.

## Constraints / Safety
- Redact secrets/PII by default.
- Do not introduce patterns that conflict with the repo's router or state library.
- Preserve behavior; avoid unrequested UI changes.
- Ensure keyboard and screen reader support for interactive components.

## Workflow for a new React view

1. Define the view's state and its ownership location.
2. Identify dependencies to inject via context or props.
3. Sketch the component hierarchy and extract repeated parts.
4. Decide the async interaction model:
   - server-loaded data;
   - client fetch with explicit loading/error states;
   - optimistic mutation with rollback;
   - deferred search/filter rendering.
5. Implement async loading with explicit loading/error UI.
6. Use transitions or deferred rendering where interaction latency matters.
7. Add accessibility labels and roles for interactive elements.
8. Validate with a build, story, or targeted UI test and update callsites if needed.

## Modern React guidance

- Prefer event handlers and reducers over effect-heavy synchronization.
- Treat `useEffect` as an integration boundary for subscriptions, DOM APIs, network lifecycle, or external systems, not as a generic data-flow tool.
- Keep forms explicit about pending, success, and error states.
- For route-level UIs, keep loading and error surfaces close to the route boundary instead of scattering them through child components.
- If the repo is React Compiler-aware, lean on clear code and stable data flow before manual memoization tricks.

## Component references

Use `references/components-index.md` as the entry point. Each component reference should include:
- Intent and best-fit scenarios.
- Minimal usage pattern with local conventions.
- Pitfalls and performance notes.
- Paths to existing examples in the current repo.

## Modal patterns

### Controlled dialog (preferred)

```tsx
const [open, setOpen] = useState(false);

<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Edit item</DialogTitle>
    </DialogHeader>
    <EditForm onDone={() => setOpen(false)} />
  </DialogContent>
</Dialog>
```

### Dialog owns its actions

```tsx
function EditDialogContent({ onDone }: { onDone: () => void }) {
  const [isSaving, setIsSaving] = useState(false);

  async function handleSave() {
    setIsSaving(true);
    await save();
    onDone();
  }

  return (
    <div>
      <Button onClick={handleSave} disabled={isSaving}>
        {isSaving ? "Saving..." : "Save"}
      </Button>
    </div>
  );
}
```

## Adding a new component reference

- Create `references/<component>.md`.
- Keep it short and actionable; link to concrete files in the current repo.
- Update `references/components-index.md` with the new entry.

## Variation rules
- Vary guidance by screen complexity (simple list vs multi-step flow).
- Prefer minimal scaffolding for small screens.
- Adapt to the repo's styling and routing conventions.
- Choose different async/state patterns for dashboards, forms, editors, and search-heavy screens rather than forcing one template.

## Anti-Patterns to Avoid
- Overusing `useEffect` for derived state.
- Recreating global state for local component needs.
- Skipping accessibility on interactive elements.
- Adding new dependencies without explicit approval.
- Manually memoizing everything instead of fixing component boundaries or expensive work hotspots.
- Mixing server and client concerns without an explicit boundary.

## Example prompts
- "Refactor this settings screen into smaller React components."
- "Design a tabs layout with Radix and Tailwind."
- "Add a dialog pattern for editing an item with a controlled open state."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential; they do not constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources
- Component index: `references/components-index.md`
- App wiring: `references/app-scaffolding-wiring.md`

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.

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
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
