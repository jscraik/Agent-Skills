---
name: project-improvement-ideator
description: Generate, score, and winnow project improvement ideas into a top 5 with
  impact/effort notes. Use when asked for roadmap ideas, prioritization, or improvement
  brainstorming.
---

# Project Improvement Ideator

Concise workflow to brainstorm broadly (30 ideas) and converge to the top 5 that are impactful, feasible, and aligned.

- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md.
- Keep outputs concise and decision-oriented; avoid boilerplate.

## Quick mental model
- Axes: Impact × Feasibility × Alignment × Time-to-value × Risk.
- Audience lenses: developers, ops/sec, users/stakeholders.
- Favor ideas that are incremental yet defensible (“gold standard” ready).

## Steps (high freedom)
1) Clarify context (if missing: stack, user goals, constraints). Assume current repo state otherwise.
2) Generate 30 ideas rapidly (bullets, 1 line each). Cover breadth: reliability, performance, security, DX, UX, governance, observability.
3) Expand each idea briefly: user perception, how it works, implementation sketch, risk/mitigation (1–2 lines).
4) Score each idea (1–5) on: Impact, Feasibility, Alignment, Time-to-value. Note major risks if any.
5) Winnow: sort by composite score (tie-breaker = lower risk / faster value). Select top 5.
6) Present the 5 in rank order with: title, why it helps (1–2 sentences), how to implement (1–3 bullets), risks/mitigations (1 bullet).
7) (Optional) Provide a short next-step plan (MVP slice) if requested.

## Output format
- Section “Top 5 (ranked)” with the details above.
- Section “Scoring summary” (table or bullets with scores).
- Keep the full 30 ideas list concise; include it after the top 5.

## Guardrails
- No new deps unless explicitly justified and low risk.
- Prefer incremental changes; call out when an idea is a larger initiative.
- Note if any idea depends on unpublished/private assets or policies.
- Keep assumptions explicit (dates, environments, platforms).

## References
- Contract: references/contract.yaml
- Evals: references/evals.yaml

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Required inputs
- User request details and any relevant files/links.


## Deliverables
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.

## Examples
- "Provide a concise response for this task."
- "Follow the workflow and summarize outputs."

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

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
