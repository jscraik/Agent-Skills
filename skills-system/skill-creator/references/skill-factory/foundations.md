# Skill Factory Foundations

Read when: the Codex `.system/skill-creator` flow needs local Skill Factory
contracts for routing, governance, evals, or validation.

Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, inappropriate,
superseded, or low-signal text.

## Local Additions

- Use the upstream `.system/skill-creator` `SKILL.md` as the base authoring
  procedure.
- In Agent Skills Kit, use `./bin/ask skills init <skill-name> --category <Skills/category> --description "<routing description>" --json --robot` for repo-owned creation so writes land in canonical source.
- Use `skills-system/skill-creator/scripts/init_skill.py` directly only outside Agent Skills Kit or for an explicitly unmanaged draft path.
- Before creating a new skill, search the advanced skill inventory and nearby canonical sources for an owner to improve. Create a separate package only when the trigger, procedure, or lifecycle contract is distinct.
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
- Start new reusable skills from the Skill Factory reference templates:
  `Plugins/skill-factory/skills/code_quality_review/skill-builder/references/contract.template.yaml`
  and `.../evals.template.yaml`. They encode the current operator shape.

## Generated Skill Shape

New or substantially rewritten skills should keep `SKILL.md` compact while
preserving the operational details in references. Do not delete useful
negative prompts, gotchas, constraints, examples, or failure ladders; move them
behind progressive disclosure unless they are needed for routing or the first
operator action.

Every reusable skill draft should include or reference:

- routing payload: domain, verbs, objects, constraints
- immediate operator path: first command/tool/read and proceed rule
- source order: local truth, live readback, docs/source/types, user confirmation
- tool resolution: preferred tool, fallback, doctor/status check
- freshness/proof: live read before writes and targeted readback after writes
- boundaries: forbidden external/destructive/credential actions without intent
- retry/stop: bounded retry, exact blocker, attempted fallback, next step
- validation tiers: fast, standard, deep
- concise closeout: changed files, decisions, validation, residual risks

When wrapping `.system` skills, preserve upstream update flow with an overlay
and attached references. Do not create a plugin-owned standalone fork of the
upstream `SKILL.md`.

## Pattern References

- `creation-playbook.md`: first-draft workflow and scaffold guidance.
- `factory-governance-spine.md`: traceability mode and governance depth.
- `examples-and-gotchas.md`: anti-patterns and edge cases.
- `evals.yaml`: smoke/release cases, including external pattern extraction and
  anti-copy pressure cases.
