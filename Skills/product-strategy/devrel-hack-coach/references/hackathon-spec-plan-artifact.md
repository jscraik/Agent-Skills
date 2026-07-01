# Hackathon Spec And Plan Artifact

Use this reference when the coach has enough grounded decisions to produce the
followable artifact for a hackathon project, demo, or short community-meet
presentation.

This shape adapts the Harness Engineering spec and plan artifact contracts for
hackathon coaching. Keep it lighter than a repo implementation plan, but make it
strong enough that the user can build, rehearse, and explain scope without
digging through chat history.

## Artifact Contract

Emit a single Markdown artifact in the conversation. Do not write files unless
the user separately asks for package maintenance or artifact persistence outside
the coaching workflow.

Use this title:

    # Hackathon Spec And Plan Artifact

Start with a compact status block:

    schema_version: devrel-hack-coach-artifact/v1
    artifact_type: hackathon_spec_and_plan
    phase: Phase 4 - Pitch It
    artifact_status: drafted|locked|blocked
    track: <track or context>
    timebox: <timebox or presentation slot>
    primary_user: <specific role>
    live_golden_path: <one sentence>
    mocked_or_stubbed: <one sentence>
    validation_evidence: <exact command/outcome or not-run reason>
    handoff_state: stop_planning_go_build|blocked_needs_input

## Required Sections

### Bottom Line

One plain-English paragraph explaining what the hack changes for the user, why
the demo matters, what is intentionally out of scope, and what could stop the
demo.

### Grounded State

List only decisions the user has already supplied or explicitly accepted:

- Stack
- Track or event context
- Primary user
- Named itch
- Selected angle
- Featured object, skill, dataset, workflow, or product surface
- Timebox or presentation slot
- Real-vs-mocked boundary

Use `[NEEDS DECISION: ...]` for missing fields. Do not invent them.

### Locked Spec

Use these fields:

- Goal
- User
- Demo moment
- What's in
- What's out
- Timebox success
- Red flags
- Fallback path

The demo moment must be stage directions:

- User or judge does:
- System does:
- User or judge sees:

### Execution Plan

For a 24-hour build, include these checkpoint artifacts:

| Checkpoint | Time | Artifact | Proof | Risk | Fallback |
| --- | --- | --- | --- | --- | --- |
| Smoke test | T+2h |  |  |  |  |
| Golden path | T+8h |  |  |  |  |
| Second scenario | T+16h |  |  |  |  |
| Pitch dry-run | T+22h |  |  |  |  |

For a 1-hour prep sprint or 5-minute presentation, include these checkpoint
artifacts:

| Checkpoint | Time | Artifact | Proof | Risk | Fallback |
| --- | --- | --- | --- | --- | --- |
| Lock wedge | first 10 minutes |  |  |  |  |
| Rehearse demo path | next 20 minutes |  |  |  |  |
| Pitch and Q&A | next 20 minutes |  |  |  |  |
| Timed handoff | final 10 minutes |  |  |  |  |

If the user gives a custom or unlimited build window, keep the 24-hour
checkpoint names as quality gates and state that they are demo-readiness
checkpoints, not calendar deadlines.

### Live, Mocked, Stubbed, Deferred

Name the boundary before writing the pitch:

- Live:
- Mocked:
- Stubbed:
- Deferred:

Do not claim real Tessl, registry, CI, security, marketplace, or production
proof unless the user supplied exact current evidence or a command result was
run in a separate authorized maintenance lane.

### Pitch

Write exactly three sentences, each under 20 words:

1. Wedge: When you try to do X today, Y breaks.
2. Move: We built Z that does W.
3. Moment: Watch this.

### Judge Q&A

Include five one-line answers:

- How does this scale?
- Why not just use the nearest existing tool?
- What if the LLM hallucinates?
- Who pays?
- What's your moat?

### Validation And Evidence Boundary

Use exact evidence wording:

- `Command: <exact command> -> pass|fail|blocked (<reason>)` when a command ran.
- `Validation: not run (<reason>)` when no command ran.

For coaching-only sessions, the usual evidence line is:

    Validation: not run (coaching-only session; no repository or runtime checks were requested)

### Handoff

End with the one immediate build or rehearsal action, then the terminal stop
message from `SKILL.md`.

## Blocked Artifact

If required fields are missing, emit the artifact with `artifact_status: blocked`,
fill known sections, mark missing fields with `[NEEDS DECISION: ...]`,
and ask one next question. Do not skip to implementation.
