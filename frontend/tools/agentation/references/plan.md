# Agentation skill update plan

## Objective
Upgrade the `agentation` skill so it reliably handles real-world setup issues observed in desktop/web projects:
- MCP vs webhook transport confusion (often called "websocket issues").
- Local listener port collisions (`EADDRINUSE`).
- Submit-driven automation and timeout-safe completion semantics.

## Task graph

- **T1 (depends_on: [])** — Draft new skill workflow for multi-framework support (Next.js + Vite/Tauri) and transport triage.
- **T2 (depends_on: [T1])** — Add webhook + listener troubleshooting steps, including deterministic port collision recovery.
- **T3 (depends_on: [T1])** — Add annotation-to-autopilot automation guidance (implementation + review + status artifacts + refresh/notifications).
- **T4 (depends_on: [T2, T3])** — Update `references/contract.yaml` with new scope, risks, and guardrails.
- **T5 (depends_on: [T2, T3])** — Update `references/evals.yaml` with happy/edge/pressure/negative tests covering new behavior.
- **T6 (depends_on: [T4, T5])** — Run `quick_validate.py` then `skill_gate.py`; fail-fast and fix first failing gate.

## Acceptance criteria

- Skill description triggers on Agentation install/verify/troubleshoot and automation setup prompts.
- Workflow clearly distinguishes MCP health from webhook delivery.
- Includes concrete mitigation for `EADDRINUSE`.
- Includes timeout-aware success rule for automation status.
- Local validators pass in the repository root.
