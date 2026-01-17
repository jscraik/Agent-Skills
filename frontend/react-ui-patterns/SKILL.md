---
name: react-ui-patterns
description: Provide React UI patterns and examples with TypeScript, Tailwind, and Radix. Not for design-system governance or visual regression; use ui-design-system or ui-visual-regression.
metadata:
  short-description: React UI patterns and component guidance
---
# React UI Patterns

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Provide concrete, example-driven guidance for React UI composition, state, routing, and component patterns in a TypeScript + Tailwind + Radix stack.

## Philosophy
- Prefer composable, accessible primitives over bespoke UI logic.
- Keep state local when possible; lift only when needed.
- Preserve repo conventions; do not introduce new patterns without need.

## When to use
- Building or refactoring React screens and components.
- Designing layout, routing, or tabbed navigation structures.
- Choosing component-specific patterns or examples in a React stack.

## Inputs
- Target React component(s) or feature description.
- Existing repo conventions, design system, and component references.
- Constraints (router, state library, or data fetching approach).

## Outputs
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

- Use idiomatic React hooks (`useState`, `useMemo`, `useCallback`, `useEffect`) and avoid derived state when possible.
- Prefer composition; keep components small and focused.
- Use async/await for data fetchers and explicit loading/error states.
- Maintain existing legacy patterns only when editing legacy files.
- Follow the project's formatter and style guide (TypeScript + Tailwind + Biome).
- Avoid adding new dependencies without user approval.

## Constraints / Safety
- Do not introduce patterns that conflict with the repo's router or state library.
- Preserve behavior; avoid unrequested UI changes.
- Ensure keyboard and screen reader support for interactive components.

## Workflow for a new React view

1. Define the view's state and its ownership location.
2. Identify dependencies to inject via context or props.
3. Sketch the component hierarchy and extract repeated parts.
4. Implement async loading with explicit loading/error UI.
5. Add accessibility labels and roles for interactive elements.
6. Validate with a build or story and update callsites if needed.

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

## Anti-Patterns to Avoid
- Overusing `useEffect` for derived state.
- Recreating global state for local component needs.
- Skipping accessibility on interactive elements.
- Adding new dependencies without explicit approval.

## Example prompts
- "Refactor this settings screen into smaller React components."
- "Design a tabs layout with Radix and Tailwind."
- "Add a dialog pattern for editing an item with a controlled open state."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources
- Component index: `references/components-index.md`
- App wiring: `references/app-scaffolding-wiring.md`

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: react-ui-patterns
description: Best practices and example-driven guidance for building React UI components and screens. Use when creating or refactoring React UI, designing routing/layout composition, or needing component-specific patterns and examples with React, TypeScript, Tailwind, and Radix.
metadata:
  short-description: React UI patterns and component guidance
---
```
Body:

# React UI Patterns

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Provide concrete, example-driven guidance for React UI composition, state, routing, and component patterns in a TypeScript + Tailwind + Radix stack.

## Philosophy
- Prefer composable, accessible primitives over bespoke UI logic.
- Keep state local when possible; lift only when needed.
- Preserve repo conventions; do not introduce new patterns without need.

## When to use
- Building or refactoring React screens and components.
- Designing layout, routing, or tabbed navigation structures.
- Choosing component-specific patterns or examples in a React stack.

## Inputs
- Target React component(s) or feature description.
- Existing repo conventions, design system, and component references.
- Constraints (router, state library, or data fetching approach).

## Outputs
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

- Use idiomatic React hooks (`useState`, `useMemo`, `useCallback`, `useEffect`) and avoid derived state when possible.
- Prefer composition; keep components small and focused.
- Use async/await for data fetchers and explicit loading/error states.
- Maintain existing legacy patterns only when editing legacy files.
- Follow the project's formatter and style guide (TypeScript + Tailwind + Biome).
- Avoid adding new dependencies without user approval.

## Constraints / Safety
- Do not introduce patterns that conflict with the repo's router or state library.
- Preserve behavior; avoid unrequested UI changes.
- Ensure keyboard and screen reader support for interactive components.

## Workflow for a new React view

1. Define the view's state and its ownership location.
2. Identify dependencies to inject via context or props.
3. Sketch the component hierarchy and extract repeated parts.
4. Implement async loading with explicit loading/error UI.
5. Add accessibility labels and roles for interactive elements.
6. Validate with a build or story and update callsites if needed.

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

## Anti-Patterns to Avoid
- Overusing `useEffect` for derived state.
- Recreating global state for local component needs.
- Skipping accessibility on interactive elements.
- Adding new dependencies without explicit approval.

## Example prompts
- "Refactor this settings screen into smaller React components."
- "Design a tabs layout with Radix and Tailwind."
- "Add a dialog pattern for editing an item with a controlled open state."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources
- Component index: `references/components-index.md`
- App wiring: `references/app-scaffolding-wiring.md`

### copilot variant
Frontmatter:

```yaml
---
name: react-ui-patterns
description: Best practices and example-driven guidance for building React UI components and screens. Use when creating or refactoring React UI, designing routing/layout composition, or needing component-specific patterns and examples with React, TypeScript, Tailwind, and Radix.
metadata:
  short-description: React UI patterns and component guidance
---
```
Body:

# React UI Patterns

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Provide concrete, example-driven guidance for React UI composition, state, routing, and component patterns in a TypeScript + Tailwind + Radix stack.

## Philosophy
- Prefer composable, accessible primitives over bespoke UI logic.
- Keep state local when possible; lift only when needed.
- Preserve repo conventions; do not introduce new patterns without need.

## When to use
- Building or refactoring React screens and components.
- Designing layout, routing, or tabbed navigation structures.
- Choosing component-specific patterns or examples in a React stack.

## Inputs
- Target React component(s) or feature description.
- Existing repo conventions, design system, and component references.
- Constraints (router, state library, or data fetching approach).

## Outputs
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

- Use idiomatic React hooks (`useState`, `useMemo`, `useCallback`, `useEffect`) and avoid derived state when possible.
- Prefer composition; keep components small and focused.
- Use async/await for data fetchers and explicit loading/error states.
- Maintain existing legacy patterns only when editing legacy files.
- Follow the project's formatter and style guide (TypeScript + Tailwind + Biome).
- Avoid adding new dependencies without user approval.

## Constraints / Safety
- Do not introduce patterns that conflict with the repo's router or state library.
- Preserve behavior; avoid unrequested UI changes.
- Ensure keyboard and screen reader support for interactive components.

## Workflow for a new React view

1. Define the view's state and its ownership location.
2. Identify dependencies to inject via context or props.
3. Sketch the component hierarchy and extract repeated parts.
4. Implement async loading with explicit loading/error UI.
5. Add accessibility labels and roles for interactive elements.
6. Validate with a build or story and update callsites if needed.

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

## Anti-Patterns to Avoid
- Overusing `useEffect` for derived state.
- Recreating global state for local component needs.
- Skipping accessibility on interactive elements.
- Adding new dependencies without explicit approval.

## Example prompts
- "Refactor this settings screen into smaller React components."
- "Design a tabs layout with Radix and Tailwind."
- "Add a dialog pattern for editing an item with a controlled open state."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources
- Component index: `references/components-index.md`
- App wiring: `references/app-scaffolding-wiring.md`
