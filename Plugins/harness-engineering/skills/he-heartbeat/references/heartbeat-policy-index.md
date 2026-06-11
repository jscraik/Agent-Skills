# Heartbeat Policy Index

## Preserved Compact Entrypoint Lines

These lines were moved out of the active `SKILL.md` body during compact-entrypoint tightening and remain here for progressive-disclosure auditability:

```text
description: "Create or repair Harness Engineering thread heartbeats when monitoring, wakeups, until-green loops, scheduled live checks, or follow-through automation must re-enter the correct HE stage."
Wake the thread with fresh state, not stale memory. Scheduling keeps cadence; the HE lifecycle still owns the work.
## Anti-patterns
- Do not create duplicate heartbeats for the same target and stop rule.
- Do not use a heartbeat prompt or `/goal` objective as a replacement for Linear, PR, validation, or lifecycle exit evidence.
- Do not schedule unattended destructive actions, merges, deploys, or tracker closure without explicit approval.
- "Wake this thread every 30 minutes until PR #68 is green, then route to `he-work` for the merge handoff."
- "Monitor the deployment check for JSC-246 and stop once the live health query passes twice."
```
