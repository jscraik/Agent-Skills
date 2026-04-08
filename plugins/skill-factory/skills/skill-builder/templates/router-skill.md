---
name: {{skill-name}}
description: "{{What it does}} Use when {{primary trigger conditions}}. Don't use when {{common near-miss / out-of-scope cases}}. Outputs: {{artifact paths + formats}}. Success: {{what 'done' means}}."
---

# {{Skill Title}}

## Scope
- **Primary triggers:** {{First trigger scenario}}, {{Second trigger scenario}}, {{Third trigger scenario}}
- **Non-triggers (route elsewhere):** {{First non-trigger}}, {{Second non-trigger}}
- **Assumptions:** {{Key assumptions}}

## Required context
- {{Required input 1}}
- {{Required input 2}}
- {{Optional input}}

## Core principles
1. {{First principle}} — {{Explanation}}
2. {{Second principle}} — {{Explanation}}
3. {{Third principle}} — {{Explanation}}

## Intake
Ask **one** concise routing question and wait for the user response.

**Question:**
What would you like to do?
1. {{First option}}
2. {{Second option}}
3. {{Third option}}

## Routes
| Response | Workflow |
|----------|----------|
| 1, "{{keywords}}" | `workflows/{{first-workflow}}.md` |
| 2, "{{keywords}}" | `workflows/{{second-workflow}}.md` |
| 3, "{{keywords}}" | `workflows/{{third-workflow}}.md` |

## Execution rules
- After choosing a route, **read the target workflow fully**, then follow it exactly.
- Write artifacts to:
  - Local CLI: `./artifacts/`
  - Hosted shell: `/mnt/data/`
- End with a short checklist: created/modified files + commands run.

## Domain knowledge map
Prefer pointers over pasted docs.

See `references/`:
- {{reference-1.md}} — {{purpose}}
- {{reference-2.md}} — {{purpose}}

## Workflows map
See `workflows/`:

| Workflow | Purpose |
|----------|---------|
| {{first-workflow}}.md | {{purpose}} |
| {{second-workflow}}.md | {{purpose}} |
| {{third-workflow}}.md | {{purpose}} |

## Validation
- {{How to verify correctness}}
- {{Tests/checks to run}}

## Anti-patterns
- ❌ {{Common mistake to avoid}}
- ❌ {{What not to do}}
- ❌ {{How the skill can go wrong}}

## Done when
{{Skill Title}} is complete when:
- [ ] {{First success criterion}}
- [ ] {{Second success criterion}}
- [ ] {{Third success criterion}}
