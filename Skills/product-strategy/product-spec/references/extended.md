# Extended guidance

## Philosophy
- Evidence-led: clarify problem/users/metrics before solutioning; debate until consensus `[AGREE]`.
- Interview-first when uncertain; make assumptions explicit and testable.
- Visual-first: diagrams-as-code to prevent ambiguity.
- Safety-first: default to least privilege, avoid secrets, and redact sensitive info in prompts/outputs.
- **Pipeline-driven:** Foundation → UX → Build Plan ensures clarity, removes ambiguity, yields executable plans.
- **Tests are the truth:** TDD is non-negotiable for non-trivial work. Code without tests is not complete.
- **Design system first:** Prefer existing components over building from scratch; component registry prevents divergence.
- **Vibe engineering:** Combine design system + TDD to make AI output trustworthy and maintainable.

## Required inputs
- User-chosen document type (`PRD` or `tech`).
- Starting point: file path to existing spec or new concept description.
- Optional: focus areas (security, scalability, performance, ux, reliability, cost), opponent models, interview mode preference.
- All inputs must exclude secrets/PII; redact if present.

## Deliverables
- **Foundation Spec** (`.spec/foundation-YYYY-MM-DD-<slug>.md`) — What + Why
- **UX Spec** (`.spec/ux-YYYY-MM-DD-<slug>.md`) — How it feels
- **Build Plan** (`.spec/build-plan-YYYY-MM-DD-<slug>.md`) — How we execute
- (Optionally) Traditional PRD or tech spec following templates, with Mermaid/PlantUML diagrams inline.
- Explicit assumptions, risks, and out-of-scope items called out.
- Evidence included per paragraph (`Evidence:` or `Evidence gap:`) plus `Evidence Gaps` and `Evidence Map` sections.
- Never write or edit `prd.json` directly; the compiler owns it.
- Include `schema_version: 1` when outputs are contract-bound.

## Response format (required)
Every user-facing response must include these headings:
- `## Inputs`
- `## Outputs`
- `## When to use`
And in `## Outputs`, include a bullet that contains the exact text `Evidence Map`.
If the request is out of scope or refused, still include all three headings.
The first line of any response MUST be `## Inputs`.

Failure/out-of-scope template (use verbatim structure):
```markdown
## Required inputs
Objective: <what you received>

Plan:
1) <brief>
2) <brief>

Next step: <single request>

## Deliverables
- Evidence Map
- <what would be produced if in scope>

## Scope and triggers
- <when this skill applies>
```

## Validation
- Prefer the local venv if present:
  - `Skills/skill-builder/.venv/bin/python Skills/skill-builder/Infrastructure/scripts/quick_validate.py design/product-spec`
  - `Skills/skill-builder/.venv/bin/python Skills/skill-builder/Infrastructure/scripts/skill_gate.py design/product-spec`
- If the venv is missing, fall back to system Python 3.11:
  - `/opt/homebrew/bin/python3.11 Skills/skill-builder/Infrastructure/scripts/quick_validate.py design/product-spec`
  - `/opt/homebrew/bin/python3.11 Skills/skill-builder/Infrastructure/scripts/skill_gate.py design/product-spec`
- If validation scripts are not present in the repo, report "not run" with the reason and proceed; do not block or ask for a choice.
- For spec output linting: run `Infrastructure/scripts/evidence-map.py --input <spec>.md --append-missing --update-map --in-place` then `Infrastructure/scripts/spec-lint.py <spec>.md --strict`.
- Run `Infrastructure/scripts/run-quality-gates.sh <spec>.md` to validate: spec lint → mermaid diagrams → template export → optional Vale prose lint.
- Self-review against gold standards, critique criteria, and completeness checklist before `[AGREE]`; fail fast on any missing mandatory section or redaction gap.
- **TDD validation:** Verify that every non-trivial story has test cases defined in the Build Plan. Failing tests block acceptance of stories.
- **Component registry validation:** Verify that UI stories reference existing components or specify new components to add to the registry. Custom implementations require explicit justification.

## Anti-patterns
- Skipping stages of the pipeline (Foundation → UX → Build Plan) without justification.
- Skipping sections or leaving placeholders without assumptions.
- Omitting evidence lines per paragraph or missing Evidence Gaps/Evidence Map sections.
- Accepting vague user stories (missing "so that" benefit) or metrics without targets.
- Omitting security/privacy or accessibility requirements.
- Removing unconventional but intentional choices without justification; instead, add safeguards and rationale.
- Forcing state machines on stateless components; prefer flow/sequence diagrams when state is trivial.
- Shipping without an explicit rollout/kill-switch plan for risky changes (AI, payments, auth).
- Conflating PRD and tech spec: keep product intent separate from implementation details.
- Reusing stale metrics or personas across projects without revalidation.
- Design review anti-patterns: generic advice, aesthetic-only feedback, skipping accessibility/edge states, or unscoped redesigns.
- Silent scope changes without updating assumptions, risks, and out-of-scope lists.
- Treating audit outputs as implementation work (code/spec changes) without explicit user request.
- Creating new documentation artifacts without accounting for ongoing maintenance burden.

## Examples
- "Draft a Foundation Spec for a habit-tracking app; include problem, success metrics, and user stories."
- "Create a full spec pipeline (Foundation → UX → Build Plan) for a B2B onboarding flow."
- "Interview me first, then write the Foundation Spec for a CSV ingest API."
- "Review this existing project and produce a Project Review Report."

## Variation
- Vary document depth based on product stage: discovery (brief, assumption-heavy), validate (metrics/experiments emphasized), build (full tech spec, APIs, data models).
- Vary diagram types by need: stateDiagram-v2 for stateful workflows; sequence for request/response; flowchart for simple user paths.
- Adjust tone for audience: exec/stakeholder summaries concise; engineering sections detailed and unambiguous.
- Vary structure, personas, and examples per domain; avoid reusing the same ordering, labels, or sample stories across different specs.
- Avoid repeating the same default personas; create role-appropriate personas that map to the current product domain.

## Quality notes
See `Infrastructure/references/quality-notes.md` for vibe anti-patterns, empowerment guidance, and compliance checks.

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

---

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

---

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

---

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
