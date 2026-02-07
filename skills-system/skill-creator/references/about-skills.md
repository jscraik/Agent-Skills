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
- references/contract.yaml (required)
- references/evals.yaml (required, >= 3 cases)
- scripts/ (optional, for deterministic operations)

## Evaluation Requirement

- MUST provide at least 3 eval cases (happy, edge, failure) with acceptance criteria.
- MUST include a clear Definition of Done in the skill body or contract.

## Design Reminder

Keep SKILL.md lean and move details into references and scripts. This preserves context
for actual task execution and speeds retrieval of targeted information.

## Automation Mapping

- skill_gate.py: frontmatter limits, required sections, contract/evals presence, size budget.
- analyze_skill.py: quality scoring and coverage signals.
- upgrade_skill.py: improvement suggestions (non-gating).
- gold-skill-rubric.md: canonical MUST/SHOULD checklist.

## Example Folder Layout

```text
my-skill/
  SKILL.md
  scripts/
  references/
    contract.yaml
    evals.yaml
  assets/
```
