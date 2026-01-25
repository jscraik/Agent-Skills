# Component Spec (template)

> Use this for every new UI component or major refactor.
> Treat it as a contract between design intent and coded behavior.

## Name
- **Component name**:
- **Owner / area**:
- **Related screens/flows**:

## Purpose
- What problem does this component solve?
- When should it *not* be used?

## Anatomy & structure
- Regions/slots:
  - `root`
  - `icon` (optional)
  - `label`
  - `description` (optional)
  - `actions` (optional)
- Content rules (max lengths, wrapping behavior)

## Behavior & states
List *all* states with expected UI changes:

- default
- hover
- focus-visible
- active/pressed
- disabled
- loading
- success (if applicable)
- error (if applicable)

### Keyboard & focus
- Tab/Shift+Tab behavior:
- Arrow keys (if relevant):
- Enter/Space behavior:
- Focus trap (dialogs/menus) details:
- Initial focus target:
- Escape behavior:

## Implementation plan (React + Radix + Tailwind v4)
- **Radix primitive(s)** used:
- **Composition pattern**:
  - `asChild` usage (if needed)
  - controlled vs uncontrolled state
- **Styling strategy**:
  - tokens used (CSS variables / `@theme`)
  - state styling via `data-*` attributes
  - variants (size, intent, density, etc.)
- **Accessibility**:
  - labels / aria-* usage
  - announcements (toasts/live regions) if applicable
- **Motion**:
  - enter/exit
  - feedback (press/hover)
  - reduced-motion fallback

## API
### Props
| prop | type | default | notes |
|------|------|---------|------|

### Events
- onChange:
- onOpenChange:
- etc.

## Visual QA checklist
- Spacing consistent with tokens
- Focus ring visible on all backgrounds
- Text truncation/wrapping rules validated
- High-contrast mode (if relevant)
- Reduced motion validated

## Test plan
- Unit/integration tests (if applicable)
- Storybook stories:
  - default
  - variants
  - edge states
- Argos snapshots:
  - baseline
  - dark mode (if applicable)
  - dense/compact (if applicable)

## Notes / rationale
Why this approach (tradeoffs)?
