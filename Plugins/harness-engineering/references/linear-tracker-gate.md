# Linear Tracker Gate

Use this reference whenever `he-brainstorm`, `he-spec`, or `he-plan` handles non-trivial work that is intended to become delivery, QA, bug-fix, improvement, refactor, or operator-visible change.

## Rule

Linear is the tracker of record. A Harness Engineering brainstorm, spec, or plan can support Linear, but it does not replace it.

Before a non-trivial HE stage hands work to the next lifecycle stage, the agent must resolve an existing Linear issue or create one through the Linear workflow. If creation is blocked, the stage must stop with a `linear_blocked` status, exact missing fields, and a ready-to-create issue payload.

## Applies To

Run the gate when any of these are true:

- the user mentions a bug, issue, QA report, feature, improvement, refactor, release, plan, spec, PR, or tracked delivery work;
- the output will become a durable requirements, spec, plan, or implementation handoff artifact;
- work needs acceptance criteria, priority, owner, blocker ordering, or PR traceability;
- multiple HE stages or agents will use the artifact later.

The gate does not apply to throwaway exploration, tiny local-only edits, private note cleanup, or requests where the user explicitly says not to use Linear. When the user opts out, record `linear_status: user_opted_out` and do not present the work as normally traceable.

## Required Workflow

1. Read first. Use the Linear workflow to search/list/get likely existing issues before creating a new one.
2. Reuse if found. Link the issue key/URL and summarize why it is the tracker of record.
3. Create if missing and required metadata is available. Use the appropriate team, project, title, description, labels, priority, cycle, assignee, and blocker links.
4. Block if metadata or tooling is missing. Return `linear_status: linear_blocked`, the exact missing fields or disconnected tool state, and a complete issue payload the user can approve or use after reconnecting Linear.
5. Continue only after the stage has either `linear_status: resolved|created|user_opted_out` or an explicit user decision to proceed despite `linear_blocked`.

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
