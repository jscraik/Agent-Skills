# UI Plan Routing Contract

Use this when `he-plan`, `he-work`, `he-code-review`, or `he-compound` sees a
UI implementation plan path.

## Canonical Root

Dedicated UI plans are Harness Engineering plan artifacts. New UI plans belong
under:

```text
.harness/plan/YYYY-MM-DD-<topic>-ui-plan.md
```

Use `docs/ui-plans/**`, `docs/ui-plan/**`, `Docs/plans/*-ui-plan.md`, or
`Docs/ui-plans/**` only as legacy source evidence or when the user explicitly
asks to maintain the existing repo convention.

## Stage Ownership

- `he-spec` owns dedicated UI specs under `.harness/specs/**`.
- `he-plan` owns dedicated UI plans under `.harness/plan/**-ui-plan.md`.
- `he-work` may execute an approved UI plan after checking it maps to one
  selected execution slice.
- `he-code-review` may review a UI plan or UI-plan implementation for fidelity,
  accessibility, responsive behavior, and screenshot evidence.
- `he-compound` may route or resume UI-plan work, but it should hand off to
  `he-plan`, `he-work`, or `he-code-review` instead of inventing UI execution
  scope.

## Required UI Plan Shape

Dedicated UI plans should include:

- source UI spec or parent spec path;
- selected Linear/refactor slice when tracked;
- `UP` phase IDs;
- `UAC` acceptance/checklist IDs;
- prototype or visual-direction decision when design direction is unsettled;
- accessibility, responsive, and visual-verification gates;
- screenshot or browser evidence requirements before review/closeout.

If a legacy UI plan lacks those fields, treat it as source evidence and create a
replacement `.harness/plan/**-ui-plan.md` when planning is in scope.

## Project Brain Feed

When the repo has `.harness/knowledge/**` or an explicit Project Brain contract,
UI plans must report one of:

```yaml
project_brain_status: updated|blocked|not_applicable|explicitly_deferred
project_brain_evidence:
  source: ".harness/plan/<topic>-ui-plan.md"
  target: ".harness/knowledge/ui/knowledge.md"
  reason: "<why synced, deferred, blocked, or not applicable>"
```

Feed UI plans into Project Brain as plan/decision reference, not as solved
knowledge by default. Capture:

- source UI spec or parent spec path;
- selected Linear/refactor slice;
- UI direction or prototype decision;
- major accessibility/responsive constraints;
- visual verification gates.

Promote a UI-plan result into `.harness/solutions/**` only after implementation
or review proves a reusable solved pattern. Until then, keep it as Project Brain
context for future planning and execution.

Apply the same redaction gate used by solution capture before syncing to Project
Brain or Local Memory.
