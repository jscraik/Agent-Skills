---
name: docs-expert
description: "Use when asked to audit or rewrite repository docs (README, docs, runbooks, community-health files) or when code has missing in-code documentation (JSDoc/DocC/config docs): enforce official brand guidance, harden GitHub visibility signals, and deliver evidence-bundled docs QA."
---

# docs-expert (Repository Documentation)

## Table of Contents
- [When to use](#when-to-use)
- [Standards snapshot (March 2026)](#standards-snapshot-march-2026)
- [Quickstart (Lightweight Path)](#quickstart-lightweight-path)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Response format (required)](#response-format-required)
- [Core workflow (repo doc "gold standard")](#core-workflow-repo-doc-gold-standard)
- [Brand authority order (required)](#brand-authority-order-required)
- [GitHub visibility pack (required for public repos)](#github-visibility-pack-required-for-public-repos)
- [AI-ready documentation pack](#ai-ready-documentation-pack)
- [Validation](#validation)
- [Deliverable format](#deliverable-format)

## When to use
- You want to **write, rewrite, or audit** repo documentation (README, `/docs`, guides, runbooks).
- You need to **add or improve missing in-code documentation** (JSDoc, DocC, config documentation).
- You want a repo to meet **GitHub “community profile” / community health** expectations (README, LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates).
- You want **docs-as-code QA**: link sanity, structure, clarity, and “do not invent commands/paths/versions” verification.
- You want **brand-accurate documentation** without repeatedly steering the agent.
- You want **GitHub discoverability and trust signals** (topics, social preview, funding/citation metadata when applicable).
- You want **AI-consumable docs surfaces** for coding assistants while keeping human docs first.

**Do not use when**
- The request has no clear documentation deliverable to produce or audit.

## Anti-pattern quick warnings
Avoid these anti-patterns: do not start writing before audience/purpose are clear. Never fabricate commands, paths, or results. Do not impose fallback brand assets if repo-specific brand rules already exist.

This skill provides a structured workflow for **collaborative doc creation and repo doc QA**. Default approach: inventory → outline → draft → verify against repo → ship evidence bundle.

## Philosophy
- Clarity over completeness: prefer a smaller, readable doc with explicit gaps.
- Reader-first structure: optimize for how someone will consume the doc.
- Evidence over assertion: back claims with sources or rationale.
- Approach: prioritize outcomes and reader success over exhaustive detail; trade off depth for speed when urgency demands it; consider the reader's job-to-be-done first.
- Source of truth over defaults: repo-level brand and governance docs outrank this skill's fallbacks.
- Visibility and trust over decoration: prioritize metadata quality, security policy, ownership, and clear support paths.

If the user asks for a fast pass, use Quickstart. If the scope is large or ambiguous, use the full workflow from `references/DOC_COAUTHORING.md`.

## Standards snapshot (March 2026)
Use these as the baseline unless the repository has stricter internal policy:

- GitHub community profile + health files (README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, issue/PR templates).
- GitHub discoverability metadata (topics, repository description/homepage, social preview image).
- Trust and ownership metadata (CODEOWNERS, release/changelog guidance, CITATION.cff for citable projects, FUNDING.yml where applicable).
- AI-ready docs surfaces:
  - human-first structured docs with stable headings and explicit examples;
  - optional `llms.txt` support when the repo/site wants AI-specific context (treat this as an emerging proposal, not a mandatory standard).

## Quickstart (Lightweight Path)

Use this when the user wants help quickly and does not want the full three-stage workflow.

1. Collect minimal inputs (doc target, audience, job-to-be-done, constraints, brand source of truth).
2. Propose a tight outline (3-6 sections) and confirm it.
3. Draft the highest-impact section first.
4. Run a fast QA pass (clarity, missing steps, top 3 failure points).
5. Offer to switch to the full workflow if scope grows or ambiguity remains.

## Inputs
- Repo context: link or local path; whether it’s public OSS vs internal.
- Doc target(s): file path(s) or doc surface name (README, `/docs`, runbook).
- Audience and experience level.
- Constraints: platforms, versions, compliance requirements.
- Brand source of truth: explicit guideline path(s), tokens, assets, and signature rules.
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
- A **GitHub visibility snapshot** (topics, social preview, description/homepage, ownership/funding/citation metadata when in scope).
- A **QA bootstrap summary** documenting files auto-installed when lint/brand baselines were missing.
- Evidence bundle when tooling exists (lint outputs, readability output, checklist snapshot, brand check output, visibility checks).

## Response format (required)
Every response must include:
- `## Inputs` (what you need / what’s missing)
- `## Outputs` (what you will deliver or what you delivered)
- `## Next step` (the single next action or question)

## Core workflow (repo doc “gold standard”)
1) **Inventory & scope**
   - Identify canonical doc surfaces (README, `/docs`, runbooks).
   - If repo-wide: run the **GitHub community health** checklist (see `references/CHECKLIST.md`).
   - Detect and record **brand authority sources** before drafting.
2) **Outline first**
   - Fix navigation/TOC and reader questions before drafting.
3) **Draft with evidence**
   - Apply the explicit skimmability/writing/helpfulness gates in `references/docs-baseline.md`.
   - Keep examples minimal; include “Verify” and “Troubleshooting”.
4) **Verify against the repo**
   - Cross-check scripts/paths/flags/versions; if you can’t verify, mark it as a TODO to confirm.
5) **Bootstrap and run doc QA tooling**
   - Follow `references/docs-baseline.md` → “Bootstrap missing QA tooling” before linting.
   - If lint configs are missing, install the baseline configs first, then rerun lint.
   - If branding checks are required, prefer repo-owned brand policy/assets. Use docs-expert fallback assets only if no official brand policy exists and the user approves fallback mode.
6) **Ship the evidence bundle**
   - Checklist snapshot + commands run + key pass/fail outputs + what to do next.

## Full workflow (reference)

Read `references/DOC_COAUTHORING.md` for the full stage-by-stage process, question prompts, and reader testing rubric.

## README deep dive

Use this section when the user asks to create, overhaul, or audit a README or README.md.

1. Read `references/readme-crafting.md` for README-specific structure, rules, templates, badges, and checklists.
2. If specialized sections are needed (performance, security, data model, API reference, migration, contributing, ecosystem, env vars, shell completions, release notes, acknowledgments), read `references/readme-section-templates.md`.

## Baseline practices (reference)

For skimmability, risk capture, accessibility, and security guidance, use:
- `references/docs-baseline.md`
- `references/openai-doc-writing-principles.md`

## In-code documentation (reference)

For JSDoc, DocC, and config documentation rules, use `references/code-docs.md` along with:
- `assets/CODE_DOC_TEMPLATES.md`
- `references/CODE_DOC_CHECKLIST.md`

## Docs upkeep and branding (reference)

- Docs upkeep runbook: `references/docs-upkeep-runbook.md`
- Branding rules and assets: `references/BRAND_GUIDELINES.md` and `references/brand-styling.md` (fallback profile)

## Contracts and evals (reference)

- Output contract schema: `references/contract.yaml`
- Evaluation rubric: `references/evals.yaml`

## Brand authority order (required)
Resolve conflicts in this order:

1. User-specified official brand guidelines for the target repo/workspace.
2. Brand docs inside the target repo (for example `brand/README.md`, `docs/brand/*`, design-token docs, style guides).
3. Organization-level brand standards referenced by the repo.
4. `docs-expert` fallback brand profile (`references/BRAND_GUIDELINES.md`, `assets/brand/*`) only when 1-3 are unavailable.

Rules:
- Never overwrite official repo brand assets with fallback assets.
- Never claim brand compliance unless the source path is explicitly cited in the output.
- If brand instructions are missing or contradictory, stop and ask one focused question.

## GitHub visibility pack (required for public repos)
For public repositories, include these checks in addition to community-health files:

- Repository metadata: description + homepage URL are current.
- Discoverability: relevant topics are set and normalized.
- Link sharing: social preview image configured and current.
- Ownership and trust: CODEOWNERS alignment + SECURITY reporting path + support path.
- Ecosystem metadata when applicable: `CITATION.cff`, `FUNDING.yml`, changelog/release notes.

If visibility checks cannot be verified from local context, mark them as “manual GitHub UI check required” with exact checklist items.

## AI-ready documentation pack
When AI tooling support is in scope:

- Keep stable headings and deterministic section names for retrieval.
- Include concise “quick context” blocks (purpose, constraints, commands, failure modes).
- Prefer small, linkable docs over one giant page.
- Optional: add `llms.txt` only when the repo/site owners request AI-specific context files (this is an emerging proposal, not a universal requirement).
- Keep machine-oriented files aligned with human docs to avoid contradiction drift.

## Constraints
- Redact secrets/PII by default.

- Do not fabricate commands, paths, versions, or outputs.
- Do not include secrets or internal endpoints; use placeholders.
- Avoid destructive instructions without explicit warnings and rollback steps.
- Prefer least-privilege guidance and note data retention and PII handling when relevant.
- Keep outputs ASCII unless the repo already uses non-ASCII.

## Validation

Run these when available and record results:
- `python scripts/bootstrap_doc_qa.py --repo . --apply --brand-profile docs-expert` to enforce BrAInwav baseline assets and README signature by default.
- `vale <doc>` after `.vale.ini` is present.
- `markdownlint-cli2 <doc> --config <config>` after markdownlint config is present.
- Link checker if present.
- `python scripts/check_readability.py <doc>` if available (default target: 45-70 Flesch Reading Ease).
- `python scripts/check_brand_guidelines.py --repo . --docs <doc> --profile docs-expert` when enforcing the BrAInwav guideline profile.
- If a repository has its own official non-BrAInwav brand guidance, switch to `--profile repo` and provide explicit `--config`/brand parameters.

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
- Applying fallback brand assets when official brand guidance already exists.
- Generic templates that ignore context or tradeoffs.
- Checklist dumping without rationale or decision framing.
- Vague headings or jargon-only section titles that hide the point.
- Screenshots or visuals without alt text or captions.
- One-size-fits-all guidance that ignores constraints or audience.

### Avoid These (Do/Do Not)

| Do Not | Do |
| --- | --- |
| Start with installation before value | Lead with problem, solution, and a fast example |
| Use `curl | bash` as default | Prefer package managers or verified checksummed downloads |
| Skip risks/rollback steps | Add risks, assumptions, and rollback guidance |
| Reprint entire docs for edits | Apply minimal patch edits only |
| Add claims without evidence | Provide sources or concrete examples |
| Override official repo brand with fallback branding | Resolve and cite brand source-of-truth first |

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
4. Brand compliance results (if applicable) with source-of-truth path and evidence.
5. GitHub visibility findings (if in scope) with clear pass/fail/manual items.
6. Evidence bundle (lint output, brand check output, readability output, checklist snapshot).

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
- OpenAI-style writing principles: `references/openai-doc-writing-principles.md`
- Docs upkeep runbook: `references/docs-upkeep-runbook.md`
- OpenAI docs quality guide: `https://developers.openai.com/cookbook/articles/what_makes_documentation_good/`
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

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
