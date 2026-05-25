# PU-008 Docs And Agent-Instruction Accuracy Check

Status: pass_with_boundaries

## Scope

Checked the browser implementation notes, goal board, live GitHub PR stack, Linear JSC-364 tracker truth, and repo closeout surface after the PU-008 placement visual and PR-template refresh work.

## Evidence

- Browser implementation notes are served successfully from \`http://127.0.0.1:18080/.harness/implementation-notes/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-execution-notes.html\`.
- The deep-modules visual maps work placement across public command surfaces, deep internals, schema and validator contracts, runtime proof evidence, review/governance artifacts, GitHub PRs, and Linear.
- Live GitHub truth shows PRs 200-207 are ready, \`MERGEABLE\`, and have no visible failing or pending checks.
- Linear JSC-364 remains \`In Progress\` and has attachments for PRs 199-207, including PR 207.
- \`./bin/ask repo closeout --changed --json --robot\` exits success with no changed files and repo-surface diagnostic debt as a warning.
- \`python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane\` passes.

## Boundaries

- Runtime proof cards for \`context7\`, \`testing\`, and \`autofix\` remain \`blocked_runtime\`; they are intentionally not live Codex runtime parity claims.
- Broad local gates remain blocked by pre-existing projection-integrity drift in \`cache-harness-engineering\` and \`cache-skill-factory\`.
- No merge or cleanup was performed because the active completion contract requires explicit current-turn merge authority.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/docs-agents-accuracy.md
