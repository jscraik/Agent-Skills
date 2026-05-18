# High-Signal Steering Feedback

## Purpose

Jamie steering is operating evidence. Treat every steering item as a
high-signal candidate until classified otherwise. It may prove that the current
agent loop, repo guidance, or validation surface failed to preserve an important
rule. Do not answer the immediate comment and move on when the feedback implies
a durable behavior change.

This document exists so future agents do not require the same correction twice.
It is not sufficient on its own. High-signal steering also needs a ledger record
in `.harness/quality/steering-uptake.md` and a passing
`validate_steering_uptake.py` check when the feedback changes future behavior.

## OODA Horizon

Do not orient only on the current turn when the user is correcting agent
behavior. A single-turn horizon is too small for repo operations, skill work,
review loops, and harness strategy.

Use two context axes before deciding scope:

- Horizontal OODA Context: adjacent organizational activity, active workstreams,
  related repo conventions, recent review findings, and known operating
  policies that may change what action is appropriate.
- Vertical OODA Context: stacked trajectories such as prior user steering,
  current branch intent, generated projections, validation gates, review
  artifacts, memory surfaces, and future-agent inheritance.

The action radius should be narrow enough to avoid drift and broad enough to
preserve the rule across the trajectory where it matters.

## Cross-Boundary Recall

Horizontal orientation requires recall beyond the active transcript. When the
needed context may live across compaction, harness, or environment boundaries,
use targeted context-window resume rather than relying on the current turn.

The expected pattern is:

1. Identify the missing context boundary: compaction, harness, environment,
   repository, worktree, review loop, or external tracker.
2. Resume or query the smallest target context window that can reflect on that
   boundary. The target may be a prior Codex context, harness artifact,
   automation run, review loop, tracker item, memory surface, or active child
   agent.
3. Ask for reflection on the specific operating question, not a broad summary:
   what is still active, what changed, which blockers remain, which gates were
   proven, and what would be unsafe to assume from the current turn alone.
4. Convert the returned context into a decision about feedback type, intent
   radius, durable surface, or validation scope.
5. Preserve the conclusion in the current artifact and the steering uptake
   ledger when it changes future behavior.

This is the bridge between ordinary memory and the cross-boundary tooling this
repo is designed to support.

Cross-boundary OODA is not optional ceremony. Horizontal OODA asks what adjacent
organizational activity changes the decision. Vertical OODA asks which stacked
trajectories the action must survive: prior steering, current plan, spec,
review, validation, tracker, projection, memory, future compaction, and future
agent inheritance. If either axis depends on context outside the current turn,
the agent must use the smallest available target context window and ask it to
reflect before claiming orientation.

## Trigger

Apply this protocol by default when Jamie gives steering or review feedback.
Classify the feedback first; only downgrade it to non-durable when the reason is
explicit and recorded in the current work artifact.

The following phrases are mandatory triggers rather than the full trigger set:

- a behavior is being repeated after prior correction;
- the agent is applying feedback too narrowly;
- a review comment points to a design rule, not only one line;
- the repo, docs, skill, or harness should remember the preference;
- agent behavior is failing operationally, not just producing a bad answer;
- the substance is "this is high signal" or "never make me say this again."

## Required Response Shape

Before proceeding with more ordinary implementation, perform these steps:

1. Name the operating failure in one sentence.
2. Classify the feedback type.
3. Choose an intent radius.
4. Check horizontal and vertical OODA context.
5. Identify the durable surface that should carry the rule.
6. Make the smallest safe meta-change to that surface.
7. State the environment refinement: the repo, doc, validator, test, ledger,
   skill, or workflow mechanism that now makes the repeated failure harder to
   reproduce.
8. Create or update `.harness/quality/steering-uptake.md`.
9. Validate the changed surface and run the steering uptake validator.
10. Report the new rule and how it prevents repeat feedback.

If no durable surface is appropriate, say why and record the feedback as a
deliberate non-persistent decision in the work artifact.

Do not wait for phrases such as "high signal" or "never again" before doing
this classification. Those phrases only raise confidence that the feedback is
durable; they are not the entry condition.

## Larger Perspective Rule

Principle-shaped feedback is not a request to patch only the named example. The
agent must first ask what class of failure the feedback reveals.

Use this loop:

Correction -> Pattern -> Sweep -> Classification -> Enforcement

The named function, file, command, review line, failing test, or doc paragraph is
often the pointer, not the whole problem. If the feedback can be restated without
the local proper noun or path and still makes sense as a design, workflow, API,
validation, safety, or documentation rule, treat it as transferable until the
repo evidence proves otherwise.

Required behavior:

1. State the class of failure in repo language.
2. Search sibling instances or equivalent cases in the nearest relevant surface.
3. Classify each match as fixed now, different semantics, deferred with reason,
   or not applicable.
4. Add or update the enforcement surface: tests, validators, docs, skill
   contracts, evals, or review checklists.
5. Report the sweep and enforcement before claiming the feedback was handled.

Do not let one successful local edit masquerade as system learning. A line-local
fix is acceptable only after the pattern sweep proves that the feedback is local.

## Steering Override Halt

When Jamie says the agent is failing to operate effectively, repeating prior
feedback, or making him give the same feedback twice, treat the message as a
lane-changing stop signal. Do not keep trying to finish the previous
implementation, heartbeat, review, or closeout lane while preparing a better
explanation.

The required behavior is:

- stop the active lane and update the plan to make meta-work the only
  in-progress item;
- close or cancel stale child agents when their results would no longer answer
  the newest steering;
- classify the blocker in systems-thinking terms: who is blocked, why the
  environment allowed it, and what durable mechanism would prevent the repeat;
- make the smallest durable environment refinement in instructions, docs,
  validator, tests, skill contract, or workflow surface;
- validate the changed surface and the steering uptake ledger;
- report the mechanism and proof before resuming ordinary work.

Acknowledgement alone is not uptake. A prettier final answer is not uptake. The
environment has to change, or the agent must stop and report why no durable
change can be made.

## Feedback Types

Use these categories:

| Type | Meaning | Required action |
| --- | --- | --- |
| `local_bug` | The feedback applies only to the named line, function, or file. | Fix locally and explain why no wider sweep is needed. |
| `repeated_pattern` | The named issue may exist in similar code. | Run a bounded pattern search and classify matches. |
| `api_design_rule` | The feedback expresses an interface philosophy. | Extract the generalized API rule, search the same API layer for equivalent misuse, and update tests or docs for the rule. |
| `architecture_boundary` | The feedback protects ownership or layering. | Update the relevant boundary doc or validation gate. |
| `naming_language` | The feedback clarifies project vocabulary. | Update `UBIQUITOUS_LANGUAGE.md` or the closest owning glossary. |
| `validation_gap` | The feedback shows an untested failure mode. | Add or plan a check, fixture, or explicit blocker classification. |
| `test_contract_gap` | The feedback shows tests are proving the wrong thing. | Adjust tests or test guidance to prove the user-visible contract. |
| `documentation_drift` | The feedback shows docs and behavior diverged. | Refresh the canonical doc and cite current evidence. |
| `agent_operating_rule` | The feedback changes how agents should behave. | Update `AGENTS.md` or `Docs/agents/**`, update the steering ledger, and ensure the validator treats it as transferable feedback. |
| `product_contract_rule` | The feedback changes what the repo must make possible for users or agents. | Update the owning product, workflow, validation, or SDK surface so the capability is not left as advice. |

## Intent Radius

Choose the narrowest radius that preserves the principle:

| Radius | Use when |
| --- | --- |
| `line` | The issue is truly local and has no design implication. |
| `function` | The function contract is wrong but callers or siblings are not implicated. |
| `file` | The pattern is local to one module. |
| `package` | The feedback describes an API or workflow rule for one layer. |
| `repository` | The rule should affect all equivalent cases in the repo. |
| `architecture_rule` | The rule protects ownership, layering, or lifecycle invariants. |
| `durable_memory` | The rule must survive future sessions or generated artifacts. |

Default away from `line` when the feedback contains principle language such as
"should", "instead of", "pattern", "generally", "same issue", "class of",
"not just here", or "this is how I think about". The named line, function,
file, command, doc section, or review comment may be only the example Jamie used
to point at a wider operating rule.

Transferable feedback cannot use `line` or `function` radius. Even when the
local example names one function, command, doc paragraph, test, PR comment, or
error, the minimum useful radius is the nearest surface that can contain
equivalent misuse.

## Pattern Sweep Contract

When the radius is broader than `line`, run a bounded sweep before editing
similar cases. Report each match as:

- `fixed_now`
- `left_different_semantics`
- `deferred_public_api`
- `deferred_risk`
- `not_applicable`

Include the search terms or command used, the scope searched, and exclusions.
For broad or transferable feedback, the steering ledger must make this explicit
with:

- `Sweep scope:`
- `Search terms:`
- `Matches considered:`
- `Exclusions:`

For transferable feedback, the ledger must also state:

- `Generalized rule:`
- `Similar-case disposition:`

Transferable feedback must not be scoped to only `line` or `function`;
choose at least the nearest file, package, workflow, policy, repository, or
architecture boundary and classify equivalent cases unless a source sweep is
explicitly deferred with reason.

Do not turn every principle into a repo-wide rewrite. Fix only matches that are
clearly inside the chosen radius and safe for the current task.

The generalized rule is the principle Jamie is communicating, stated without
the incidental local example. The similar-case disposition is a compact
classification of equivalent cases found in the chosen radius: fixed now,
different semantics, deferred with reason, or not applicable. A grep command
alone is not enough when the pattern is semantic; use repo structure, callers,
tests, docs, workflows, validators, type signatures, or AST-aware inspection
when needed.

## Durable Surface Selection

Pick the closest authoritative surface:

| Feedback target | Durable surface |
| --- | --- |
| Agent behavior | `AGENTS.md` plus `Docs/agents/**` |
| Project vocabulary | `UBIQUITOUS_LANGUAGE.md` |
| Skill behavior | Canonical `Skills/**` or `Plugins/**/skills/**`, not runtime projections |
| Harness Engineering workflow | `Plugins/harness-engineering/**` or `.harness/**` |
| Validation behavior | `Infrastructure/scripts/**`, tests, and `Docs/agents/04-validation.md` |
| Architecture boundary | `Docs/agents/14-path-ownership-boundaries.md` or the relevant architecture doc |
| Review handling | `Docs/agents/13-workflow-and-safety-guidance.md` and this document |

If the correct durable surface is ignored or generated, record the rule in the
nearest canonical source and note the projection or ignore constraint.

## Steering Uptake Ledger

The ledger is the executable memory surface for this protocol. Each high-signal
steering event that changes future behavior must add or refresh one uptake
record with:

- `Operating failure:`
- `Feedback type:`
- `Intent radius:`
- `Blocker:`
- `Horizontal OODA:`
- `Vertical OODA:`
- `Durable surface:`
- `Pattern sweep:`
- `Generalized rule:` for transferable feedback
- `Similar-case disposition:` for transferable feedback
- `Disposition:`
- `Environment refinement:`
- `Mechanism:`
- `Proof:`
- `Validation:`
- `Repeat prevention:`

For any broad-radius or transferable feedback, especially `api_design_rule`,
the ledger record must state the searched scope and classify matches. This is
the mechanism that prevents a line-local correction from masquerading as
principle uptake.

For every record, the agent must also explain the blocker, environment
refinement, mechanism, and proof. A record that cannot name what changed in the
operating environment is still advice, not uptake.

When the feedback mentions diagnostics, warnings, blocker counts, or residual
risk, the record must also include:

- `Diagnostic classification:`

That line must name the dominant category, the owner or decision boundary, and
the next action. Do not flatten large diagnostic counts into "nonblocking debt"
without proving what kind of debt it is and who or what can resolve it.

When the feedback mentions repeated errors, retry loops, or "do not fight
errors," the record must also include:

- `Repeated error protocol:`

That line must state that the same error twice triggers research, 3-5 possible
fixes, choosing the most efficient safe option, and implementing it. If web
research is unavailable, record the network blocker and use repo-local docs or
cached official docs.

When the feedback mentions cross-boundary context, target context windows,
stacked trajectories, or OODA beyond the current turn, the record must also
include:

- `OODA scaling protocol:`

That line must name horizontal OODA, vertical OODA, compaction, harness,
environment boundaries, target context window reflection, and how the result is
recorded before action. A current-turn summary is not enough evidence.

Run:

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
```

The validator does not prove the reasoning is brilliant. It proves the agent did
not stop at another prose-only guardrail rewrite.

## Example: API Design Review Comment

Input feedback:

```text
Instead of returning success/failure as a bool, return an error with a named
sentinel error in function XYZ.
```

Classification:

```yaml
feedback_type: api_design_rule
intent_radius: package
local_instance: function XYZ
inferred_rule: meaningful operational failures in this API layer should be named errors, not bools
required_sweep:
  - exported functions in the same API layer returning bool for failure
  - callers branching on false without error detail
exclusions:
  - pure predicate helpers
  - cache-hit or existence checks where bool is the semantic value
  - public APIs requiring a migration plan
required_output:
  - local fix
  - similar cases table
  - tests for named error behavior
  - deferred cases with reason
  - durable guidance update or explicit non-persistence reason
```

## Stop Rule

Do not continue ordinary implementation after high-signal steering until the
feedback has either:

- been converted into a durable rule and validated; or
- been explicitly classified as not durable with the reason recorded.

If the durable update is blocked by permissions, generated surfaces, ignored
paths, or unclear ownership, stop and report the blocker instead of proceeding.
