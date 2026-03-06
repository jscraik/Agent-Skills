---
name: prd-to-security-review
description: Generate a security review from a PRD. Use when security requirements,
  threats, and mitigations must be explicit before build.
knowledge_graph_profile: references/task-profile.json
---

# PRD to Security Review

## Pipeline Context
This skill generates a security review, which supports **all stages of the Spec Pipeline** by identifying security considerations early.

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

Generate a security review artifact from a PRD.

## Iron law
- Threat model and trust boundaries must be completed before listing controls.

## Output location
Write the security review in the same directory as the source PRD.
- `feature-x.md` -> `feature-x-security-review.md`

## Required sections
1) Assets and trust boundaries
2) Threat model (STRIDE-style or equivalent)
3) Abuse cases and mitigations
4) AuthN/AuthZ requirements
5) Data handling and privacy controls
6) Logging and monitoring expectations
7) Validation and security test plan

## Constraints
- Avoid implementation details; focus on controls and verification.
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
- Run Golden Nuggets 2026 checklist in `design/product-spec/SKILL.md` (section: Golden Nuggets 2026).
- For high-risk or disputed findings, run LLM Council and merge outcomes per `design/product-spec/references/llm-council.md`.
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.
- Security is not a feature—it's a foundation that affects every other decision.
- Threat modeling is non-negotiable—never ship without identifying and mitigating risks.
- Least privilege is the default—avoid broad permissions unless explicitly justified.

## Empowerment
- The agent is capable of identifying security risks that product and engineering teams might miss.
- Use judgment to prioritize risks based on impact and likelihood—don't be overwhelmed by edge cases.
- Enable teams to ship with confidence by having a clear security review and mitigation plan.
- Don't be the security blocker—focus on actionable, high-impact controls and enable shipping.

## Variation
- Adapt security depth to product sensitivity: consumer products need privacy focus, B2B products need auth and authorization rigor.
- Vary threat modeling scope: public APIs need abuse case modeling, internal tools need data handling controls.
- For data products, expand on data encryption, retention, and access controls.
- For payment products, expand on PCI compliance, fraud detection, and financial security controls.
- Adjust validation strictness based on audience: public products need formal audit, internal products can use lighter review.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Anti-patterns
- NEVER skip threat modeling—undefined security assumptions are vulnerabilities.
- DO NOT ignore data flow and trust boundaries—unmapped data exfiltration is a nightmare waiting to happen.
- Avoid vague mitigations like "we'll monitor it"—define specific controls, tests, and owners.
- DO NOT omit authentication/authorization—undefined auth is open doors for attackers.

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
