---
name: context7
description: "Analyze current external library/API documentation and generate Context7 CLI guidance when the user asks for version-sensitive dependency behavior, library API references, or Context7 skills/setup/auth command help."
metadata:
  skill-type: library_api_reference
---

# Context7 Docs + Skill Wizard

Retrieve current external library documentation via Context7 so implementation guidance is grounded in current docs instead of memory, and support explicit Context7 CLI requests (`ctx7 library|docs|skills|setup|login|whoami`).

## When to use

- Use this skill when the user needs current external library or framework documentation.
- Use this skill when the user explicitly asks for Context7 CLI flows such as `ctx7 skills generate`, `ctx7 skills install`, `ctx7 skills suggest`, or `ctx7 setup`.
- Use this for version-sensitive API behavior, dependency troubleshooting, and skill-wizard install target guidance.
- Use this when docs lookup should run CLI-first with MCP as a backup retrieval path.
- Do not use it for OpenAI platform docs; route those to `openai-docs`.

## Philosophy

- Prefer current-source documentation over memory for drift-prone dependency behavior.
- Run CLI-first with explicit command safety and fallback behavior.
- Keep answers implementation-shaped and directly tied to the user’s concrete task.

## Required inputs

- For docs lookup: library or product name, implementation question, optional version constraints.
- For skill wizard: requested action (`search|install|list|remove|suggest|info|generate|setup|login|whoami|logout`) and target scope.
- For secure CLI execution: prefer `op run --env-file ~/.codex/.env -- ctx7 ...`.
- For exact flag mapping and command forms, use `references/context7-skill-wizard.md`.

## Deliverables

- Docs lookup outputs:

1. Resolved Context7 library id.
2. Focused docs-backed answer tied to the user question.
3. Source basis (documentation source or retrieval context).
4. Explicit assumptions or ambiguity notes when needed.
5. Execution path used (`cli_primary`, `mcp_backup`, or `api_backup`) and fallback reason when not CLI-primary.

- Skill wizard outputs:

1. Exact `ctx7` command(s).
2. Selected target flags and scope (`project` vs `global`).
3. Source basis (command documentation or CLI reference).
4. Post-install verification commands and restart reminder when applicable.

## Workflow

### Lane A: Docs lookup (CLI primary, MCP/API backup)

1. Run CLI-first using secure env injection:
   - `op run --env-file ~/.codex/.env -- ctx7 library <name> "<query>" --json`
   - `op run --env-file ~/.codex/.env -- ctx7 docs <libraryId> "<query>" --json`
2. If CLI is unavailable or blocked, use MCP backup:
   - `mcp__context7__resolve_library_id`
   - `mcp__context7__query_docs`
3. If both CLI and MCP are unavailable, use API backup with local helper:
   - `op run --env-file ~/.codex/.env -- python3 Infrastructure/scripts/context7.py search <library_name> --query "<query>"`
   - `op run --env-file ~/.codex/.env -- python3 Infrastructure/scripts/context7.py context <library_id> "<query>" --type md`
4. Answer from retrieved docs and label any inference as inference.

### Lane B: Skill wizard / CLI

1. Match the user request to the correct `ctx7` command and options.
2. For generation flows, default to secure invocation:
   - `op run --env-file ~/.codex/.env -- ctx7 skills generate`
3. Include setup/auth flows when requested:
   - `ctx7 setup`, `ctx7 login`, `ctx7 whoami`, `ctx7 logout`
4. Include verification commands (`ctx7 skills list ...`) and restart guidance.
5. For option/flag uncertainty, use `references/context7-skill-wizard.md` rather than guessing.

## Failure mode

- If no good library match exists, ask for minimum clarification instead of guessing.
- If quota is exhausted, state that explicitly, recommend `ctx7 login`, and use API backup if available.
- If the request is skill-install/generate and CLI is unavailable, report the blocker explicitly instead of inventing MCP alternatives.

## Constraints

- Redact secrets, tokens, credentials, and sensitive data by default.
- Never expose or echo `CONTEXT7_API_KEY`.
- Treat network access as limited to the Context7 documentation service and returned library metadata.
- Network allowlist for `Infrastructure/scripts/context7.py`: only `context7.com` and `api.context7.com` over HTTPS.
- Prefer focused excerpts over full-document dumps.
- Do not invent `ctx7` options that are not listed in `references/context7-skill-wizard.md`.

## Validation

- Fail fast: stop at the first failed gate, fix it, then continue.
- Confirm the library id matches the intended ecosystem before using results.
- If results look stale or off-target, refine the query or re-run with narrower scope.
- Cap retrieval attempts per user question:
  - max 3 `library` resolution attempts
  - max 3 `docs` retrieval attempts
- For wizard requests, confirm command/flag correctness against `references/context7-skill-wizard.md`.
- For `skills install`, enforce repository format `/owner/repo`.
- See `references/contract.yaml` and `references/evals.yaml` for required outputs and eval cases.
- For schema-bound outputs, include `schema_version` in the response contract.

## Examples

- "When the user asks: We just upgraded Next.js and middleware stopped matching. What is the current matcher pattern to exclude static assets and API routes?"
- "User says: Our Supabase RLS policy works locally but fails in prod after a bump. Pull current docs and show the service-role-safe pattern."
- "Can you help me generate a custom skill for OAuth hardening with `op run --env-file ~/.codex/.env -- ctx7 skills generate`, and explain where it installs?"
- "Can you install every skill from `/anthropics/skills` for both Cursor and Codex, then show me how to validate the install?"
- "Can you set up Context7 in MCP mode for Codex, and confirm auth is active?"

## Anti-patterns

- Guessing API behavior without checking current docs.
- Using outdated versions or deprecated endpoints without calling that out.
- Dumping large doc excerpts instead of answering the user’s actual question.
- Treating a weak library match as authoritative.
- Inventing wizard subcommands/flags without reference validation.

## See Also

| Skill                | When to use together                                    |
| -------------------- | ------------------------------------------------------- |
| [[openai-docs]]      | Use OpenAI docs MCP for OpenAI-specific library content |
| [[docs-expert]]      | Combine repo documentation context with Context7 library docs |
| [[mcp-builder]]      | Reference Context7 docs when building MCP tool schemas  |
| [[backend-engineer]] | Use Context7 to check API docs during backend work      |

**Topic map:** [[product-strategy]]

## References and assets

- Open the execution contract: `references/contract.yaml`
- Open eval coverage and adversarial cases: `references/evals.yaml`
- Open Context7 CLI wizard command map and options: `references/context7-skill-wizard.md`
- Open extended strategy and fallback decision notes: `references/decision-guidance.md`
- Task profile for graph/runtime metadata: `references/task-profile.json`
- Local helper script: `Infrastructure/scripts/context7.py`
- Skill visual asset: `assets/context7.png`
- OpenAI Apps metadata and icons: `agents/openai.yaml`, `agents/assets/icon-small.png`, `agents/assets/icon-large.png`

<!-- decision-feedback-protocol:v2 -->

**Decision feedback protocol (required):**

- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas

- `ctx7 skills generate` requires login and usually works best via `op run --env-file ~/.codex/.env -- ctx7 skills generate`.
- Docs lookup can fall back to MCP or API, but skill install/generate flows remain CLI-only.
- Skill wizard installs may require agent restart to appear in discovery lists.
