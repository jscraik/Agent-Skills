---
name: context7
description: "Retrieve current third-party library docs and Context7 Skill Wizard command guidance; use this skill when users need version-sensitive dependency answers or explicit `ctx7 skills` generate/install/list help."
metadata:
  skill-type: library_api_reference
---

# Context7 Docs + Skill Wizard

Retrieve current external library documentation via Context7 so implementation guidance is grounded in current docs instead of memory, and support explicit `ctx7 skills` requests (search/install/list/remove/suggest/info/generate).

## When to use
- Use this skill when the user needs current external library or framework documentation.
- Use this skill when the user explicitly asks for Context7 CLI flows such as `ctx7 skills generate`, `ctx7 skills install`, or `ctx7 skills suggest`.
- Use this for version-sensitive API behavior, dependency troubleshooting, and skill-wizard install target guidance.
- Do not use it for OpenAI platform docs; route those to `openai-docs`.

## Philosophy
- Prefer current-source documentation over memory for drift-prone dependency behavior.
- Keep answers implementation-shaped and directly tied to the user’s concrete task.
- For CLI flows, prioritize command correctness and target-flag safety over verbosity.

## Required inputs
- For docs lookup: library or product name, implementation question, optional version constraints.
- For skill wizard: expertise target, requested action (`search|install|list|remove|suggest|info|generate`), and install target scope.
- For exact flag mapping, use `references/context7-skill-wizard.md`.

## Deliverables
- Docs lookup outputs:
1. Resolved Context7 library id.
2. Focused docs-backed answer tied to the user question.
3. Source basis (documentation source or retrieval context).
4. Explicit assumptions or ambiguity notes when needed.
- Skill wizard outputs:
1. Exact `ctx7 skills` command(s).
2. Selected target flags and scope (`project` vs `global`).
3. Source basis (command documentation or CLI reference).
4. Post-install verification commands and restart reminder when applicable.

## Workflow

### Lane A: Docs lookup
1. Use `mcp__context7__resolve-library-id` to identify the best library match.
2. Use `mcp__context7__query-docs` with a narrow, implementation-shaped question.
3. Answer from retrieved docs and label any inference as inference.

### Lane B: Skill wizard / CLI
1. Match the user request to the correct `ctx7 skills` subcommand and options.
2. Generate command(s) that preserve user intent and install target scope.
3. Include verification commands (`ctx7 skills list ...`) and any restart guidance.
4. For option/flag uncertainty, use `references/context7-skill-wizard.md` rather than guessing.

## Failure mode
If no good library match exists, or wizard command intent is ambiguous, ask for the minimum clarification instead of guessing.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Never expose or echo `CONTEXT7_API_KEY`.
- Treat network access as limited to the Context7 documentation service and the library metadata it returns.
- Network allowlist for `scripts/context7.py`: only `context7.com` and `api.context7.com` over HTTPS.
- Prefer focused excerpts over full-document dumps.
- Do not invent `ctx7` options that are not listed in `references/context7-skill-wizard.md`.

## Validation
- Confirm the library id matches the intended ecosystem before using results.
- If results look stale or off-target, refine the query or re-run with a narrower scope.
- Fail fast: stop at the first validation error and fix before continuing.
- For wizard requests, confirm command/flag correctness against `references/context7-skill-wizard.md`.
- See `references/contract.yaml` and `references/evals.yaml` for required outputs and eval cases.
- For schema-bound outputs, include `schema_version` in the response contract.

## Examples
- "When the user asks: We just upgraded Next.js and middleware stopped matching. What is the current matcher pattern to exclude static assets and API routes?"
- "User says: Our Supabase RLS policy works locally but fails in prod after a bump. Pull current docs and show the service-role-safe pattern."
- "Can you help me generate a custom skill for OAuth hardening with `ctx7 skills generate`, and explain where it installs?"
- "Can you install every skill from `/anthropics/skills` for both Cursor and Claude, then show me how to validate the install?"

## Anti-patterns
- Guessing API behavior without checking current docs.
- Using outdated versions or deprecated endpoints without calling that out.
- Dumping large doc excerpts instead of answering the user’s actual question.
- Treating a weak library match as authoritative.
- Inventing wizard subcommands/flags without reference validation.

## See Also

| Skill | When to use together |
|---|---|
| [[openai-docs]] | Use OpenAI docs MCP for OpenAI-specific library content |
| [[repoprompt]] | Combine repo context with Context7 library docs |
| [[mcp-builder]] | Reference Context7 docs when building MCP tool schemas |
| [[backend-engineer]] | Use Context7 to check API docs during backend work |

**Topic map:** [[product-strategy]]

## References and assets
- Open the execution contract: `references/contract.yaml`
- Open eval coverage and adversarial cases: `references/evals.yaml`
- Open Context7 CLI wizard command map and options: `references/context7-skill-wizard.md`
- Open extended strategy and decision notes moved out of SKILL.md: `references/decision-guidance.md`
- Task profile for graph/runtime metadata: `references/task-profile.json`
- Local helper script: `scripts/context7.py`
- Skill visual asset: `assets/context7.png`
- OpenAI Apps metadata and icons: `agents/openai.yaml`, `agents/assets/icon-small.png`, `agents/assets/icon-large.png`

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- Skill wizard installs may require agent restart to appear in discovery lists.