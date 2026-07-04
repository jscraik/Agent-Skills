# Rust and Tauri Standards

## Table of Contents
- [Rust & Tauri Standards](#rust--tauri-standards)

## Rust & Tauri Standards

### Formatting (Required)

* **rustfmt** is the formatter of record.
* Formatting MUST be enforced in CI (`cargo fmt --check`).
* Formatting config is shared repo-wide.

### Linting (Required)

* **Clippy** is required.
* Allow-lists MUST include rule ID, reason, tracking ticket, and expiry (date) or ADR reference per waiver model.

### Concurrency (Required)

* Implementations SHOULD prefer structured concurrency (async/await + explicit cancellation).
* Shared mutable state MUST be isolated (channels, actors, or controlled ownership).
* `unsafe` MUST NOT be used unless:

  * ADR exists,
  * mitigation is documented,
  * concurrency test exists.

### Tauri

* Commands MUST validate inputs and return typed errors.
* Tauri v2 capabilities and permissions MUST be treated as the app security boundary:

  * grant only the commands and plugin permissions each window needs,
  * keep filesystem, shell, dialog, network, and OS integration permissions least-privilege,
  * review capability JSON changes like code, with explicit rationale for any broad allow rule.

* UI-facing state MUST be deterministic and testable.
* Implementations MUST NOT block the main thread; heavy work MUST be moved to worker tasks.
* Frontend-to-Rust command payloads MUST be schema-validated at the boundary before touching filesystem, process, network, credential, or OS APIs.

### Testing

* Unit tests MUST run in CI (`cargo test`).
* Security-sensitive Tauri permission or command changes SHOULD include a focused test, fixture, or manual verification note that exercises denied and allowed paths.
* UI/desktop end-to-end tests SHOULD be separated from unit tests in CI.

---
