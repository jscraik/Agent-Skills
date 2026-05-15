# Skill Factory Foundations

Read when: the Codex `.system/skill-creator` flow needs local Skill Factory
contracts for routing, governance, evals, or validation.

Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, inappropriate,
superseded, or low-signal text.

## Local Additions

- Use the upstream `.system/skill-creator` `SKILL.md` as the base authoring
  procedure.
- Keep Skill Factory additions under `skills-system/skill-creator/references/skill-factory/`.
- Do not recreate a plugin-owned `Plugins/skill-factory/**/skill-creator/SKILL.md`.
- For small private helper skills, infer conservatively and keep traceability
  light.
- For reusable delivery or externally-visible workflow skills, add explicit
  trigger, first action, source order, stop rule, proof artifact, evals, and
  validation evidence.
- Ask only when missing input changes path ownership, destructive behavior,
  publication, or external writes.
- For non-trivial create/reshape work, use
  `Infrastructure/references/first-principles-factory-gate.md` before claiming
  the skill should exist.

## Pattern References

- `creation-playbook.md`: first-draft workflow and scaffold guidance.
- `factory-governance-spine.md`: traceability mode and governance depth.
- `examples-and-gotchas.md`: anti-patterns and edge cases.
- `evals.yaml`: smoke/release cases, including external pattern extraction and
  anti-copy pressure cases.
