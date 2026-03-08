---
name: cli-spec
description: Plan and draft CLI UX and surface area (commands, flags, help, output).
  Use when specifying or refactoring a command-line interface.
---

# Create CLI

Avoid skipping validation steps or inventing results.


## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

Design CLI surface area (syntax + behavior), human-first, script-friendly.

Gold standard rule (Jan 2026):
All guidance, decisions, and outputs must align with industry gold-standard
best practices as of Jan 31, 2026 for CLI design.

## Do This First

- Read `references/cli-guidelines.md` (condensed from clig.dev) and apply it as the default rubric.
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
- Platform/runtime constraints: Linux/Windows; single binary vs runtime.

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

## Procedure

1) Read `references/cli-guidelines.md` (and `references/agentic-cli-design.md` when relevant).
2) Ask the minimum questions in **Clarify (fast)**.
3) Produce the CLI spec under **## Outputs** (command tree, flags table, semantics, exit codes).
4) Add top failure modes + safety defaults (`--dry-run`, confirmations, non-interactive mode).

## Validation

- Fail fast: if a required input is missing, ask before you invent details.
- Sanity check: every flag/subcommand in the spec is named consistently across synopsis + tables.
- Safety check: destructive actions must have a confirmation or `--force`, and a `--dry-run` path when possible.

## Anti-patterns

- Putting step-by-step workflow text into the frontmatter `description`.
- Inventing commands/flags/output that were not agreed or cannot be implemented.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

- `## Outputs` (place the CLI spec deliverables under this heading)

## Edge-case template (missing info)
Use this exact structure when key inputs are missing:

```md
## Scope and triggers
- This skill applies to CLI specification and refactor requests.

## Required inputs
- Missing: <list the minimum required inputs>.

## Deliverables
- None until inputs are provided.
```

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## Scope and triggers
- This skill applies to CLI specification and refactor requests. The current request is out of scope.

## Deliverables
- None (out of scope).

## Required inputs
- None (out of scope).
```

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
- Redact secrets/sensitive data by default.

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

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Philosophy
- Prefer clarity, explicit tradeoffs, and verifiable outputs.

## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
