---
name: cli-spec
description: Design CLI surface area and UX (args, flags, subcommands, help, outputs, exit codes). Not for implementation or backend API design.
metadata:
  short-description: CLI spec design
---

# Create CLI

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


Design CLI surface area (syntax + behavior), human-first, script-friendly.

Gold standard rule (Jan 2026):
All guidance, decisions, and outputs must align with industry gold-standard
best practices as of Jan 31, 2026 for CLI design.

## Philosophy
- Optimize for clarity and safe automation.
- Prefer explicit contracts over clever syntax.
- Design for both humans and scripts without ambiguity.

## Guiding questions
- What is the smallest CLI surface that solves the task?
- Why is each flag or subcommand necessary?
- How will users and scripts verify success or failure?
- What are the highest-risk actions and how are they gated?

## Do This First

- Read `references/cli-guidelines.md` (condensed from clig.dev) and apply it as the default rubric.
- If TypeScript/Node code is requested, note the Commander.js preference in `references/cli-guidelines.md`.
- If designing an AI/agentic CLI, also read `references/agentic-cli-design.md`.
- For gold-standard sources, read `references/standards-dec-2025-cli.md`.
- Ask only the minimum clarifying questions needed to lock the interface.

## Clarify (fast)

Ask, then proceed with best-guess defaults if user is unsure:

- Command name + one-sentence purpose.
- Primary user: humans, scripts, or both.
- Input sources: args vs stdin; files vs URLs; secrets (never via flags).
- Output contract: human text, `--json`, `--plain`, exit codes.
- Interactivity: prompts allowed? need `--no-input`? confirmations for destructive ops?
- Config model: flags/env/config-file; precedence; XDG vs repo-local.
- Security/telemetry: how auth is provided, stored, and redacted; any analytics opt-in?
- Platform/runtime constraints: macOS/Linux/Windows; single binary vs runtime.

## Deliverables (what to output)

When designing a CLI, produce a compact spec the user can implement:

- Command tree + USAGE synopsis.
- Args/flags table (types, defaults, required/optional, examples).
- Subcommand semantics (what each does; idempotence; state changes).
- Output rules: stdout vs stderr; TTY detection; `--json`/`--plain`; `--quiet`/`--verbose`.
- Error + exit code map (top failure modes).
- Safety rules: `--dry-run`, confirmations, `--force`, `--no-input`.
- Config/env rules + precedence (flags > env > project config > user config > system).
- Help/docs ergonomics: `--help` layout, `cmd help`, docs/manpage link, shell completions if shipping.
- 5-10 example invocations (common flows; include piped/stdin examples).

## Decision ladder (flags vs subcommands vs prompts)
- Use flags for small variations in a single operation.
- Use subcommands for distinct verbs or workflows.
- Use prompts only for missing, sensitive, or destructive inputs; always allow non-interactive flags.

## Tool-use reliability (agent-focused)
Design CLIs that are easy for LLMs/tools to select and safe under partial failure.

Rules:
- Keep command names unique and non-overlapping; avoid duplicate semantics.
- Keep help text short and disambiguating; include exact inputs/outputs.
- Prefer composable subcommands over multi-step "do everything" commands.
- Always provide `--json` with a stable, versioned schema.
- Emit deterministic exit codes and machine-parseable error codes.

## Decision rubric (for agent-facing CLIs)
If the CLI will be used by agents, include this rubric in help/docs:
- Don't call the CLI if the answer is already known from context.
- Avoid redundant or destructive calls; confirm intent if unsure.
- Use the CLI only when it returns new, verifiable output.

## Context-limit aware design
- Keep command help short and distinct.
- Avoid similarly named flags with overlapping meanings.
- Use one sentence per flag that explains its effect on output.

## Output schema template (for `--json`)
- Use the stable schema in `references/json-output-schema.md`.
- Version outputs and keep changes additive.

## Exit codes and failure semantics
- `0` success
- `1` generic failure
- `2` invalid usage / validation failure
- `3` policy refusal / missing required metadata
- `4` partial success / partial failure
- `130` user abort (Ctrl-C)
- Errors must include machine-parseable codes in JSON output.

## Error code namespace
Keep error codes consistent and searchable. Use stable, prefixed codes.

Suggested set (expand as needed):
- `E_USAGE` invalid args or command misuse
- `E_VALIDATION` input validation failed
- `E_POLICY` policy refusal / missing metadata
- `E_PARTIAL` partial success / partial failure
- `E_AUTH` auth or permission failure
- `E_NETWORK` network failure or timeout
- `E_INTERNAL` unexpected internal error

## Default Conventions (unless user says otherwise)

- `-h/--help` always shows help and ignores other args.
- `--version` prints version to stdout.
- Primary data to stdout; diagnostics/errors to stderr.
- Add `--json` for machine output; consider `--plain` for stable line-based text.
- Prompts only when stdin is a TTY; `--no-input` disables prompts.
- Destructive operations: interactive confirmation + non-interactive requires `--force` or explicit `--confirm=...`.
- Respect `NO_COLOR`, `TERM=dumb`; provide `--no-color`.
- Handle Ctrl-C: exit fast; bounded cleanup; be crash-only when possible.

## Safety defaults checklist
- Default to no writes, no network, no exec unless explicitly enabled.
- Prompt only when stdin is a TTY; fail with guidance under `--no-input`.
- `--dry-run` must never change state.

## Security, privacy, and telemetry
- Never accept secrets via flags; prefer stdin, files, or OS secret stores.
- Redact secrets from logs; avoid echoing tokens in errors or debug output.
- Set safe file permissions for credential files (e.g., 0600).
- Telemetry is opt-in; provide `--no-telemetry` or env opt-out if any data is collected.

## Multi-step safety and idempotency
- Commands are idempotent by default.
- Side effects require explicit flags (`--write`, `--exec`, `--network`).
- Provide `--dry-run` and `--no-input` for safe automation.
- Ensure outputs are verifiable with stable `--plain` or `--json`.

## Resilience and performance
- Use timeouts for network work; expose `--timeout` and document defaults.
- Retry with backoff for transient failures; allow `--no-retry` or `--retry=N`.
- For large output, support pagination/limits and stable ordering.
- Emit an early progress signal if work will be long-running.

## Config precedence example
Flags > Environment > Project config > User config > System config

## Naming consistency
- Prefer verb-first subcommands (e.g., `init`, `run`, `lint`), avoid mixing verb/noun styles.
- Avoid ambiguous pairs like `update` vs `upgrade` unless clearly differentiated.

## Stdin/stdout conventions
- Accept `-` to mean stdin/stdout for file arguments where applicable.

## Logging/verbosity behavior
- `--quiet`: suppress non-essential output, keep errors.
- `--verbose`: include diagnostics and timing.
- `--debug`: include internal detail; never default to debug.

## CLI for agents checklist (optional)
- `--json` output schema is versioned and documented.
- `--plain` output is stable for line parsing.
- `--no-input` disables prompts.
- `--no-color` or respect `NO_COLOR`.
- `--quiet`, `--verbose`, `--debug` rules are defined.
- Uses `stdin`/`stdout` conventions and supports `-` for streams.

## Minimal test checklist (verification)
- Help output snapshot(s) for top-level and a subcommand.
- Exit code mapping sanity checks for common failures.
- JSON output schema validation for `--json` (including `errors[].code`).

## Templates (copy into your answer)

### CLI spec skeleton

Fill these sections, drop anything irrelevant:

1. **Name**: `mycmd`
2. **One-liner**: `...`
3. **USAGE**:
   - `mycmd [global flags] <subcommand> [args]`
4. **Subcommands**:
   - `mycmd init ...`
   - `mycmd run ...`
5. **Global flags**:
   - `-h, --help`
   - `--version`
   - `-q, --quiet` / `-v, --verbose` (define exactly)
   - `--json` / `--plain` (if applicable)
6. **I/O contract**:
   - stdout:
   - stderr:
7. **Exit codes**:
   - `0` success
   - `1` generic failure
   - `2` invalid usage / validation failure
   - `3` policy refusal / missing metadata
   - `4` partial success / partial failure
   - `130` user abort
   - (add command-specific codes only when actually useful)
8. **Env/config**:
   - env vars:
   - config file path + precedence:
9. **Docs/completions**:
   - shell completions (command or file): `mycmd completion <shell>` or `mycmd --generate-completions <shell>`
   - manpage/help docs entrypoint (if shipped): `mycmd man` or `mycmd docs`
9. **Examples**:
   - ...

### Agentic CLI skeleton (run/review/apply)

1. **Name**: `mycmd`
2. **One-liner**: `...`
3. **USAGE**:
   - `mycmd [global flags] <run|review|apply> [args]`
4. **Subcommands**:
   - `mycmd run` (plan; no side effects)
   - `mycmd review` (validate; no side effects)
   - `mycmd apply` (execute; requires explicit risk flags)
5. **Risk flags**:
   - `--write` / `--exec` / `--network`
6. **Output modes**:
   - `--plain` (default)
   - `--json` (stable schema)
7. **Exit codes**:
   - `0` success
   - `1` generic failure
   - `2` invalid usage / validation failure
   - `3` policy refusal / missing metadata
   - `4` partial success / partial failure
   - `130` user abort
8. **Examples**:
   - `mycmd run --json | mycmd review --json`
   - `mycmd apply --write`

## Language examples (uv + TS/JS)

### Python (uv + Typer)
```bash
uv add typer rich
```

```python
import typer

app = typer.Typer(no_args_is_help=True)

@app.command()
def run(json: bool = False):
    \"\"\"Plan only; no side effects.\"\"\"
    if json:
        typer.echo(\"{\\\"schema\\\":\\\"mycmd.run.v1\\\"}\")
    else:
        typer.echo(\"Plan preview\")

if __name__ == \"__main__\":
    app()
```

### TypeScript/Node (tsx + commander)
```bash
npm i commander
npm i -D tsx typescript
```

```ts
// src/index.ts
import { Command } from \"commander\";
import { registerRun } from \"./commands/run.js\";

const program = new Command();
program.name(\"mycmd\").description(\"Plan only; no side effects\");
registerRun(program);
program.parse();
```

```ts
// src/commands/run.ts
import type { Command } from \"commander\";

export function registerRun(program: Command): void {
  program
    .command(\"run\")
    .description(\"Plan only; no side effects\")
    .option(\"--json\", \"emit machine output\")
    .action((opts) => {
      if (opts.json) {
        process.stdout.write(JSON.stringify({ schema: \"mycmd.run.v1\" }));
      } else {
        process.stdout.write(\"Plan preview\\n\");
      }
    });
}
```

## Implementation guardrails (when asked for code)

- Do not produce a single-file monolith; default to a small multi-file structure (entrypoint + command modules + shared IO/utils).
- For Node/TypeScript, prefer Commander.js unless the user explicitly requests another CLI framework. Commander v14 requires Node.js 20+ LTS.
- Keep business logic out of the CLI layer; route flags/args into pure functions that are unit-testable.

## Notes

- Prefer recommending a parsing library (language-specific) only when asked; otherwise keep this skill language-agnostic.
- If the request is "design parameters", do not drift into implementation.
- When showing code, keep examples minimal and multi-file (entrypoint + commands), not a full app in one block.

## Anti-patterns to avoid
- Overloading a single command with unrelated behaviors.
- Breaking scripts by changing defaults without versioning.
- Hiding destructive behavior behind ambiguous flags.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

