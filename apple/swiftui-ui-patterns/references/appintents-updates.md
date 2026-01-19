# AppIntents Updates

## Overview
Use this reference when you need AppIntents updates, Apple Intelligence integrations, new intent modes, convenience macros, snippets, or Spotlight indexing patterns.

## New System Integrations

### Visual Intelligence integration
```swift
@UnionValue
enum VisualSearchResult {
    case landmark(LandmarkEntity)
    case collection(CollectionEntity)
}

struct LandmarkIntentValueQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [VisualSearchResult] {
        // Map visual input to app entities
    }
}

struct OpenLandmarkIntent: OpenIntent { /* ... */ }
struct OpenCollectionIntent: OpenIntent { /* ... */ }
```

### Onscreen entities
```swift
struct LandmarkDetailView: View {
    let landmark: LandmarkEntity

    var body: some View {
        Group { /* View content */ }
            .userActivity("com.landmarks.ViewingLandmark") { activity in
                activity.title = "Viewing \(landmark.name)"
                activity.appEntityIdentifier = EntityIdentifier(for: landmark)
            }
    }
}
```

## User Experience Refinements

### Intent modes
```swift
struct GetCrowdStatusIntent: AppIntent {
    static let supportedModes: IntentModes = [.background, .foreground(.dynamic)]

    func perform() async throws -> some ReturnsValue<Int> & ProvidesDialog {
        guard await modelData.isOpen(landmark) else {
            return .result(value: 0, dialog: "The landmark is currently closed.")
        }

        if systemContext.currentMode.canContinueInForeground {
            do {
                try await continueInForeground(alwaysConfirm: false)
                await navigator.navigateToCrowdStatus(landmark)
            } catch {
                // Foreground request denied
            }
        }

        let status = await modelData.getCrowdStatus(landmark)
        return .result(value: status, dialog: "Current crowd level: \(status)")
    }
}
```

Modes:
- `.background`
- `.foreground(.immediate)`
- `.foreground(.dynamic)`
- `.foreground(.deferred)`

### Continue in foreground
```swift
try await continueInForeground(alwaysConfirm: false)

throw needsToContinueInForegroundError(
    IntentDialog("Need to open app to complete this action"),
    alwaysConfirm: true
)
```

### Multiple choice API
```swift
let options = [
    IntentChoiceOption(title: "Option 1", subtitle: "Description 1"),
    IntentChoiceOption(title: "Option 2", subtitle: "Description 2"),
    IntentChoiceOption.cancel(title: "Not now")
]

let choice = try await requestChoice(
    between: options,
    dialog: IntentDialog("Please select an option")
)

switch choice.id {
case options[0].id:
    break
case options[1].id:
    break
default:
    break
}
```

## Convenience APIs

### @ComputedProperty
```swift
struct SettingsEntity: UniqueAppEntity {
    @ComputedProperty
    var defaultPlace: PlaceDescriptor {
        UserDefaults.standard.defaultPlace
    }

    init() { }
}
```

### @DeferredProperty
```swift
struct LandmarkEntity: IndexedEntity {
    @DeferredProperty
    var crowdStatus: Int {
        get async throws {
            await modelData.getCrowdStatus(self)
        }
    }
}
```

### Swift Package support
```swift
public struct LandmarksKitPackage: AppIntentsPackage { }

struct LandmarksPackage: AppIntentsPackage {
    static var includedPackages: [any AppIntentsPackage.Type] {
        [LandmarksKitPackage.self]
    }
}
```

## Interactive snippets

### Static snippet
```swift
func perform() async throws -> some IntentResult {
    return .result(view: Text("Some example text.").font(.title))
}
```

### Interactive snippet
```swift
func perform() async throws -> some IntentResult {
    let landmark = await findNearestLandmark()
    return .result(
        value: landmark,
        opensIntent: OpenLandmarkIntent(landmark: landmark),
        snippetIntent: LandmarkSnippetIntent(landmark: landmark)
    )
}

struct LandmarkSnippetIntent: SnippetIntent {
    @Parameter var landmark: LandmarkEntity

    var snippet: some View {
        VStack {
            Text(landmark.name).font(.headline)
            Text(landmark.description).font(.body)

            HStack {
                Button("Add to Favorites") { }
                Button("Search Tickets") { }
            }
        }
        .padding()
    }
}
```

## Spotlight integration
```swift
struct OpenLandmarkIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Landmark"

    @Parameter(title: "Landmark", requestValueDialog: "Which landmark?")
    var target: LandmarkEntity

    func perform() async throws -> some IntentResult {
        return .result()
    }
}
```

```swift
struct LandmarkEntity: AppEntity, IndexedEntity {
    static var typeDisplayRepresentation = TypeDisplayRepresentation(
        name: "Landmark",
        systemImage: "mountain.2"
    )

    var id: String
    var name: String
    var description: String
    var coordinate: CLLocationCoordinate2D
    var activities: [String]
    var regionDescription: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: "\(regionDescription)",
            image: .init(systemName: "mountain.2")
        )
    }

    var searchableAttributes: CSSearchableItemAttributeSet {
        let attributes = CSSearchableItemAttributeSet()
        attributes.title = name
        attributes.namedLocation = regionDescription
        attributes.keywords = activities
        attributes.latitude = NSNumber(value: coordinate.latitude)
        attributes.longitude = NSNumber(value: coordinate.longitude)
        attributes.supportsNavigation = true
        return attributes
    }
}
```

```swift
func indexLandmarks() async {
    let landmarks = await fetchLandmarks()
    do {
        try await CSSearchableIndex.default().indexAppEntities(
            landmarks,
            priority: .normal
        )
    } catch {
        print("Failed to index landmarks: \(error)")
    }
}
```

## References
- https://developer.apple.com/documentation/Updates/AppIntents
- https://developer.apple.com/documentation/AppIntents/adopting-app-intents-to-support-system-experiences
- https://developer.apple.com/documentation/AppIntents/making-app-entities-available-in-spotlight
- https://developer.apple.com/documentation/AppIntents/displaying-static-and-interactive-snippets
- https://developer.apple.com/videos/play/wwdc2025/275
- https://developer.apple.com/videos/play/wwdc2025/244
