# Handoff Package Template

## Table of Contents
- [When to use](#when-to-use)
- [Template scaffold workflow](#template-scaffold-workflow)
- [Template](#template)
- [Field guidance](#field-guidance)

## When to use

Use this template when `skill-creator` is handing non-trivial work to `skill-builder`.

Create the artifact in the target skill at:

`Infrastructure/references/handoff-package.md`

## Template scaffold workflow

Canonical scaffold files for this skill:
- `Infrastructure/templates/handoff-package.md.tmpl`
- rendered baseline: `Infrastructure/references/handoff-package-scaffold.md`

Render / refresh:

```bash
python3 Plugins/skill-factory/skills/skill-creator/Infrastructure/scripts/render_handoff_package_template.py
python3 Plugins/skill-factory/skills/skill-creator/Infrastructure/scripts/check_handoff_package_template_drift.py --update
```

Verify no drift:

```bash
python3 Plugins/skill-factory/skills/skill-creator/Infrastructure/scripts/check_handoff_package_template_drift.py
```

## Template

```markdown
# Handoff Package

## skill_goal
- <What the skill should enable in one clear sentence.>

## boundary_summary
- In scope: <What this skill should handle now.>
- Out of scope: <What should route elsewhere.>
- Deliverable boundary: <Standalone skill vs plugin package notes if relevant.>

## trigger_contexts
- Should trigger:
  - "<Realistic prompt or context 1>"
  - "<Realistic prompt or context 2>"
- Should not trigger:
  - "<Near-miss prompt or context 1>"
  - "<Near-miss prompt or context 2>"

## resource_inventory
- scripts:
  - <script path and purpose>
- references:
  - <reference path and purpose>
- assets:
  - <asset path and purpose>
- metadata:
  - <openai.yaml or other lifecycle-relevant metadata notes>

## starter_prompts
- "<Prompt 1>"
- "<Prompt 2>"
- "<Prompt 3>"

## known_risks_or_unknowns
- <Routing ambiguity, weak eval signal, provenance concern, missing dependency, etc.>

## validation_state
- Ran: `<exact command>`
- Result: `<pass|fail|warn>`
- Notes: <Any blockers or caveats>

## authoring_state
- Stage: <brand_new|scaffold_complete|partially_hardened>
- Next owner: `skill-builder`
- Handoff reason: <Why creator stage should stop here>
```

## Field guidance

- Keep each section short and specific.
- Use realistic user-language prompts, not synthetic checker text.
- Include exact command evidence under `validation_state`.
- Do not claim downstream readiness here; this artifact is a bridge to lifecycle hardening.
