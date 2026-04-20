# CE Spec Artifact Templates

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
title: <Spec Title>
type: feat|fix|refactor
status: draft
date: YYYY-MM-DD
origin: docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md  # if applicable
risk: low|medium|high
spec_depth: none|lite|full
ui_required: true|false
---
```

Required sections:
- Problem Statement
- Goals
- Non-Goals
- System Boundary
- Core Domain Model
- Main Flow / Lifecycle
- Interfaces and Dependencies
- Invariants / Safety Requirements
- Failure Model and Recovery
- Observability
- Acceptance and Test Matrix
- Open Questions
- Definition of Done

Acceptance and Test Matrix rules:
- every item carries a stable `SA` identifier
- each item is specific enough for planning to reference directly
- include operational, failure, and validation checks when relevant

## Dedicated UI spec template
Suggested frontmatter:

```yaml
---
title: <UI Spec Title>
type: feat|fix|refactor
status: draft
date: YYYY-MM-DD
parent_spec: Docs/specs/YYYY-MM-DD-<name>-spec.md  # if applicable
origin: docs/brainstorms/YYYY-MM-DD-<name>-brainstorm.md  # if applicable
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
  - confirm frontmatter includes `risk`, `spec_depth`, and `ui_required`
- dedicated UI spec:
  - confirm required sections exist
  - confirm `VAC` IDs exist in Visual Acceptance Criteria
  - confirm frontmatter includes `wcag_level` and any relevant `parent_spec` or `origin`

Suggested commands:

```bash
rg 'SA[0-9]+' Docs/specs/<filename>.md
rg 'VAC[0-9]+' docs/ui-specs/<filename>.md
rg 'Problem Statement|Failure Model|Observability|Acceptance and Test Matrix' Docs/specs/<filename>.md
rg 'Component Inventory|Interaction States|Accessibility Requirements|Visual Acceptance Criteria' docs/ui-specs/<filename>.md
rg 'ui_required|spec_depth|risk|wcag_level' <spec-path>
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
