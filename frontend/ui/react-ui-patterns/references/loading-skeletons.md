# Loading and Skeletons

## Intent
Communicate loading state without causing layout shifts.

## Minimal pattern
- Use skeletons for known layouts.
- Use spinners for unknown durations.

## Pitfalls
- Avoid indefinite skeletons without fallback.

## Accessibility
- Provide aria-busy and loading text where needed.
