# Implementing Liquid Glass Design in Widgets

## Overview
Liquid Glass is a dynamic, adaptive material introduced across Apple platforms that combines the optical properties of glass with a sense of fluidity. When applied to widgets, Liquid Glass creates a modern, cohesive look that integrates with system UI. Use this guide to implement and optimize Liquid Glass in widgets, including rendering modes, appearance configuration, and cross-platform behavior.

Key features:
- Blurs content behind the material
- Reflects color and light from surrounding content
- Reacts to touch and pointer interactions
- Can morph between shapes during transitions
- Available for standard and custom components

## Understanding Widget Rendering Modes
Widgets can appear in two primary rendering modes when using Liquid Glass:

### Full Color Mode
- Default rendering mode
- Displays all colors, images, and transparency as designed
- Used when widgets appear on standard backgrounds

### Accented Mode
- Used when a person chooses a tinted or clear appearance
- Primary and accented content is tinted white (iOS and macOS)
- Opaque images are tinted with a single white color
- Transparent content and gradients keep opacity but are tinted white
- Background is replaced with themed glass or tinted color effect

## Supporting Liquid Glass in Widgets

### Detect rendering mode
```swift
struct MyWidgetView: View {
    @Environment(\.widgetRenderingMode) var renderingMode

    var body: some View {
        if renderingMode == .accented {
            // Layout optimized for accented mode
        } else {
            // Standard full-color layout
        }
    }
}
```

### Accent grouping
```swift
HStack(alignment: .center, spacing: 0) {
    VStack(alignment: .leading) {
        Text("Widget Title")
            .font(.headline)
            .widgetAccentable()
        Text("Widget Subtitle")
    }
    Image(systemName: "star.fill")
        .widgetAccentable()
}
```

### Accented image rendering
```swift
Image("myImage")
    .widgetAccentedRenderingMode(.monochrome)
```

### Guidelines
- Display full-color images only in `fullColor` mode
- Adjust layout for `accented` mode
- Use `widgetAccentable()` to establish hierarchy

## Container Backgrounds
```swift
var body: some View {
    VStack {
        // Widget content
    }
    .containerBackground(for: .widget) {
        Color.blue.opacity(0.2)
    }
}
```

When a person chooses a tinted or clear appearance, the system:
- Removes the background
- Replaces it with a themed glass or tinted color effect

## Background Removal
```swift
var body: some WidgetConfiguration {
    StaticConfiguration(kind: "MyWidget", provider: Provider()) { entry in
        MyWidgetView(entry: entry)
    }
    .containerBackgroundRemovable(false)
}
```

Note: Marking a background as non-removable excludes the widget from contexts that require removable backgrounds (iPad Lock Screen, StandBy).

## visionOS Widget Textures
```swift
var body: some WidgetConfiguration {
    StaticConfiguration(kind: "MyWidget", provider: Provider()) { entry in
        MyWidgetView(entry: entry)
    }
    .widgetTexture(.glass)
}
```

Available textures:
- `.glass` (default)
- `.paper`

## visionOS Mounting Styles
```swift
var body: some WidgetConfiguration {
    StaticConfiguration(kind: "MyWidget", provider: Provider()) { entry in
        MyWidgetView(entry: entry)
    }
    .supportedMountingStyles([.recessed, .elevated])
}
```

Available mounting styles:
- `.recessed`
- `.elevated`

## Custom Widget Elements
```swift
Text("Custom Element")
    .padding()
    .glassEffect()

Image(systemName: "star.fill")
    .frame(width: 60, height: 60)
    .glassEffect(.regular, in: .rect(cornerRadius: 12))

Button("Action") {
    // Action
}
.buttonStyle(.glass)
```

## Combining Multiple Glass Elements
```swift
GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        Image(systemName: "cloud")
            .frame(width: 60, height: 60)
            .glassEffect()
        Image(systemName: "sun")
            .frame(width: 60, height: 60)
            .glassEffect()
    }
}
```

To unify specific elements:
```swift
GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(items.indices, id: \.self) { item in
            Image(systemName: items[item])
                .frame(width: 60, height: 60)
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "group1" : "group2", namespace: namespace)
        }
    }
}
```

## Platform Notes
### iOS and iPadOS
- Support full color and accented modes
- Test Home Screen and Lock Screen
- Verify readability in light and dark

### macOS
- Verify sizing across widget sizes
- Test standard and accented modes

### visionOS
- Support `levelOfDetail` for distance
```swift
@Environment(\.levelOfDetail) var levelOfDetail

var fontSize: Font {
    levelOfDetail == .simplified ? .largeTitle : .title
}
```

## Testing Checklist
- Light and dark modes
- Home Screen and Lock Screen
- Different accent colors
- Different backgrounds
- StandBy mode
- visionOS mounting styles and distances

## References
- Optimizing your widget for accented rendering mode and Liquid Glass
- Applying Liquid Glass to custom views
- Landmarks: Building an app with Liquid Glass
- Displaying the right widget background
- Updating your widgets for visionOS
