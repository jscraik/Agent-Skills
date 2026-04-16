# Folded Legacy Modes (Core60)

Destination skill: `Skills/systematic-debugging`

This file captures legacy capabilities migrated from retired skills.

## `recent-commit-lens`
- Source skill: `Skills/recent-code-bugfix`
- Legacy description: Diagnose and fix a bug introduced by the current author within the last week. Use when a user asks for a proactive bugfix from their recent commits, asks to triage/fix issues caused by their own changes, or leaves the prompt empty. Don’t use when failures are unrelated to the author’s recent edits or there is no local git history. Outputs: root-cause summary, minimal fix, and targeted verification evidence. Success: root cause maps directly to the author’s own recent changes.
- Fold rationale: Recent-code bugfix is a scoping lens over systematic debugging, not a separate method.
- Legacy section map:
  - Table of Contents
  - When to use
  - Inputs
  - Outputs
  - Reference map
  - Constraints and safety
