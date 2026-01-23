### 12) Delivery with RALPH loop (optional but recommended for implementation)
- After a PRD and/or Tech Spec is finalized, offer: "Would you like to run the Golden Ralph Loop to deliver incrementally?"
- If yes:
  1) **Initialize the loop scaffold** (in repo root):
     - Run `ralph init` to create `.ralph/ralph.toml`, `.ralph/PRD.md`, `.ralph/prd.json`, `.ralph/AGENTS.md`, `.ralph/progress.md`, `.ralph/specs/`, `.ralph/PROMPT_build.md`, `.ralph/PROMPT_plan.md`, `.ralph/PROMPT_judge.md`, `.ralph/logs/`, and `.ralph/state.json`.
     - Verify `ralph --help` and `ralph doctor` if needed (ensures git + agent CLIs are available).
     - Run `ralph diagnose --test-gates` to validate gate commands before the loop.
  2) **Choose the PRD format** (set in `ralph.toml` under `[files].prd`):
     - JSON (`.ralph/prd.json`) with a `stories` array (id, priority, title, description, acceptance, and done state).
     - Markdown (`.ralph/PRD.md`) with a `## Tasks` section and checkbox lines.
     - If you use `[tracker].kind`, set it to `auto|markdown|json|beads` and keep `files.prd` aligned.
  3) **Write loop instructions and commands**:
     - Update `.ralph/PROMPT_build.md` with the implementation plan and guardrails.
     - Update `.ralph/AGENTS.md` with repo-specific build/test/run commands.
     - If `CLAUDE.md` is present, list dependencies and commands there and reference `.ralph/AGENTS.md` to keep a single source of truth.
  4) **Wire quality gates**:
     - Set `ralph.toml` `[gates].commands` to the repo's quality gate commands (lint/test/typecheck).
     - Gates run after each iteration; failures keep the task open and block exit.
  5) **Generate or refine the PRD** (optional):
     - Use `ralph plan --agent <runner> --desc "<summary>"` to create or update tasks.
     - Ensure tasks are atomic (5–15 minutes) with explicit acceptance criteria + a test command.
     - Enforce evidence discipline: cite file paths and command output, or state "Unable to verify: <reason>".
  6) **Run the loop (attended first)**:
     - `ralph step --agent codex` (single iteration), or
     - `ralph run --agent codex --max-iterations N`
     - The agent must print `EXIT_SIGNAL: true|false` at the end of output.
  7) **Monitor progress**:
     - `ralph status` for progress and last iteration summary.
     - Logs are in `.ralph/logs/`; loop state in `.ralph/state.json`.
  8) **Exit conditions**:
     - Loop exits only when all tasks are done AND the agent prints `EXIT_SIGNAL: true`.
     - The orchestrator ignores `EXIT_SIGNAL: true` if the repo is dirty or gates/judge fail.
     - Circuit breaker stops on repeated no-progress iterations (`loop.no_progress_limit`).
