---
name: telos
description: "Read or safely update personal TELOS, or analyze project documentation for goals, dependencies, bottlenecks, narratives, reports, and dashboards. Use for life goals, beliefs, strategies, TELOS updates, project relationship analysis, narrative points, or professional TELOS reports. Do not use for general constitutional interviews."
metadata:
  skill-type: runbook
---

# Telos

TELOS has two distinct lanes:

- **Personal TELOS** reads or updates the principal's private life context.
- **Project TELOS** analyzes a user-named directory of Markdown and CSV sources.

Establish the lane and current source before acting. Never mix private personal
TELOS with a project report or public output.

## When to use

- Update goals, beliefs, lessons, books, narratives, strategies, or other TELOS
  material.
- Extract interview content or produce narrative points from supplied sources.
- Map project problems, goals, strategies, projects, dependencies, progress, or
  bottlenecks.
- Produce a source-grounded executive report or dashboard when requested.

For conversational constitutional review, use the Interview skill instead.

## Required inputs

For personal work:

- The exact fact or text to add.
- The intended TELOS file.
- Jamie's confirmation when the change is consequential, ambiguous, protected,
  or replaces current meaning.
- An explicit `LIFEOS_DIR` or `CODEX_LIFEOS_DIR` for candidate-bound writes.

For project work:

- The source directory or named owner route.
- The requested analysis or deliverable.
- Any privacy, publication, or audience constraints.

If the owner, target file, privacy class, or intended meaning is unclear, stop
and ask one direct question.

## Workflow routing

Before a selected workflow, send a best-effort local notification and state:
`Running the <WorkflowName> workflow in the Telos skill to <action>...`.
Notification failure does not authorize a different write route.

- **Personal update:** read [Workflows/Update.md](Workflows/Update.md).
- **Interview extraction:** read
  [Workflows/InterviewExtraction.md](Workflows/InterviewExtraction.md).
- **Narrative points:** read
  [Workflows/CreateNarrativePoints.md](Workflows/CreateNarrativePoints.md).
- **Professional report:** read [Workflows/WriteReport.md](Workflows/WriteReport.md).
- **Direct project analysis:** inspect the named `.md` and `.csv` files, build
  only the relationship model required by the request, and cite the sources.

Load only the selected workflow. The dashboard and report templates are output
assets, not instructions; inspect or copy them only when that deliverable is
requested.

## Personal TELOS contract

Personal TELOS lives under the USER directory returned by the installed
`TOOLS/LifeosConfig.ts` contract. The updater resolves configuration from the
explicit LifeOS runtime root and uses `paths.userDir`; it must not derive the
USER owner by appending to `~/.claude` or `~/.codex`.

Never hand-edit a personal TELOS file. Use `Tools/UpdateTelos.ts`, which must:

1. validate the requested file;
2. create a timestamped pre-change backup;
3. update the target without corrupting a template footer;
4. record the change in the existing-casing changelog; and
5. stop without writing when validation or backup creation fails.

Read current bytes before advising. A successful write does not prove that
derived state, retrieval, publication, or an external owner is current.

## Project analysis contract

Treat the named project repository or source directory as the owner. Discover
only relevant Markdown and CSV files, then make relationships explicit:

`PROBLEMS -> GOALS -> STRATEGIES -> PROJECTS`

Report missing links, contradictions, blockers, freshness limits, and source
paths. Do not invent completion percentages, dependencies, people, budgets, or
current project truth. A dashboard or report is a derived view, not an owner
system.

## Deliverables

Return the smallest requested artifact:

- personal update receipt with target, backup, changelog entry, and readback;
- source-grounded Markdown or JSON analysis;
- narrative points from the selected workflow;
- professional report from the selected workflow; or
- dashboard based on the bundled template when explicitly requested.

Always identify what changed, the source or owner route, validation evidence,
and what remains unproven.

## Execution boundaries

- Personal, medical, family, legal, financial, and trauma material is private.
- Never publish, message, apply, deploy, or share TELOS material without the
  matching explicit authorization.
- Never copy mutable project truth into personal TELOS merely to simplify
  retrieval.
- Preserve unrelated dirty files and external owner systems.
- Helpers may analyze sanitized inputs but cannot approve a personal write or
  declare verification complete.
- A failed notification, optional visualization, or template build must not
  bypass the updater, backup, privacy, or source checks.

## Failure mode

Stop before mutation when:

- the file is unsupported;
- the LifeOS configuration or USER owner path cannot be resolved;
- backup creation fails;
- the requested change conflicts with current meaning without explicit review;
- protected material is headed to an ordinary or public surface; or
- the project source or requested output owner is missing.

After a partial failure, report whether a backup, target write, or changelog
entry occurred. Do not claim atomicity unless the implementation proves it.

## Validation and acceptance criteria

For updater changes, run:

`python3 -m unittest -v Skills/product-strategy/telos/Tools/test_update_telos.py`

For package and projection changes, run:

- `./bin/ask skills audit Skills/product-strategy/telos --level compat --json --robot`
- `./bin/ask skills resolve telos --json --robot`
- `./bin/ask skills proof telos --runtime-target codex --json --robot`
- `git diff --check -- Skills/product-strategy/telos`

Acceptance requires updater tests, package audit, unique canonical resolution,
and structural runtime gates to pass. Missing live invocation telemetry blocks
only the live-runtime claim; it does not negate source or projection evidence.

## Gotchas

- The runtime root and USER owner may be different physical paths; trust
  `LifeosConfig.paths.userDir`.
- `updates.md` and `Updates.md` are one logical changelog; preserve whichever
  casing already exists.
- A backup plus target write is not a complete success when changelog recording
  fails; report the partial state.
- A generated dashboard, report, or state file is derived evidence, not new
  owner truth.

## Expected artifacts

- Canonical source: `Skills/product-strategy/telos/`.
- Runtime projection: `.agents/skills/telos`.
- Personal backup: `<userDir>/TELOS/Backups/<FILE>-<timestamp>.md`.
- Personal changelog: existing `updates.md` or `Updates.md`.
- Derived reports or dashboards: the user-approved project output directory.

Keep generated runtime-proof evidence, caches, private TELOS data, and local
build output out of the canonical package.
