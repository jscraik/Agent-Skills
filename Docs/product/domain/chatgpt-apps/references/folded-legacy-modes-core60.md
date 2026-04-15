# Folded Legacy Modes (Core60)

Destination skill: `product/domain/chatgpt-apps`

This file captures legacy capabilities migrated from retired skills.

## `agentation-integration`
- Source skill: `frontend/tools/agentation`
- Legacy description: Use when a user wants to install, verify, or troubleshoot Agentation in React/Next.js/Vite/Tauri apps; this skill validates toolbar wiring, MCP health, live webhook delivery, and automation modes (self-driving autopilot + critique mode) with end-to-end submit verification.
- Fold rationale: Both cover Apps SDK wiring, tool invocation paths, and submit flow validation.
- Legacy section map:
  - Usage triggers
  - Requirements
  - Deliverables
  - Philosophy
  - Workflow
  - Encouraging variation

## `production-gate`
- Source skill: `product/domain/chatgpt-apps-production-checklist`
- Legacy description: Turn ChatGPT Apps implementation work into a production-ready checklist with concrete tasks, tests, widget changes, and tool-result patterns mapped by priority (P0/P1/P2). Use when designing or hardening Apps SDK products for shipping; do not use for generic web-only apps, static code review, or non-ChatGPT integration planning.
- Fold rationale: Checklist work is a readiness phase of Apps implementation.
- Legacy section map:
  - Scope and triggers
  - Requirements and context
  - Deliverables
  - Philosophy
  - Encouraging variation
  - Workflow
