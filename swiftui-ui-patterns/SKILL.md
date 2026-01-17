---
name: swiftui-ui-patterns
description: SwiftUI UI patterns and example structures for building screens and components. Not for refactors or Liquid Glass adoption; use swiftui-view-refactor or swiftui-liquid-glass.
metadata:
  short-description: SwiftUI patterns
---

# SwiftUI UI Patterns

## Philosophy
- Prefer native SwiftUI patterns over heavy view-model scaffolding.
- Keep views small, composable, and predictable.
- Preserve project conventions and avoid premature abstraction.

## When to use
- Building or refactoring SwiftUI screens and components.
- Designing navigation with TabView/NavigationStack.
- Choosing component-specific patterns or examples.

## Inputs
- Target SwiftUI file(s) or feature description.
- Existing repo conventions and component references.

## Outputs
- Pattern guidance and example structure for the requested view.
- References to relevant component docs or in-repo examples.

## Quick start

Choose a track based on your goal:

### Existing project

- Identify the feature or screen and the primary interaction model (list, detail, editor, settings, tabbed).
- Find a nearby example in the repo with `rg "TabView\("` or similar, then read the closest SwiftUI view.
- Apply local conventions: prefer SwiftUI-native state, keep state local when possible, and use environment injection for shared dependencies.
- Choose the relevant component reference from `references/components-index.md` and follow its guidance.
- Build the view with small, focused subviews and SwiftUI-native data flow.

### New project scaffolding

- Start with `references/app-scaffolding-wiring.md` to wire TabView + NavigationStack + sheets.
- Add a minimal `AppTab` and `RouterPath` based on the provided skeletons.
- Choose the next component reference based on the UI you need first (TabView, NavigationStack, Sheets).
- Expand the route and sheet enums as new screens are added.

## General rules to follow

- Use modern SwiftUI state (`@State`, `@Binding`, `@Observable`, `@Environment`) and avoid unnecessary view models.
- Prefer composition; keep views small and focused.
- Use async/await with `.task` and explicit loading/error states.
- Maintain existing legacy patterns only when editing legacy files.
- Follow the project's formatter and style guide.
- Sheets: Prefer `.sheet(item:)` over `.sheet(isPresented:)` when state represents a selected model. Avoid `if let` inside a sheet body. Sheets should own their actions and call `dismiss()` internally instead of forwarding `onCancel`/`onConfirm` closures.

## Constraints / Safety
- Do not introduce non-native patterns unless the repo already uses them.
- Preserve behavior; avoid unrequested UI changes.

## Workflow for a new SwiftUI view

1. Define the view's state and its ownership location.
2. Identify dependencies to inject via `@Environment`.
3. Sketch the view hierarchy and extract repeated parts into subviews.
4. Implement async loading with `.task` and explicit state enum if needed.
5. Add accessibility labels or identifiers when the UI is interactive.
6. Validate with a build and update usage callsites if needed.

## Component references

Use `references/components-index.md` as the entry point. Each component reference should include:
- Intent and best-fit scenarios.
- Minimal usage pattern with local conventions.
- Pitfalls and performance notes.
- Paths to existing examples in the current repo.
- For any shared design-system work, load `references/design-guidelines-summary.md` (quick) or `references/design-guidelines-canonical.md` (full) for colors/typography/a11y/review gates and token usage.

## Sheet patterns

### Item-driven sheet (preferred)

```swift
@State private var selectedItem: Item?

.sheet(item: $selectedItem) { item in
    EditItemSheet(item: item)
}
```

### Sheet owns its actions

```swift
struct EditItemSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(Store.self) private var store

    let item: Item
    @State private var isSaving = false

    var body: some View {
        VStack {
            Button(isSaving ? "Saving…" : "Save") {
                Task { await save() }
            }
        }
    }

    private func save() async {
        isSaving = true
        await store.save(item)
        dismiss()
    }
}
```

## Adding a new component reference

- Create `references/<component>.md`.
- Keep it short and actionable; link to concrete files in the current repo.
- Update `references/components-index.md` with the new entry.

## Variation rules
- Vary guidance by screen complexity (simple list vs multi-step flow).
- Prefer minimal scaffolding for small screens.

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
