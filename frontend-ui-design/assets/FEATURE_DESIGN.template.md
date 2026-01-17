# FEATURE_DESIGN: [Feature Name]

## 0) Summary
- Goal:
- Primary users:
- Critical path (<=7 steps):
- Non-goals:

## 1) User journeys
### 1.1 Happy path
1)
2)
...

### 1.2 Failure/edge paths
- Case A:
- Case B:

## 2) Information architecture + navigation
- Entry points:
- Navigation model:
- Back/escape behavior (widget + iOS + macOS):

## 3) Screens and states (token-referenced)
For each screen/state:
- Layout (token refs + px/rem + pt)
- Components used (React + Swift names)
- States: default / loading / empty / error / offline / permission-denied
- Error prevention and recovery
- Feedback timing (<=100ms)

## 4) Interaction patterns
- Inputs + validation
- Primary/secondary actions (widget inline: <=2 primary)
- Undo/cancel
- Destructive actions: confirmation

## 5) Responsive/adaptive behavior
- Breakpoints (px):
- Widget (maxHeight + displayMode):
- iOS size class rules:
- macOS window resizing rules:

## 6) Motion
- Animations (tokenized duration/easing)
- Reduced motion alternatives (required for each)

## 7) Accessibility map (WCAG 2.2 AA + Apple AX)
### 7.1 Semantics and labels
- ARIA intent + Apple equivalents
- Accessible names/labels
- Hints only if needed

### 7.2 Focus order
State: Default
1)
2)
...

State: Error
1)
2)
...

### 7.3 Keyboard + shortcuts
- Tab order:
- Activation keys:
- Escape/back:
- Shortcuts (macOS):

### 7.4 Contrast + accommodations
- Contrast checks per state:
- Reduce transparency handling:
- Increased contrast handling:
- Dynamic Type expectations:

## 8) Acceptance criteria
- Task success >=95% (measurement plan)
- WCAG 2.2 AA verification steps
- Performance: <=100ms feedback evidence
- Keyboard completeness evidence
- Contrast evidence for all states

## 9) Implementation guide
### 9.1 React (Apps SDK widget)
- toolOutput usage
- widgetState usage
- callTool wiring
- requestDisplayMode usage

### 9.2 SwiftUI
(snippets)

### 9.3 UIKit / AppKit (if in scope)
(snippets)

## 10) Test plan (step-by-step)
- VoiceOver / Switch Control:
- Dynamic Type:
- Reduce Motion:
- Reduce Transparency:
- Keyboard nav:
- AX Inspector:
- Regression checklist:
