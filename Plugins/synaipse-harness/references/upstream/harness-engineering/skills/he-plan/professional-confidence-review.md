# Professional Confidence Review

Read when the user asks to deepen a plan, run technical review, review with
professional engineering confidence standards, or uses a prompt shape such as
senior software engineering reviewer, systems architect, implementation-risk
analyst, specification maintainer, Codex harness engineer, Skill Factory
validation partner, media artifact operator, adversarial validation partner, or
`Plan Under Review: current`.

## Purpose

Turn a draft plan and its associated spec into the highest defensible
implementation-ready contract available from current evidence. Do not make the
plan sound safer than the proof supports.

## Triggered Mode

Use `mode: professional_confidence_review` and keep the plan/spec pair
untrusted until validated. This is a plan/spec assurance mode, not normal plan
drafting.

## Current-State Resolver

Before reviewing content, resolve concrete sources:

- current repo and branch
- dirty worktree status
- selected Linear issue, parent, milestone, or approved slice when tracked
- current plan path
- current associated spec path
- local Linear plan path under `.harness/linear/` when present
- prior review, eval, report, or media artifacts referenced by the plan
- validation evidence recency and whether artifacts still exist

Resolve `current` by this deterministic order and stop at the first complete,
unambiguous plan/spec pair:

1. explicit plan/spec path supplied in the user request
2. active heartbeat, phase, or automation target path
3. plan/spec path in current command, request metadata, or handoff artifact
4. current issue key from the request, branch name, or `.harness/linear/` queue
5. active/status frontmatter, stable plan ID, or selected execution-slice ID in
   `.harness/plan/**`
6. staged or git-touched `.harness/plan/**` and `.harness/specs/**` artifacts
   when they match the same issue key or stable slice identity
7. associated spec path declared in plan frontmatter, traceability, linked
   acceptance criteria, or `.harness/specs/**` issue-key match
8. local Linear plan path under `.harness/linear/` when it names the same repo
   and issue slice

If multiple candidates remain after this order, report all candidates and block
instead of choosing the newest file by date alone. If a plan is unambiguous but
the spec is not, review only when the user explicitly asked for plan-only
review; otherwise block the associated spec update with the missing spec paths
or source-of-truth decision.

If `current` cannot resolve to one unambiguous plan/spec pair, stop with
`blocked_reason: unclear_source_of_truth` and list the exact paths or decisions
needed. Do not invent current content from chat memory.

For tracked work, run or explicitly block the Linear Delta Capture Gate before
deepening the plan. Changed tracker state must be admitted, rejected, or queued
before the revised plan claims current scope.

## Required Output Sections

Use these sections for professional confidence review responses:

1. Initial Confidence Assessment
2. Plan Intent & Scope Check
3. Issues and Loopholes Found
4. Evidence Check
5. Recommended Fixes
6. Revised Plan
7. Associated Spec Update
8. Iterative Re-review Loop
9. Final Confidence Report
10. Before / After Impact Table
11. Infographic / `$imagegen` Artifact when requested or explicitly required by
    the workflow prompt

These headings are a contract. Do not rename them to generic alternatives such
as `Confidence Review`, `Findings`, `Technical Review`, or `Recommendation`
when the user asks for professional engineering confidence standards, technical
review, or plan deepening. If the review is blocked before content analysis,
return the blocked source-resolution status and the minimum missing inputs
instead of pretending the full review ran.

When writing a durable artifact, preserve stable plan IDs and acceptance IDs.
When returning in chat, keep the same structure but compress non-material rows.

## Confidence Model

Report initial and final confidence with a percentage, band, evidence basis,
remaining blockers, and evidence that would raise confidence. Apply the lowest
applicable ceiling:

| Condition | Maximum confidence |
| --- | ---: |
| goal unclear | 60% |
| associated spec missing when required | 68% |
| plan/spec contradiction unresolved | 70% |
| ownership unclear | 70% |
| validation gates missing | 75% |
| rollback missing | 80% |
| security-sensitive plan without security review | 82% |
| user-facing plan without accessibility review | 85% |
| production-facing plan without smoke/release validation | 88% |
| external dependency unverified | 90% |
| runtime behavior untested | 92% |
| current/tool-specific claims unverified | 90% |
| implementation not yet tested | 94% |
| formal or repeatable validation absent | 97% |

Use these confidence bands:

- 20-40%: early hypothesis
- 40-60%: plausible but weakly verified
- 60-75%: usable draft with material risk
- 75-90%: strong candidate with validation gaps
- 90-97%: production-ready only with strong evidence
- 98-99.9%: high assurance, repeatably verified
- 100%: deterministic or formally proven only

Never claim 100% unless the matter is deterministic, formally proven, or
empirically validated with repeatable evidence.

## Evidence Classification

Classify claims as:

- `verified`: directly supported by current local evidence
- `assumption`: plausible but not proven
- `inferred`: reasoned from context but not directly proven
- `unresolved`: needs more information
- `blocked`: cannot be checked in the current environment

Evidence must cite paths, issue IDs, command output, artifact paths, or a
specific blocker. Do not fabricate citations, tool behavior, API behavior,
security guarantees, benchmarks, or production readiness.

For non-trivial professional reviews, include a compact evidence pack in the
answer or durable artifact:

| Field | Required meaning |
| --- | --- |
| `source_path` | plan, spec, issue, command, report, or artifact path |
| `claim_id` | stable ID for the claim using the evidence |
| `classification` | verified, assumption, inferred, unresolved, or blocked |
| `freshness` | fresh, historical, stale, mixed, or unknown |
| `observed_at` | command time, artifact timestamp, or `unknown` |
| `redaction_status` | non_sensitive, redacted, sensitive_excluded, or unknown |
| `confidence_impact` | raises, lowers, caps, or neutral |
| `used_by_section` | review section or acceptance criterion relying on it |

If the evidence pack cannot be built from available artifacts, mark that as
evidence debt and cap confidence accordingly instead of implying every claim is
fully traced.

## Adversarial Review

Attack the plan like a hostile reviewer. For each material issue, record:

- failure mode
- blast radius
- likelihood
- impact
- confidence killer
- recommended mitigation
- whether the associated spec must change

Check at minimum: hidden assumptions, weak sequencing, unclear ownership,
validation gaps, rollback gaps, observability gaps, security and privacy risk,
accessibility risk, reliability risk, performance risk, migration risk,
deployment risk, user-experience risk, agent-execution risk, stale evidence,
spec drift, and places the plan can appear successful while failing in practice.

## Patch Requirements

Patch the operating model, not just wording. For every material issue, provide:

| Problem | Why it matters | Recommended fix | Expected improvement | Validation method | Spec update needed |
| --- | --- | --- | --- | --- | --- |

The revised plan must include goal, non-goals, assumptions, dependencies,
proposed approach, ownership, validation gates, observability, rollback, risks,
acceptance criteria, spec alignment, and open questions.

## Spec Coupling

If the revised plan changes scope, assumptions, requirements, architecture,
interfaces, data model, workflow, permissions, ownership, validation,
observability, rollback, risks, acceptance criteria, implementation sequence,
accessibility, security, performance, reliability, agent execution, or
documentation requirements, update the associated spec or produce a proposed
spec patch.

If no spec content or path is available, mark:

`Status: blocked`

Reason: no associated specification content or path was provided.

Needed: provide the spec content or path so the plan and spec can be reconciled.

If source-of-truth authority is unclear, mark the spec update blocked by unclear
source of truth instead of silently overwriting.

## Iterative Re-review Loop

After revising the plan and spec update, review both from scratch:

1. Compare plan and spec for contradictions, omissions, stale requirements, and
   mismatched acceptance criteria.
2. Classify each remaining weakness as `fixable now`, `requires user decision`,
   `requires external verification`, `requires implementation testing`,
   `requires production/runtime evidence`, or `requires spec owner decision`.
3. Patch every `fixable now` material issue.
4. Recalculate confidence.
5. Stop only when no material fixable issues remain or additional changes would
   be cosmetic or increase complexity without improving safety, validation,
   spec alignment, or execution quality.

Report the loop summary:

| Pass | Main issues found | Fixes applied | Spec changes applied | Confidence after pass | Stop/continue reason |
| --- | --- | --- | --- | --- | --- |

Explain confidence plateau when confidence no longer improves.

## Artifact Freshness

Before citing prior proof, verify referenced artifacts still exist. Missing
plans, specs, review reports, eval reports, generated media, or validation logs
must be classified as stale, historical, blocked, or mixed evidence. Do not
recreate missing artifacts during review unless explicitly authorized.

Run or explicitly block relevant artifact checks when durable files are written:

- `he_artifact_identity_lint.py`
- `he_linear_traceability_lint.py`
- unresolved-marker scan for draft-only labels, unfilled bracket prompts,
  unsupported absence claims, and other text that proves the artifact was not
  finalized

## Media Artifact Rule

If the workflow explicitly requires an infographic and image generation is
available, create the image through the active image-generation tool. If local
persistence is also required but the tool contract does not expose a writable
path, mark persistence blocked and provide the fallback prompt. Do not claim a
repository-local bitmap exists unless the file was written and verified.

Derive the prompt from actual plan/spec findings: plan name, spec name, original
state, target state, main weakness, main improvement, validation evidence, spec
update status, confidence movement, and loop outcome.
