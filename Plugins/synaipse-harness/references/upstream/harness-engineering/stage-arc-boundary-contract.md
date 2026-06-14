# HE Stage Arc Boundary Contract

Read when: any Harness Engineering skill accepts a task, writes an artifact,
routes to another stage, mutates code or trackers, schedules continuation, or
claims closure.

This contract prevents a stage from treating the visible task as the whole arc.
Every stage must name what came before it, what it owns, what it must hand off,
and what it explicitly does not prove.

## Required Arc Fields

Use this compact shape in stage outputs, artifacts, or handoff payloads:

```yaml
stage_arc_boundary:
  left_arc:
    source_of_truth: "<repo, tracker, artifact, PR, runtime, or user authority>"
    entry_authority: explicit|inferred|blocked
    freshness_required: fresh|allowed_stale|not_applicable
    not_proof: "<chat, transcript, provenance, green CI, or local artifact limits>"
  active_arc:
    owned_stage: he-reconcile|he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-reconcile|he-reinforce|he-phase-work|he-eval-report|he-strategy|he-reframe|he-linear-plan|he-phase-work|he-phase-heartbeat
    allowed_actions: "<read, artifact write, repo edit, external mutation, schedule>"
    forbidden_actions: "<actions outside this stage>"
    mutation_boundary: none|local_artifact|repo_edit|external_mutation|destructive
  right_arc:
    handoff_target: "<next HE stage, human, tracker, PR, eval, or none>"
    handoff_artifact: "<path, payload, issue id, PR, heartbeat id, or none>"
    proof_required: "<validation, review, live state, runtime receipt, or blocker>"
    closure_boundary: not_closure|local_only|live_ready|closed_with_receipt
    resume_key: "<issue, PR, artifact chain, heartbeat id, or not_applicable>"
  persona_lenses:
    coding_lens: required|conditional|not_applicable
    testing_lens: required|conditional|not_applicable
    coverage_parity_required: yes|no
```

## Left Arc

The left arc is the task's entry side. It names the current authority and the
evidence that is fresh enough to use.

- Specs and plans need an approved selected slice, not just a broad goal.
- Work and repair need an admitted execution unit plus edit authority.
- Review and eval need the exact diff, artifact, PR, or closure claim being
  judged.
- Heartbeats need a stop rule and resume target, not autonomous execution
  authority.
- Session, transcript, rollout, OTEL, provenance, and collector evidence can
  explain recurrence, but they are not proof of current repo state, tracker
  state, CI, tests, runtime health, or user acceptance without live refresh.

## Active Arc

The active arc is the stage-owned middle. It names what the skill may do now and
what is outside its authority.

- Non-mutating stages may write local review, strategy, brainstorm, or routing
  artifacts only when artifact writes are authorized.
- Local artifact generation does not imply permission to edit product code,
  mutate Linear/GitHub, resolve review threads, commit, push, merge, deploy, or
  delete state.
- Implementation-capable stages must keep allowed paths, forbidden paths,
  external mutation boundaries, and validation ownership visible.

## Right Arc

The right arc is the exit side. It names what must be true before the next stage
or closure can trust the output.

- A handoff must include a target, artifact or payload, proof required, and
  resume key.
- A stage cannot close work from its own local output unless the closure boundary
  says exactly what live proof was refreshed.
- If a source request asked for full implementation, any downscope must preserve
  unfinished scope and name explicit approval or block.

## Coding and Testing Persona Lenses

Apply coding and testing lenses whenever the stage can create, route, review,
repair, validate, or close implementation work.

- `coding_lens` names ownership, allowed surfaces, forbidden surfaces, API or
  schema impact, data boundaries, rollback posture, and maintainability risk.
- `testing_lens` names observable behavior, required positive/negative/stale
  checks, proof command, missing proof, and validation ownership.
- If a requested reviewer role is unavailable, the replacement must include
  `coverage_parity_required: yes` with the omitted lens, substitute evidence,
  unresolved risk, and whether the gap blocks handoff.

## Stop Rules

Block rather than infer when:

- `left_arc.entry_authority` is `blocked` or only historical session evidence.
- `left_arc.freshness_required` is fresh but live state is stale or unavailable.
- `active_arc.mutation_boundary` exceeds current approval.
- `right_arc.proof_required` is unknown, skipped, or only local prose.
- `persona_lenses.coding_lens` or `testing_lens` is required but absent.
