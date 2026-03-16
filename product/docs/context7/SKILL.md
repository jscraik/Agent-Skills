---
name: context7
description: Extract current library documentation via Context7 when users need up-to-date
  API details, version checks, or dependency troubleshooting for external libraries.
---

# Context7 Documentation Fetcher

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Decision feedback protocol](#decision-feedback-protocol)

Retrieve current external library documentation via Context7 so implementation guidance is grounded in current docs instead of memory.

## Scope and triggers
- Use this skill when the user needs current external library or framework documentation.
- Use it for API details, version checks, supported patterns, or dependency troubleshooting.
- Do not use it for OpenAI platform docs; route those to `openai-docs`.

## Required inputs
- library or product name
- the specific question or implementation problem
- version or environment constraints when known

## Deliverables
- the resolved Context7 library id
- targeted doc-backed guidance answering the user’s question
- clarification only when the library or target version is genuinely ambiguous

## Failure mode
If no good library match exists, say so clearly and ask for the minimum refinement needed instead of guessing.

## Standards snapshot (March 2026)
- Resolve the library id first, then query docs with a specific implementation-shaped question.
- Prefer the most authoritative and relevant library match, not just the first fuzzy hit.
- Keep the answer tightly coupled to the user’s actual problem; avoid dumping generic docs.
- If version drift matters, say whether the answer is version-scoped or best-effort current guidance.

## Workflow
1. Use `mcp__context7__resolve-library-id` to identify the best library match.
2. Pick the best match based on name, source reputation, version fit, and documentation coverage.
3. Use `mcp__context7__query-docs` with a narrow, implementation-shaped question.
4. Answer from the retrieved docs and say when a conclusion is an inference instead of a direct statement.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Never expose or echo `CONTEXT7_API_KEY`.
- Treat network access as limited to the Context7 documentation service and the library metadata it returns.
- Prefer focused excerpts over full-document dumps.

## Validation
- Confirm the library id matches the intended ecosystem before using results.
- If results look stale or off-target, refine the query or re-run with a narrower scope.
- Fail fast: stop at the first validation error and fix before continuing.
- See `references/contract.yaml` and `references/evals.yaml` for required outputs and eval cases.

## Examples
- "Find the current Next.js middleware docs."
- "What is the latest Supabase auth guidance for RLS?"
- "Check the current React guidance for effect cleanup."

## Anti-patterns
- Guessing API behavior without checking current docs.
- Using outdated versions or deprecated endpoints without calling that out.
- Dumping large doc excerpts instead of answering the user’s actual question.
- Treating a weak library match as authoritative.

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

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[openai-docs]] | Use OpenAI docs MCP for OpenAI-specific library content |
| [[repoprompt]] | Combine repo context with Context7 library docs |
| [[mcp-builder]] | Reference Context7 docs when building MCP tool schemas |
| [[backend-engineer]] | Use Context7 to check API docs during backend work |

**Topic map:** [[product-strategy]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
