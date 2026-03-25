---
name: docs-expert
description: Audit and rewrite repository documentation, runbooks, and in-code docs with repo-visibility and brand-quality checks. Use when the user wants README, docs, JSDoc, DocC, or config documentation improved, not editorial house-style copyediting.
metadata:
  skill-type: code_quality_review
---

# docs-expert (Repository Documentation)

## Table of Contents
- [When to use](#when-to-use)
- [Philosophy](#philosophy)
- [Standards snapshot (March 2026)](#standards-snapshot-march-2026)
- [Quickstart (Lightweight Path)](#quickstart-lightweight-path)
- [Discovery interview](#discovery-interview)
- [README reality audit mode](#readme-reality-audit-mode)
- [Operational workflow mode](#operational-workflow-mode)
- [Output contract mode](#output-contract-mode)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Response format (required)](#response-format-required)
- [Core workflow (repo doc "gold standard")](#core-workflow-repo-doc-gold-standard)
- [Brand authority order (required)](#brand-authority-order-required)
- [GitHub visibility pack (required for public repos)](#github-visibility-pack-required-for-public-repos)
- [AI-ready documentation pack](#ai-ready-documentation-pack)
- [Reference map](#reference-map)
- [Constraints](#constraints)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Gotchas](#gotchas)
- [Failure mode](#failure-mode)

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
- Treat repository-local files and organization-level default community health files in a public `.github` repository as valid GitHub trust surfaces; if they are not visible from local checkout, mark them as a manual GitHub UI check.
- GitHub discoverability metadata (topics, repository description/homepage, social preview image).
- Trust and ownership metadata (CODEOWNERS, release/changelog guidance, CITATION.cff for citable projects, FUNDING.yml where applicable).
- Reader-first information architecture: separate tutorials, how-to guides, reference, and explanation instead of mixing user needs into one page.
- Procedure writing: one action per step, goal-first where helpful, verification points when confidence matters, and links to canonical repeated procedures.
- Accessibility and readability: avoid directional language, avoid color-only meaning, require descriptive headings/alt text/captions, and keep docs usable without images.
- AI-ready docs surfaces: human-first structured docs with stable headings and explicit examples; add `llms.txt` only when repo owners explicitly want AI-specific context files.
- Brand handling: prefer official repo or organization brand guidance first, use a neutral repo baseline by default, and only apply the docs-expert fallback brand profile when the repo owner explicitly wants it.
- Prefer the current global instruction flow from `~/.codex/AGENTS.md` over older legacy config-file conventions.

## Quickstart (Lightweight Path)

Use this when the user wants help quickly and does not want the full three-stage workflow.

1. Collect minimal inputs (doc target, audience, job-to-be-done, constraints, brand source of truth).
2. Classify the primary doc type with `references/document-types.md`.
3. Keep one primary doc type per page; link to adjacent doc types instead of mixing them into one draft.
4. Propose a tight outline (3-6 sections) and confirm it.
5. Draft the highest-impact section first.
6. Run a fast QA pass (clarity, missing steps, top 3 failure points).
7. Offer to switch to the full workflow if scope grows or ambiguity remains.

## Discovery interview

Run discovery for underspecified docs work before drafting.
- Ask one round at a time and wait before moving on.
- Start with one plain-language question.
- Explain why the round matters with one short `Why this matters:` line so the user understands the decision point.
- Avoid dumping the whole interview plan at once.
- Skip already-answered rounds.
- Stop when doc target, audience, source of truth, validation path, and brand authority are clear enough to write safely.
- Before implementation, summarize confirmed inputs, assumptions, and the next approval checkpoint.
- Use `references/discovery-interview.md` for reusable round templates.

## README reality audit mode

Use this mode when the user wants the README to reflect what the project can actually do today, not just what older docs say it does.

Core contract:
- audit code, tests, examples, and recent history for understated or omitted capabilities;
- separate verified capabilities from inferred ones;
- revise the README with concrete value framing, practical usage guidance, and trustworthy language.
Reference: `references/readme-reality-audit.md`.

## Operational workflow mode

Use this mode when the user wants a workflow, runbook, or agent procedure converted into a compact operational spec.

Default contract:
- choose the most efficient representation: transition table, state machine, pseudocode, or diagram;
- treat the transition table as the source of truth;
- model `S=state`, `E=event`, `G=guard`, `A=action`, `N=next`;
- include deterministic transitions, explicit failure states, idempotency, invariants, metadata, logs, and dry-run behavior.
Reference: `references/operational-workflow-mode.md`.

## Output contract mode

Use this mode when the user wants canonical output contracts for agent-facing commands, validators, reporters, or automation entry points.

Default contract:
- define the default machine-readable mode and the explicit human-readable mode;
- define schema versioning, deterministic error handling, and compatibility rules for future fields;
- keep the machine-readable contract stable and machine-first;
- when robot mode is in scope, define no-arg quick-start, intent-based command taxonomy, and errors that teach correct usage.
Reference: `references/output-contract-mode.md`.

## Required inputs
- Repo context and target surface: path/link plus README, `/docs`, runbook, or code-doc target.
- Audience, experience level, and job-to-be-done.
- Constraints that change the draft: platform, version, compliance, rollout risk.
- Source material: existing content plus the brand/source-of-truth path if one exists.
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short, externalize decisions/assumptions, and show the single next step.
- Provide ELI5 explanations for non-trivial logic and ask one focused question at a time.

## Deliverables
- Updated Markdown docs (**PR-ready edits**).
- A **doc audit summary** with what changed, what is still unknown, and what to verify.
- Community-health, GitHub visibility, and brand findings when they are in scope.
- A QA bootstrap summary plus an evidence bundle when tooling exists.
- Final handoff format:
  - summary of changes
  - doc QA checklist results
  - open questions or facts needing confirmation
  - brand compliance, GitHub visibility, and evidence-bundle findings when in scope
  - code-doc QA results when in-code documentation changed

## Response format (required)
Every response must include:
- `schema_version` in any structured or schema-bound output
- `## Required inputs` (what you need / what’s missing)
- `## Deliverables` (what you will deliver or what you delivered)
- `## Next step` (the single next action or question)

## Core workflow (repo doc “gold standard”)
1) **Inventory & scope**
   - Identify canonical doc surfaces (README, `/docs`, runbooks).
   - If repo-wide: run the **GitHub community health** checklist (see `references/CHECKLIST.md`).
   - Check whether community health files come from the repo itself or from an organization-level `.github` defaults repository.
   - Detect and record **brand authority sources** before drafting.
2) **Classify the document type**
   - Decide whether the work is primarily a tutorial, how-to guide, reference page, or explanation.
   - Use `references/document-types.md` for routing and page-shape rules.
3) **Outline first**
   - Fix navigation/TOC and reader questions before drafting.
   - Match the outline to the chosen doc type.
4) **Draft with evidence**
   - Apply the explicit skimmability/writing/helpfulness gates in `references/docs-baseline.md`.
   - Keep examples minimal; include “Verify” and “Troubleshooting”.
   - Preserve separation of concerns; split or cross-link when types mix.
5) **Verify against the repo**
   - Cross-check scripts/paths/flags/versions; if you can’t verify, mark it as a TODO to confirm.
6) **Bootstrap and run doc QA tooling**
   - See `references/docs-baseline.md` → “Bootstrap missing QA tooling”, then lint.
   - If lint configs are missing, install the baseline configs first, then rerun lint.
   - If branding checks are required, prefer repo-owned brand policy/assets. Use the neutral repo profile by default. Use docs-expert fallback assets only if no official brand policy exists and the user approves fallback mode.
7) **Ship the evidence bundle**
   - Checklist snapshot + validation steps run + key pass/fail outputs + what to do next.

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
If community-health coverage depends on an organization `.github` defaults repository, call that out explicitly instead of marking the repo as simply missing files.

## AI-ready documentation pack
When AI tooling support is in scope:

- Keep stable headings and deterministic section names for retrieval.
- Include concise “quick context” blocks (purpose, constraints, verified steps, failure modes).
- Prefer small, linkable docs over one giant page.
- Optional: add `llms.txt` only when the repo/site owners request AI-specific context files (this is an emerging proposal, not a universal requirement).
- Keep machine-oriented files aligned with human docs to avoid contradiction drift.

## Reference map
- Full workflow and reader-testing rubric: `references/DOC_COAUTHORING.md`
- README structure and templates: `references/readme-crafting.md`, `references/readme-section-templates.md`, `references/readme-reality-audit.md`
- Doc-type routing and baseline writing rules: `references/document-types.md`, `references/docs-baseline.md`, `references/openai-doc-writing-principles.md`, `references/industry-gold-standard-2026.md`, `references/official-docs-baseline.md`
- Operational spec and output-contract modes: `references/operational-workflow-mode.md`, `references/output-contract-mode.md`, `references/contract.yaml`, `references/evals.yaml`
- In-code docs, upkeep, and branding: `references/code-docs.md`, `references/CODE_DOC_CHECKLIST.md`, `references/docs-upkeep-runbook.md`, `references/BRAND_GUIDELINES.md`, `references/brand-styling.md`, `assets/CODE_DOC_TEMPLATES.md`
- Checklists and templates: `references/CHECKLIST.md`, `assets/DOC_TEMPLATE.md`, `assets/README_TEMPLATE.md`, `assets/AGENTS_TEMPLATE.md`

## Constraints
- Redact secrets/PII by default.
- Do not fabricate commands, paths, versions, or outputs.
- Do not include secrets or internal endpoints; use placeholders.
- Avoid destructive instructions without explicit warnings and rollback steps.
- Prefer least-privilege guidance and note data retention and PII handling when relevant.
- Keep outputs ASCII unless the repo already uses non-ASCII.

## Validation

Validation options to run when available and record:
- `python scripts/bootstrap_doc_qa.py --repo . --apply --brand-profile repo` for a neutral docs QA baseline.
- `vale <doc>` after `.vale.ini` is present.
- `markdownlint-cli2 <doc> --config <config>` after markdownlint config is present.
- Link checker if present.
- `python scripts/check_readability.py <doc>` if available (default target: 45-70 Flesch Reading Ease).
- `python scripts/check_brand_guidelines.py --repo . --docs <doc> --profile repo` for neutral brand-policy verification.
- Use `--brand-profile docs-expert` and `--profile docs-expert` only when the docs-expert fallback brand profile is explicitly in scope.
- If a repository has its own official non-docs-expert brand guidance, keep `--profile repo` and provide explicit `--config` or brand parameters.

Fail fast: if any validation fails, stop and report before continuing edits.
If tooling is missing and bootstrap is not approved, state what is missing and why checks were skipped.

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

Quick corrections:
- Do not lead with installation when the reader needs value first; start with the problem, outcome, or quick example.
- Do not use generic boilerplate; state audience, constraints, and concrete use cases.
- Do not skip risks or rollback; add them when failure modes matter.
- Do not replace official repo branding with fallback assets; resolve and cite the real source of truth.

## Examples

- "Can you help me rewrite our README so onboarding is faster and the quickstart is easier to scan?"
- "Please audit this runbook for missing rollback steps, verification checks, and trust signals."
- "Inspect these docs and split them into tutorial, how-to, reference, and explanation pages without mixing audiences."
- "Validate whether our public repo is relying on org-level default community health files or whether we still need local copies."
- "Audit the code, tests, and recent history, then update the README so it reflects the product's current real capabilities."
- "Convert this approval workflow into a compact operational spec with a transition table, invariants, and dry-run behavior."
- "Define canonical output contracts for these agent-facing commands, including machine-readable defaults, human-readable mode, schema versioning, and deterministic errors."
- "Design a robot-mode interface so agents can use the command surface without the UI, including no-arg quick-start behavior and errors that teach correct usage."

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the repo context, target audience, or governing source material is unclear, stop, name the ambiguity, and fall back to a scoped docs audit or clarification request instead of rewriting documentation on assumption.

## See Also
| Skill | When to use |
|---|---|
| [[agents-md]] | Refactor or tighten AGENTS.md and related repo instruction routing |
| [[markdown-converter]] | Convert source materials into clean Markdown before docs restructuring |
| [[fixing-metadata]] | Repair page metadata and SEO surfaces after docs or web content edits |
| [[visual-explainer]] | Present a complex system, workflow, or docs audit as a visual artifact |

**Topic map:** [[agent-ops]]
