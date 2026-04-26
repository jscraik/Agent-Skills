# Sub-Agent Map

Read when: selecting helper lanes for `he-refine`.

## Purpose
Keep browser-first refinement delegation bounded so polish loops stay fast and actionable.

## Baseline lanes
Start with:
- `repo-research-analyst`
- `learnings-researcher`

## Conditional lanes
Add only when the signal is present:
- `worker`: apply isolated refinement edits quickly.
- `testing-reviewer`: confirm a polish change does not break expected behavior.
- `correctness-reviewer`: high-risk edits where regression risk is non-trivial.
- `design-implementation-reviewer`: visual/layout refinement requiring design-fidelity checks.
- `julik-frontend-races-reviewer`: race-condition risk in UI interaction flows.

## Selection rules
1. Keep the smallest role set that materially improves confidence.
2. Do not run broad review swarms for low-risk copy/layout polish.
3. If auto-spawn is unavailable, continue inline and return manual role guidance.

## Role availability fallback
- Check role availability from `~/.codex/agents/manifest.json` before delegation.
- If auto-spawn is unavailable, continue inline and list manual launch guidance.
- If required roles are missing, route role creation/install to `[[codex-agent-creator]]`.
