# Web Standards

## Table of Contents
- [Scope](#scope)
- [React](#react)
- [Vite](#vite)
- [Tailwind](#tailwind)
- [Storybook](#storybook)
- [Apps SDK UI and chat widgets](#apps-sdk-ui-and-chat-widgets)
- [Accessibility](#accessibility)
- [Enforcement](#enforcement)

## Scope
- This module covers web application standards for React, Vite, Tailwind, Storybook, Apps SDK UI, and chat widget surfaces.

## React
- Web surfaces MUST use semantic HTML first; ARIA SHOULD be added only where semantics are insufficient.
- Hooks MUST follow Rules of Hooks and keep side effects in effect hooks.
- Implementations SHOULD prefer controlled inputs unless uncontrolled behavior is intentional and documented.
- State SHOULD stay local by default; global mutable state drift MUST be avoided.

## Vite
- Environment variable usage MUST be explicit, typed, and documented.
- Secrets MUST NOT be exposed in client bundles.
- Mode-dependent runtime behavior changes MUST NOT ship without explicit test coverage.

## Tailwind
- Utility usage MUST remain consistent with repo formatting/lint policy.
- Implementations SHOULD prefer design tokens over one-off magic values.
- Conditional class composition SHOULD remain readable.
- Visible focus states MUST be present and color-only status communication MUST be avoided.

## Storybook
- Stories MUST use deterministic fixtures and MUST avoid hidden network calls.
- Interaction and accessibility checks SHOULD stay enabled where applicable.
- Storybook SHOULD be treated as behavior and visual contract documentation for reusable UI components.

## Apps SDK UI and chat widgets
- Apps SDK UI and chat widget work MUST use retrieval-led reasoning from current official/library docs before implementation.
- Bridge contracts, message schemas, and component metadata MUST be explicit and tested at the boundary where host and widget exchange data.
- Widget UI MUST degrade cleanly when host capabilities, auth state, network access, or embedded resources are unavailable.
- Browser-targeted secrets MUST remain server-side; client bundles MUST receive only scoped, non-sensitive configuration.

## Accessibility
- Interactive web surfaces MUST target WCAG 2.2 AA.
- Full keyboard operation, visible focus, and screen-reader-meaningful labels MUST be present.

## Enforcement
- Web changes MUST pass:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - `pnpm audit`
  - `pnpm check`
  - `bash scripts/validate-codestyle.sh`
  - `bash scripts/verify-work.sh --fast`
- For component-system work, include Storybook/accessibility checks when configured in the touched project.
- All waivers require documented metadata with rule ID or section, reason, tracking ticket, and expiry or ADR reference.
