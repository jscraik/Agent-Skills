# Agent Operating Contract

## Purpose

Keep the root `AGENTS.md` small while preserving the repo-specific command
contract agents need for everyday work.

## `ask` CLI

All agents should use `./bin/ask` for repo operations.

| Task            | Command                                        |
| --------------- | ---------------------------------------------- |
| Repo health     | `./bin/ask repo status`                        |
| Full validation | `./bin/ask repo validate`                      |
| List skills     | `./bin/ask skills list --category <topic>`     |
| Audit skill     | `./bin/ask skills audit <path> --level strict` |
| Install skill   | `./bin/ask skills install <url> --remediate`   |
| Find related    | `./bin/ask graph related <skill> --depth 2`    |

`bin/` and `scripts/` at repo root are stable wrapper entrypoints that forward
into `Infrastructure/**`; keep them as real files/directories, not symlinks.

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
