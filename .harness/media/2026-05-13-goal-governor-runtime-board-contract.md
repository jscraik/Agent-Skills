# From Goal Board Drift -> Runtime-Reconciled Goal Governance

## Purpose

This review artifact records the intended infographic for the goal-governor hardening pass. It exists because the review workflow required a bespoke media artifact tied to the actual patch, validation evidence, and residual risks.

## Image Generation & Persistence Evidence

* media status: fallback-only
* $imagegen invoked: blocked
* generated-image cache source path: blocked; no callable built-in image generation tool was exposed in this session
* repository .harness/media/ PNG path: blocked; no PNG was generated
* prompt metadata path: /Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-13-goal-governor-runtime-board-contract-prompt.md
* sidecar path: /Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-13-goal-governor-runtime-board-contract.md
* repository PNG existence verification: blocked
* persistence method: blocked
* final user-facing text after imagegen permitted: yes
* residual risk: The fallback prompt and SVG exist, but no generated bitmap can be claimed until an image generation tool is actually invoked and a PNG is copied under .harness/media/.

## Bespoke Framing

* skill name: goal-governor
* skill type: governance / orchestration / validation
* original state: Goal board governance with drift risks between native Codex goal state, repo-visible board state, verifier freshness, and receipts.
* target state: Runtime-reconciled goal governance with native metadata, objective edits, budget-limited state, receipts, and validation gates aligned.
* main weakness: The skill could appear operationally correct while native goal state and board state diverged or while validation evidence was stale.
* main improvement: Continuation now requires explicit reconciliation across native goal state, board state, receipts, verifier freshness, and completion audit.
* validation evidence: deterministic tests pass; YAML parse pass; strict audit pass; skill gate pass; OpenAI skill format pass; package boundary check pass; Plugin Eval 77/100 with residual cost/complexity warnings; smoke eval fail.
* package alignment status: updated
* artifact impact: SKILL.md, references/evals.yaml, scripts/check_goal_board.py, and .harness/media review artifacts changed in this pass; prior aligned references and contracts remain in package.
* confidence movement: 88% -> 82%
* loop outcome: blocked by required runtime validation

## Prompt Summary

Use the prompt metadata file to generate a 2048x1152 technical infographic titled "From Goal Board Drift -> Runtime-Reconciled Goal Governance" with panels for drift risks, reconciliation, validation evidence, and residual blocked checks.

## Linked Context

Reviewed package: /Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor

Generated handle, not edited: /Users/jamiecraik/dev/agent-skills/.agents/skills/goal-governor/SKILL.md

Fallback SVG: /Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-13-goal-governor-runtime-board-contract.svg
