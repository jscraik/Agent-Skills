# Foundation AttributedString Updates

## Overview
Use this reference when you need modern AttributedString APIs, selection/editing helpers, or new alignment/line height features.

## Core patterns

### Create and style
```swift
let attributedText = AttributedString("Hello, world!")

var text = AttributedString("Styled text")
text.foregroundColor = .red
text.backgroundColor = .yellow
text.font = .systemFont(ofSize: 14)
```

### Apply attributes to ranges
```swift
let range = text.range(of: "Styled")!
text[range].underlineStyle = .single
text[range].underlineColor = .blue
```

## Alignment and writing direction
```swift
var paragraph = AttributedString("Centered text")
paragraph.alignment = .center

var rtl = AttributedString("Hello عربي")
rtl.writingDirection = .rightToLeft
```

## Line height
```swift
var multiline = AttributedString("Line one\nLine two")
multiline.lineHeight = .exact(points: 32)
multiline.lineHeight = .multiple(factor: 2.0)
multiline.lineHeight = .loose
```

## Editing and selection
```swift
var text = AttributedString("Here is my dog")
var selection = AttributedTextSelection(range: text.range(of: "dog")!)
text.replaceSelection(&selection, withCharacters: "cat")
```

## Discontiguous selection
```swift
let text = AttributedString("Select multiple parts of this text")
let range1 = text.range(of: "Select")!
let range2 = text.range(of: "text")!
let rangeSet = RangeSet([range1, range2])
var substring = text[rangeSet]
substring.backgroundColor = .yellow
```

## SwiftUI integration
```swift
Text(AttributedString("Styled text in SwiftUI"))
```

```swift
struct CommentEditor: View {
    @Binding var commentText: AttributedString

    var body: some View {
        TextEditor(text: $commentText)
    }
}
```

## References
- https://developer.apple.com/documentation/Foundation/AttributedString
- https://developer.apple.com/documentation/Foundation/AttributedString/TextAlignment
- https://developer.apple.com/documentation/Foundation/AttributedString/LineHeight
- https://developer.apple.com/documentation/Foundation/DiscontiguousAttributedSubstring
