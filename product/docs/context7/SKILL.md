---
name: context7
description: "Extract current library documentation via Context7 when users need up-to-date API details, version checks, or dependency troubleshooting for external libraries."
---

# Context7 Documentation Fetcher

Retrieve current library documentation via Context7 API.

## Philosophy

- Prefer authoritative, current docs over memory or guesses.
- Keep queries narrow and purposeful to reduce noise.
- Validate version-specific details before implementation.

## Inputs

- Library name or product name.
- Specific question or feature area (API, patterns, version behavior).
- Desired output format (txt or md).
- Token/length budget (optional).

## Outputs

- Resolved library ID from Context7.
- Targeted documentation snippets relevant to the query.
- Clarifying questions if the query is ambiguous.

## Constraints

- Never expose or echo `CONTEXT7_API_KEY`.
- Redact secrets or sensitive data in outputs by default.
- Avoid full-document dumps; return focused excerpts.
- Prefer official docs and versioned guidance when available.

## Authentication

This skill requires a Context7 API key in `CONTEXT7_API_KEY`.

Recommended setup options:
1) Export it in your shell profile (global):

```bash
export CONTEXT7_API_KEY="your-context7-key"
```

2) Use a local `.env` file (per-repo):

```bash
cp skills/context7/.env.example .env
set -a; source .env; set +a
```

## Workflow

Set `CODEX_HOME` to your Codex config directory (defaults to `~/.codex`).

### 1. Search for the library

```bash
python3 "$CODEX_HOME/skills/context7/scripts/context7.py" search "<library-name>"
```

Example:
```bash
python3 "$CODEX_HOME/skills/context7/scripts/context7.py" search "next.js"
```

Returns library metadata including the `id` field needed for step 2.

### 2. Fetch documentation context

```bash
python3 "$CODEX_HOME/skills/context7/scripts/context7.py" context "<library-id>" "<query>"
```

Example:
```bash
python3 ~/.codex/skills/context7/scripts/context7.py context "/vercel/next.js" "app router middleware"
```

Options:
- `--type txt|md` - Output format (default: txt)
- `--tokens N` - Limit response tokens

## Quick Reference

| Task | Command |
|------|---------|
| Find React docs | `search "react"` |
| Get React hooks info | `context "/facebook/react" "useEffect cleanup"` |
| Find Supabase | `search "supabase"` |
| Get Supabase auth | `context "/supabase/supabase" "authentication row level security"` |

## Validation

- Confirm the library ID matches the intended ecosystem before using results.
- If results look stale or off-target, refine the query or re-run with a narrower scope.
- Fail fast: stop at the first validation error and fix before continuing.
- See `references/contract.yaml` and `references/evals.yaml` for required outputs and eval cases.
- The output contract includes `schema_version` in `references/contract.yaml`.

## Anti-Patterns

- Guessing API behavior without checking current docs.
- Using outdated versions or deprecated endpoints.
- Sharing or logging API keys.

## Examples

- “Find the latest Next.js middleware docs.”
- “What is the current Supabase auth API for RLS?”

## When to Use

- Before implementing any library-dependent feature
- When unsure about current API signatures
- For library version-specific behavior
- To verify best practices and patterns
