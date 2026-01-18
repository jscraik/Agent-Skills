# AppKit Liquid Glass (NSGlassEffectView)

## Scope
Use when the user asks for Liquid Glass in AppKit/macOS. Verify API names and availability in the current SDK before implementation.

## Core Classes
- `NSGlassEffectView`: Primary view for Liquid Glass in AppKit.
- `NSGlassEffectContainerView`: Merges nearby glass views and improves performance.

## Basic Setup
```swift
import AppKit

final class MyViewController: NSViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let glassView = NSGlassEffectView(frame: NSRect(x: 20, y: 20, width: 200, height: 100))

        let label = NSTextField(labelWithString: "Liquid Glass")
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        label.textColor = .white

        glassView.contentView = label

        if let contentView = glassView.contentView {
            NSLayoutConstraint.activate([
                label.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
                label.centerYAnchor.constraint(equalTo: contentView.centerYAnchor)
            ])
        }

        view.addSubview(glassView)
    }
}
```

## Common Customization
### Corner Radius
```swift
let glassView = NSGlassEffectView(frame: NSRect(x: 20, y: 20, width: 200, height: 100))
glassView.cornerRadius = 16.0
```

### Tint Color
```swift
let glassView = NSGlassEffectView(frame: NSRect(x: 20, y: 20, width: 200, height: 100))
glassView.tintColor = NSColor.systemBlue.withAlphaComponent(0.3)
```

## Container Usage
```swift
func setupGlassContainer(in view: NSView) {
    let containerView = NSGlassEffectContainerView(frame: NSRect(x: 20, y: 20, width: 400, height: 200))
    containerView.spacing = 40.0

    let contentView = NSView(frame: containerView.bounds)
    contentView.autoresizingMask = [.width, .height]
    containerView.contentView = contentView

    let glassView1 = NSGlassEffectView(frame: NSRect(x: 20, y: 50, width: 150, height: 100))
    glassView1.cornerRadius = 12.0
    let label1 = NSTextField(labelWithString: "Glass View 1")
    label1.translatesAutoresizingMaskIntoConstraints = false
    glassView1.contentView = label1

    let glassView2 = NSGlassEffectView(frame: NSRect(x: 190, y: 50, width: 150, height: 100))
    glassView2.cornerRadius = 12.0
    let label2 = NSTextField(labelWithString: "Glass View 2")
    label2.translatesAutoresizingMaskIntoConstraints = false
    glassView2.contentView = label2

    contentView.addSubview(glassView1)
    contentView.addSubview(glassView2)

    if let contentView1 = glassView1.contentView, let contentView2 = glassView2.contentView {
        NSLayoutConstraint.activate([
            label1.centerXAnchor.constraint(equalTo: contentView1.centerXAnchor),
            label1.centerYAnchor.constraint(equalTo: contentView1.centerYAnchor),
            label2.centerXAnchor.constraint(equalTo: contentView2.centerXAnchor),
            label2.centerYAnchor.constraint(equalTo: contentView2.centerYAnchor)
        ])
    }

    view.addSubview(containerView)
}
```

## Interactive Effects
```swift
final class InteractiveGlassView: NSGlassEffectView {
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        setupTracking()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupTracking()
    }

    private func setupTracking() {
        let options: NSTrackingArea.Options = [.mouseEnteredAndExited, .mouseMoved, .activeInActiveApp]
        let trackingArea = NSTrackingArea(rect: bounds, options: options, owner: self, userInfo: nil)
        addTrackingArea(trackingArea)
    }

    override func mouseEntered(with event: NSEvent) {
        super.mouseEntered(with: event)
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.2
            animator().tintColor = NSColor.systemBlue.withAlphaComponent(0.2)
        }
    }

    override func mouseExited(with event: NSEvent) {
        super.mouseExited(with: event)
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.2
            animator().tintColor = nil
        }
    }
}
```

## Animation in Containers
```swift
NSAnimationContext.runAnimationGroup { context in
    context.duration = 0.5
    context.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
    glassView2.animator().frame = NSRect(x: 100, y: 50, width: 150, height: 100)
}
```

## Toolbar Glass (Window Chrome Area)
```swift
func setupToolbarWithGlassEffect() {
    let window = NSWindow(
        contentRect: NSRect(x: 0, y: 0, width: 800, height: 600),
        styleMask: [.titled, .closable, .miniaturizable, .resizable],
        backing: .buffered,
        defer: false
    )

    let toolbar = NSToolbar(identifier: "GlassToolbar")
    toolbar.displayMode = .iconAndLabel
    toolbar.delegate = self
    window.toolbar = toolbar

    let toolbarHeight: CGFloat = 50.0
    let glassView = NSGlassEffectView(
        frame: NSRect(
            x: 0,
            y: window.contentView!.bounds.height - toolbarHeight,
            width: window.contentView!.bounds.width,
            height: toolbarHeight
        )
    )
    glassView.autoresizingMask = [.width, .minYMargin]
    window.contentView?.addSubview(glassView)

    window.makeKeyAndOrderFront(nil)
}
```

## Best Practices
- Prefer `NSGlassEffectContainerView` when multiple glass views are nearby.
- Limit the number of glass effects to avoid GPU overuse.
- Use subtle `tintColor` for state and hierarchy.
- Keep shapes consistent across related elements.
- Animate position changes to trigger fluid merges.

## References
- AppKit: NSGlassEffectView
- AppKit: NSGlassEffectContainerView
- SwiftUI: Applying Liquid Glass to custom views
- SwiftUI: Landmarks - Building an app with Liquid Glass
