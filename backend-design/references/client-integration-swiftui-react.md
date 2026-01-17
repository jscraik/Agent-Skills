# Client Integration Notes (SwiftUI + React)

Purpose: Help backend specs align with common SwiftUI and React client wiring patterns found in local skills.

## SwiftUI client expectations
- Use a single app-shell to install global dependencies (auth/session, client, streaming) and keep feature state local.
- Prefer lightweight, closure-based clients for networking so they are easy to stub in previews/tests.
- Keep decode + URL construction inside the client; keep state mutations inside a store.
- Trigger initial loads via `.task` and ensure cancellation is respected.

## React client expectations
- Wire router + providers at the root layout and keep consistent layout shells.
- Keep route maps stable; prefer contract-first API paths and typed clients.
- Centralize auth/data providers and avoid duplicating request state across routes.

## Backend API implications
- Provide consistent error schemas and pagination for predictable client-side handling.
- Keep auth flows explicit (token/session refresh), and document request/response shapes for codegen.
- Avoid breaking response shapes without versioning; both SwiftUI and React patterns favor stable contracts.

