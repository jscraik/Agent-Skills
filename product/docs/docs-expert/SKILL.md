---
name: docs-expert
description: "Co-author and QA documentation such as READMEs, guides, and runbooks. Use when writing or auditing docs (not PRDs/specs)."
---

# Doc Co-Authoring Workflow

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md. If missing, use `references/docs-baseline.md`.

## Anti-pattern quick warnings
Avoid these anti-patterns: DO NOT start writing before audience/purpose are clear. NEVER fabricate commands, paths, or results. These mistakes and pitfalls lead to wrong or incorrect guidance. Treat this as a warning to keep docs grounded and verifiable.

This skill provides a structured workflow for guiding users through collaborative document creation. Act as an active guide, walking users through three stages: Context Gathering, Refinement and Structure, and Reader Testing.

## Philosophy
- Clarity over completeness: prefer a smaller, readable doc with explicit gaps.
- Reader-first structure: optimize for how someone will consume the doc.
- Evidence over assertion: back claims with sources or rationale.
- Approach: prioritize outcomes and reader success over exhaustive detail; trade off depth for speed when urgency demands it; consider the reader's job-to-be-done first.

If the user asks for a fast pass, use Quickstart. If the scope is large or ambiguous, use the full workflow from `references/DOC_COAUTHORING.md`.

## Quickstart (Lightweight Path)

Use this when the user wants help quickly and does not want the full three-stage workflow.

1. Collect minimal inputs (doc target, audience, job-to-be-done, constraints).
2. Propose a tight outline (3-6 sections) and confirm it.
3. Draft the highest-impact section first.
4. Run a fast QA pass (clarity, missing steps, top 3 failure points).
5. Offer to switch to the full workflow if scope grows or ambiguity remains.

## Inputs

- Doc target(s): file path(s) or doc surface name.
- Audience and experience level.
- Constraints: platforms, versions, compliance requirements.
- Existing content or links (if any).

## Outputs

- Updated Markdown docs (PR-ready edits).
- Doc QA summary (what changed and what to verify).
- Open questions or items requiring confirmation.
- Evidence bundle (lint outputs, brand checks, readability, checklist snapshot).

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs`

## Full workflow (reference)

Read `references/DOC_COAUTHORING.md` for the full stage-by-stage process, question prompts, and reader testing rubric.

## README deep dive

Use this section when the user asks to create, overhaul, or audit a README or README.md.

1. Read `references/readme-crafting.md` for README-specific structure, rules, templates, badges, and checklists.
2. If specialized sections are needed (performance, security, data model, API reference, migration, contributing, ecosystem, env vars, shell completions, release notes, acknowledgments), read `references/readme-section-templates.md`.

## Baseline practices (reference)

For skimmability, risk capture, accessibility, and security guidance, use `references/docs-baseline.md`.

## In-code documentation (reference)

For JSDoc, DocC, and config documentation rules, use `references/code-docs.md` along with:
- `assets/CODE_DOC_TEMPLATES.md`
- `references/CODE_DOC_CHECKLIST.md`

## Docs upkeep and branding (reference)

- Docs upkeep runbook: `references/docs-upkeep-runbook.md`
- Branding rules and assets: `references/BRAND_GUIDELINES.md` and `references/brand-styling.md`

## Contracts and evals (reference)

- Output contract schema: `references/contract.yaml`
- Evaluation rubric: `references/evals.yaml`

## Constraints
- Redact secrets/PII by default.

- Do not fabricate commands, paths, versions, or outputs.
- Do not include secrets or internal endpoints; use placeholders.
- Avoid destructive instructions without explicit warnings and rollback steps.
- Prefer least-privilege guidance and note data retention and PII handling when relevant.
- Keep outputs ASCII unless the repo already uses non-ASCII.

## Validation

Run these when available and record results:
- `vale <doc>` if `.vale.ini` exists.
- `markdownlint-cli2 <doc> --config <config>` if configured.
- Link checker if present.
- `python scripts/check_readability.py <doc>` if available (default target: 45-70 Flesch Reading Ease).
- `python scripts/check_brand_guidelines.py --repo . --docs <doc>` when branding applies.

Fail fast: if any validation fails, stop and report before continuing edits.
If tooling is missing, state what is missing and how to enable it.

## Examples

- "Draft a decision doc for migrating from REST to GraphQL"
- "Rewrite our README to make onboarding faster and add a quickstart"
- "Audit this runbook for missing rollback steps and unclear prerequisites"

## Anti-patterns

- Writing without confirming audience and purpose.
- Burying key decisions or risks in long prose.
- Shipping drafts without a verification pass.
- Inventing commands, paths, or results.
- Generic templates that ignore context or tradeoffs.
- Checklist dumping without rationale or decision framing.
- Vague headings or jargon-only section titles that hide the point.
- Screenshots or visuals without alt text or captions.
- One-size-fits-all guidance that ignores constraints or audience.

### Avoid These (Do/Do Not)

| Do Not | Do |
| --- | --- |
| Start with installation before value | Lead with problem, solution, and a fast example |
| Use `curl | bash` as default | Prefer package managers or verified downloads |
| Skip risks/rollback steps | Add risks, assumptions, and rollback guidance |
| Reprint entire docs for edits | Apply minimal patch edits only |
| Add claims without evidence | Provide sources or concrete examples |

| Anti-Pattern | Why it fails | Fix |
| --- | --- | --- |
| Installation-first README | Hides value and slows onboarding | Lead with TL;DR and a quick example |
| Generic boilerplate | Readers cannot map to their context | Use concrete examples and constraints |
| Missing risks section | Failure modes go unaddressed | Add risks, assumptions, and rollback |

Anti-pattern guidance: avoid installation-first ordering because it obscures value; fix by leading with the problem, solution, and a quick example. Avoid generic boilerplate because it hides tradeoffs; fix by stating constraints, audience, and concrete use cases. Avoid skipping risks because failures will surface in production; fix by adding risks, assumptions, and rollback steps.

## Deliverable format

When you finish edits, include:

1. Summary of changes (3-7 bullets).
2. Doc QA checklist results (use `references/CHECKLIST.md`).
3. Open questions or items requiring confirmation.
4. Brand compliance results (if applicable) with evidence of signature and assets.
5. Evidence bundle (lint output, brand check output, readability output, checklist snapshot).

If you touch in-code documentation, also include Code Doc QA checklist results (use `references/CODE_DOC_CHECKLIST.md`).

## References and templates

- Doc co-authoring workflow reference: `references/DOC_COAUTHORING.md`
- Doc QA checklist: `references/CHECKLIST.md`
- Code Doc QA checklist: `references/CODE_DOC_CHECKLIST.md`
- Doc template skeleton: `assets/DOC_TEMPLATE.md`
- Code doc templates (JSDoc and language equivalents): `assets/CODE_DOC_TEMPLATES.md`
- README example template: `assets/README_TEMPLATE.md`
- AGENTS example template: `assets/AGENTS_TEMPLATE.md`
- Brand guidelines: `references/BRAND_GUIDELINES.md`
- Brand styling: `references/brand-styling.md`
- Docs baseline practices: `references/docs-baseline.md`
- Docs upkeep runbook: `references/docs-upkeep-runbook.md`
- README deep dive: `references/readme-crafting.md`
- README extended sections: `references/readme-section-templates.md`
- Automation scripts: `scripts/check_brand_guidelines.py`, `scripts/check_readability.py`
- Output contract schema: `references/contract.yaml`
- Evaluation rubric: `references/evals.yaml`

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential - they do not constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
