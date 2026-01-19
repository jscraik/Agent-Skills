# SwiftUI New Toolbar Features

## Overview
SwiftUI adds customizable toolbars, enhanced search integration, new placement options, and transition effects across iOS, iPadOS, and macOS. Use this reference when building or refining toolbars.

## Customizable Toolbars

### Customizable toolbar with IDs
```swift
ContentView()
    .toolbar(id: "main-toolbar") {
        ToolbarItem(id: "tag") { TagButton() }
        ToolbarItem(id: "share") { ShareButton() }
        ToolbarSpacer(.fixed)
        ToolbarItem(id: "more") { MoreButton() }
    }
```

### Toolbar spacers
```swift
ToolbarSpacer(.fixed)
ToolbarSpacer(.flexible)
```

## Enhanced Search Integration

### Search toolbar behavior
```swift
@State private var searchText = ""

NavigationStack {
    RecipeList()
        .searchable($searchText)
        .searchToolbarBehavior(.minimize)
}
```

### Repositioning search items
```swift
NavigationSplitView {
    AllCalendarsView()
} detail: {
    SelectedCalendarView()
        .searchable($query)
        .toolbar {
            ToolbarItem(placement: .bottomBar) { CalendarPicker() }
            ToolbarItem(placement: .bottomBar) { Invites() }
            DefaultToolbarItem(kind: .search, placement: .bottomBar)
            ToolbarSpacer(placement: .bottomBar)
            ToolbarItem(placement: .bottomBar) { NewEventButton() }
        }
}
```

## New Toolbar Item Placements

### Large subtitle placement
```swift
NavigationStack {
    DetailView()
        .navigationTitle("Title")
        .navigationSubtitle("Subtitle")
        .toolbar {
            ToolbarItem(placement: .largeSubtitle) {
                CustomLargeNavigationSubtitle()
            }
        }
}
```

## Visual Effects and Transitions

### Matched transition source
```swift
struct ContentView: View {
    @State private var isPresented = false
    @Namespace private var namespace

    var body: some View {
        NavigationStack {
            DetailView()
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Show Sheet", systemImage: "globe") {
                            isPresented = true
                        }
                    }
                    .matchedTransitionSource(id: "world", in: namespace)
                }
                .sheet(isPresented: $isPresented) {
                    SheetView()
                        .navigationTransition(.zoom(sourceID: "world", in: namespace))
                }
        }
    }
}
```

### Shared background visibility
```swift
ContentView()
    .toolbar(id: "main") {
        ToolbarItem(id: "build-status", placement: .principal) {
            BuildStatus()
        }
        .sharedBackgroundVisibility(.hidden)
    }
```

## System-Defined Toolbar Items
```swift
.toolbar {
    DefaultToolbarItem(kind: .search, placement: .bottomBar)
    DefaultToolbarItem(kind: .sidebar, placement: .navigationBarLeading)
}
```

## Platform Notes
- iOS/iPadOS: bottomBar placement is especially useful on phones; `.searchToolbarBehavior(.minimize)` saves space.
- macOS: customizable toolbars are expected in productivity apps; use spacers for grouping.

## Best Practices
- Use meaningful IDs for customizable items.
- Group related actions with spacers.
- Prefer system-defined items where appropriate.
- Test customization and placement across device classes.
- Use transitions sparingly to avoid distraction.

## References
- https://developer.apple.com/documentation/SwiftUI/SearchToolbarBehavior
- https://developer.apple.com/documentation/SwiftUI/ToolbarSpacer
- https://developer.apple.com/documentation/SwiftUI/DefaultToolbarItem
- https://developer.apple.com/documentation/SwiftUI/ToolbarItemPlacement
- https://developer.apple.com/documentation/SwiftUI/CustomizableToolbarContent
