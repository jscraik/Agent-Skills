# Closure And Mutation Contract

Read when: an HE stage evaluates completion, tracker state, or live external
mutation.

Keep these states separate:

- proof artifact written: local evidence exists and is validated or blocked
- closure recommendation made: the report says Complete, Complete with
  follow-up, Blocked, Needs rework, or Unsafe to close
- live state read: current Linear, PR, CI, release, or runtime state was checked
- mutation authorized: the user explicitly approved the specific external write
- mutation applied: the tool returned the created or updated object identifier
- readback verified: a targeted live read confirmed the changed object state

A local HE artifact never proves live tracker mutation. A merged PR never proves
release or Linear completion. Closure language must name which of the above
states is proven, blocked, or not applicable.

Default output fields:

- proof_artifact_status
- closure_recommendation
- live_state_read_status
- mutation_authority
- mutation_applied_status
- readback_status
- next_safe_action
