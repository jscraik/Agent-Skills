---
name: he-spec
description: "Creates Harness Engineering behavior, test, BDD, and acceptance specs that define criteria, validation evidence, observability, rollback, and ownership. Use when requirements need a testable contract."
metadata:
  version: 1.0.0
  skill-type: team_automation
---

# Harness Engineering Spec

## Philosophy
A spec pins behavior. It should make the selected slice testable, traceable, observable, reversible, and ready for planning.

## When to Use
Use when a selected issue, strategy slice, bug, user flow, UI artifact, or session evidence needs acceptance criteria before planning or implementation.

## When Not to Use
Do not write implementation plans, code, Linear payloads, strategy, or review findings. Route those to the matching HE skill.

## Inputs
- Selected behavior or requirement slice.
- Source artifact path, issue/PR link, or session evidence reference.
- Known owner authority, validation command, observability signal, rollback/supersession rule, and relevant `.harness/**` evidence.

## Outputs
Write a spec or replacement section, or return `blocked`. Include stable acceptance IDs, source evidence, validation command, pass/fail condition, observability, rollback/supersession, risks, owner evidence, and handoff.

## Modes
- `standard-spec`: create a new behavior contract from a selected issue, strategy slice, bug, or requirement.
- `dedicated-ui-spec`: create UI/browser acceptance criteria from screenshots, browser feedback, visual references, or interaction evidence.
- `revision`: replace an existing spec section while preserving stable IDs unless the user explicitly asks to renumber.
- `deepen`: add missing acceptance, validation, observability, rollback, or ownership fields to an existing spec.

## Procedure
1. Choose one mode from `Modes`; if two apply, prefer `revision` for existing specs and `dedicated-ui-spec` for browser-visible behavior.
2. Verify the source artifact exists and the selected behavior is unambiguous.
3. Write acceptance criteria as stable IDs. Each ID needs behavior, source evidence, validation, risk, observability, and rollback/supersession.
4. Keep implementation notes secondary. The main spec is behavior, not task sequence.
5. Run the artifact gate in `Validation`. Fix the missing field, broken structure, or absent source once and re-run; if the same gate still fails, return blocked with the exact command and output.
6. Hand off to `he-plan` only after acceptance IDs and validation are explicit.

## Validation
Fail fast: stop at the first failed gate and do not proceed until fixed, waived by an authorized gate, or reported as blocked.

~~~bash
test -f <source-artifact>
rg -n "AC-|acceptance|validation|rollback|observability" <spec-path>
python3 Plugins/harness-engineering/scripts/check_bluf_structure.py <spec-path> --json
~~~

Pass/fail criteria:
- `test -f` passes only when the cited source artifact exists locally. If the source is remote or from chat, cite the exact URL/message and mark local file proof unavailable.
- `rg` passes only when the spec includes acceptance IDs plus validation, rollback, and observability terms.
- `check_bluf_structure.py` passes only when it exits 0 and returns JSON without structural errors.
- If any required validation is impossible in the current environment, report `blocked_validation` with the missing permission, file, or tool.

## Failure Mode
Block when behavior, source evidence, owner authority, validation, observability, rollback, or tracker linkage is missing.

## Safety Boundaries
Redact secrets and sensitive data by default. Do not invent requirements, skip validation, edit generated projections as source, or present local spec state as live tracker state.

## Handoff Rules
Hand off to `he-plan` for implementation planning, `he-linear-plan` for tracker payloads, and humans for unresolved authority or requirement conflicts.

## Gotchas
- HE ritual is not the spec; user-visible behavior and acceptance criteria are.
- Secondary strategy/review docs are evidence only unless the selected slice admits them.
- Do not leave a criterion with validation like "manual review" unless the user explicitly accepts manual proof; prefer one runnable command plus one observable artifact.

## Output Format
Use this compact shape:

~~~yaml
schema_version: 1
selected_stage: he-spec
mode: standard-spec
spec_path: .harness/specs/JSC-246-local-review-dashboard.md
acceptance:
  - id: AC-001
    behavior: "Dashboard refresh runs only after skill validation or eval commands"
    source: "User browser feedback on local dashboard"
    validation: "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
observability: "Generated HTML includes updated timestamp and source report path"
rollback: "Disable auto-open/refresh and keep artifact generation only"
handoff:
  next_skill: he-plan
~~~

## Examples
- When the user asks, "Spec the browser refresh behavior," inspect the browser feedback and write acceptance IDs with a pytest/browser gate.
- When the user asks, "Revise this spec section," return the full replacement section, not a vague delta.

## Worked Transformation
Source evidence:
~~~text
User feedback: The browser refreshes when nothing is being validated.
Expected: refresh only after a skill validation or eval run.
~~~

Acceptance criterion:
~~~yaml
- id: AC-001
  behavior: "Dashboard refresh runs only after skill validation or eval commands"
  source: "User browser feedback on local dashboard refresh behavior"
  validation: "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
  risk: "Stale dashboard could hide current eval state"
  observability: "Generated HTML timestamp and source report path change after eval"
  rollback: "Disable browser refresh and keep artifact generation only"
~~~

Mode selection:
~~~yaml
mode: dedicated-ui-spec
why: "The source evidence is browser feedback about visible dashboard refresh behavior."
gate:
  command: "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
  pass_condition: "pytest exits 0 and covers refresh trigger behavior"
  evidence: "Generated dashboard timestamp changes only after eval command"
~~~

## Assets
Reference `assets/` only for skill packaging and browseability; spec evidence belongs in artifacts, validation output, and handoff notes.

## References
- Spec modes/artifacts: `../../references/skills/he-spec/spec-mode-rules.md`, `../../references/skills/he-spec/spec-artifact-contract.md`
- Session evidence: `../../references/skills/he-spec/codex-and-session-evidence.md`
- Reviewability: `../../references/bluf-review-contract.md`, `../../references/visual-reference-contract.md`
- Shared subagent call policy: `../../references/subagent-call-contract.md`
- Deferred context index: `../../references/deferred-context-index.md`
- Software-literature spec lenses: `../../../../Infrastructure/references/software-literature-expert-lens-pack.md`, `../../../../Infrastructure/references/software-literature-skill-expertise-map.md`
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
