# Agent Browser Runbook

Read when: `test-browser` has selected `agent-browser` as the execution surface and the run needs a concrete browser-ops playbook for install checks, headed or headless choice, route derivation, port detection, human verification pauses, or failure handling.

Imported from the upstream `test-browser` skill in `EveryInc/compound-engineering-plugin` commit `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`, adapted so the local `test-browser` skill stays a broader browser-verification router instead of becoming `agent-browser`-only.

## Purpose

Provide a deterministic `agent-browser` workflow for browser verification runs that are tightly tied to PR scope, branch diffs, or changed routes.

## Use `agent-browser` only when it is the chosen operator

This runbook preserves the upstream detailed `agent-browser` procedure, but the local wrapper skill still supports other browser-testing operators.

Use this runbook when:
- the user wants a reproducible CLI browser run
- the changed surface can be mapped to concrete routes
- deterministic page interaction and screenshots are the primary need

Do not force this runbook when:
- persistent local debugging is better served by `playwright-interactive`
- visual diff review is the primary signal and `ui-visual-regression` is more appropriate

## Setup and installation

Check whether `agent-browser` is available before starting:

```bash
command -v agent-browser >/dev/null 2>&1 && echo "Installed" || echo "NOT INSTALLED"
```

If installation is required and allowed:

```bash
npm install -g agent-browser
agent-browser install
```

If install is blocked or fails, stop and return the smallest unblock step instead of pretending browser verification ran.

## Headed or headless mode

When the user should choose whether to watch the browser run, ask explicitly:
- headed: visible browser window
- headless: faster background execution

Carry the choice into commands:
- headed: `agent-browser --headed ...`
- headless: `agent-browser ...`

## Scope detection

### PR number

Use the PR diff to derive changed files:

```bash
gh pr view <number> --json files -q '.files[].path'
```

### Current branch

Use the current diff against the base branch:

```bash
git diff --name-only main...HEAD
```

### Named branch

Use the named branch diff:

```bash
git diff --name-only main...<branch>
```

Turn changed files into candidate routes and then prune the list to the smallest high-signal QA matrix.

## Dev-server port detection

Use this order:
1. explicit user-provided port
2. repo instruction files such as `AGENTS.md`
3. app scripts such as `package.json`
4. environment files such as `.env.local`
5. default `3000`

Example detection flow:

```bash
PORT="${EXPLICIT_PORT:-}"
if [ -z "$PORT" ]; then
  PORT=$(grep -Eio '(port\\s*[:=]\\s*|localhost:)([0-9]{4,5})' AGENTS.md 2>/dev/null | grep -Eo '[0-9]{4,5}' | head -1)
fi
if [ -z "$PORT" ]; then
  PORT=$(grep -Eo '\\-\\-port[= ]+[0-9]{4,5}' package.json 2>/dev/null | grep -Eo '[0-9]{4,5}' | head -1)
fi
if [ -z "$PORT" ]; then
  PORT=$(grep -h '^PORT=' .env .env.local .env.development 2>/dev/null | tail -1 | cut -d= -f2)
fi
PORT="${PORT:-3000}"
```

## Server verification

Before testing routes:

```bash
agent-browser open http://localhost:${PORT}
agent-browser snapshot -i
```

If the server is not running, stop and tell the user the exact start command or port clarification needed.

## Route execution

For each target route:

```bash
agent-browser open "http://localhost:${PORT}/<route>"
agent-browser snapshot -i
```

Headed variant:

```bash
agent-browser --headed open "http://localhost:${PORT}/<route>"
agent-browser --headed snapshot -i
```

Verify:
- page heading or title
- primary content present
- no obvious error state
- required controls or form fields present

For interactions:

```bash
agent-browser click @e1
agent-browser snapshot -i
```

For evidence:

```bash
agent-browser screenshot route.png
agent-browser screenshot --full route-full.png
```

## Human verification pauses

Pause and ask the user when the flow requires:
- OAuth
- email delivery
- SMS
- payments
- external systems that cannot be safely auto-verified

Record whether the human confirmation succeeded and keep it separate from fully automated checks.

## Failure handling

When a route fails:
1. capture the failing state
2. record the exact route and reproduction step
3. ask whether to:
   - fix now
   - create a todo
   - skip and continue

This preserves the upstream decision point without forcing the local wrapper to become a bug-fixing workflow by default.

## Final summary

A strong closeout should include:
- test scope: PR, branch, or explicit routes
- server base URL
- pages tested
- pass, fail, or skip per route
- console or visible error notes
- human-verification items
- created todo artifacts, if any
- final overall result

## CLI reference

```bash
agent-browser open <url>
agent-browser back
agent-browser close
agent-browser snapshot -i
agent-browser snapshot -i --json
agent-browser click @e1
agent-browser fill @e1 "text"
agent-browser type @e1 "text"
agent-browser press Enter
agent-browser screenshot out.png
agent-browser screenshot --full out.png
agent-browser --headed open <url>
agent-browser wait @e1
agent-browser wait 2000
```

## Local adaptation notes

- The upstream skill was `agent-browser`-only.
- The local `test-browser` wrapper intentionally stays broader and can still route to `playwright-interactive` or `ui-visual-regression`.
- The detailed `agent-browser` flow is preserved here so none of the practical QA detail is lost.
