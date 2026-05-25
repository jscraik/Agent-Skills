# Implementation Notes Contract

Read when Goal Governor creates, imports, continues, repairs, or closes a
governed implementation goal with Worker tasks.

## Contract

Every governed implementation lane with a Worker task must produce an MDX
implementation notes artifact in the target project:

```text
.harness/implementation-notes/<date>-<project-or-work>-notes.mdx
```

The file is part of the harness operating surface. It is not optional
documentation, not a screenshot bundle, and not a static HTML dump.

## Board Linkage

`state.yaml` must reference the artifact:

```yaml
artifacts:
  implementation_notes:
    path: ".harness/implementation-notes/2026-05-25-example-notes.mdx"
    format: mdx
    status: present
    browser_preview:
      surface: localhost
      status: blocked
      blocker: "Browser preview unavailable in this environment."
      live_update:
        status: blocked
        blocker: "Browser live update unavailable in this environment."
```

The artifact path must also appear in the active Worker task's
`allowed_files`. If it is missing from `allowed_files`, the Worker is not
authorized to create or update the artifact.

## Required MDX Sections

The artifact must include frontmatter with `schema_version` and these visual
sections:

- Deep Module Topology
- Current Slice Insertion Map
- Runtime Truth Surface
- Blast Radius View
- Validation Coverage

## Required React Components

The MDX source must embed data-driven React components. At minimum, the
validator expects:

- `<DeepModuleMap />`
- `<InsertionPoint />`
- `<RuntimeCardState />`
- `<BlastRadiusMap />`
- `<ValidatorCoverage />`

Additional components such as `RuntimeFlow`, `TraceTopology`,
`GovernanceBoundary`, `RecoveryFlow`, `ArtifactLifecycle`,
`ReviewState`, and `DependencyGraph` should be used when they clarify the
current work.

## Browser Preview Lane

Browser verification should use a rendered localhost surface. Raw MDX or hidden
`.harness` file paths are not enough because the Browser plugin can inspect a
rendered page more reliably than a hidden local source file.

When Browser preview passes, record:

```yaml
browser_preview:
  surface: localhost
  status: verified
  url: "http://localhost:<port>/<preview-path>"
  live_update:
    status: enabled
    command: "<localhost MDX renderer or dev-server watch command>"
    watched_path: ".harness/implementation-notes/2026-05-25-example-notes.mdx"
```

`live_update.status: enabled` means the Browser-visible localhost surface is
watching the MDX source and updates when the artifact changes, through hot
reload, file watch, or timed refresh. The `watched_path` must match
`artifacts.implementation_notes.path` so future agents know which source file
drives the live view.

When Browser preview cannot run, record a blocked lane with the exact reason:

```yaml
browser_preview:
  surface: localhost
  status: blocked
  blocker: "Browser plugin unavailable in this environment."
  live_update:
    status: blocked
    blocker: "No localhost MDX renderer is available in this environment."
```

Blocked Browser preview does not remove the MDX artifact requirement. It only
classifies the visual verification lane. A verified Browser preview must not
claim success unless the live-update lane is enabled.

## Invalid Outputs

- Plain HTML notes as the source artifact.
- Prose-only Markdown notes.
- Static screenshots without runtime linkage.
- Notes outside `.harness/implementation-notes/`.
- Worker implementation that changes source without updating the MDX artifact.
- Completion claims where the artifact exists but lacks required sections or
  required React component tags.
