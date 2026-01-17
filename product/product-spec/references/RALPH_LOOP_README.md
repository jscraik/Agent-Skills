# Golden Ralph Loop (ralph-gold)

This loop orchestrates fresh CLI-agent sessions (Codex, Claude Code, Copilot) in a deterministic loop. Each iteration is a new agent invocation; memory lives in files and git, not in model context.

## Files created by `ralph init`

- `.ralph/ralph.toml` -- loop configuration (files, gates, runners)
- `.ralph/PRD.md` and `.ralph/prd.json` -- task tracker in Markdown or JSON
- `.ralph/AGENTS.md` -- repo-specific build/test/run commands and rules
- `.ralph/progress.md` -- append-only memory across iterations
- `.ralph/specs/` -- requirements and acceptance criteria
- `.ralph/PROMPT_build.md` / `.ralph/PROMPT_plan.md` / `.ralph/PROMPT_judge.md` (plus optional `.ralph/PROMPT.md` fallback)
- `.ralph/logs/` -- per-iteration logs
- `.ralph/state.json` -- loop state and history

## Quick start

```bash
ralph init
ralph run --agent codex --max-iterations 10
```

Run a single iteration:

```bash
ralph step --agent claude
```

Check status:

```bash
ralph status
```

## PRD formats

`ralph-gold` supports two PRD formats. Configure which file is authoritative via `.ralph/ralph.toml` under `[files].prd` and/or `[tracker].kind`.

### JSON PRD (`.ralph/prd.json`)

Create a JSON object with a top-level `stories` array. Each story must include:

- `id` (int)
- `priority` (int)
- `title`
- `description`
- `acceptance` (array of strings)
- Done state: either `passes: true|false` or `status: "open"|"in_progress"|"done"`

### Markdown PRD (`.ralph/PRD.md`)

Include a `## Tasks` section with checkbox lines:

```md
## Tasks
- [ ] Task 1
- [ ] Task 2
```

## Loop behavior and exit gates

- One task per iteration.
- Backpressure via gate commands in `.ralph/ralph.toml` under `[gates].commands`.
- Dual exit gate: all tasks done AND the agent prints `EXIT_SIGNAL: true` at the end of output.
- The orchestrator will treat `EXIT_SIGNAL` as false if the repo is dirty or gates/judge fail.
- Circuit breaker: stops after `loop.no_progress_limit` consecutive no-progress iterations.
- Optional rate limiting: `loop.rate_limit_per_hour`.

Exit codes (ralph run):
- 0: successful completion
- 1: incomplete exit (e.g., max iterations / no-progress)
- 2: iteration failed (non-zero return, gate failure, or judge failure)

## Runner configuration (`.ralph/ralph.toml`)

You install agent CLIs separately and configure their argv under `[runners]`. Example:

```toml
[runners.codex]
argv = ["codex", "exec", "--full-auto", "-"]

[runners.claude]
argv = ["claude", "-p", "--output-format", "stream-json"]
```

Prompt transport rules:
- `codex`: if argv contains `-`, prompt is sent via stdin.
- `claude`: if argv contains `-p`, prompt is inserted immediately after `-p`.
- `copilot`: if argv contains `--prompt`, prompt is inserted immediately after `--prompt`.
- You can also use `{prompt}` in argv to inline.

## PRD generation (optional)

Generate or update a PRD from a description:

```bash
ralph plan --agent codex --desc "Build a small service with health endpoint and tests"
```

## Notes

- Start attended and review the first iterations.
- Use a dedicated branch if your repo policy requires it.
