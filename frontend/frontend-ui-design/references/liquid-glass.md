# Liquid Glass (SwiftUI)

Last verified: 2026-01-01

Use this guidance when asked to adopt new Apple design patterns or implement
Liquid Glass in SwiftUI. Prefer official Apple documentation for API details
and updates.

## Overview
Liquid Glass is a dynamic material that blurs content behind it, reflects color
and light from surrounding content, and reacts to touch and pointer
interactions. It can morph between shapes during transitions and is available
for standard and custom components.

## Basic implementation
```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()
```

### Customizing the shape
```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(in: .rect(cornerRadius: 16.0))
```

Common shapes:
- `.capsule` (default)
- `.rect(cornerRadius: CGFloat)`
- `.circle`

## Customizing effects
```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())
```

Key options:
- `.regular` - standard glass
- `.tint(Color)` - color tint
- `.interactive()` - react to touch/pointer

## Multiple glass effects
Wrap multiple glass elements in `GlassEffectContainer` for performance and
blending:

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

### Uniting multiple glass effects
```swift
@Namespace private var namespace

GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "1" : "2", namespace: namespace)
        }
    }
}
```

## Morphing transitions
```swift
@State private var isExpanded: Bool = false
@Namespace private var namespace

var body: some View {
    GlassEffectContainer(spacing: 40.0) {
        HStack(spacing: 40.0) {
            Image(systemName: "scribble.variable")
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectID("pencil", in: namespace)

            if isExpanded {
                Image(systemName: "eraser.fill")
                    .frame(width: 80.0, height: 80.0)
                    .font(.system(size: 36))
                    .glassEffect()
                    .glassEffectID("eraser", in: namespace)
            }
        }
    }

    Button("Toggle") {
        withAnimation {
            isExpanded.toggle()
        }
    }
    .buttonStyle(.glass)
}
```

## Button styles
```swift
Button("Click Me") { }
    .buttonStyle(.glass)
```

```swift
Button("Important Action") { }
    .buttonStyle(.glassProminent)
```

## Best practices
- Use `GlassEffectContainer` when multiple glass elements coexist.
- Apply `.glassEffect()` after layout/appearance modifiers.
- Use `.interactive()` only for interactive elements.
- Keep shapes consistent across related elements.
- Gate APIs with `#available(iOS 26, *)` and provide a fallback.

## References
Prefer Apple documentation for API accuracy and updates.
