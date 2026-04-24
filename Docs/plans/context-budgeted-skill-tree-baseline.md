# Context-Budgeted Skill Tree Baseline

Date: 2026-04-24

Source commit before Phase A implementation: `bcba348c7`

## Task Graph

```yaml
tasks:
  - id: BASELINE
    title: "Record current runtime surface"
    depends_on: []
```

## Command Evidence

```bash
PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python python3 bin/ask runtime surface --json
PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python python3 bin/ask runtime budget --json
PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python python3 bin/ask skills budget --json
PYTHON_BIN=/Users/jamiecraik/.venvs/pyyaml/bin/python python3 bin/ask skills sync --scope workspace --projection flat --dry-run --json
```

## Runtime Surface Summary

| Field | Value |
| --- | ---: |
| `status` | `pass` |
| `budget_status` | `pass` |
| `projection_mode` | `flat` |
| `policy_identity` | `ccc42d9df4a2db2e` |
| `default_visible_count` | 18 |
| `catalog_default_count` | 18 |
| `advanced_visible_count` | 106 |
| `first_level_default_count` | 18 |
| `hidden_system_count` | 6 |
| `root_skill_set_count` | 0 |
| `estimated_description_words` | 490 |
| `estimated_description_tokens` | 654 |

## Scope Counts

| Scope | Count |
| --- | ---: |
| `global` | 75 |
| `project` | 0 |
| `local-plugin` | 30 |
| `system` | 2 |
| `primary-runtime` | 0 |
| `unknown` | 0 |
| `external` | 0 |

## Largest Descriptions

| Skill | Path | Words |
| --- | --- | ---: |
| `imagegen` | `skills-system/imagegen` | 83 |
| `ubiquitous-language` | `Skills/agent-ops/ubiquitous-language` | 64 |
| `design-system` | `Skills/frontend-ui/design-system` | 61 |
| `openai-docs` | `skills-system/openai-docs` | 56 |
| `frontend-ui-design` | `Skills/frontend-ui/frontend-ui-design` | 46 |

## Flat Sync Dry-Run Summary

| Field | Value |
| --- | ---: |
| `validation_status` | `pass` |
| planned writes | 2 |
| planned deletes | 0 |
| planned symlinks | 19 |

Preserved bridge-lane entries:

- `imagegen`
- `openai-docs`
- `plugin-creator`
- `plugin-installer`
- `skill-creator`
- `skill-installer`

Preserved system-lane entries:

- `imagegen`
- `openai-docs`
- `plugin-creator`
- `plugin-installer`
- `skill-creator`
- `skill-installer`

## Notes

- The default flat runtime surface is bounded and passing.
- Rooted projection is not active yet; `root_skill_set_count` is expected to be `0` in this baseline.
- Project skill overlays use `Skills/project/<skill>/SKILL.md`; none exist in this baseline.
- Local plugin skills remain separately browsable and are counted as `local-plugin`, not first-level rooted runtime entries.
