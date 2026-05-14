# Architecture Evolution Compression

Use when a user asks `he-reframe` to preserve or execute the broader prompt
family around strategic compression, reframe programs, ADR compression, and core
invariants.

`he-reframe` owns deterministic reframe programs under `.harness/reframes/`.
It may generate ADR or core-invariant candidates only when they are directly
required to make a selected reframe program safe, durable, or anti-drift. It
must not create strategy, ADR, or core artifacts as process theater, and it
must never author `.harness/strategy/**`; formal strategy artifacts belong to
`he-strategy`.

## Lane Routing

| Lane | Owner behavior | Output |
| --- | --- | --- |
| Strategic compression | Treat as upstream input or route to `he-strategy` when no strategy artifact exists. Do not repeat reviews or author strategy files from this skill. | `.harness/strategy/<repo-name>-strategy.md` via `he-strategy`, or `Blocked: strategy missing`. |
| Reframe program generation | Primary `he-reframe` lane. Generate only high-leverage, staged, rollback-safe migration programs. | `.harness/reframes/YYYY-MM-DD-JSC-###-<slug>.md` or repo-name equivalent. |
| ADR compression | Create only high-value architectural memory when a reframe would otherwise lose irreversible tradeoff reasoning. | `.harness/decisions/ADR-###-<slug>.md`, or `Do Not Create`. |
| Core invariant compression | Create or update only irreducible operating rules that future agents must preserve across migrations. | `.harness/core/<invariant-domain>.md`, or `Do Not Create`. |

## Strategic Compression Intake

When reading `.harness/features`, `.harness/review`, `.harness/triage`, and
`.harness/strategy`, compress rather than repeat. Extract:

- strategic truths
- irreducible core
- actual moat and false moat signals
- complexity without leverage
- architectural non-negotiables
- safe rewrite zones
- contradictions and drift risks
- core investment priorities
- future-agent preservation rules

If a strategy artifact is missing and the request depends on it, return
`next_handoff: he-strategy` or `Blocked: strategy missing`; do not author a
repo-wide strategy inside `he-reframe`.

If the user explicitly asks for a combined workflow, `he-reframe` may produce a
transient Strategic Compression Intake summary to select or block reframe work,
but formal `.harness/strategy/**` creation still routes to `he-strategy`.

When a strategy artifact exists, use its deletion candidates, architectural
non-negotiables, safe rewrite zones, moat-critical systems, contradictions, and
core investment priorities only to select, reject, or scope reframe candidates;
do not re-expand them into another strategy review.

## Reframe Program Gate

Create a reframe program only when completion meaningfully improves one or more
of: structural complexity, orchestration determinism, routing clarity, context
load, cognition quality, governance simplicity, eval reliability, moat-critical
stability, plugin/skill boundaries, or Linear execution hygiene.

Reject as `Do Not Create` when the candidate is cosmetic, tactical, speculative,
a generic cleanup, a routine dependency update, a vague modernization plan, a
clean-slate rewrite, or better handled by one small Linear issue.

## ADR Gate

Create an ADR only when future agents could plausibly reverse a costly decision
because the reason is not compressed elsewhere. ADRs must be short and include:
Decision, Context, Why This Decision Exists, Alternatives Considered, Accepted
Tradeoffs, Anti-Drift Constraints, Safe Revisit Conditions, Related Systems,
Evidence.

ADR creation requires all of:

- named irreversible or expensive-to-reverse decision;
- explicit reversal cost if the decision is undocumented;
- failed `Do Not Create` subtraction test;
- linkage to a selected reframe phase.

Do not create ADRs for implementation details, temporary experiments, low-impact
reframes, cosmetics, or framework preferences without strategic impact.

## ADR Record Contract

Use `.harness/decisions/ADR-###-<slug>.md` for accepted ADR candidates. Keep
records compressed and include only these sections unless repo-local ADR
standards require more: `ADR-###`, Title, Status, Decision, Context, Why This
Decision Exists, Alternatives Considered, Accepted Tradeoffs, Anti-Drift
Constraints, Safe Revisit Conditions, Related Systems, Evidence.

Status must be one of: `proposed`, `accepted`, `deprecated`, or
`superseded`. Evidence must separate facts, interpretation, and assumptions.
When ADR compression reads migration artifacts, treat existing
`.harness/refactors/**` files as legacy source evidence and current
`.harness/reframes/**` files as preferred migration evidence; do not create or
revive legacy refactor roots from the ADR lane.

## Core Invariant Gate

Create core invariant files only for durable, cross-run operating truths. Keep
files small and stable. Prefer these domains only when evidence justifies them:
architecture, routing, execution, governance, cognition, moat, anti-drift, and
future-agent operating rules.

Each invariant must be classified as one of: `proven invariant`, `strategic
assumption`, or `preferred operating principle`. Exclude tactical details,
transient frameworks, speculative roadmap ideas, and review repetition.

Core invariant creation requires all of:

- named invariant domain;
- classification as `proven invariant`, `strategic assumption`, or `preferred operating principle`;
- explanation of the drift or reversal risk if omitted;
- linkage to a selected reframe phase or anti-drift closure proof.

## Core Invariant Record Contract

Use `.harness/core/<invariant-domain>.md` for accepted core candidates. Allowed
default domains are architecture, routing, execution, governance, cognition,
moat, anti-drift, and future-agent operating rules; add repo-local domains only
when evidence proves the split reduces context load or drift risk.

Keep each core file compressed and include: Purpose, Scope, Invariant
Classification, Core Invariants, Forbidden Drift, Operational Justification,
Evidence, Safe Revisit Conditions, and Future-Agent Rules. Evidence must map
each invariant to repository behavior or prior `.harness` findings and must
separate proven invariants, strategic assumptions, and preferred operating
principles.

Do not create every example core file by default. Merge adjacent low-volume
domains when separation would add retrieval cost, governance surface, or
maintenance burden without reducing drift risk.

## Downstream Handoff Criteria

Do not hand off to planning or execution until these fields exist:

- selected migration candidate;
- phase-1 reversible step;
- rollback condition;
- validation command list;
- eval artifact pattern;
- Linear mapping without mutation.

## Required Evidence Shape

For every major conclusion or generated artifact, record:

- Fact: source artifact, repo evidence, validation output, or runtime evidence
- Interpretation: what the evidence means for architecture evolution
- Assumption: unresolved or sampled reasoning
- Confidence: high, medium, low, or blocked
- Operational impact: why this matters for migration, drift, moat, or future agents

## Linear and Eval Discipline

Do not create Linear objects. Map future execution only:

- Workspace/team: Jscraik
- Team key: JSC
- Top-level initiative: Dev Portfolio
- Cross-repo project: Portfolio Ops
- Repo-specific work: matching repo project when known

## Linear Execution Handoff Contract

`he-reframe` may define Linear mapping inside selected reframe programs, but it
must not author `.harness/linear/**` execution orchestration plans or create
Linear objects. Formal Linear execution planning routes to `he-linear-plan`.

When handing off to `he-linear-plan`, include: selected migration candidate,
source artifacts read, current `.harness/reframes/**` inputs, legacy
`.harness/refactors/**` inputs when present, phase ordering, validation and eval
gates, rollback conditions, agent-safe or human-review classification,
dependency notes, and Linear mapping without mutation.

Preserve the JSC operating model: use `Dev Portfolio` as the top-level
initiative, `Portfolio Ops` for cross-repo coordination, and the matching repo
project for repo-specific work. Do not propose new initiatives, projects,
labels, milestones, parent issues, or sub-issues from `he-reframe`; leave those
decisions to `he-linear-plan` and human confirmation.

Every reframe program must define an eval artifact before closure:

`.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<slug>-eval.md`

No milestone, parent issue, or migration slice should be considered complete
without eval proof or a documented exception.
