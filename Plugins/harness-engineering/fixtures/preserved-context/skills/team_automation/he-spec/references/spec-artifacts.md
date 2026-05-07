# HE Spec Artifact Templates

Read when: you are writing the actual spec file and need the canonical section set, frontmatter, or verification checks.

## Table of Contents
- [Standard spec template](#standard-spec-template)
- [Dedicated UI spec template](#dedicated-ui-spec-template)
- [Verification matrix](#verification-matrix)
- [Notes for full service specs](#notes-for-full-service-specs)

## Standard spec template
Suggested frontmatter:

```yaml
---
schema_version: 1
title: <Spec Title>
type: feat|fix|refactor
status: draft
date: YYYY-MM-DD
origin: .harness/brainstorm/YYYY-MM-DD-<topic>-requirements.md  # if applicable; resume legacy *-brainstorm.md only when that is the source artifact
linear_project: TEAM|project-slug                           # required for non-trivial tracked work
linear_issue: ABC-123                                       # required for non-trivial tracked work
linear_parent: ABC-100                                      # if applicable
linear_children: []                                         # if applicable
linear_status: Todo|In Progress|In Review|Done
traceability_required: true
risk: low|medium|high
spec_depth: none|lite|full
ui_required: true|false
---
```

Required sections:
- Problem Statement
- Goals
- Non-Goals
- Linear Work Item Contract
- System Boundary
- Core Domain Model
- Main Flow / Lifecycle
- Interfaces and Dependencies
- Invariants / Safety Requirements
- Failure Model and Recovery
- Observability
- Acceptance and Test Matrix
- Linear Acceptance Traceability
- Open Questions
- Definition of Done

Acceptance and Test Matrix rules:
- every item carries a stable `SA` identifier
- each item is specific enough for planning to reference directly
- include operational, failure, and validation checks when relevant
- tracked specs map every `SA` item to the active Linear issue and any parent/child issue context

## Dedicated UI spec template
Suggested frontmatter:

```yaml
---
schema_version: 1
title: <UI Spec Title>
type: feat|fix|refactor
status: draft
date: YYYY-MM-DD
parent_spec: .harness/specs/YYYY-MM-DD-<name>-spec.md  # if applicable
origin: .harness/brainstorm/YYYY-MM-DD-<name>-requirements.md  # if applicable; resume legacy *-brainstorm.md only when that is the source artifact
linear_project: TEAM|project-slug                           # required for non-trivial tracked work
linear_issue: ABC-123                                       # required for non-trivial tracked work
linear_parent: ABC-100                                      # if applicable
linear_children: []                                         # if applicable
linear_status: Todo|In Progress|In Review|Done
traceability_required: true
wcag_level: AA
---
```

Required sections:
- Overview
- Component Inventory
- Interaction States
- Design Tokens
- Interaction Flows
- Accessibility Requirements
- Responsive Behaviour
- Telemetry and UX Success Metrics
- Visual Acceptance Criteria
- Out of Scope
- Open Questions
- Decision Log

Visual Acceptance Criteria rules:
- every item carries a stable `VAC` identifier
- cover default, focus, active, loading, empty, error, and success states when relevant
- make each item precise enough for automated or reproducible manual verification

## Verification matrix
Run these checks immediately after writing and patch failures before handoff:

- standard spec:
  - confirm required sections exist
  - confirm `SA` IDs exist in the Acceptance and Test Matrix
  - confirm tracked specs include Linear issue frontmatter and a Linear Acceptance Traceability table
  - confirm frontmatter includes `schema_version`, `risk`, `spec_depth`, and `ui_required`
- dedicated UI spec:
  - confirm required sections exist
  - confirm `VAC` IDs exist in Visual Acceptance Criteria
  - confirm tracked UI specs include Linear issue frontmatter and a Linear Acceptance Traceability table
  - confirm frontmatter includes `schema_version`, `wcag_level`, and any relevant `parent_spec` or `origin`

Suggested commands:

```bash
rg 'SA[0-9]+' .harness/specs/<filename>.md
rg 'VAC[0-9]+' .harness/specs/<filename>.md
rg 'Problem Statement|Failure Model|Observability|Acceptance and Test Matrix' .harness/specs/<filename>.md
rg 'Component Inventory|Interaction States|Accessibility Requirements|Visual Acceptance Criteria' .harness/specs/<filename>.md
rg 'schema_version|ui_required|spec_depth|risk|wcag_level' <spec-path>
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <spec-path>
```

## Notes for full service specs
For service, daemon, orchestrator, or agent-heavy work, expand the standard template into a deeper structure when helpful.

Useful subsections often include:
- system overview and main components
- abstraction layers
- external dependencies
- orchestration or lifecycle states
- failure classes and recovery strategy
- reference algorithms
- test and validation matrix

The user's Symphony example is a good model for this deeper full-spec shape: it is explicit about domain model, state machine, failure handling, observability, and conformance testing without collapsing into a task list.
