# Context7 Decision Guidance (Trimmed From SKILL.md)

Use this reference when deeper strategic guidance is needed without expanding `SKILL.md`.

## Philosophy and tradeoffs
- Prioritize current-source evidence over memory when behavior may have drifted.
- Prefer narrow, implementation-shaped retrieval queries over broad documentation pulls.
- If ambiguity remains after retrieval, ask for minimal clarification rather than filling gaps with assumptions.

## Caveats
- Do not treat weak fuzzy library matches as authoritative.
- Do not skip validation steps when output will drive implementation decisions.
- Do not replace engineering judgment with a rigid checklist; adapt to repo constraints and risk.

## Adaptation heuristics
- Small tasks: one focused retrieval query with explicit assumptions.
- Medium tasks: compare two likely library matches and explain why one was selected.
- Large tasks: produce version-scoped guidance plus a short risk list for migration gaps.

## Decision prompts
- Why is this the right library match?
- What version constraints are inferred vs confirmed?
- Which part of the final answer is direct documentation vs interpretation?
