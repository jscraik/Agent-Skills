# Adversarial Review Prompting (Persona Template)

Purpose: apply consistent, high-signal prompting for adversarial personas using tagged blocks, strict formatting, and explicit rules. Techniques are adapted from steipete/summarize prompt patterns (tagged sections, strict formatting, and hard rules), plus recon-workbench evidence gap handling.

## Prompt structure (required)

Use tagged sections to separate instructions, context, and content:

```
<instructions>
Role: <persona name>
Goal: find risks, gaps, contradictions, and missing requirements in the spec.
Output format:
- Findings (bulleted, severity-tagged: ERROR/WARN/INFO)
- Questions (bulleted, only if needed)
- Fixes (bulleted, concise)
Hard rules:
- Do not invent missing facts; label as Evidence gap.
- Do not propose implementation details in PRD review.
- Cite evidence by file path or section name.
- Keep output compact; no filler or speculation.
Final check:
- Remove fluff, ensure each finding is specific and testable.
</instructions>

<context>
Project type: <inferred types + evidence (use repo-inference.md)>
Spec type: PRD | Tech Spec | Review Report
Constraints: <security/reliability/perf/cost/UX focus>
Persona focus: <what this persona cares about>
Evidence notes: <truncation, missing probes, or gaps>
</context>

<content>
[SPEC]
... spec content ...
[/SPEC]
</content>
```

## Prompting techniques to apply (from steipete/summarize)

- Tagged blocks: keep instructions/context/content isolated to reduce drift.
- Hard rules and a final check block to enforce output discipline.
- Strict output format with severity tags and evidence citation.
- Explicit “do not” guidance (no speculation, no filler).
- Include context metadata (project type, constraints, truncation/gaps).

## Persona focus prompts (set in <context>)

- PM: scope, metrics, personas, value/viability, success signals.
- UX: flows, edge/error/empty states, accessibility, IA, copy.
- Frontend: state/loading/errors, perf budgets, API integration risk.
- Backend: data model, concurrency, background jobs, failure modes.
- Security: authN/Z, input validation, secrets, abuse cases.
- Reliability/SRE: timeouts, retries, SLOs, observability, rollback.
- Data/ML: data quality, evals, drift, privacy, reproducibility.
- Platform/Infra: deploy, envs, CI/CD, runtime limits, scaling.
- QA/Test (optional): test plan gaps, coverage, determinism.
- DevEx/Tooling (optional): setup friction, reproducibility, CLI ergonomics.

## Evidence handling (required)

- Every paragraph in the review output ends with `Evidence:` or `Evidence gap:`.
- Cite file paths/links or section names; do not infer unstated facts.
- If source content is truncated or missing, note it in `<context>` and as Evidence gaps.

## Persona checklists (required)

Use the persona-specific checklist for pass/fail items:
- `references/persona-checklists/pm.md`
- `references/persona-checklists/ux.md`
- `references/persona-checklists/frontend.md`
- `references/persona-checklists/backend.md`
- `references/persona-checklists/security.md`
- `references/persona-checklists/reliability-sre.md`
- `references/persona-checklists/data-ml.md`
- `references/persona-checklists/platform-infra.md`
- `references/persona-checklists/qa-test.md`
- `references/persona-checklists/devex-tooling.md`

## Recon-workbench evidence usage

When available, use these artifacts as evidence sources:
- `runs/<id>/derived/report.md` for synthesized findings.
- `runs/<id>/derived/findings.json` for structured claims.
- `runs/<id>/manifest.json` for artifact hashes and integrity.
- `runs/<id>/raw/<probe>/metadata.json` to explain missing evidence (failed probes).

If a probe failed or evidence is missing, record it as an Evidence gap and cite the corresponding `raw/<probe>/metadata.json` file.
