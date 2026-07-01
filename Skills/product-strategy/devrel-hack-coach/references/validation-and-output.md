# Validation And Output

## Coaching Output Fields

Every coaching response must expose these fields in plain language:

- `schema_version`: use `devrel-hack-coach-output/v1`.
- `phase`: current workflow phase.
- `gate_state`: what is complete and what is still missing.
- `next_prompt_or_artifact`: one next question or the next artifact.
- `grounded_state`: decisions already supplied by the user.
- `boundary_status`: whether the request stayed inside hackathon coaching.
- `artifact_status`: use `drafted`, `locked`, or `blocked` for the
  Hackathon Spec And Plan Artifact.

## Final Artifact Contract

Before the terminal stop message, emit the consolidated artifact from
`references/hackathon-spec-plan-artifact.md`. The artifact must include the
locked spec, checkpoint plan, pitch, Q&A, live/mocked/stubbed/deferred boundary,
validation evidence or not-run reason, and one handoff action.

Do not claim a prototype, app, Tessl score, security pass, registry state, or
runtime integration exists unless the session has exact command evidence or a
workflow-closeout/v1 receipt for that lane.

## Package Validation Lane

Use repository wrappers for package checks:

```sh
./bin/ask skills package verify Skills/product-strategy/devrel-hack-coach --json --robot
./bin/ask sdk eval scenario-quality Skills/product-strategy/devrel-hack-coach --preview --json --robot
```

These commands prove package and scenario gates only. They do not prove OSS,
Tessl, registry, PR, or runtime readiness.
