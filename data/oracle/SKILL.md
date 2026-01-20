---
name: oracle
description: Use the @steipete/oracle CLI to bundle a prompt plus the right files and get a second-model review (API or browser) for debugging, refactors, design checks, or cross-validation. Use when you need a second-model review with real repo context, multi-model comparisons, or browser-mode verification.
---

# Oracle (CLI) — best use

Oracle bundles your prompt + selected files into one “one-shot” request so another model can answer with real repo context (API or browser automation). Treat outputs as advisory: verify against the codebase + tests.

## When to use
- You need a second-model review with real repo context.
- You want a multi-model comparison for risk/uncertainty.
- You need browser automation runs against ChatGPT/Gemini.

## Philosophy
- Prefer minimal, high-signal context over bulk file dumps.
- Treat outputs as advisory; validate with code/tests.
- Default to API runs for reliability; use browser mode when needed.

## Anti-patterns
- Do not attach secrets or `.env` files.
- Do not re-run after a timeout; reattach to the session.
- Do not use browser automation for API-only requirements when API is available.

## Current defaults (from ~/dev/data)
- Node requirement: 22+.
- Engine auto-picks API when `OPENAI_API_KEY` is set, otherwise browser.
- Default API model: `gpt-5.1-pro` (API alias to GPT‑5.2 Pro).
- Browser model selection: use `--browser-model-strategy current` to keep the active ChatGPT model (or `ignore` to skip the picker).

## Philosophy (practical)
- Minimize scope first; add files only when necessary.
- Prefer deterministic runs; avoid browser mode unless UI or cookies are required.
- Validate outputs against source and tests; never treat them as ground truth.

## Anti-patterns (expanded)
- Do not include secrets, tokens, or `.env` files in `--file` globs.
- Do not run API mode without explicit approval due to cost.
- Do not attach large directories without a dry-run file report.

## Variation options
- Small change: add/remove `--files-report` based on budget.
- Medium change: switch engine (`api` vs `browser`) based on access and reliability.
- Large change: run multi-model comparison with `--models` when uncertainty is high.

## Empowerment
- You control the file scope: smaller sets yield sharper answers.
- You can always reattach to sessions instead of re-running.
- You can turn any run into a manual paste flow via `--render --copy`.

## Golden path (fast + reliable)
1. Pick a tight file set (fewest files that still contain the truth).
2. Preview what you’re about to send (`--dry-run summary` and `--files-report` if needed).
3. Prefer API runs for reliability; use browser runs when needed.
4. If a run detaches/timeouts: reattach to the stored session (don’t re-run).

## Output format (required)
- For browser-mode questions, include the exact flags `--engine browser` and `--browser-model-strategy current`.
- For dry-run questions, include the flag `--files-report`.
- For safety questions, include the literal strings `.env` and `secrets`.

## Commands (preferred)
- Help (once/session):
  - `npx -y @steipete/oracle --help`

- Preview (no tokens):
  - `npx -y @steipete/oracle --dry-run summary -p "<task>" --file "src/**" --file "!**/*.test.*"`
  - `npx -y @steipete/oracle --dry-run full -p "<task>" --file "src/**"`

- Token/cost sanity:
  - `npx -y @steipete/oracle --dry-run summary --files-report -p "<task>" --file "src/**"`

- API run (default when `OPENAI_API_KEY` is set):
  - `npx -y @steipete/oracle -p "<task>" --file "src/**"`
  - Add `--wait` to stay attached for GPT‑5 Pro background runs.

- Browser run (experimental):
  - `npx -y @steipete/oracle --engine browser --browser-model-strategy current -p "<task>" --file "src/**"`

- Manual paste fallback (assemble bundle, copy to clipboard):
  - `npx -y @steipete/oracle --render --copy -p "<task>" --file "src/**"`

## Files + size limits (from code)
- Default ignored dirs: `node_modules`, `dist`, `coverage`, `.git`, `.turbo`, `.next`, `build`, `tmp`.
- Honors `.gitignore` when expanding globs.
- Does not follow symlinks (`followSymbolicLinks: false`).
- Dotfiles are filtered unless explicitly included (e.g., `--file ".github/**"`).
- Hard cap: files > 1 MB are rejected.

## Models + multi-model
- Built-ins: `gpt-5.1-pro` (default), `gpt-5-pro`, `gpt-5.1`, `gpt-5.1-codex` (API-only), `gpt-5.2`, `gpt-5.2-instant`, `gpt-5.2-pro`, `gemini-3-pro`, `claude-4.5-sonnet`, `claude-4.1-opus`.
- Multi-model API run:
  - `npx -y @steipete/oracle --models gpt-5.1-pro,gemini-3-pro -p "<task>" --file "src/**"`
- OpenRouter fallback (if `OPENROUTER_API_KEY` is set and provider keys are missing): use `--base-url https://openrouter.ai/api/v1` or let Oracle infer.

## Browser mode essentials
- `--engine browser` routes through ChatGPT UI; use `--browser-model-strategy current` to keep the active model.
- Manual login: `--browser-manual-login` uses a persistent profile at `~/.oracle/browser-profile`.
- Cookie options: `--browser-inline-cookies[(-file)]`, `ORACLE_BROWSER_COOKIES_JSON/FILE`.
- Timeouts: `--browser-timeout`, `--browser-input-timeout`.
- Remote service: `oracle serve` on a signed-in host; clients use `--remote-host/--remote-token`.

## Configuration
- Defaults in `~/.oracle/config.json` (JSON5).
- Use `browser.chatgptUrl` or `--chatgpt-url` to target a ChatGPT project/folder.
- `ORACLE_ENGINE=api|browser` overrides the engine selection.

## MCP
- Run the stdio server via `oracle-mcp`.
- Example: `npx -y @steipete/oracle oracle-mcp`.

## Sessions + reattach
- Stored under `~/.oracle/sessions` (override with `ORACLE_HOME_DIR`).
- Runs may detach; reattach via `oracle status --hours 72` and `oracle session <id> --render`.
- Use `--slug "<3-5 words>"` to keep session IDs readable.

## Project-specific notes (~/dev/data/AGENTS.md)
- ChatGPT project URLs:
  - steipete@gmail.com -> `https://chatgpt.com/g/g-p-691edc9fec088191b553a35093da1ea8-oracle/project`
  - studpete@gmail.com -> `https://chatgpt.com/g/g-p-69505ed97e3081918a275477a647a682/project` (prefer if steipete project not found)
- Pro browser runs: allow up to 10 minutes; never click “Answer now”.
- gpt‑5‑pro API runs detach by default; use `--wait` to stay attached.
- Sessions live in `~/.oracle`; delete for a clean slate.
- CLI banner should start with `🧿 oracle (<version>) ...`.

## Prompt template (high signal)
Oracle starts with zero project knowledge. Include:
- Project briefing (stack + build/test commands + platform constraints).
- “Where things live” (key directories, entrypoints, config files).
- Exact question + what you tried + error text (verbatim).
- Constraints (“don’t change X”, “must keep public API”, “perf budget”).
- Desired output (“return patch plan + tests”, “list risky assumptions”).

## Safety
- Don’t attach secrets by default (`.env`, key files, tokens). Redact aggressively.
- Prefer “just enough context”: fewer files + better prompt beats whole-repo dumps.
- API runs incur usage costs; get explicit approval before launching them.
