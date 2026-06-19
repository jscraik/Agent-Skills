# Autoreview Discovery Interview

Use this only when the review target, proof command, engine, or permission boundary is underspecified.

Ask one round at a time. Use a plain-language question, explain why this matters, and avoid dumping the whole interview plan at once.

## Request user input mini-templates

Round 1 target question:

What should this skill help you do?

What exact local diff, branch, PR, commit ref, or review artifact should the structured review inspect?

Why this matters: wrong target selection can review an empty diff, stale patch, or the wrong commit.

## Copy-paste payload examples

Ambiguous target:

What exact local diff, branch, PR, commit ref, or review artifact should the structured review inspect?

Ambiguous proof:

Which validation should run with the review: the helper's auto-detected check, a specific test command, or no parallel tests?

Ambiguous engine:

Should the review use the default Codex engine, a named engine such as Claude, or an explicit review panel?

Ambiguous permissions:

Should the helper use its normal sandbox and approval posture, or should it request explicit elevated review mode because a previous run was blocked?

## Round 1: Target

What should this skill help you do?

What exact local diff, branch, PR, commit ref, or review artifact should the structured review inspect?

Why this matters: target mode changes the helper path and prevents reviewing an empty diff, stale patch, or wrong commit.

## Round 2: Proof

Which validation should run with the review: the helper's auto-detected check, a specific test command, or no parallel tests?

Why this matters: validation ownership must separate current-patch failures, pre-existing failures, unrelated dirty worktree issues, and environment or tooling failures.

## Round 3: Engine

Should the review use the default Codex engine, a named engine such as Claude, or an explicit review panel?

Why this matters: engine choice changes runtime, cost, and failure recovery. Do not switch engines silently after capacity or sandbox failures.

## Round 4: Permission Boundary

Should the helper use its normal sandbox and approval posture, or should it request explicit elevated review mode because a previous run was blocked?

Why this matters: elevated review mode changes side-effect risk and must stay an explicit operator decision.
