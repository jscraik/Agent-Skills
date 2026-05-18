---
name: he-plan
description: "Turns approved Harness Engineering specs, issues, strategy slices, or bug evidence into bounded implementation plans with units, validation gates, rollback, ownership, and handoff. Use when execution needs a plan before code changes."
metadata:
  version: 1.0.0
  skill-type: team_automation
---

# Harness Engineering Plan

## Philosophy
A plan is an execution contract, not a brainstorm. It should name the slice, files or boundaries, units of work, validation, rollback, blockers, and next handoff.

## When to Use
Use when a selected spec, issue, reframe phase, strategy slice, or reproduced bug needs implementation units before code or artifact edits.

## When Not to Use
Do not invent requirements, write specs, mutate Linear, implement code, or review PRs. Route missing behavior to `he-spec`, missing tracker topology to `he-linear-plan`, and implementation to `he-work`.

## Inputs
Source spec/issue/plan, selected slice, repo instructions, dirty state, validation commands, risk notes, owner/authority evidence, and relevant `.harness/**` artifacts.

## Outputs
Write a plan artifact or return `blocked`. Include mode, source slice, units, allowed files/boundaries, validation, rollback, risks, blockers, and handoff.

## Procedure
1. Choose mode:
   - selected issue/spec -> `standard-plan`
   - existing plan missing detail -> `deepen`
   - browser/screenshot/UI behavior -> `dedicated-ui-plan`
   - ambiguous next stage -> `blocked`
2. Verify source artifact exists and names acceptance, validation, rollback, and scope.
3. Break the work into small ordered units. Each unit needs allowed files or boundaries, expected behavior, validation, and rollback.
4. Add risk and stop conditions. Do not plan unapproved external mutation, destructive commands, or broad refactors.
5. Run the artifact gate. Fix once and re-run; if still failing, return blocked.
6. Hand off to `he-work` only when the first unit is selected and validation is explicit.

## Validation
Fail fast: stop at the first failed gate and do not proceed until fixed, waived by an authorized gate, or reported as blocked.

~~~bash
test -f <source-spec-or-plan>
rg -n "AC-|acceptance|validation|rollback|scope" <source-spec-or-plan>
python3 Plugins/harness-engineering/scripts/check_bluf_structure.py <plan-path> --json
~~~

## Failure Mode
Block when source slice, acceptance, validation, rollback, owner authority, or implementation boundary is unclear.

## Safety Boundaries
Redact secrets and sensitive data by default. Do not edit code, stage files, mutate trackers, or present an unvalidated plan as implementation proof.

## Handoff Rules
Use `he-work` for the selected implementation unit, `he-spec` for missing behavior, `he-linear-plan` for tracker payloads, and `he-code-review` for review or repair.

## Gotchas
- A plan without a validation command is not ready for implementation.
- Secondary strategy or review docs are evidence only unless the selected slice admits them.

## Examples
- When the user asks, "Plan the dashboard scorecard fix from this spec," inspect the spec, write units with validation, and hand off only U1.
- When the user asks, "Deepen this plan," inspect the existing plan and add missing validation, rollback, and file boundaries.

## Output Template
~~~yaml
schema_version: 1
selected_stage: he-plan
mode: standard-plan
plan_path: .harness/plan/JSC-246-dashboard-scorecard.md
source_slice: "Dashboard score summary and validation evidence"
units:
  - id: U1
    change: "Align dashboard summary count with scorecard JSON"
    files_allowed:
      - Infrastructure/scripts/lib/ask/skill_review_dashboard.py
    validation:
      - "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
rollback: "Revert the dashboard renderer change."
handoff: he-work
~~~

## Assets
Reference `assets/` only for skill packaging and browseability; plan evidence belongs in artifacts, validation output, and handoff notes.

## References
- Plan contracts: `../../references/skills/he-plan/plan-artifact-contract.md`, `../../references/skills/he-plan/planning-depth.md`
- Test strategy: `../../references/skills/he-plan/test-strategy.md`
- Handoff: `../../references/skills/he-plan/post-plan-handoff.md`
- Shared subagent call policy: `../../references/subagent-call-contract.md`
- Deferred context index: `../../references/deferred-context-index.md`
- Cookbook-derived execution-plan and evaluation flywheel lenses: `../../../../Infrastructure/references/openai-cookbook-expert-lens-pack.md`, `../../../../Infrastructure/references/openai-cookbook-skill-expertise-map.md`
- Software-literature planning lenses: `../../../../Infrastructure/references/software-literature-expert-lens-pack.md`, `../../../../Infrastructure/references/software-literature-skill-expertise-map.md`
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
