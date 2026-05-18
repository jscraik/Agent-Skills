# Harness Engineering Plan Doctrine

Retained doctrine for `he-plan`; keep the active skill short and load this only when planning depth or provenance matters.

## Sources

- Live `/Users/jamiecraik/dev/codex` and codex-repo MCP: Plan Mode source behavior for `update_plan`, non-mutating discovery, and plan/work separation.
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md` and `Docs/product/agent-capability-control-plane.md`: command-contract and proof expectations.
- `Plugins/harness-engineering/references/lifecycle-exit-contract.md`, `linear-tracker-gate.md`, and `subagent-call-contract.md`: HE lifecycle, tracker, and delegation contracts.
- `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-deepen-plan/` and `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/`: preserved planning doctrine and templates from prior source imports.

## Codex Plan Mode Lessons

Plan Mode works by separating discovery, intent, and implementation shape:

1. Inspect repo facts before asking.
2. Ask only when the answer changes scope, architecture, sequencing, risk, or an assumption.
3. Keep non-mutating inspection separate from implementation.
4. Treat `update_plan` as a live checklist only, not the durable plan artifact.
5. Produce a complete replacement plan that another agent can implement from fresh context.

## HE Plan Shape

A Harness Engineering plan is ready when it includes source traceability to Linear/spec/requirements, stable unit IDs, acceptance IDs, dependency order, repo-relative file paths, concrete validation, rollout/rollback notes, residual risks, and a Linear/spec/plan/PR evidence matrix for tracked work.

Do not include copy-paste implementation code, commit choreography, or RED/GREEN/REFACTOR micro-steps. Directional sketches, diagrams, and pseudocode are allowed only when explicitly non-prescriptive.

## Source Resolution

Prefer existing plan, then active Linear issue graph, then brainstorm/requirements, then approved spec/UI spec, then direct request. For non-trivial tracked work, Linear is mandatory: resolve or create the issue through `linear-tracker-gate.md` before sequencing delivery. If blocked, return `linear_status: linear_blocked` plus the ready-to-create payload.

## Depth

Use lightweight plans for straight-line low-risk work, standard plans for normal feature/refactor/bug work, and deep plans for cross-cutting, security/privacy/payment/API, migration, or ambiguous work. Local research comes first; external research is warranted only when local patterns cannot answer the risk.

## Synthesis

Use Stated, Inferred, and Out-of-scope checkpoints for consequential assumptions. In headless runs, put unconfirmed bets in `## Assumptions`; in interactive runs, revise after user correction until confirmed.

## Deepening

Deepen only sections with real confidence gaps: weak rationale, vague units, shallow tests, hidden blockers, missing rollout, or unclear system impact. Dispatch targeted reviewers for the specific gap, then integrate accepted findings into the plan.

## Testing Guidance

Plans must require real behavior tests. Avoid plans that only test mocks, snapshots of mocked children, or implementation internals. Include happy path, edge case, error path, and integration scenarios where they genuinely apply; otherwise give an explicit no-test rationale.

## Visual Guidance

Use dependency graphs, interaction diagrams, comparison tables, or state diagrams only when they reduce reader work. Skip visuals that duplicate prose or smuggle implementation decisions into the plan.

## Handoff

Hand off to `he-work` for implementation after the plan is complete. Use `he-deepen-plan` or document review when confidence gaps remain. `he-plan` itself remains plan-only.

## Compression Recovery Plans

For cockpit or golden-path recovery, the first slice should be boring and
subtractive: name the exact first-contact budget, shrink default help, hide
plumbing from agent catalogs, require full catalogs to sit behind an
advanced/all flag, rewrite the README/front door around the golden path, add a
failing help-budget test, add a failing standalone-command admission test, and
create a fresh-agent eval fixture. Only then add metadata or policy surfaces.
Each visible command family needs an ablation decision: keep visible, make
reachable only through the golden path, merge into readiness/learning, hide as
plumbing, or remove. Do not accept a compression plan that says "declutter" but
does not list the concrete public rails, demoted commands, and future command
admission criteria.
