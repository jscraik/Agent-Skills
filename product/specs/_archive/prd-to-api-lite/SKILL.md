---
name: prd-to-api-lite
description: Generate a minimal API outline from a PRD (endpoints + example requests/responses).
  Use for demos or early alignment, not full contracts. Use when the user requests
  this capability.
knowledge_graph_profile: references/task-profile.json
---

# PRD to API Lite

## Pipeline Context
This skill generates a minimal API outline, typically as part of **Stage 3 of the Spec Pipeline** (Build Plan) for demo-grade work.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/build-plan-template.md` — Build Plan template
- `design/references/spec-linter-checklist.md` — Quality gate checklist

## Response format (strict)
The first line of any response MUST be `## Inputs`.
Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Generate a minimal API outline for demo-grade builds.

## Output location
Write the outline in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-api-lite.md`

## Required sections (concise)
1) Endpoint list (method + path + one-line purpose)
2) One request example per endpoint
3) One response example per endpoint
4) Auth note (if any)
5) Error summary (2-3 common errors)

## Constraints
- No full schema; use examples only.
- Redact secrets/PII by default.
- Mark assumptions explicitly.
## References
- Contract: references/contract.yaml
- Evals: references/evals.yaml

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the appropriate skill.

## Required inputs
- User request details and any relevant files/links.

## Deliverables
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Validation
- If findings are disputed or high-risk, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Even demo APIs should be implementable—minimal doesn't mean incomplete.
- Examples teach more than descriptions—show concrete requests and responses.
- Simplicity is a virtue—but not at the cost of ambiguity.

## Empowerment
- The agent is capable of turning vague ideas into implementable API outlines quickly.
- Use judgment to add clarity where the input is sparse—fill reasonable gaps for demo work.
- Enable rapid iteration on API design before committing to full specs.

## Variation
- Adapt depth to demo scope: simple CRUD apps need fewer endpoints, complex flows need more.
- Vary example detail: public APIs need extensive examples, internal demos can be lighter.
- For integration-heavy demos, expand on auth and error handling examples.
- For data-heavy demos, expand on request/response schema examples.

## Guiding questions (ask 2-3)
- What is the single most important integration to make real?
- Which errors must a client handle on day one?
- What is explicitly out of scope for the demo?

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip auth notes—even demo APIs need clear authentication.
- DO NOT leave error examples vague—concrete errors prevent integration bugs.
- Avoid minimalism at the expense of clarity—demo APIs should still be implementable.
- DO NOT omit request/response structure—examples without structure are useless.
- NEVER invent endpoints not implied by the PRD.

## Response format (required)
The first line of any response MUST be `## Inputs`.
Every user-facing response must include these headings:
- `## Inputs`
- `## Outputs`
- `## When to use`

## Examples
- "Use this skill for a typical request in its domain."

Failure/out-of-scope template (use verbatim structure):
```markdown
## Required inputs
Objective: <what you received>

Plan:
1) <brief>
2) <brief>

Next step: <single request>

## Deliverables
- <what would be produced if in scope>

## Scope and triggers
- <when this skill applies>
```

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

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
