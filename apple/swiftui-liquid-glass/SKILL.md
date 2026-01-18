---
name: swiftui-liquid-glass
description: "Use this skill to build or review SwiftUI features that align with the iOS 26+ Liquid Glass API. Prioritize native APIs (glassEffect, GlassEffectContainer, glass button styles) and Apple design guidance. Keep usage consistent, interactive where needed, and performance-aware. Also use this skill to provide AppKit Liquid Glass notes for macOS when requested."
metadata:
  short-description: SwiftUI + AppKit Liquid Glass guidance, patterns, and reviews.
---

# SwiftUI Liquid Glass

## Overview
Use this skill to build or review SwiftUI features that fully align with the iOS 26+ Liquid Glass API. Prioritize native APIs (`glassEffect`, `GlassEffectContainer`, glass button styles) and Apple design guidance. Keep usage consistent, interactive where needed, and performance aware.
If the request targets AppKit/macOS, follow the AppKit notes in `references/appkit-liquid-glass.md` and confirm API availability in the current SDK.
If the request targets widgets or WidgetKit rendering modes, follow `references/widget-liquid-glass.md`.
If the request targets UIKit, follow `references/uikit-liquid-glass.md` and confirm API availability in the current SDK.

## When to use
- Adopting Liquid Glass in SwiftUI views or components.
- Auditing Liquid Glass usage for performance, accessibility, and design alignment.
- Adapting Liquid Glass behavior for AppKit, UIKit, or WidgetKit.

## Philosophy
- Prefer native Liquid Glass APIs over custom effects to match platform behavior.
- Treat glass as a design system layer, not an afterthought.
- Keep the feature readable first; glass is an enhancement, not a replacement for structure.
- Favor clarity over novelty; glass should clarify hierarchy, not blur it.
- Use motion sparingly to reinforce state changes and transitions.
- Maintain accessibility first: contrast, legibility, and focus must remain strong.

## Principles
- Principle: prioritize platform fidelity over bespoke effects.
- Principle: preserve legibility and focus states before adding glass.
- Principle: reduce visual noise; fewer glass surfaces beat many.
- Principle: smooth transitions should communicate state changes, not distract.

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
- Redact secrets/PII by default.
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
- Overusing glass on large surfaces that reduce readability.
- Mixing multiple glass styles in the same hierarchy without intent.
- Animating glass effects on every frame or interaction without need.
- Adding glass to critical text backgrounds without verifying contrast.
- Anti-pattern: shipping glass without verifying contrast across light/dark.
- Anti-pattern: layering glass on top of glass with no hierarchy cue.
- Anti-pattern: applying interactive glass to passive decorative elements.
- Anti-pattern: hiding focus rings or reducing focus visibility on glass surfaces.
- Anti-pattern: mismatched corner radii across a glass group.
- Anti-pattern: skipping container grouping when multiple glass views merge.
- Anti-pattern: using glass to mask layout issues instead of fixing layout.
- Anti-pattern: relying on glass to separate content without spacing or dividers.
- Anti-pattern: prioritizing glass visuals over accessibility requirements.

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
- AppKit guide: `references/appkit-liquid-glass.md`
- Widget guide: `references/widget-liquid-glass.md`
- UIKit guide: `references/uikit-liquid-glass.md`
- Prefer Apple docs for up-to-date API details.

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
- Do not ship glass without explicit fallback UI and availability guards.
- Do not degrade input focus visibility or pointer clarity.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.

## Response format (required)
Always use this format, including for out-of-scope requests.

## When to use
- ...

## Inputs
- ...

## Outputs
- ...

## Failure mode (required)
If the request is out of scope, respond using the same headings and explain when this skill should be used instead. Include `## When to use` in the response.
