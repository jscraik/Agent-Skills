# SwiftUI WebKit Integration

## Overview
Use this reference when embedding web content in SwiftUI using WebKit's `WebView` and `WebPage`.

## WebView Basics
```swift
import SwiftUI
import WebKit

struct ContentView: View {
    var body: some View {
        WebView(url: URL(string: "https://www.apple.com"))
            .frame(height: 400)
    }
}
```

### Toggling URLs
```swift
struct ContentView: View {
    @State private var toggle = false

    private var url: URL? {
        toggle ? URL(string: "https://www.webkit.org") : URL(string: "https://www.swift.org")
    }

    var body: some View {
        WebView(url: url)
            .toolbar {
                Button(toggle ? "Show Swift" : "Show WebKit",
                       systemImage: toggle ? "swift" : "network") {
                    toggle.toggle()
                }
            }
    }
}
```

### WebView with WebPage
```swift
struct ContentView: View {
    @State private var page = WebPage()

    var body: some View {
        NavigationStack {
            WebView(page)
                .navigationTitle(page.title)
        }
        .onAppear {
            if let url = URL(string: "https://www.apple.com") {
                let _ = page.load(URLRequest(url: url))
            }
        }
    }
}
```

### Text search
```swift
WebView(url: URL(string: "https://www.apple.com"))
    .frame(height: 400)
    .findNavigator(isPresented: $searchVisible)
```

## WebPage Configuration
```swift
var configuration = WebPage.Configuration()
configuration.loadsSubresources = true
configuration.defaultNavigationPreferences.allowsContentJavaScript = true
configuration.websiteDataStore = .default()

let page = WebPage(configuration: configuration)
```

## Navigation Management
```swift
let navigationID = page.load(URLRequest(url: url))
let _ = page.reload(fromOrigin: false)
page.stopLoading()

let canGoBack = !page.backForwardList.backList.isEmpty
let canGoForward = !page.backForwardList.forwardList.isEmpty
```

## JavaScript Interaction
```swift
let title = try await page.callJavaScript("document.title")
```

```swift
let script = """
function findElement(selector) {
    return document.querySelector(selector)?.textContent;
}
return findElement(selector);
"""

let result = try await page.callJavaScript(script, arguments: ["selector": ".main-content h1"])
```

## Customization
```swift
WebView(url: url)
    .webViewBackForwardNavigationGestures(.disabled)
    .webViewMagnificationGestures(.enabled)
    .webViewLinkPreviews(.disabled)
    .webViewTextSelection(.enabled)
    .webViewContentBackground(.color(.systemBackground))
```

## Advanced Features
```swift
let image = try await page.snapshot(WKSnapshotConfiguration())
let pdfData = try await page.pdf(configuration: WKPDFConfiguration())
let archive = try await page.webArchiveData()
```

## References
- https://developer.apple.com/documentation/WebKit/webkit-for-swiftui
- https://developer.apple.com/documentation/WebKit/WebView-swift.struct
- https://developer.apple.com/documentation/WebKit/WebPage
- https://developer.apple.com/documentation/WebKit/WebPage#Executing-JavaScript
- https://developer.apple.com/documentation/WebKit/webkit-for-swiftui#Managing-navigation-between-webpages
