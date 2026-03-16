---
type: moc
name: mobile-native
description: "Skills for iOS/macOS native app development — Xcode scaffolding, Makefile tooling, and Apple platform workflows."
covers:
  - ios
  - macos
  - xcode
  - apple-platforms
---

# Mobile & Native

> Skills for iOS/macOS native app development: Xcode scaffolding, Makefile tooling, and Apple platform workflows.

## Table of Contents
- [App Scaffolding](#app-scaffolding)
- [Build Tooling](#build-tooling)

---

## App Scaffolding

- [[apple-app-creator]] — Orchestrate iOS/macOS app scaffolding with XcodeGen and optionally install xcode-makefiles and simple-tasks via a guided wizard.

## Build Tooling

- [[xcode-makefiles]] — Install strict Xcode Makefile tooling for iOS/macOS projects: build/run/test scripts with AGENT_NAME-based per-agent isolation under `build/`.

## macOS Automation

- [[atlas]] — AppleScript control for the ChatGPT Atlas desktop app on macOS: tabs, bookmarks, and history.
- [[process-watch]] — Analyze system processes and resource usage on macOS to diagnose runaway CPU/memory/IO.

---

## Pipelines

- New iOS app: [[apple-app-creator]] → [[xcode-makefiles]] → [[test-driven-development]].

## Cross-links

- Testing and TDD? See [[agent-ops]].
- Topic maps: [[agent-ops]] | [[backend-platform]] | [[product-strategy]]
