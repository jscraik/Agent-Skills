---
name: swiftui-liquid-glass
description: Adopt or review iOS 26+ Liquid Glass in SwiftUI. Not for general SwiftUI patterns or refactors; use swiftui-ui-patterns or swiftui-view-refactor.
metadata:
  short-description: SwiftUI Liquid Glass patterns and reviews
---
# SwiftUI Liquid Glass

## Overview
Use this skill to build or review SwiftUI features that fully align with the iOS 26+ Liquid Glass API. Prioritize native APIs (`glassEffect`, `GlassEffectContainer`, glass button styles) and Apple design guidance. Keep usage consistent, interactive where needed, and performance aware.

## Philosophy
- Prefer native Liquid Glass APIs over custom effects to match platform behavior.
- Treat glass as a design system layer, not an afterthought.
- Keep the feature readable first; glass is an enhancement, not a replacement for structure.

## When to use
- When adopting Liquid Glass in new SwiftUI UI or components.
- When refactoring an existing SwiftUI feature to Liquid Glass.
- When reviewing Liquid Glass usage for correctness, performance, or design alignment.

## Inputs
- Target SwiftUI view(s) or feature description.
- iOS availability constraints and fallback requirements.
- Existing design guidelines or component references.

## Outputs
- Guidance or refactor plan aligned to Liquid Glass APIs.
- Updated SwiftUI code examples or changes for the feature.
- Review notes highlighting issues and fixes.

## Workflow Decision Tree
Choose the path that matches the request:

### 1) Review an existing feature
- Inspect where Liquid Glass should be used and where it should not.
- Verify correct modifier order, shape usage, and container placement.
- Check for iOS 26+ availability handling and sensible fallbacks.

### 2) Improve a feature using Liquid Glass
- Identify target components for glass treatment (surfaces, chips, buttons, cards).
- Refactor to use `GlassEffectContainer` where multiple glass elements appear.
- Introduce interactive glass only for tappable or focusable elements.

### 3) Implement a new feature using Liquid Glass
- Design the glass surfaces and interactions first (shape, prominence, grouping).
- Add glass modifiers after layout/appearance modifiers.
- Add morphing transitions only when the view hierarchy changes with animation.

## Core Guidelines
- Prefer native Liquid Glass APIs over custom blurs.
- Use `GlassEffectContainer` when multiple glass elements coexist.
- Apply `.glassEffect(...)` after layout and visual modifiers.
- Use `.interactive()` for elements that respond to touch/pointer.
- Keep shapes consistent across related elements for a cohesive look.
- Gate with `#available(iOS 26, *)` and provide a non-glass fallback.

## Constraints / Safety
- Do not break iOS version compatibility; always provide a fallback.
- Avoid excessive glass effects that reduce readability or contrast.
- Do not use interactive glass on non-interactive elements.

## Review Checklist
- **Availability**: `#available(iOS 26, *)` present with fallback UI.
- **Composition**: Multiple glass views wrapped in `GlassEffectContainer`.
- **Modifier order**: `glassEffect` applied after layout/appearance modifiers.
- **Interactivity**: `interactive()` only where user interaction exists.
- **Transitions**: `glassEffectID` used with `@Namespace` for morphing.
- **Consistency**: Shapes, tinting, and spacing align across the feature.

## Implementation Checklist
- Define target elements and desired glass prominence.
- Wrap grouped glass elements in `GlassEffectContainer` and tune spacing.
- Use `.glassEffect(.regular.tint(...).interactive(), in: .rect(cornerRadius: ...))` as needed.
- Use `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)` for actions.
- Add morphing transitions with `glassEffectID` when hierarchy changes.
- Provide fallback materials and visuals for earlier iOS versions.

## Variation rules
- Vary glass intensity and tint based on hierarchy and emphasis.
- Prefer subtle glass for backgrounds and stronger glass for primary actions.
- Adapt spacing and grouping to match the interaction model (list vs card vs chip).

## Anti-Patterns to Avoid
- Using custom blur effects when native Liquid Glass is available.
- Applying `.interactive()` to non-interactive elements.
- Missing `#available(iOS 26, *)` guards or fallback UI.
- Inconsistent shapes/tints across related elements.

## Example prompts
- "Refactor this SwiftUI card to use Liquid Glass with proper fallback."
- "Review my Liquid Glass usage for modifier order and performance."
- "Add Liquid Glass to the settings screen and keep iOS 25 compatibility."

## Quick Snippets
Use these patterns directly and tailor shapes/tints/spacing.

```swift
if #available(iOS 26, *) {
    Text("Hello")
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    Text("Hello")
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
    }
}
```

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

## Resources
- Reference guide: `references/liquid-glass.md`
- Prefer Apple docs for up-to-date API details.

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: swiftui-liquid-glass
description: Implement, review, or improve SwiftUI features using the iOS 26+ Liquid Glass API. Use when asked to adopt Liquid Glass in new SwiftUI UI, refactor an existing feature to Liquid Glass, or review Liquid Glass usage for correctness, performance, and design alignment.
metadata:
  short-description: SwiftUI Liquid Glass patterns and reviews
---
```
Body:

# SwiftUI Liquid Glass

## Overview
Use this skill to build or review SwiftUI features that fully align with the iOS 26+ Liquid Glass API. Prioritize native APIs (`glassEffect`, `GlassEffectContainer`, glass button styles) and Apple design guidance. Keep usage consistent, interactive where needed, and performance aware.

## Philosophy
- Prefer native Liquid Glass APIs over custom effects to match platform behavior.
- Treat glass as a design system layer, not an afterthought.
- Keep the feature readable first; glass is an enhancement, not a replacement for structure.

## When to use
- When adopting Liquid Glass in new SwiftUI UI or components.
- When refactoring an existing SwiftUI feature to Liquid Glass.
- When reviewing Liquid Glass usage for correctness, performance, or design alignment.

## Inputs
- Target SwiftUI view(s) or feature description.
- iOS availability constraints and fallback requirements.
- Existing design guidelines or component references.

## Outputs
- Guidance or refactor plan aligned to Liquid Glass APIs.
- Updated SwiftUI code examples or changes for the feature.
- Review notes highlighting issues and fixes.

## Workflow Decision Tree
Choose the path that matches the request:

### 1) Review an existing feature
- Inspect where Liquid Glass should be used and where it should not.
- Verify correct modifier order, shape usage, and container placement.
- Check for iOS 26+ availability handling and sensible fallbacks.

### 2) Improve a feature using Liquid Glass
- Identify target components for glass treatment (surfaces, chips, buttons, cards).
- Refactor to use `GlassEffectContainer` where multiple glass elements appear.
- Introduce interactive glass only for tappable or focusable elements.

### 3) Implement a new feature using Liquid Glass
- Design the glass surfaces and interactions first (shape, prominence, grouping).
- Add glass modifiers after layout/appearance modifiers.
- Add morphing transitions only when the view hierarchy changes with animation.

## Core Guidelines
- Prefer native Liquid Glass APIs over custom blurs.
- Use `GlassEffectContainer` when multiple glass elements coexist.
- Apply `.glassEffect(...)` after layout and visual modifiers.
- Use `.interactive()` for elements that respond to touch/pointer.
- Keep shapes consistent across related elements for a cohesive look.
- Gate with `#available(iOS 26, *)` and provide a non-glass fallback.

## Constraints / Safety
- Do not break iOS version compatibility; always provide a fallback.
- Avoid excessive glass effects that reduce readability or contrast.
- Do not use interactive glass on non-interactive elements.

## Review Checklist
- **Availability**: `#available(iOS 26, *)` present with fallback UI.
- **Composition**: Multiple glass views wrapped in `GlassEffectContainer`.
- **Modifier order**: `glassEffect` applied after layout/appearance modifiers.
- **Interactivity**: `interactive()` only where user interaction exists.
- **Transitions**: `glassEffectID` used with `@Namespace` for morphing.
- **Consistency**: Shapes, tinting, and spacing align across the feature.

## Implementation Checklist
- Define target elements and desired glass prominence.
- Wrap grouped glass elements in `GlassEffectContainer` and tune spacing.
- Use `.glassEffect(.regular.tint(...).interactive(), in: .rect(cornerRadius: ...))` as needed.
- Use `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)` for actions.
- Add morphing transitions with `glassEffectID` when hierarchy changes.
- Provide fallback materials and visuals for earlier iOS versions.

## Variation rules
- Vary glass intensity and tint based on hierarchy and emphasis.
- Prefer subtle glass for backgrounds and stronger glass for primary actions.
- Adapt spacing and grouping to match the interaction model (list vs card vs chip).

## Anti-Patterns to Avoid
- Using custom blur effects when native Liquid Glass is available.
- Applying `.interactive()` to non-interactive elements.
- Missing `#available(iOS 26, *)` guards or fallback UI.
- Inconsistent shapes/tints across related elements.

## Example prompts
- "Refactor this SwiftUI card to use Liquid Glass with proper fallback."
- "Review my Liquid Glass usage for modifier order and performance."
- "Add Liquid Glass to the settings screen and keep iOS 25 compatibility."

## Quick Snippets
Use these patterns directly and tailor shapes/tints/spacing.

```swift
if #available(iOS 26, *) {
    Text("Hello")
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    Text("Hello")
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
    }
}
```

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

## Resources
- Reference guide: `references/liquid-glass.md`
- Prefer Apple docs for up-to-date API details.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

### copilot variant
Frontmatter:

```yaml
---
name: swiftui-liquid-glass
description: Implement, review, or improve SwiftUI features using the iOS 26+ Liquid Glass API. Use when asked to adopt Liquid Glass in new SwiftUI UI, refactor an existing feature to Liquid Glass, or review Liquid Glass usage for correctness, performance, and design alignment.
metadata:
  short-description: SwiftUI Liquid Glass patterns and reviews
---
```
Body:

# SwiftUI Liquid Glass

## Overview
Use this skill to build or review SwiftUI features that fully align with the iOS 26+ Liquid Glass API. Prioritize native APIs (`glassEffect`, `GlassEffectContainer`, glass button styles) and Apple design guidance. Keep usage consistent, interactive where needed, and performance aware.

## Philosophy
- Prefer native Liquid Glass APIs over custom effects to match platform behavior.
- Treat glass as a design system layer, not an afterthought.
- Keep the feature readable first; glass is an enhancement, not a replacement for structure.

## When to use
- When adopting Liquid Glass in new SwiftUI UI or components.
- When refactoring an existing SwiftUI feature to Liquid Glass.
- When reviewing Liquid Glass usage for correctness, performance, or design alignment.

## Inputs
- Target SwiftUI view(s) or feature description.
- iOS availability constraints and fallback requirements.
- Existing design guidelines or component references.

## Outputs
- Guidance or refactor plan aligned to Liquid Glass APIs.
- Updated SwiftUI code examples or changes for the feature.
- Review notes highlighting issues and fixes.

## Workflow Decision Tree
Choose the path that matches the request:

### 1) Review an existing feature
- Inspect where Liquid Glass should be used and where it should not.
- Verify correct modifier order, shape usage, and container placement.
- Check for iOS 26+ availability handling and sensible fallbacks.

### 2) Improve a feature using Liquid Glass
- Identify target components for glass treatment (surfaces, chips, buttons, cards).
- Refactor to use `GlassEffectContainer` where multiple glass elements appear.
- Introduce interactive glass only for tappable or focusable elements.

### 3) Implement a new feature using Liquid Glass
- Design the glass surfaces and interactions first (shape, prominence, grouping).
- Add glass modifiers after layout/appearance modifiers.
- Add morphing transitions only when the view hierarchy changes with animation.

## Core Guidelines
- Prefer native Liquid Glass APIs over custom blurs.
- Use `GlassEffectContainer` when multiple glass elements coexist.
- Apply `.glassEffect(...)` after layout and visual modifiers.
- Use `.interactive()` for elements that respond to touch/pointer.
- Keep shapes consistent across related elements for a cohesive look.
- Gate with `#available(iOS 26, *)` and provide a non-glass fallback.

## Constraints / Safety
- Do not break iOS version compatibility; always provide a fallback.
- Avoid excessive glass effects that reduce readability or contrast.
- Do not use interactive glass on non-interactive elements.

## Review Checklist
- **Availability**: `#available(iOS 26, *)` present with fallback UI.
- **Composition**: Multiple glass views wrapped in `GlassEffectContainer`.
- **Modifier order**: `glassEffect` applied after layout/appearance modifiers.
- **Interactivity**: `interactive()` only where user interaction exists.
- **Transitions**: `glassEffectID` used with `@Namespace` for morphing.
- **Consistency**: Shapes, tinting, and spacing align across the feature.

## Implementation Checklist
- Define target elements and desired glass prominence.
- Wrap grouped glass elements in `GlassEffectContainer` and tune spacing.
- Use `.glassEffect(.regular.tint(...).interactive(), in: .rect(cornerRadius: ...))` as needed.
- Use `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)` for actions.
- Add morphing transitions with `glassEffectID` when hierarchy changes.
- Provide fallback materials and visuals for earlier iOS versions.

## Variation rules
- Vary glass intensity and tint based on hierarchy and emphasis.
- Prefer subtle glass for backgrounds and stronger glass for primary actions.
- Adapt spacing and grouping to match the interaction model (list vs card vs chip).

## Anti-Patterns to Avoid
- Using custom blur effects when native Liquid Glass is available.
- Applying `.interactive()` to non-interactive elements.
- Missing `#available(iOS 26, *)` guards or fallback UI.
- Inconsistent shapes/tints across related elements.

## Example prompts
- "Refactor this SwiftUI card to use Liquid Glass with proper fallback."
- "Review my Liquid Glass usage for modifier order and performance."
- "Add Liquid Glass to the settings screen and keep iOS 25 compatibility."

## Quick Snippets
Use these patterns directly and tailor shapes/tints/spacing.

```swift
if #available(iOS 26, *) {
    Text("Hello")
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    Text("Hello")
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
    }
}
```

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

## Resources
- Reference guide: `references/liquid-glass.md`
- Prefer Apple docs for up-to-date API details.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
