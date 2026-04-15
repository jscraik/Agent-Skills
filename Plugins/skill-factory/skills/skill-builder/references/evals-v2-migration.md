# Evals schema v2 (migration guide)

## Why v2

v2 keeps v1 compatibility while adding fields needed for systematic skill quality:
- trigger intent (`should_trigger`, `prepend_skill`, `category`)
- deterministic trace checks (`deterministic_checks`)
- efficiency/style budgets (`budgets`)
- stable identifiers (`id`)

## New optional case fields

```yaml
id: implicit-trigger
should_trigger: true
category: happy # happy | edge | negative | pressure
prepend_skill: false
output_schema: Infrastructure/references/schemas/your-rubric.schema.json
deterministic_checks:
  required_commands: ["npm install"]
  forbidden_commands: ["rm -rf"]
  command_order: ["npm install", "npm run build"]
  max_command_executions: 12
  max_duplicate_command_ratio: 0.4
  required_event_types: ["turn.started"]
budgets:
  max_total_tokens: 6000
  max_input_tokens: 4500
  max_output_tokens: 1500
  max_command_budget: 15
  max_duplicate_command_ratio: 0.35
  min_rubric_score: 85
  require_overall_pass: true
```

## Migration rules (v1 -> v2)

1. Keep existing `name`, `prompt`, `acceptance` unchanged (fully supported).
2. Add `schema_version: "2.0"` at top-level.
3. Add `id` to each case (kebab-case, stable).
4. Add `category` to each case.
5. Add at least one `should_trigger: false` negative control.
6. Set `prepend_skill: false` on implicit/contextual/negative cases.
7. Add `deterministic_checks` for at least the explicit trigger case.
8. Add `budgets` for token/command budgets (tier-2 by default).

## CI / gating defaults

- Tier 1 (hard fail):
  - eval runner exit codes
  - acceptance assertions
  - deterministic trace checks
- Tier 2 (warn initially):
  - rubric score thresholds
  - efficiency/token budgets

Run with:

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <skill> \
  --dual-run --capture-jsonl --tier2-mode warn
```

Promote to strict after soak:

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <skill> \
  --dual-run --capture-jsonl --tier2-mode fail
```
