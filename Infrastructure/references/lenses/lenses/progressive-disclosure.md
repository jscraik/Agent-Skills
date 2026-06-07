---
id: lens.progressive-disclosure
title: Progressive Disclosure
type: expert_lens
version: 1.0.0
status: stable
triggers:
  keywords:
    - progressive disclosure
    - references
    - hot path
    - context budget
    - SKILL.md
    - heading
  task_intents:
    - skill_authoring
    - documentation_review
    - reference_design
    - agent_workflow_design
    - sdk_contract_review
  file_signals:
    - SKILL.md
    - references/
    - schemas/
strengths:
  - context_budget
  - skill_routing
  - reference_boundaries
  - load_order
  - agent_usability
avoid_when:
  - task_intent: isolated_bugfix
  - task_intent: pure_visual_polish
pairs_well_with:
  - lens.operator-evidence
  - lens.testing-confidence
output_categories:
  - overloaded_hot_path
  - missing_reference_boundary
  - unclear_load_trigger
  - buried_required_instruction
priority: 90
---

# Progressive Disclosure

## Review Questions

1. Is the always-loaded file small enough for first-pass agent use?
2. Are optional details moved into references with explicit load triggers?
3. Can the agent tell which reference to load without scanning every file?
4. Are required procedure, examples, and background separated cleanly?
5. Does the output contract say what proof or handoff the agent must emit?

## Failure Modes

- A hot-path file becomes a complete handbook.
- Reference files exist but are not directly mapped from the workflow.
- Optional context silently becomes required context.
- The agent has to infer load order from prose.
- Examples and gotchas obscure the required operating procedure.

## Recommended Moves

- Keep the hot path as router plus procedure.
- Move bulky examples, policies, schemas, and edge cases to named references.
- Add Read when triggers for each reference.
- Validate direct links from the hot path to required references.
- Require long references to carry a table of contents.
