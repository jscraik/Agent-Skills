# Swift InlineArray and Span

## Overview
Use this reference when performance-critical Swift code benefits from fixed-size inline storage (InlineArray) or safe contiguous memory access (Span).

## InlineArray
```swift
let a: InlineArray<4, Int> = [1, 2, 4, 8]
let b: InlineArray<_, Int> = [1, 2, 4, 8]
let c: InlineArray<4, _> = [1, 2, 4, 8]
let d: InlineArray = [1, 2, 4, 8]
```

```swift
var array: InlineArray<3, Int> = [1, 2, 3]
array[0] = 4
```

Notes:
- Fixed size, no append/remove.
- Inline storage, no heap allocation.
- Eager copy, no CoW.

## Span
```swift
let array = [1, 2, 3, 4]
let span = array.span

var result = 0
for i in 0..<span.count {
    result += span[i]
}
```

Safety constraints:
- Span cannot escape scope.
- Span cannot be captured by closures.
- Mutating the original container invalidates the span.

## References
- https://developer.apple.com/documentation/Swift/InlineArray
- https://developer.apple.com/documentation/Swift/Span
- https://developer.apple.com/documentation/swift/array/span
- https://developer.apple.com/documentation/swift/array/mutablespan
- https://developer.apple.com/videos/play/wwdc2025/245/
- https://developer.apple.com/videos/play/wwdc2025/312/
