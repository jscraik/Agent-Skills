# Folded Legacy Modes (Core60)

Destination skill: `frontend/ui/ui-visual-regression`

This file captures legacy capabilities migrated from retired skills.

## `trace-debug`
- Source skill: `frontend/tools/agent-trace-debug`
- Legacy description: Analyze Agent Trace data flow when AIAttributionPanel shows empty/incorrect trace by tracing expected vs actual shapes across agentTraceStore and API.
- Fold rationale: Visual breakage triage and trace mismatch diagnosis overlap in UI quality workflows.
- Legacy section map:
  - Scope and triggers
  - Required inputs
  - Deliverables
  - Philosophy
  - Guardrails (must follow)
  - Procedure (exact sequence)
  - Report template
  - Common failure patterns
  - Validation
  - Constraints
- Live guidance preserved in destination:
  - consumer -> store -> API tracing order
  - shape-only instrumentation rules
  - first-divergence-point reporting contract
  - no-fix-yet debugging posture unless explicitly requested
