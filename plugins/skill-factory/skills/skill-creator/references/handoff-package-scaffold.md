# Handoff Package

## skill_goal
- Provide deterministic issue-to-workspace orchestration guidance for coding agent sessions.

## boundary_summary
- In scope: Scaffold, route, and validate the core orchestration skill contract and references.
- Out of scope: Plugin distribution, installer wiring, and marketplace publication.
- Deliverable boundary: Standalone skill package ready for skill-builder hardening.

## trigger_contexts
- Should trigger:
  - "Build a skill that orchestrates issue polling with bounded concurrency."
  - "Scaffold a new skill for deterministic worker retry and reconciliation behavior."
- Should not trigger:
  - "Package this as a plugin and publish marketplace metadata now."
  - "Install this skill to my global catalog only."

## resource_inventory
- scripts:
  - scripts/init_skill.py (scaffold + metadata generation)
- references:
  - references/creation-playbook.md (stage and quality checklist)
- assets:
  - none
- metadata:
  - openai.yaml scaffolded by init script; lifecycle values marked for hardening.

## starter_prompts
- "Create a skill that turns tracker issues into deterministic worker runs."
- "Scaffold a router skill for issue-state based dispatch policies."
- "Draft a skill with strict template-backed references and drift checks."

## known_risks_or_unknowns
- Trigger boundaries may overlap with plugin-factory lanes without clear handoff notes.

## validation_state
- Ran: `python3 plugins/skill-factory/skills/skill-creator/scripts/init_skill.py orchestration --path /tmp --resources references`
- Result: `pass`
- Notes: Scaffold command executes and writes template-backed SKILL.md output.

## authoring_state
- Stage: scaffold_complete
- Next owner: `skill-builder`
- Handoff reason: Requires eval calibration and contract hardening before install/plugin handoff.
