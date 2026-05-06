# Design Complexity Contract

Read when: improving, reviewing, or routing Harness Engineering skills where a change may alter stage boundaries, context handoffs, output contracts, or caller cognitive load.

This contract keeps HE stages deep, small, and agent-native. It complements `domain-context-contract.md`: domain context protects meaning; design complexity protects the interface that carries that meaning.

## Interface Goal

Each HE stage should be a deep module: a small caller-facing contract with enough behavior hidden behind it that the next agent can act without carrying unrelated lifecycle state in working memory.

Prefer changing shared contracts, evals, or references when the same rule would otherwise need to be copied across multiple stage entrypoints.

## Complexity Red Flags

Classify at least one red flag before changing HE skill behavior:

- `change_amplification`: one behavior change requires edits to several unrelated stage files.
- `cognitive_load`: the caller must know stage internals, validation policy, tracker rules, or output shapes that the stage could own.
- `unknown_unknown`: the skill does not say which evidence must be fresh before action.
- `obscurity`: rule ownership is unclear between `SKILL.md`, `contract.yaml`, `evals.yaml`, and references.
- `shallow_stage`: a stage mostly passes through to another stage without adding a distinct abstraction.
- `leaked_state`: Linear, PR, Project Brain, validation, heartbeat, or goal state must be repeated manually instead of moving through a lifecycle exit.
- `special_case_sprawl`: a narrow prompt fix adds another branch where a general stage contract or eval would reduce future branches.
- `term_drift`: Linear, spec, plan, code, or review names diverge in ways that can change behavior.
- `context_bleed`: one HE stage or artifact silently applies another context's model without translation.
- `source_model_corruption`: external review, CI, session, or user wording changes HE meaning without anti-corruption translation.
- `unmapped_context_handoff`: an artifact handoff lacks source context, target context, freshness, or conflict status.
- `core_domain_obscured`: supporting workflow detail hides HE's core domain of intent, evidence, and lifecycle truth.

## Shared Output Envelope

When a stage returns structured output or hands off to another HE stage, include the lifecycle exit contract fields and preserve this compact envelope:

```yaml
schema_version: 1
he_stage: "<he-router|he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-compound|he-heartbeat>"
status: pass|blocked|needs_route|needs_user
owned_artifact: "<path or not_applicable>"
evidence_freshness: fresh|stale|blocked|not_applicable
red_flags: []
domain_language:
  status: stable|ambiguous|conflicted|not_applicable
context_map:
  source_of_truth: user_request|linear|spec|plan|worktree|pr|validation|project_brain|heartbeat|goal|session_evidence|not_applicable
  conflict_status: none|blocked|resolved|not_applicable
blocker: "<smallest recovery step or null>"
next_stage: "<he-stage|done|null>"
validation:
  commands: []
  outcomes: []
```

Stage-specific output may add fields, but it should not omit blocker, evidence freshness, validation status, or next-stage state when those are relevant.

## Design It Twice

Before changing a stage interface, sketch two alternatives:

- `patch_design`: the smallest local edit to the current stage.
- `interface_design`: a shared contract, reference, or eval change that reduces future caller burden.

Choose by answering:

- Which design makes the caller know less?
- Which design changes fewer files next time?
- Which design has the clearer eval?

If the local patch wins, record why the shared interface would be overreach. If the shared interface wins, keep `SKILL.md` to a signpost plus the stage-specific rule.

## Ownership Rule

Keep each rule in the narrowest durable owner:

- `routing-map.json`: stage selection rules.
- `SKILL.md`: stage boundary, caller contract, and signposts.
- `contract.yaml`: inputs, outputs, risks, observability, rollback.
- `evals.yaml`: executable or reviewable proof cases.
- `references/*.md`: rationale, retained context, cross-stage contracts.

When the same rule appears in more than one owner, keep the canonical owner and replace duplicates with a signpost unless the duplicate is required for runtime routing.

## Evaluation Requirements

Add or update evals when a change addresses any of these failure modes:

- repeated feedback that should become a broken-window classification;
- low-confidence router output that needs deterministic clarification;
- pass-through stage behavior that should be folded or split;
- stale evidence acted on as fresh;
- duplicated ownership rules with conflicting wording;
- an improvement made without recording the red flag or design alternative;
- domain term drift, context bleed, or source-model corruption changes behavior without a mapped handoff.

## Stop Rule

A design-complexity improvement is not complete until:

- the changed skill still passes strict audit;
- at least one eval or contract field covers the triggering red flag;
- retained rationale is in a reference, not bloated entrypoint prose;
- lifecycle exit output still includes blocker, freshness, validation, and next-stage state;
- remaining limitations are explicit blockers or non-goals.
