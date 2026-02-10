# Gold Skill Rubric (MUST-PASS)

This rubric is the single source of truth for enforceable skill quality. If any MUST item fails, the skill fails the gate.

## Normative Rules

- MUST items fail the gate when violated.
- SHOULD items require a documented rationale when skipped.
- MAY items are optional enhancements.
- Use judgment for SHOULD/MAY trade-offs, but MUST requirements remain non-negotiable.

## MUST-PASS Checklist

### Frontmatter
- `name` is present, single-line, <= 100 chars, kebab-case preferred.
- `description` is present, single-line, <= 500 chars.
- `description` encodes WHAT + WHEN triggers.

### Required Sections (SKILL.md)
- When/Usage/Triggers
- Inputs/Requirements
- Outputs/Deliverables
- Workflow/Procedure/Steps
- Validation/Checks
- Anti-patterns/What to avoid
- Examples/Example prompts
- Constraints/Safety

### Progressive Disclosure
- SKILL.md body stays concise (<= 500 lines default).
- Bulk content moved to references/; deterministic ops moved to scripts/.

### Contract + Evals
- `references/contract.yaml` present with required keys:
  - purpose, triggers, inputs, outputs, non_goals, risks
- `references/evals.yaml` present with >= 3 cases:
  - happy path, edge case, failure mode
- Each eval case includes name, prompt, acceptance.

### Output Contract
- Structured outputs include schema + schema_version.
- Errors are separated and machine-consumable when partial results exist.

### Workflow Gates
- Fragile steps include gates (schema/lint/tests/security/a11y/artifact-exists).
- On gate failure: stop, report evidence, propose smallest fix.

## SHOULD (Best Practice)

- Clear philosophy section (1–2 patterns only).
- Explicit variation dimensions (2–3) where variation is appropriate.
- Conflict resolution policy for composable skills.
- Redaction rules for sensitive data.

## Automation Mapping

- skill_gate.py enforces MUST items where possible.
- analyze_skill.py provides quality scoring.
- upgrade_skill.py provides improvement suggestions.
