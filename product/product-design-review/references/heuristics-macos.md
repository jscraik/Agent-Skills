# macOS Heuristics and Criteria (Concise)

Use this reference for macOS-specific UX reviews (AppKit/SwiftUI desktop apps).

## Usability Heuristics
- Follow macOS patterns for windows, toolbars, sidebars, and menus.
- Ensure keyboard shortcuts and menu access for primary actions.
- Use familiar selection, drag-and-drop, and context menu behaviors.
- Provide clear status indicators for background or long-running tasks.

## Accessibility (Apple AX + WCAG 2.2 AA oriented)
- Full keyboard access and visible focus ring.
- VoiceOver labels, roles, and hints for custom controls.
- Sufficient contrast and color-independent meaning.
- Support larger text sizes and reflow where possible.
- Respect Reduce Motion and Reduce Transparency settings.

## Content and Microcopy
- Use system terminology and conventional macOS labels.
- Avoid dense, wall-of-text dialogs; break into steps.
- Make destructive actions explicit and confirm.

## Trust and Safety
- Explain permissions and file access clearly.
- Show clear data handling cues for sensitive inputs.

## Performance and Resilience
- Use progress indicators for long operations.
- Handle offline, error, and empty states gracefully.
- Preserve user inputs on failure when possible.
