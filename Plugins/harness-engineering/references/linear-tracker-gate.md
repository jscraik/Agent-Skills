# Linear Tracker Gate

Use this when `he-brainstorm`, `he-spec`, or `he-plan` handles non-trivial delivery, QA, bug-fix, improvement, refactor, or operator-visible work.

## Rule

Linear is the tracker of record. HE brainstorms, specs, and plans support Linear; they do not replace it.

Before handoff, resolve or create the Linear issue. If creation is blocked, stop with `linear_blocked`, exact missing fields, and a ready-to-create payload.

When the target repo is coding-harness-managed, prefer the repo's Harness Linear gate or transition command when available, and record the result in the `coding_harness` lifecycle block. The Linear issue remains mandatory; Harness state does not replace it.

## Applies To

Run the gate when any of these are true:

- the user mentions a bug, issue, QA report, feature, improvement, refactor, release, plan, spec, PR, or tracked delivery;
- the output becomes durable requirements, spec, plan, or implementation handoff;
- work needs acceptance criteria, priority, owner, blocker ordering, or PR traceability;
- multiple HE stages or agents will use the artifact.

The gate does not apply to throwaway exploration, tiny local-only edits, private note cleanup, or explicit no-Linear requests. When opted out, record `linear_status: user_opted_out` and do not present the work as normally traceable.

## Required Workflow

1. Search/list/get likely Linear issues before creating one.
2. Reuse if found; link key/URL and why it is tracker of record.
3. Create if missing and metadata is available.
4. If metadata/tooling is missing, return `linear_status: linear_blocked`, exact missing fields/tool state, and a complete ready payload.
5. Continue only after `linear_status: resolved|created|user_opted_out` or an explicit decision to proceed despite `linear_blocked`.

## Minimum Issue Payload

```yaml
linear_status: created|resolved|linear_blocked|user_opted_out
linear_issue:
  key: "<issue key when known>"
  url: "<issue URL when known>"
  team: "<team key or missing>"
  project: "<project or missing>"
  title: "<plain behavior title>"
  priority: "<priority or missing>"
  labels: ["<labels>"]
  blocked_by: ["<issue keys or None - can start immediately>"]
  body_sections:
    - Problem / actual behavior
    - Expected behavior or decision needed
    - Acceptance criteria or required clarification
    - Source artifacts and HE stage links
```

## Stage-Specific Behavior

`he-brainstorm` clarifies ambiguity first, then gates before durable handoff. If the problem is not clear enough for a delivery issue, create or prepare a discovery/requirements issue rather than pretending there is no tracker need.

`he-spec` gates before writing or revising a tracked spec. The spec must include Linear Work Item Contract frontmatter and Linear Acceptance Traceability.

`he-plan` gates before sequencing delivery. The plan must include source-to-plan-to-PR traceability and any parent/child/blocker issue graph.

## Blocker Language

Use concise blocker language:

```md
linear_status: linear_blocked
missing_fields: team, project, priority
blocked_reason: Linear issue is mandatory for this tracked HE stage, but I cannot create it without the missing metadata.
ready_to_create_payload: ...
next_action: Provide the missing fields or connect Linear, then rerun this stage from the same source artifact.
```

Do not silently downgrade the stage to optional tracker usage. Do not rely on a GitHub PR, local plan, spec, or session summary as the tracker of record.
