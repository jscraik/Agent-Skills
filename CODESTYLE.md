# CODESTYLE.md

## Purpose

This is the codestyle front door for Agent Skills Kit. Apply standards for the
changed surface: read the common foundations, then only the matching modules.
The linked rules remain mandatory in their scope; this routing does not waive
security, validation, signing, accessibility, or evidence requirements.

## Toolchain Authority

Use the current repository `.mise.toml`, package manifests, lockfiles, and
applicable `AGENTS.md` files. The root has no package-manager install step.
Use `./bin/ask` and the locked Infrastructure Python wrapper as documented in
[AGENTS.md](/AGENTS.md). Technology-specific examples do not override those
executable command contracts. Security advisories override baseline versions.

## Choose The Relevant Standards

| Changed surface | Read |
| --- | --- |
| Any implementation or instruction change | [Common foundations](/Docs/reference/codestyle/foundations.md) |
| JavaScript, TypeScript, React, Vite, Tailwind, Storybook | [JavaScript and UI](/Docs/reference/codestyle/javascript-ui.md) |
| Rust or Tauri | [Rust and Tauri](/Docs/reference/codestyle/rust-tauri.md) |
| Documentation, YAML, TOML, JSON, naming, commits, releases, lockfiles | [Docs, config, and release](/Docs/reference/codestyle/docs-config-release.md) |
| Quality gates, security, accessibility, observability, resources, external tools | [Quality, security, and operations](/Docs/reference/codestyle/quality-security-ops.md) |
| Governance dates or project-specific overrides | [Appendices and overrides](/Docs/reference/codestyle/appendices.md) |

## Validation Scope

Run the owning check for the changed surface before widening to the repository's
required aggregate gates. A documentation typo does not select unrelated
language or runtime checks. Preserve exact commands and pass, fail, or blocked
outcomes, and keep local, runtime, hosted, and release claims separate.
