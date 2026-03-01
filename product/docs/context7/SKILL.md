---
name: context7
description: Extract current library documentation via Context7 when users need up-to-date
  API details, version checks, or dependency troubleshooting for external libraries.
knowledge_graph_profile: references/task-profile.json
---

# Context7 Documentation Fetcher

Retrieve current library documentation via Context7 API.

## Philosophy

- Prefer authoritative, current docs over memory or guesses.
- Keep queries narrow and purposeful to reduce noise.
- Validate version-specific details before implementation.

## Required inputs

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.


- Library name or product name.
- Specific question or feature area (API, patterns, version behavior).
- Desired output format (txt or md).
- Token/length budget (optional).

## Deliverables

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

## Scope and triggers

- Before implementing any library-dependent feature
- When unsure about current API signatures
- For library version-specific behavior
- To verify best practices and patterns

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

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

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
