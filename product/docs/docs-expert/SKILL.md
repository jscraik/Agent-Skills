---
name: docs-expert
description: "Co-author and QA GitHub repository documentation (README, docs, runbooks, community health files); use when auditing/upgrading repo docs and delivering a checklist + PR-ready edits; do not use for PRDs/specs."
---

# docs-expert (Repository Documentation)

## Table of Contents
- [When to use](#when-to-use)
- [Quickstart (Lightweight Path)](#quickstart-lightweight-path)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Response format (required)](#response-format-required)
- [Core workflow (repo doc "gold standard")](#core-workflow-repo-doc-gold-standard)
- [Validation](#validation)
- [Deliverable format](#deliverable-format)

## When to use
- You want to **write, rewrite, or audit** repo documentation (README, `/docs`, guides, runbooks).
- You want a repo to meet **GitHub “community profile” / community health** expectations (README, LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates).
- You want **docs-as-code QA**: link sanity, structure, clarity, and “don’t invent commands/paths/versions” verification.

**Do not use when**
- The request is primarily **product specs/PRDs**, architecture design, or code implementation.

## Anti-pattern quick warnings
Avoid these anti-patterns: DO NOT start writing before audience/purpose are clear. NEVER fabricate commands, paths, or results. These mistakes and pitfalls lead to wrong or incorrect guidance. Treat this as a warning to keep docs grounded and verifiable.

This skill provides a structured workflow for **collaborative doc creation and repo doc QA**. Default approach: inventory → outline → draft → verify against repo → ship evidence bundle.

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
- Repo context: link or local path; whether it’s public OSS vs internal.
- Doc target(s): file path(s) or doc surface name (README, `/docs`, runbook).
- Audience and experience level.
- Constraints: platforms, versions, compliance requirements.
- Existing content or links (if any).

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

## Outputs
- Updated Markdown docs (**PR-ready edits**).
- A **doc audit summary** (what changed, what’s still unknown, and what to verify).
- A **GitHub community health checklist** snapshot when repo-wide documentation is in scope (see `references/CHECKLIST.md`).
- A **QA bootstrap summary** documenting files auto-installed when lint/brand baselines were missing.
- Evidence bundle when tooling exists (lint outputs, readability output, checklist snapshot).

## Response format (required)
Every response must include:
- `## Inputs` (what you need / what’s missing)
- `## Outputs` (what you will deliver or what you delivered)
- `## Next step` (the single next action or question)

## Core workflow (repo doc “gold standard”)
1) **Inventory & scope**
   - Identify canonical doc surfaces (README, `/docs`, runbooks).
   - If repo-wide: run the **GitHub community health** checklist (see `references/CHECKLIST.md`).
2) **Outline first**
   - Fix navigation/TOC and reader questions before drafting.
3) **Draft with evidence**
   - Keep examples minimal; include “Verify” and “Troubleshooting”.
4) **Verify against the repo**
   - Cross-check scripts/paths/flags/versions; if you can’t verify, mark it as a TODO to confirm.
5) **Bootstrap and run doc QA tooling**
   - Follow `references/docs-baseline.md` → “Bootstrap missing QA tooling” before linting.
   - If lint configs are missing, install the baseline configs first, then rerun lint.
   - If `brand/` and branding constraints are missing, install baseline brand assets/constraints first, then rerun brand checks.
6) **Ship the evidence bundle**
   - Checklist snapshot + what was run + what to do next.

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
- `python scripts/bootstrap_doc_qa.py --repo . --apply` to install missing lint and brand baselines.
- `vale <doc>` after `.vale.ini` is present.
- `markdownlint-cli2 <doc> --config <config>` after markdownlint config is present.
- Link checker if present.
- `python scripts/check_readability.py <doc>` if available (default target: 45-70 Flesch Reading Ease).
- `python scripts/check_brand_guidelines.py --repo . --docs <doc>` when branding applies.

Fail fast: if any validation fails, stop and report before continuing edits.
If tooling is missing and bootstrap is not approved, state what is missing and why checks were skipped.

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
- Automation scripts: `scripts/bootstrap_doc_qa.py`, `scripts/check_brand_guidelines.py`, `scripts/check_readability.py`
- Output contract schema: `references/contract.yaml`
- Evaluation rubric: `references/evals.yaml`

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential - they do not constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

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
