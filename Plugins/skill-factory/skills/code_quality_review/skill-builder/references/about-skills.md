# About Skills

Skills are modular, self-contained packages that extend Codex's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as onboarding guides for specific
domains or tasks—they transform Codex from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

## Normative Rules

- MUST / SHOULD / MAY follow RFC 2119 semantics.
- Any MUST violation is a gate failure (CI fail if enforced).
- SHOULD items are best practice and MUST be documented if skipped.

## Selection Model (Design Constraint)

- Only `name` and `description` are loaded for selection.
- SKILL.md body and references are loaded only after a skill is invoked.
- Therefore, `description` MUST include WHAT + WHEN trigger context.

## What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains.
2. Tool integrations - Instructions for working with specific file formats or APIs.
3. Domain expertise - Company-specific knowledge, schemas, business logic.
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks.

## Gold Standard Minimum Bundle

- SKILL.md (required)
- Infrastructure/references/contract.yaml (required)
- Infrastructure/references/evals.yaml (required, >= 3 cases)
- `## See Also` in `SKILL.md` with at least 2 real related-skill links for graph-visible repo skills
- Infrastructure/references/task-profile.json (required for active/in-scope operational skills in this repository)
- Infrastructure/scripts/ (optional, for deterministic operations)

## Evaluation Requirement

- MUST provide at least 3 eval cases (happy, edge, failure) with acceptance criteria.
- SHOULD include the full 6-case coverage set (explicit/implicit/contextual/negative/edge/pressure).
- SHOULD adopt eval schema v2 fields when relevant:
  - `id`, `should_trigger`, `category`, `deterministic_checks`, `budgets`
- MUST include a clear Definition of Done in the skill body or contract.

## Design Reminder

Keep SKILL.md lean and move details into references and scripts. This preserves context
for actual task execution and speeds retrieval of targeted information.

Graph-ready skills also need navigability:
- Add `## See Also` so neighboring skills are discoverable from the wrapper itself.
- Add a topic-map signpost when the skill belongs to a graph cluster.
- Treat task-profile metadata as part of the source bundle when the repo's onboarding contract applies.

## Automation Mapping

- skill_gate.py: frontmatter limits, required sections, contract/evals presence, size budget.
- analyze_skill.py: quality scoring and coverage signals.
- upgrade_skill.py: improvement suggestions (non-gating).
- gold-skill-rubric.md: canonical MUST/SHOULD checklist.

## Example Folder Layout

```text
my-skill/
  SKILL.md
  Infrastructure/scripts/
  Infrastructure/references/
    contract.yaml
    evals.yaml
  assets/
```
