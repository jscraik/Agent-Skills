---
name: agentation
description: Audit or troubleshoot Agentation integrations in frontend apps with deterministic evidence gathering before edits. Use when annotations, MCP registration, endpoint sync, or webhook delivery are failing.
metadata:
  skill-type: product_verification
---

# Agentation Integration + Live Annotation Workflows

## When to use
- A user wants to install or verify Agentation in a frontend app.
- A user reports missing annotations, missing MCP tools, endpoint drift, or webhook delivery gaps.
- A user asks for watch mode, critique mode, or self-driving workflow readiness.
- A user needs deterministic evidence before any integration edits.

## Required inputs
- Target project root (repo-relative path).
- Runtime context (`next-app-router`, `next-pages-router`, `vite-react`, or equivalent shell).
- Target mode (`manual`, `watch`, `critique`, `self-driving`).
- Change posture (`verify-only` or `allow-edits`).
- Scope slice (`mount`, `endpoint`, `mcp`, `webhook`, or `full`).

## Deliverables
- Scoped diagnostic plan for:
  - dependency + root mount
  - endpoint sync
  - MCP registration/health
  - webhook submit path
  - mode readiness
- Layer status per item: `pass`, `blocked`, or `partial`.
- Structured recommendation for each blocker before any edit is suggested.
- Include an explicit `schema_version` in output contracts.

## Procedure
1. Start from the smallest viable layer (`mount` first, then `endpoint`, then `mcp`, then `webhook`, then `mode`).
2. Keep control-plane and data-plane checks separate.
3. Propose one deterministic next action for the first confirmed blocker only.
4. Report layered status and request permission before scope expansion.

## Validation
- Validation must include command evidence or explicit reason when evidence cannot be collected.
- If any required layer is blocked, return a partial result instead of claiming completion.
- Validation is fail-fast: stop at the first hard blocker and request confirmation before proceeding.

## Anti-patterns
- Treating mount, endpoint, MCP, and webhook checks as one monolithic step.
- Claiming production readiness from verification-only checks.
- Expanding to multiple layers before baseline checks complete.
- Suggesting edits when required validation is blocked.

## Constraints
- Keep Agentation in development-only mode unless explicitly changed by the user.
- Redact secrets, tokens, and credentials by default.
- Preserve conservative rollback posture and exact scope boundaries.

## Philosophy
- Separate concerns between integration planes (mount, endpoint, MCP, webhook, mode).
- Prefer deterministic evidence over assumption.
- Escalate scope only after the first blocker is resolved.

## Examples
- "When a user says: annotations aren't appearing for three minutes in this Next.js app, can you inspect the mount and endpoint checks and tell me the next best step?"
- "User asks for validation of webhook delivery in a Vite app but wants no file changes unless the diagnostics confirm a blocker."
- "Can you check that `next-app` annotation MCP registration and submit delivery are working after a deployment, then summarize risks."

## Variation
- Vary by intent: do a narrow one-layer verification path first, then offer a controlled expansion pass if the first layer confirms a deterministic blocker.

## References
- Runtime/state model and public contract docs:
  - `Infrastructure/references/contract.yaml`
  - `Infrastructure/references/public-sources.md`
  - `Infrastructure/references/watch-mode-state-machine.md`
  - `Infrastructure/references/annotation-format.md`
- `Infrastructure/references/evals.yaml` for expected behavior and safety checks.
- Deterministic helper: `Infrastructure/scripts/check_watch_mode_readiness.py`.

## Failure mode
- If the current layer cannot be validated because inputs, local setup, or runtime evidence are missing, stop at that layer, report the exact blocker, and fall back to the nearest smaller verification slice rather than proposing edits blindly.

## Gotchas
- Symptom: annotations never appear, even though the frontend renders. Cause: mount validation was skipped and the session started at endpoint or webhook layers first. Do instead: re-check the root mount and client bootstrap before investigating control-plane delivery. Check: confirm the app renders the Agentation mount in the intended runtime and that the smallest layer passes before expanding scope.

## See Also
| Skill | When to use |
|---|---|
| [[agent-browser]] | Run deterministic browser interactions against the app once Agentation wiring is healthy |
| [[playwright-interactive]] | Use a persistent Playwright session for iterative local inspection or debugging |
| [[frontend-ui-design]] | Improve or redesign the frontend surface after the integration path is verified |
| [[visual-explainer]] | Turn the integration state machine or failure path into a visual handoff artifact |

**Topic map:** [[frontend-ui]]
