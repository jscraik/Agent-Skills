# Sub-Agent Map

Read when: selecting helper lanes for `he-improve`.

## Purpose
Keep optimization delegation bounded and deterministic so runs remain measurable and reproducible.

## Baseline lanes
Always start with:
- `repo-research-analyst`
- `learnings-researcher`

## Conditional lanes
Add only when needed:
- `best-practices-researcher`: external optimization standards materially affect the loop.
- `framework-docs-researcher`: framework/runtime semantics affect metrics.
- `worker`: isolated experiment implementation slices.
- `testing-reviewer`: experiment changes affect test trustworthiness.
- `correctness-reviewer`: optimization changes risk correctness regressions.
- `performance-reviewer`: primary target is latency/throughput/resource efficiency.

## Selection rules
1. Keep the smallest role set that materially improves confidence.
2. Do not spawn broad review swarms for routine low-risk tuning.
3. Route to inline execution when auto-spawn is unavailable.

## Role availability fallback
- Check role availability from `~/.codex/agents/manifest.json` before delegation.
- If auto-spawn is unavailable, continue inline and list manual role launch guidance.
- If required roles are missing, route role creation/install to `[[codex-agent-creator]]`.
