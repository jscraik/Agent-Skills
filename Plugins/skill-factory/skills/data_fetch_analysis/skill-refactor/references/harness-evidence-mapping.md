# Harness Evidence Mapping

Use this reference only when supplied evidence explicitly names Harness
Engineering artifacts such as `$he-spec`, `$he-plan`, `.harness/specs/**`, or
`.harness/plan/**`.

## Attribution

- Preserve the named artifact owner as the affected skill even if a generic
  collector field points elsewhere.
- If stage signals include `he-spec` or `he-plan` but the affected-skill field
  maps to an unrelated skill, report an attribution warning and include the
  artifact owner in `affected_skill_or_plugin`.

## Prompt Signals

- "deepen spec and run a technical review" maps to
  `affected_skill_or_plugin: he-spec` with supported normalized root causes such
  as `artifact-shape-gap`, `reader-contract-gap`, or
  `generated-artifact-validator-gap`.
- "deepen plan and run a technical review" maps to
  `affected_skill_or_plugin: he-plan` with the same options plus
  `execution-contract-gap` when plan units, validation, rollback, or handoff
  evidence is missing.
- Senior-review prompts that identify a "specification maintainer" and ask to
  investigate or improve a specification map to `he-spec`.
- Senior-review prompts that identify a "specification maintainer" and ask to
  review a plan against engineering confidence standards map to `he-plan`.
