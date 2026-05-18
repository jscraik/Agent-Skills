# Agent Operating Contract

## Purpose

Keep the root `AGENTS.md` small while preserving the repo-specific command
contract agents need for everyday work.

## `ask` CLI

Fresh checkouts should prove the wrapper before depending on `./bin/ask`:

```bash
bash scripts/bootstrap-ask.sh --json
python3 bin/ask repo status --json
```

All agents should use `./bin/ask` for repo operations.

| Task            | Command                                            |
| --------------- | -------------------------------------------------- |
| Repo health     | `./bin/ask repo doctor --json --robot`             |
| Improve agents  | `./bin/ask skills improve "<goal>" --json --robot` |
| Explain skill   | `./bin/ask skills explain <handle> --json --robot` |
| Prove skill     | `./bin/ask skills prove <handle> --json --robot`   |
| Closeout        | `./bin/ask repo closeout --changed --json --robot` |
| Full validation | `./bin/ask repo validate`                          |
| List skills     | `./bin/ask skills list --category <topic>`         |
| Audit skill     | `./bin/ask skills audit <path> --level strict`     |
| Install skill   | `./bin/ask skills install <url> --remediate`       |
| Find related    | `./bin/ask graph related <skill> --depth 2`        |

`bin/` and `scripts/` at repo root are stable wrapper entrypoints that forward
into `Infrastructure/**`; keep them as real files/directories, not symlinks.

For AI coding agents, start with the compact doctor command before deeper repo
inspection:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot
./bin/ask skills explain <recommended_capability> --json --robot
./bin/ask skills prove <recommended_capability> --json --robot
./bin/ask repo closeout --changed --json --robot
```

Use the `recommended_capability` returned by `skills improve` as the handle for
`skills explain` and `skills prove`.

Run `repo doctor-catalog` or `repo surface` only when `repo doctor` names them
as diagnostic follow-up commands.

`repo doctor` is the first health entrypoint. It composes repo status, catalog
parity, runtime budget, command-handle health, and repo-surface diagnostic debt
into one agent-facing payload with `agent_summary`, `blocking`, `blockers`,
`next_command`, `signals`, and `diagnostic_debt`.

`skills improve` is the first capability recommendation entrypoint. It wraps
goal routing, runs command-handle proof for the selected capability, and returns
`agent_summary`, `recommended_capability`, `why`, `reachability`, `proof`, and
one existing `next_command`.

`skills explain` turns a command handle into concise use guidance. It returns
what the capability is for, when to use it, canonical source, runtime handle,
validation guidance, known limitations, reachability status, and the proof
command to run next.

`skills prove` is the product-facing scorecard for capability proof. It keeps
the existing command-handle `skills proof` payload as reachability evidence and
adds structural quality, analytics availability, outcome proof, and one next
command without claiming structural or invocation evidence as outcome proof.

## Robot Mode

Use `--robot` or `--agent-mode` for AI-agent command handling.

Behavior contract:

- If intent is clear, `ask` executes the command even with minor syntax mistakes
  and prints a correction note.
- If intent is ambiguous, `ask` returns a detailed error with suggested fixes and
  valid examples.

Examples where intent is recovered:

```bash
./bin/ask skill list --robot
./bin/ask list skills --robot
./bin/ask skills --advanced list --robot
```

Examples that should return clarification errors:

```bash
./bin/ask status --robot
./bin/ask skills audit --robot
```

## Shared Vocabulary

Before changing skills, sync policy, runtime projections, or agent-facing docs,
read [UBIQUITOUS_LANGUAGE.md](/UBIQUITOUS_LANGUAGE.md). Use its Prompt
Translations table for terse, ambiguous, overloaded, or project-specific user
wording.
