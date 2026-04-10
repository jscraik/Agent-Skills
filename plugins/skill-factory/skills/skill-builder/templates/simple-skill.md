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

## Constraints and safety
- {{First constraint or limitation}}
- {{Second constraint or limitation}}
- {{Safety / security consideration (secrets, destructive actions, network allowlists)}}

## Core principles
- {{Core principle or approach}}
- {{Guiding philosophy / mental model}}

## Workflow
### Step 1 — {{First action}}
{{Instructions for step 1}}

### Step 2 — {{Second action}}
{{Instructions for step 2}}

### Step 3 — {{Third action}}
{{Instructions for step 3}}

## Deliverables
- {{Primary artifact (path + format)}}
- {{Secondary artifact}}
- {{Success indicators}}
- Artifact boundary:
  - Local CLI: `./artifacts/`
  - Hosted shell: `/mnt/data/`

## Validation
- {{How to verify correctness}}
- {{Test or check to run}}

## See Also
| Skill | When to use |
|---|---|
| `{{adjacent-skill-1}}` | {{When this adjacent skill is a better fit}} |
| `{{adjacent-skill-2}}` | {{Another related route in the local skill graph}} |

**Topic map:** `[[{{topic-name}}]]`

## Anti-patterns
- ❌ {{Common mistake to avoid}}
- ❌ {{What not to do}}

## Examples
- Triggering prompt: "{{Example prompt that SHOULD use this skill}}"
- Non-triggering prompt: "{{Example prompt that should NOT use this skill}}"

## See Also

| Skill | When to use |
|---|---|
| `{{adjacent-skill-1}}` | {{When this neighboring skill is a better fit}} |
| `{{adjacent-skill-2}}` | {{Another nearby skill and its routing boundary}} |

**Topic map:** `[[{{topic-name}}]]`

## Done when
{{Skill Title}} is complete when:
- [ ] {{First success criterion}}
- [ ] {{Second success criterion}}
- [ ] {{Third success criterion}}
