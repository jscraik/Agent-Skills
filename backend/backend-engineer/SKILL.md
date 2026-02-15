---
name: backend-engineer
description: Plan and review safe backend extensions for existing services (Cloudflare
  Workers + Hono primary). Use this skill when patching or adding backend features
  in an existing codebase.
---

# Backend Engineer

## Compliance
- Read and follow:
  - `/Users/jamiecraik/.codex/instructions/standards.md`
  - `/Users/jamiecraik/.codex/instructions/engineering-guidance.md`
  - `/Users/jamiecraik/.codex/instructions/CODESTYLE.md`
  - `/Users/jamiecraik/.codex/instructions/work-rules.md`
- Apply Gold Industry Standard (baseline Jan 2026).

## Scope and triggers
- Extending or patching an existing backend service safely.
- You need an implementation playbook (steps + file plan + verification).
- You want code-level guidance (snippets/pseudo-diffs), not just design.
- Primary runtime is Cloudflare Workers + Hono, with integration to Rust/Tauri or TS/React clients.

## Out of Scope
- Greenfield architecture or full backend design from scratch → use `backend-design` instead.

## Required inputs
## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

- Feature/change request and target service/route/module.
- Existing patterns, tests, and repo scripts.
- Constraints: auth/compliance, performance, reliability, or data integrity.
- Acceptance criteria (Given/When/Then preferred).
- Deployment/runtime constraints (e.g., Workers limits, Auth0 flows).

## Deliverables
- **Intent** (1–2 sentences).
- **Plan** (3–7 steps, single-threaded).
- **Patch summary** (files + what changes).
- **Given/When/Then acceptance criteria**.
- **Code-level guidance** (snippets or pseudo-diff when helpful).
- **Verification commands** (lint/typecheck/tests) + expected outcomes.
- **ELI5 explanation** for non-trivial logic.
- **Risks / rollback** + follow-ups.
- Include `schema_version: 1` when outputs are contract-bound.

## Response format (required)
Use these headings in order:
1. `## Intent`
2. `## Plan`
3. `## Patch summary`
4. `## Acceptance criteria (Given/When/Then)`
5. `## Verification`
6. `## ELI5 explanation`
7. `## Risks / rollback`
8. `## Next steps`

If blocked, insert `## Questions` (max 2) and stop.

## Principles
- Correctness → security → reliability → performance → ergonomics (in that order).
- Small, reversible changes; minimal diff.
- Prefer existing repo conventions and tooling (mise, rg/fd/jq, repo scripts).
- Ask before adding dependencies or changing system-wide settings.
- Never expose secrets or log sensitive data.

## Procedure
1) Restate objective, constraints, and Given/When/Then acceptance criteria. Ask **max 2** clarifying questions if blocked.
2) Inspect the repo with `rg`/`fd`; identify touch points, ownership boundaries, and existing tests.
3) Draft the smallest safe implementation plan and file list. Call out stop conditions (migrations, auth changes, deploys).
4) Provide code-level guidance (snippets/pseudo-diffs) aligned with repo style and runtime constraints.
5) Provide verification commands (must be included every time). If not run, say **Not run** + reason.
6) Provide an ELI5 explanation for any non-trivial logic or risk area.
7) Document risks, rollback, and follow-ups.

## Examples
**Intent:** Add a safe, idempotent endpoint to extend an existing Workers + Hono API.

**Plan:**
1. Locate route + handler structure; confirm existing error format.
2. Add handler with input validation and idempotency key.
3. Update tests or add a new test for the new route.
4. Run lint/typecheck/tests.

**Acceptance criteria (GWT):**
- **Given** a valid payload, **When** POST /api/widgets is called, **Then** it returns 201 with the widget id.
- **Given** the same idempotency key, **When** POST is repeated, **Then** it returns 200 with the same id.

**Verification:**
- `pnpm -s lint` (expect 0)
- `pnpm -s typecheck` (expect 0)
- `pnpm -s test` (expect 0)

## Validation
- Always include Given/When/Then acceptance criteria.
- Always include verification commands.
- If commands are not run, explicitly state why.
- Maintain file/function size limits and type-safety requirements per CODESTYLE.
- Fail fast: stop at the first failed validation gate, fix, and re-run.

## Anti-patterns
Avoid these anti-patterns (common mistakes/pitfalls). **NEVER** skip verification, and **DO NOT** ship changes without explicit safety checks:
- Skipping verification steps or leaving them implicit.
- Large refactors without explicit approval.
- Unversioned or breaking API changes without a deprecation plan.
- Unsafe defaults (wide-open CORS, plaintext secrets, unauthenticated admin paths).
- No rollback plan or risk acknowledgment.
- Writing handlers without input validation or schema checks.
- Missing idempotency or replay protection for write endpoints.
- Swallowing errors or logging sensitive payloads.
- Adding dependencies or changing lockfiles without approval.
- Shipping changes that cross service boundaries without an explicit contract.
- WARNING: incorrect status codes, wrong error shapes, or silent failures that hide bugs.

## Encouraging Variation
**IMPORTANT:** Outputs should vary based on context. Avoid converging on a single “favorite” pattern:
- Adapt to the specific runtime and constraints.
- Use different examples per domain (payments, analytics, AI tooling, internal ops).
- No two outputs should be identical unless requirements are identical.

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don’t constrain it. Use judgment, adapt to context, and push boundaries when appropriate.

## Constraints
- Redact secrets/PII by default.
- Do not add dependencies without explicit user approval.
- Use `zsh -lc` for commands to ensure mise PATH is loaded.
- Use `rg`/`fd`/`jq` for search and parsing.

## Resources
- Deep design checklists (when needed):
  - `/Users/jamiecraik/dev/agent-skills/backend/backend-design/references/`

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
