# Error States

## Intent
Explain failures and provide a path to recovery.

## Minimal pattern
- Provide a short summary and a retry action.
- Include context when safe (status, cause).

## Pitfalls
- Avoid exposing raw stack traces in UI.

## Accessibility
- Use aria-live for critical error messaging.
