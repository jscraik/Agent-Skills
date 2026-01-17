# Swift.org Documentation (Backend-Oriented Summary)

## What to use and when
- **Language reference (TSPL)**: Authoritative Swift language guide for syntax, semantics, and reference details.
- **API Design Guidelines**: Naming and API surface conventions for Swift-first libraries/SDKs.
- **Standard Library + Core Libraries**: Baseline types and cross-platform libraries that shape API choices and data models.
- **Swift Package Manager (SwiftPM)**: Primary package and build system for Swift services, libraries, and tools.
- **REPL & Debugger (LLDB)**: Swift REPL and debugging environment.
- **Swift on Server**: Swift as a backend/server language (deployment and server ecosystem context).
- **DocC**: Documentation compiler for Swift packages and frameworks.
- **Concurrency checking**: Guidance for enabling complete concurrency checks when targeting Swift 6.
- **OpenAPI for Swift.org APIs**: Example of OpenAPI usage and Swift client generation.

## Backend design implications
- Use **Swift API Design Guidelines** when exposing Swift SDKs or server-side libraries.
- Prefer **SwiftPM** for package layout, dependencies, and modular boundaries.
- Use **DocC** for SDK and service documentation that ships with packages.
- If backend services are in Swift, align API/client generation with **OpenAPI** where applicable.
- Account for **Swift 6 concurrency** checks in CI for server-side Swift codebases.

## Pointers (official)
- Swift.org documentation hub, TSPL, and article index.
- Swift.org OpenAPI docs for API modeling and client generation.
