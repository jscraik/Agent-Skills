# Styled Text Editing in SwiftUI

## Overview
Use this reference for rich text display and editing with `Text`, `AttributedString`, and `TextEditor`.

## Basic Text Styling

### Fonts
```swift
Text("Hello World")
    .font(.largeTitle)

Text("Custom Size")
    .font(.system(size: 24))

Text("Bold Text")
    .fontWeight(.bold)

Text("Different Design")
    .font(.system(.body, design: .serif))
```

### Color
```swift
Text("Colored Text")
    .foregroundColor(.blue)

Text("Styled Text")
    .foregroundStyle(.red)

Text("Gradient Text")
    .foregroundStyle(
        .linearGradient(
            colors: [.yellow, .blue],
            startPoint: .top,
            endPoint: .bottom
        )
    )
```

### Decoration
```swift
Text("Underlined")
    .underline(true, color: .red)

Text("Strikethrough")
    .strikethrough(true, color: .green)
```

### Alignment and layout
```swift
Text("Aligned")
    .multilineTextAlignment(.center)
    .lineSpacing(10)
    .lineLimit(1)
    .truncationMode(.tail)
```

## AttributedString

### Create and style
```swift
var text = AttributedString("Red and Blue")
if let redRange = text.range(of: "Red") {
    text[redRange].foregroundColor = .red
}
if let blueRange = text.range(of: "Blue") {
    text[blueRange].foregroundColor = .blue
}

Text(text)
```

### Common attributes
```swift
var text = AttributedString("Styled text example")
text.font = .headline
text.foregroundColor = .blue
text.backgroundColor = .yellow
text.underlineStyle = .single
text.underlineColor = .red
text.strikethroughStyle = .single
text.strikethroughColor = .green
```

## TextEditor

### Basic TextEditor
```swift
struct SimpleTextEditorView: View {
    @State private var text = "Edit this text"

    var body: some View {
        TextEditor(text: $text)
            .frame(minHeight: 100)
            .border(Color.gray)
    }
}
```

### AttributedString editing
```swift
struct RichTextEditorView: View {
    @State private var text = AttributedString("Editable styled text")

    var body: some View {
        TextEditor(text: $text)
            .frame(minHeight: 100)
            .border(Color.gray)
    }
}
```

### Selection + formatting
```swift
struct StyledTextEditingView: View {
    @State private var text: AttributedString = AttributedString("Select text to format")
    @State private var selection = AttributedTextSelection()
    @Environment(\.fontResolutionContext) private var fontResolutionContext

    var body: some View {
        VStack {
            TextEditor(text: $text, selection: $selection)
                .frame(height: 200)
                .border(Color.gray)

            HStack {
                Button(action: toggleBold) { Image(systemName: "bold") }
                Button(action: toggleItalic) { Image(systemName: "italic") }
                Button(action: toggleUnderline) { Image(systemName: "underline") }
                ColorPicker("", selection: Binding(
                    get: { selection.typingAttributes(in: text).foregroundColor ?? .primary },
                    set: { color in
                        text.transformAttributes(in: &selection) { $0.foregroundColor = color }
                    }
                ))
            }
        }
    }

    private func toggleBold() {
        text.transformAttributes(in: &selection) {
            let font = $0.font ?? .default
            let resolved = font.resolve(in: fontResolutionContext)
            $0.font = font.bold(!resolved.isBold)
        }
    }

    private func toggleItalic() {
        text.transformAttributes(in: &selection) {
            let font = $0.font ?? .default
            let resolved = font.resolve(in: fontResolutionContext)
            $0.font = font.italic(!resolved.isItalic)
        }
    }

    private func toggleUnderline() {
        text.transformAttributes(in: &selection) {
            $0.underlineStyle = ($0.underlineStyle == nil) ? .single : nil
        }
    }
}
```

## Markdown in Text
```swift
Text("This is **bold** and *italic* text")
Text("Visit [Apple](https://www.apple.com)")
```

## Best Practices
- Cache complex `AttributedString` values when possible.
- Avoid recomputing attributed text every render.
- Validate contrast and Dynamic Type.

## References
- https://developer.apple.com/documentation/SwiftUI/View-Text-and-Symbols
- https://developer.apple.com/documentation/SwiftUI/Applying-Custom-Fonts-to-Text
- https://developer.apple.com/documentation/SwiftUI/building-rich-swiftui-text-experiences
- https://developer.apple.com/documentation/SwiftUI/Text
- https://developer.apple.com/documentation/Foundation/AttributedString
- https://developer.apple.com/documentation/SwiftUI/TextEditor
