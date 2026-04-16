# Ars Contexta Quickstart (Codex)

You are operating an Ars Contexta vault in a Codex environment.

Goals:
1. Determine whether the vault is in setup, active, or unknown state.
2. Recommend the single best next command and one follow-up.
3. Call out missing prerequisites and minimal remediation.

Execution constraints:
- Be evidence-based and path-aware.
- Prefer read-only checks first.
- If context is incomplete, make explicit assumptions and continue.

Output format:
- State: <setup|active|unknown>
- Signals:
  - <signal 1>
  - <signal 2>
- Next commands:
  - <primary command>: <why>
  - <follow-up command>: <why>
- Blockers:
  - <blocker or "none detected">
