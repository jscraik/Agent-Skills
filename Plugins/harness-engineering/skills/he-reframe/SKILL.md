---
name: he-reframe
description: "Creates migration, architecture-refactor, and process-repair plans from evidence by identifying drift patterns, target shape, phases, risks, and validation gates. Use when repeated failures or system changes need a staged fix before implementation."
metadata:
  version: 1.0.0
  skill-type: team_automation
---

# Harness Engineering Reframe

## Philosophy
A reframe changes the shape of work. Prove the current pattern, define the target pattern, then migrate in reversible phases.

## When to Use
Use for architecture evolution, process redesign, source-prompt preservation gaps, repeated workflow failures, or cross-skill/system drift that needs a phased program before implementation.

## When Not to Use
Do not use for a normal implementation task, isolated bug fix, code review, Linear planning, or strategy note. Route those to `he-work`, `he-code-review`, `he-linear-plan`, or `he-strategy`.

## Inputs
Current pattern evidence, target pattern evidence, affected repos/skills/files, constraints, validation commands, rollback strategy, and source-prompt evidence when applicable.

## Outputs
Write a reframe artifact or return `blocked`. Include current pattern, target pattern, phases, allowed changes, validation, rollback, stop conditions, and handoff.

## Procedure
1. Prove the current pattern from repo files or artifacts. Do not accept the prompt alone.
2. Prove the target pattern or mark it as an assumption with confidence.
3. Pick the smallest reversible first phase. Require approval for public API, auth, data, CI, routing, skill/plugin, or dependency changes.
4. Define each phase with scope, allowed files, validation gate, rollback, and handoff.
5. Run the artifact gate. Fix once and re-run; if still failing, block the reframe.
6. Hand off the first approved phase to `he-plan`, not directly to broad implementation.

## Validation
Fail fast: stop at the first failed gate and do not proceed until fixed, waived by an authorized gate, or reported as blocked.

~~~bash
test -f Plugins/harness-engineering/references/routing-map.json
rg -n "<old-pattern>|<new-pattern>" <repo-or-scope>
rg -n "decision|ADR|invariant|rollback|validation" .harness Plugins Docs
python3 Plugins/harness-engineering/scripts/check_bluf_structure.py <reframe-path> --json
~~~

## Failure Mode
Block when current pattern, target pattern, phase boundary, validation, rollback, or authority is missing.

## Execution Boundaries
This skill designs phased change. It does not implement code, mutate trackers, or stage files.

## Constraints
Redact secrets, preserve user edits, and keep generated/runtime projections out of canonical edits.

## Gotchas
- A reframe without rollback is a risky refactor plan, not a migration program.
- Process-theater findings need observed failure evidence before becoming phases.

## Anti-Patterns
One giant migration, unvalidated target pattern, broad refactor disguised as reframe, or implementation without a selected phase.

## Examples
- When the user asks, "Move dashboard and runner to one score vocabulary," prove both current vocabularies, write one reversible phase, and validate the artifact.
- When the user asks, "Our prompt flow keeps drifting," compare source prompt evidence before proposing migration phases.

## Output Template
~~~yaml
schema_version: 1
selected_stage: he-reframe
program_path: .harness/reframe/2026-05-16-skill-review-contract.md
current_pattern: "Runner and dashboard each define score status language"
target_pattern: "Shared score signal vocabulary imported by both"
phases:
  - id: RF-1
    scope: "Introduce shared constants only"
    validation:
      - "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
    rollback: "Remove constants and restore local labels"
handoff: he-plan
~~~

## References
- Reframe contract: `../../references/skills/he-reframe/reframe-program-contract.md`
- Architecture compression: `../../references/skills/he-reframe/architecture-evolution-compression.md`
- Source-prompt preservation: `../../references/skills/he-reframe/source-prompt-preservation.md`
- Shared contracts: `../../references/deferred-context-index.md`, `../../references/source-prompt-coverage-contract.md`
