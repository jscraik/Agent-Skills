# Assistive Access (iOS)

## Overview
Use this reference when you need to support Assistive Access in SwiftUI or UIKit apps, or when building simplified interfaces for cognitive accessibility.

## Enable Assistive Access

### Info.plist
```xml
<key>UISupportsAssistiveAccess</key>
<true/>
```

### Full screen support (optional)
```xml
<key>UISupportsFullScreenInAssistiveAccess</key>
<true/>
```

## SwiftUI Assistive Access scene
```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        AssistiveAccess {
            AssistiveAccessContentView()
        }
    }
}
```

```swift
struct AssistiveAccessContentView: View {
    var body: some View {
        NavigationStack {
            List {
                // Simplified controls
            }
            .navigationTitle("My App")
        }
    }
}
```

```swift
#Preview(traits: .assistiveAccess)
AssistiveAccessContentView()
```

## UIKit Assistive Access scene
```swift
class AssistiveAccessSceneDelegate: UIHostingSceneDelegate {
    static var rootScene: some Scene {
        AssistiveAccess {
            AssistiveAccessContentView()
        }
    }
}

@main
class AppDelegate: UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        configurationForConnecting connectingSceneSession: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        let role = connectingSceneSession.role
        let sceneConfiguration = UISceneConfiguration(name: nil, sessionRole: role)
        if role == .windowAssistiveAccessApplication {
            sceneConfiguration.delegateClass = AssistiveAccessSceneDelegate.self
        }
        return sceneConfiguration
    }
}
```

## Runtime detection
```swift
struct MyView: View {
    @Environment(\.accessibilityAssistiveAccessEnabled) var assistiveAccessEnabled

    var body: some View {
        if assistiveAccessEnabled {
            // Assistive Access UI
        } else {
            // Standard UI
        }
    }
}
```

## Navigation icons
```swift
.navigationTitle("My Feature")
.assistiveAccessNavigationIcon(systemImage: "star.fill")
```

## Design principles (summary)
- Distill to core functionality
- Clear, prominent controls
- Multiple representations (text + icons)
- Intuitive navigation paths
- Safe interactions and confirmations

## Testing
- SwiftUI preview: `.assistiveAccess`
- Device testing: Settings > Accessibility > Assistive Access
- Accessibility Inspector for audits

## References
- https://developer.apple.com/documentation/SwiftUI/AssistiveAccess
- https://developer.apple.com/documentation/SwiftUI/View/assistiveAccessNavigationIcon(_:)
- https://developer.apple.com/documentation/SwiftUI/EnvironmentValues/accessibilityAssistiveAccessEnabled
- https://developer.apple.com/videos/play/wwdc2025/238
- https://developer.apple.com/videos/play/wwdc2025/256
