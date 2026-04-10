# Compound Docs YAML Schema

Imported from the upstream `compound-docs` package.

Read when:
- the target repo expects structured frontmatter in `docs/solutions/`
- you need enum-guided classification or category mapping

## Required fields

- `module` (string)
- `date` (ISO `YYYY-MM-DD`)
- `problem_type` (enum)
- `component` (enum)
- `symptoms` (array with 1-5 items)
- `root_cause` (enum)
- `resolution_type` (enum)
- `severity` (enum)

## Optional fields

- `rails_version`
- `tags`

## Allowed enums

### `problem_type`

- `build_error`
- `test_failure`
- `runtime_error`
- `performance_issue`
- `database_issue`
- `security_issue`
- `ui_bug`
- `integration_issue`
- `logic_error`
- `developer_experience`
- `workflow_issue`
- `best_practice`
- `documentation_gap`

### `component`

- `rails_model`
- `rails_controller`
- `rails_view`
- `service_object`
- `background_job`
- `database`
- `frontend_stimulus`
- `hotwire_turbo`
- `email_processing`
- `brief_system`
- `assistant`
- `authentication`
- `payments`
- `development_workflow`
- `testing_framework`
- `documentation`
- `tooling`

### `root_cause`

- `missing_association`
- `missing_include`
- `missing_index`
- `wrong_api`
- `scope_issue`
- `thread_violation`
- `async_timing`
- `memory_leak`
- `config_error`
- `logic_error`
- `test_isolation`
- `missing_validation`
- `missing_permission`
- `missing_workflow_step`
- `inadequate_documentation`
- `missing_tooling`
- `incomplete_setup`

### `resolution_type`

- `code_fix`
- `migration`
- `config_change`
- `test_fix`
- `dependency_update`
- `environment_setup`
- `workflow_improvement`
- `documentation_update`
- `tooling_addition`
- `seed_data_update`

### `severity`

- `critical`
- `high`
- `medium`
- `low`

## Validation rules

1. All required fields must be present.
2. Enum values must match exactly.
3. `symptoms` must be a YAML array with 1-5 items.
4. `date` must match `YYYY-MM-DD`.
5. `rails_version`, when present, must match `X.Y.Z`.
6. `tags` should be lowercase and hyphen-separated.

## Category mapping

- `build_error` -> `docs/solutions/build-errors/`
- `test_failure` -> `docs/solutions/test-failures/`
- `runtime_error` -> `docs/solutions/runtime-errors/`
- `performance_issue` -> `docs/solutions/performance-issues/`
- `database_issue` -> `docs/solutions/database-issues/`
- `security_issue` -> `docs/solutions/security-issues/`
- `ui_bug` -> `docs/solutions/ui-bugs/`
- `integration_issue` -> `docs/solutions/integration-issues/`
- `logic_error` -> `docs/solutions/logic-errors/`
- `developer_experience` -> `docs/solutions/developer-experience/`
- `workflow_issue` -> `docs/solutions/workflow-issues/`
- `best_practice` -> `docs/solutions/best-practices/`
- `documentation_gap` -> `docs/solutions/documentation-gaps/`
