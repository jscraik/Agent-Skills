# 5-Minute Success Path

## Table of Contents

- [Goal](#goal)
- [First Validated Outcome](#first-validated-outcome)
- [If Route Is Blocked](#if-route-is-blocked)
- [What To Run Next](#what-to-run-next)

## Goal

Get one useful capability recommendation and closeout path in under five
minutes.

## First Validated Outcome

First prove the command wrapper can be reached from this checkout:

```bash
bash scripts/bootstrap-ask.sh --json
python3 bin/ask repo status --json
```

Run the agent-first path from the repo root:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "implement a feature safely" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

Validated outcome definition:

- A JSON envelope is returned.
- `repo doctor` reports whether work is blocked and gives one next command.
- `skills improve` returns `recommended_capability` or a blocked route state.
- `skills explain` and `skills prove` distinguish source, runtime, and proof.
- `repo closeout --changed` reports focused validation and commit readiness.

## If Route Is Blocked

Follow the blocked command's `next_command` or `operator_action` first. Use
`repo doctor-catalog` or `repo surface` only when `repo doctor` names them as
diagnostic follow-up commands.

## What To Run Next

- Full release-readiness checks: `./bin/ask repo validate`
- Command reference: `/AGENTS.md`
- Workflow and safety defaults: `/Docs/agents/13-workflow-and-safety-guidance.md`
