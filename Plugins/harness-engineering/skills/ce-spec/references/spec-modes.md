# CE Spec Modes

Read when: you need to choose between a standard system spec and a dedicated UI spec, or when you need the compatibility rules for UI-spec paths.

## Table of Contents
- [Mode selection](#mode-selection)
- [Depth selection](#depth-selection)
- [UI companion rules](#ui-companion-rules)
- [Artifact paths](#artifact-paths)
- [Compatibility notes](#compatibility-notes)

## Mode selection
Use `standard-spec` when the main need is a product, service, workflow, or system contract that planning can later consume directly.

Use `dedicated-ui-spec` when the main need is a UI contract:
- component inventory
- interaction states
- design tokens
- accessibility and responsive behavior
- visual acceptance criteria

## Depth selection
Use `spec_depth: none` when spec overhead outweighs value and the user did not explicitly ask for a spec.

Use `spec_depth: lite` for medium-risk work touching multiple modules, APIs, auth, caching, migrations, integrations, retries, or other non-trivial behavior.

Use `spec_depth: full` for:
- services or daemons
- concurrency or state machines
- agent or orchestration behavior
- data integrity or security-sensitive flows
- multiple failure modes with explicit recovery needs

## UI companion rules
If a standard spec involves:
- new screens, pages, views, or routes
- new or modified components or design-system changes
- user-facing interactions, forms, modals, or wizards
- visual regression or accessibility concerns

then set `ui_required: true`.

If `ui_required: true` is set and no explicit UI contract exists yet, recommend a companion dedicated UI spec before planning begins.

## Artifact paths
- standard specs: `Docs/specs/YYYY-MM-DD-<type>-<descriptive-name>-spec.md`
- dedicated UI specs: `docs/ui-specs/YYYY-MM-DD-<descriptive-name>-ui-spec.md`

## Compatibility notes
Prefer `docs/ui-specs/` for dedicated UI specs.

Support the older `Docs/specs/YYYY-MM-DD-<topic>-ui-spec.md` form only when:
- the repo already uses that convention
- the user explicitly requests compatibility
- another downstream workflow still depends on the older location
