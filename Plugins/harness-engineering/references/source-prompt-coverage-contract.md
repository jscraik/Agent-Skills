# Source Prompt Coverage Contract

Use this contract when a Harness Engineering run compares skillized output with
an original prompt, external workflow, prior manual method, or long-form source
prompt.

## Purpose

Prevent shallow lifecycle artifacts from being promoted into authoritative
strategy, reframe, Linear, ADR, or core guidance when they did not actually
cover the original prompt method.

This contract protects against evidence-depth laundering: a valid sampled
artifact can remain useful locally, but it must not become repo-wide authority
without matching source-prompt coverage evidence.

It also preserves repo-specific drift signals discovered during the comparison.
Those signals are part of the source evidence, not generic decoration; downstream
artifacts must either inherit them or explain why they do not apply.

## Trigger

Load this reference when any of these are true:

- the user asks whether HE output matches an original prompt workflow
- a source prompt, old prompt method, external workflow, or plugin comparison is
  provided as the baseline
- downstream artifacts already exist and their authority depends on upstream
  prompt coverage
- a strategy, reframe, Linear, ADR, or core artifact is about to rely on a
  sampled or partial upstream review

Do not load this reference for ordinary HE stage routing when no prompt-method
coverage claim is being made.

## Required Coverage Fields

Record these fields before routing downstream:

```yaml
source_prompt_status: preserved | summarized | missing | not_applicable
evidence_depth: full | representative | sampled | inferred | unknown
coverage_scope: repo_wide | stage_specific | slice_specific | partial | unknown
claim_scope: repo_wide | subsystem | slice | local_follow_up | unknown
coverage_gaps:
  - gap:
    impact:
    blocks_downstream_authority: yes | no
not_inspected:
  - evidence_class:
    impact:
authority_limited_to:
  - allowed_claim:
    forbidden_claim:
repo_specific_drift_signals:
  - signal:
    severity: blocker | high | medium | low
    indicator:
    corrective_action:
    blocks:
original_prompt_coverage: equivalent | partial | weak | unknown | not_applicable
downstream_confidence: high | medium | low | blocked
next_route: continue | refresh_strategy | refresh_review | restrict_scope | ask_once | blocked
```

## Authority Rules

- `equivalent` coverage requires preserved source prompt evidence, relevant HE
  stage references, and inspection depth that matches the original prompt's
  requested scope.
- `partial` or `weak` coverage may support local next steps, but it must not
  authorize repo-wide reframes, Linear closure, ADR creation, or core invariant
  updates without a refresh.
- Strategy, review, triage, and feature artifacts are cognition context; they do
  not grant implementation permission unless admitted through `he-spec`,
  `he-plan`, `he-reframe`, `he-linear-plan`, or an equivalent execution slice.
- If the user asks for equivalence to the original prompt method and coverage is
  not equivalent, route to the earliest stage that can repair the gap, usually
  `he-strategy` or a deeper review refresh.
- If downstream artifacts already exist, preserve their local validity while
  marking any repo-wide authority gap explicitly.
- Downstream `he-reframe`, `he-linear-plan`, ADR, and core artifacts must
  inherit upstream evidence depth, coverage gaps, not-inspected classes, and
  confidence downgrades when they rely on sampled upstream evidence.
- In headless mode, record assumptions instead of asking, and downgrade
  downstream confidence when source prompt status or evidence depth is unknown.

## Minimum Inspection

Before claiming equivalence:

- preserve or link the original prompt as source evidence
- load the relevant stage source-prompt preservation reference where one exists
- identify which source-prompt families are in scope: intent extraction,
  architecture review, triage, strategy compression, ADR compression, core
  invariant compression, reframe program generation, Linear orchestration, and
  eval/drift validation
- compare source prompt requirements with the actual artifact sections
- produce a compact coverage matrix that maps source-prompt requirements to HE
  artifact sections, evidence depth, gaps, and authority impact
- list not-inspected domains, files, commands, or evidence classes
- record whether the artifact is a first-pass execution slice, a subsystem
  review, or a full repo audit
- carry forward repo-specific protected surfaces, thresholds, and blocker
  signals discovered by the comparison
- separate facts, interpretations, and assumptions
- classify whether the gap blocks downstream routing

## Source Prompt Family Coverage

When the original method spans multiple prompts or phases, do not collapse the
comparison into "covered" or "not covered". Record coverage by family:

| Source prompt family | Required comparison question |
| --- | --- |
| Intent extraction | Did HE infer repository intent from implementation reality, not only docs or product language? |
| Architecture review | Did HE inspect enough source, config, tests, CI, runtime, docs, prompts, workflows, hooks, telemetry, governance, memory, integrations, TODOs, dead code, repeated abstractions, coupling, naming, and repo structure to support the claim scope? |
| Triage | Did HE compress findings into execution pressure without repeating the review or creating backlog noise? |
| Strategy | Did HE preserve what is core, what should be deleted, what creates leverage, what creates drag, and what future agents must preserve or may rewrite? |
| ADR compression | Did HE preserve only expensive-to-reverse, architecture-shaping decisions and rejected alternatives? |
| Core compression | Did HE create durable invariants instead of another review or onboarding document? |
| Reframe programs | Did HE generate only high-leverage migration plans with phases, rollback, eval proof, and anti-regression constraints? |
| Linear orchestration | Did HE route execution into the smallest useful active set without treating Linear as cognition storage? |
| Eval/drift validation | Did HE preserve proof requirements, closure blockers, drift signals, and downstream confidence before recommending completion? |

If a family is not inspected, mark it explicitly. Do not let strong evidence in
one family imply coverage in another.

## Authority Downgrade Examples

Use precise language when scope is narrower than the source prompt:

- `valid first-pass execution slice`: the HE run found a useful bounded next
  step, but did not perform the full source-prompt audit.
- `valid local reframe candidate`: the reframe is supported for the named
  subsystem, but not necessarily the highest repo-wide priority.
- `execution-disciplined Linear plan`: the Linear shape is safe for the selected
  slice, but uninspected prompt-method concerns remain open.
- `sampled cognition artifact`: the artifact can orient future work, but cannot
  authorize repo-wide ADR/core/reframe/closure claims without refresh.

## Drift Signal Inheritance

When the source documents identify concrete drift signals, preserve them as
operational checks instead of flattening them into generic "architecture risk".

Signals can include:

- protected hotspot growth in named files or subsystems
- central core/module bloat
- protocol/schema exception spread
- strategy or review artifact over-authority
- evidence-depth laundering
- roadmap or generated docs treated as current source state
- Linear issue or label taxonomy explosion
- snapshot-free UI behavior changes
- validation command drift
- skill, plugin, MCP, or runtime surface claims made without inspection
- deletion conclusions made without deletion scan depth
- prompt or skill growth without eval/proof gain
- hidden orchestration paths that bypass command surfaces or `.harness` routing

For each inherited signal, retain:

- indicator
- severity
- why it matters
- corrective action
- whether it blocks merge, release, Linear creation, closure, or broad
  architecture claims

## Output Discipline

The comparison artifact should be explicit about what remains safe:

- "valid local slice" is not the same as "complete repo-wide audit"
- "high confidence for selected reframe" is not the same as "highest repo
  priority"
- "Linear plan is execution-disciplined" is not the same as "other prompt-method
  concerns are closed"
- "no deletion candidate found" is not meaningful unless deletion scan depth is
  recorded

## Blocking Conditions

Block or ask once before advancing when:

- the source prompt is missing but the user requested equivalence
- evidence depth is sampled or inferred but downstream artifacts claim repo-wide
  authority
- reframe, Linear, ADR, or core output would be created from weak upstream
  evidence
- coverage gaps affect architecture, routing, execution safety, governance,
  moat-critical behavior, or Linear closure
- a downstream artifact drops blocker/high-severity drift signals from its
  upstream comparison evidence
- current-standards claims are requested but no current source evidence was
  gathered

## Non-Goals

- Do not copy full prompt text into `SKILL.md`.
- Do not require this contract for every normal HE run.
- Do not turn every coverage gap into a Linear issue.
- Do not reject useful sampled artifacts; downgrade their authority instead.
- Do not hard-code repo-specific drift signals as universal HE rules; preserve
  them as source evidence for the repo being evaluated.
