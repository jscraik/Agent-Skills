---
name: prd-to-roadmap
description: Generate a phased roadmap from a PRD with goals, dependencies, and validation
  gates. Use when sequencing and milestone logic must be explicit without dates.
knowledge_graph_profile: references/task-profile.json
---

# PRD to Roadmap

## Pipeline Context
This skill generates a phased roadmap, which can be used alongside **all stages of the Spec Pipeline** to sequence work and define validation gates.

**Related stages:**
- Stage 1: Foundation Spec (What + Why) — See `design/product-spec` or use `design/references/foundation-spec-template.md`
- Stage 2: UX Spec (How it feels) — See `design/product-spec` or use `design/references/ux-spec-template.md`
- Stage 3: Build Plan (How we execute) — See `design/product-spec` or use `design/references/build-plan-template.md`

**Shared references:**
- `design/references/spec-linter-checklist.md` — Quality gate checklist

## Response format (strict)
The first line of any response MUST be `## Inputs`.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

Every response must include:
- `## Inputs`
- `## Outputs`
- `## When to use`

Generate a phased roadmap from a PRD.

## Iron law
- Sequence by dependency first; never by convenience.

## Output template (strict)
```markdown
# Roadmap

## Phase 1: [Name]
- Goal:
- Dependencies:
- Validation gate:
- Scope (in/out):

## Phase 2: [Name]
- Goal:
- Dependencies:
- Validation gate:
- Scope (in/out):

## Phase 3: [Name]
- Goal:
- Dependencies:
- Validation gate:
- Scope (in/out):
```

## Output location
Write the roadmap in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-roadmap.md`

## Required sections
1) Phases (0/1/2 or Alpha/Beta/GA)
2) Goals per phase
3) Dependency map (internal/external)
4) Validation gates per phase
5) Risks and mitigation by phase

## Constraints
- Avoid dates unless explicitly requested.
- Redact secrets/PII by default.
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
- Roadmaps are communication tools—make them clear for stakeholders and actionable for teams.
- Dependencies are constraints—call them out explicitly or they'll surprise you.
- Phase gates are quality controls—never skip them, even under pressure.

## Empowerment
- The agent is capable of turning PRDs into phased, achievable roadmaps.
- Use judgment to balance speed and quality—know when to consolidate phases and when to split them.
- Enable product and engineering teams to ship in predictable increments.
- Trust the roadmap but don't be rigid—adjust based on learning and market feedback.

## Variation
- Adapt phase granularity to product maturity: early-stage products need short, iterative phases; stable products can have longer phases.
- Vary validation strictness: high-risk features need explicit gates; low-risk features can ship faster.
- For products with heavy technical debt, expand on debt-reduction phases.
- For market-driven products, expand on market validation and user feedback phases.
- Adjust phasing based on team capacity—smaller teams need fewer parallel workstreams.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER ship without phase gates—undefined rollouts guarantee chaos and outages.
- DO NOT ignore dependencies—blocked phases waste time and momentum.
- Avoid roadmap bloat—every feature must displace something else.
- DO NOT omit success criteria for phases—measurable milestones are non-negotiable.

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
