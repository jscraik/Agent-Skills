# Linear Delta Capture Gate

Use this before `he-spec`, `he-plan`, or `he-work` consumes a tracked
execution slice from `.harness/linear/**`.

## Rule

Linear is the tracker of record, but `.harness/linear/<repo-name>-linear-plan.md`
is the approved execution snapshot. New or changed Linear issues must be
captured as deltas first, then promoted into exactly one approved next slice
only after triage.

Do not let a new Linear issue, review finding, strategy note, or feature note
expand the current plugin Harness Engineering spec or work plan by itself.

## Required Workflow

1. Read the current `.harness/linear/<repo-name>-linear-plan.md`.
2. Resolve the selected Linear project, milestone, parent issue, child issues,
   labels, priority, dependencies, and agent/human route from that plan.
3. Query/list the matching live Linear objects when Linear tooling is available.
4. Reconcile required labels against the live Linear workspace before classifying
   issues.
5. Compare the live Linear graph with the plan snapshot.
6. Classify every new or changed issue as one of:

```text
already_covered
duplicate_or_superseded
candidate_next_slice
blocker_for_current_slice
out_of_scope
needs_human_triage
```

7. Update the `.harness/linear/**` plan's delta section when writing is in
   scope; otherwise return the exact delta table as the handoff.
8. Promote at most one item into `Approved Current Slice` or
   `Approved Next Slice Queue` per HE stage handoff.

## Label Reconciliation

Labels are part of the execution contract. Before selecting or promoting a
slice, verify that every required label from the plan exists in Linear and is
applied to the selected parent and child issues.

Use this order:

1. Read existing Linear labels for the target team/project.
2. Normalize only obvious spelling/case drift when the intended label is clear.
3. Reuse existing labels when they match the plan's approved label policy.
4. Create missing labels only when the plan or user has approved a reusable
   label category.
5. If label creation is blocked by permissions, missing team/project metadata,
   or uncertainty, return `label_status: blocked` with a ready-to-create label
   payload.

Minimum label payload:

```yaml
label_status: resolved|created|blocked|not_required
labels:
  - name: "<label>"
    status: existing|created|missing|blocked
    reason: "<why this label is required>"
ready_to_create:
  - name: "<label>"
    team: "<team key or missing>"
    description: "<plain reusable purpose>"
```

Do not create one-off labels for a single issue when the current `.harness`
plan calls for minimal reusable labels. Classify that as `needs_human_triage`
unless the user explicitly approves the new label.

## Plan Section Contract

When maintaining `.harness/linear/<repo-name>-linear-plan.md`, use these
sections:

```md
## Approved Current Slice

The single milestone, parent issue, refactor phase, or execution slice that
`he-spec`, `he-plan`, or `he-work` may consume now.

## Linear Delta Capture

Last synced: <YYYY-MM-DD or blocked>
Source: Linear project <project>, milestone <milestone>, parent <issue>
Label status: resolved|created|blocked|not_required

| Issue | Title | Status | Priority | Classification | Reason |
| --- | --- | --- | --- | --- | --- |

## Approved Next Slice Queue

| Order | Slice | Linear Issue | Route | Depends On | Notes |
| --- | --- | --- | --- | --- | --- |
```

## Classification Rules

`blocker_for_current_slice` blocks the active stage until the blocker is
resolved, explicitly deferred, or converted into the selected slice.

`candidate_next_slice` can enter `Approved Next Slice Queue` only when it has a
clear priority, dependency posture, and execution route.

`needs_human_triage` must not be specified, planned, or implemented until a
human or explicit Linear planning artifact admits it.

`out_of_scope`, `duplicate_or_superseded`, and `already_covered` are recorded
for traceability but do not drive implementation.

## Output Status

Use this shape in handoffs when a structured result is useful:

```yaml
schema_version: 1
linear_delta_status: updated|no_change|blocked|needs_human_triage
current_slice_status: continue|blocked|complete
label_status: resolved|created|blocked|not_required
next_slice:
  type: milestone|parent_issue|refactor_phase|execution_slice|none
  linear_issue: "<issue key or none>"
  reason: "<why this is next or why none is selected>"
updated_artifacts:
  - ".harness/linear/<repo-name>-linear-plan.md"
```

## Stop Rules

Stop and return the smallest recovery step when:

- the current `.harness/linear/**` plan is missing for tracked work;
- the selected project, milestone, parent issue, priority, dependency posture,
  or execution route cannot be resolved;
- Linear tooling is required but unavailable;
- required labels are missing and cannot be reused, created, or explicitly
  deferred;
- a live Linear delta conflicts with the approved current slice;
- more than one next slice is being promoted at once.
