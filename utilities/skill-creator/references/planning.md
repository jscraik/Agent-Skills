# Planning with `$create-plan`

Codex can optionally use a planning skill to produce a concrete build plan before it writes files.

## When to use this

Use `$create-plan` when the skill you are building is non-trivial, for example:

- multiple files or assets
- a script-backed skill
- strict output contracts / schemas
- safety or approval requirements
- integration with external tools / CLIs

## How to use it

1. Write a short problem statement:
   - what the skill should do
   - who it is for
   - important constraints (platform, sandbox, offline/online, approvals)

2. Invoke `$create-plan` (if available).
   - If `$create-plan` is not installed, create an equivalent plan manually.

3. Store the plan artifact in the target skill folder:

- `references/plan.md` (recommended, overwrite on each major revision), or
- `references/plan-YYYYMMDD.md` (keep history)

## Plan artifact template

Use this structure in `references/plan.md`:

- Goal
- Non-goals
- Inputs
- Outputs / contract
- Key design decisions (router vs single skill, scripts vs instruction-only)
- Steps (RED → GREEN → REFACTOR)
- Gates (skill_gate.py, run_skill_evals.py, smoke tests)
- Risks + mitigations (secrets, network, destructive ops)
- Rollout notes (where to install, how to invoke)

## Minimum bar

A plan should be concrete enough that a new contributor could follow it and reproduce the skill build.
