---
name: writing-plans
description: Compatibility wrapper for generic implementation planning. Use when the user asks for a general plan and route the work to `ce-plan` in `generic-plan` mode.
metadata:
  skill-type: team_automation

---

# Writing Plans

This skill has been folded into [`ce-plan`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md). Keep this wrapper only for compatibility and route execution-planning work to `ce-plan` using `generic-plan` mode.

## Standards snapshot (March 2026)
- `ce-plan` is now the canonical owner for execution-planning behavior.
- Preserve this wrapper only so older references and invocations still land in the right place.
- Do not maintain a second independent planning doctrine here.

## When to use
- The user asks for `writing-plans` explicitly.
- Older docs or neighboring skills still reference `writing-plans`.
- The request is really generic implementation sequencing and should be handled by `ce-plan` in `generic-plan` mode.

## When not to use
- Do not author a separate planning workflow here.
- Do not keep this wrapper as a competing owner beside `ce-plan`.
- Do not use this wrapper when the caller can go straight to [`ce-plan`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md).

## Required inputs
- The same planning inputs that `ce-plan` expects for `generic-plan` mode:
  - requirements, spec, or explicit user goal;
  - repository context and likely impacted areas;
  - constraints such as timeline, rollout risk, approvals, or compatibility expectations.

## Deliverables
- Immediate routing to [`ce-plan`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md) with `generic-plan` selected.
- No separate planning doctrine, checklist, or artifact contract beyond what `ce-plan` already owns.

## Failure mode
- If the request is still ambiguous, route to `brainstorming` or `ce-brainstorm` instead of improvising a plan here.
- If `ce-plan` cannot safely proceed, surface the same blocker rather than inventing wrapper-specific logic.

## Workflow
1. Detect that the request is generic implementation planning rather than a different upstream stage.
2. Route immediately to [`ce-plan`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md).
3. Use `generic-plan` mode there.
4. Preserve this wrapper only as a compatibility entrypoint.

## Validation
- Verify this wrapper does not drift into a second independent planning workflow.
- Verify routing points to [`ce-plan`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md) as the canonical owner.
- Fail fast if this wrapper starts to diverge from `ce-plan` behavior.

## Anti-patterns
- Keeping a full second planning doctrine here after the fold.
- Letting neighboring skills keep routing generic planning work here as the primary owner.
- Adding wrapper-only logic that `ce-plan` does not own.

## Constraints
- Redact secrets, tokens, and sensitive material in examples and artifacts.
- Keep this wrapper compatibility-only.
- Do not execute destructive commands while planning.

## Philosophy
- One planning owner is better than two near-identical planning owners.
- Compatibility wrappers are acceptable; duplicate doctrine is not.

## Variation
- None here; variation now belongs to `ce-plan` modes.

## Examples
- "Use writing-plans to break this feature into implementation steps." -> route to `ce-plan` with `generic-plan`.
- "Turn this approved PRD into an execution plan." -> route to `ce-plan` with `generic-plan` unless the user explicitly wants product-planning work first.

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/folded-legacy-modes-core60.md`
- `references/folded-legacy-modes-phase4.md`

## Folded legacy mode
Legacy execution-planning behavior is now owned by `ce-plan` as the canonical planner.

## See Also

| Skill | When to use together |
|---|---|
| [[brainstorming]] | Use first when scope is still ambiguous — resolve approach before planning steps |
| [[interview-me]] | Use when requirements need discovery before routing to `ce-plan` |
| [[product-spec]] | Use for product-level specs before routing to `ce-plan` |
| [[ce-plan]] | Canonical owner of both generic and CE execution-planning behavior |
| [[verification-before-completion]] | Embed in the plan's final task to gate "done" claims |
| [[systematic-debugging]] | When 3+ fix attempts fail, restart with this skill to re-plan the approach |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v2 -->

**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
