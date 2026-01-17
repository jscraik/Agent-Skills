# Command Line Interface Guidelines (condensed from clig.dev)

Use this rubric for CLI surface-area design: args/flags/subcommands/help/output/errors/config.

## Philosophy
- Human-first, script-friendly stability.
- Simple parts that compose; stdout is primary output.
- Consistency across programs and standard flag names.
- Say just enough; be informative without noise.
- Conversation as the norm: dry-run, previews, confirmations.
- Robustness and empathy: fail fast with clear errors.

## Help and documentation
- Always support `-h`/`--help`; ignore other args when present.
- On missing args: show concise help with 1-2 examples and "use --help".
- Support `cmd help` and `cmd subcmd --help` patterns.
- Lead with examples; list common flags/commands first.
- Include links to web docs and support/issue paths when available.
- Prefer short terminal help plus deeper docs on the web or man pages.
- If expecting stdin input and stdin is a TTY, show help and exit (or log a hint to stderr).
- If the user likely meant another command, suggest it. Do not auto-run it.
- Use formatting in help text, but avoid heavy escape sequences.

## Output
- Human-first, but composable; detect TTY for formatting.
- Stdout for primary output; stderr for diagnostics and errors.
- Provide machine-readable output when possible; keep `--plain` or `--json` stable.
- Use `--plain` when human formatting would break line-based output.
- Keep output pipe-friendly; do not mix logs into `--json`.
- If you change state, tell the user; show current state and suggest next commands where helpful.
- Make boundary-crossing actions explicit (writes, network, exec).
- Avoid animations when stdout is not a TTY.
- Disable color when not a TTY, `NO_COLOR` is set, `TERM=dumb`, or `--no-color`.
- Check stdout and stderr TTY status separately when deciding on color.
- Use symbols or emoji when it makes things clearer.
- Do not treat stderr like a log file by default; avoid log-level prefixes unless verbose.
- Use a pager only when stdin/stdout are TTY; prefer `less -FIRX` and avoid heavy escape sequences.

## Errors
- Catch and rewrite errors for humans; include a suggested fix.
- Keep signal-to-noise high; group repeated errors; put key info last.
- Avoid stack traces by default; provide `--debug` or a log file instead.
- Provide a clear path for bug reports and include a request ID or log path.

## Arguments and flags
- Prefer flags over positional args for clarity and future flexibility.
- Provide long versions of flags; short only for the most common.
- Standard flags: `-h/--help`, `--version`, `-q/--quiet`, `-v/--verbose` or `-d/--debug`,
  `-f/--force`, `-n/--dry-run`, `--json`, `-o/--output <file>`, `--no-input`.
- If `-v` is version, use `-d` for verbose or leave it unused to avoid ambiguity.
- Make the default the right thing for most users.
- Default behavior should work without prompts.
- Accept `-` for stdin/stdout in file arguments where applicable.
- Avoid arbitrary abbreviations; do not auto-expand unknown flags.
- Make flags, args, and subcommands order-independent when possible.
- For optional flag values, allow a clear sentinel like `none`.
- Do not accept secrets in flags; use stdin, files, or secret stores.

## Interactivity and safety
- Prompt only when stdin is a TTY; `--no-input` disables prompts and errors with guidance.
- Confirm dangerous actions; increase confirmation strictness for severe actions (typed name or `--confirm=...`).
- Allow escape/cancel; keep Ctrl-C responsive.
- Do not echo passwords; use the terminal's no-echo input.

## Subcommands
- Use subcommands for distinct workflows; keep naming consistent.
- Share global flags; avoid ambiguous pairs like `update` vs `upgrade`.

## Implementation notes (when asked for code)
- TypeScript/Node: prefer Commander.js for command parsing unless the user requests another framework.
- Commander v14 requires Node.js 20+ LTS; call this out when picking a runtime target.
- Commander wiring pattern: keep `src/index.ts` as a thin entrypoint that registers command modules; keep IO/formatting helpers in shared utils and route to pure functions.
- If targeting Node 20+, prefer an ESM entrypoint (`"type": "module"`); if you must support CJS consumers, use conditional `exports` with `import`/`require` entries.
- Example layout:
  - `src/index.ts`
  - `src/commands/run.ts`
  - `src/commands/review.ts`
  - `src/commands/apply.ts`
  - `src/lib/io.ts`
  - `src/lib/format.ts`

## Robustness and performance
- Validate early; fail fast with actionable messages.
- Print something within ~100ms if long work begins; show progress.
- Use timeouts for network work; retry carefully and back off.

## Future-proofing
- Avoid breaking changes; prefer additive updates.
- Deprecate with warnings; keep old flags working with aliases.
- Recommend `--plain`/`--json` for scripting and keep schemas versioned.
- Avoid catch-all subcommands that block future command names.

## Signals
- Handle Ctrl-C: exit fast with minimal cleanup; allow a second Ctrl-C to force.
- Assume the process can be restarted after an unclean exit.

## Configuration
- Precedence: flags > env > project config > user config > system.
- Use XDG base dirs for user config; keep project config in VCS.
- Get consent before modifying other tools' config; add dated comments if editing.

## Environment variables
- Uppercase names; avoid common global names; keep values single-line.
- Respect `NO_COLOR`, `TERM`, `PAGER`, `EDITOR`, `SHELL`, `TMPDIR`, `HOME`, `LINES`, `COLUMNS`.
- Support `.env` for per-project settings; do not treat it as a full config system.
- Avoid `.env` for long-term config: not usually in VCS, string-only, hard to organize, and often contains secrets.
- Do not read secrets from environment variables; use files, pipes, AF_UNIX sockets, or secret services.

## Naming
- Simple, memorable, lowercase, short, easy to type.

## Distribution and analytics
- Prefer single-binary installs or native package managers.
- Do not collect telemetry without consent; opt-in preferred and easy to disable.
