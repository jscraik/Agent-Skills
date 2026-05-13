# XP Operating Contract

Harness Engineering favors simple, evidence-backed improvement loops. This
contract keeps staged work close to the failing behavior and prevents ceremony
from replacing working software.

## Simple Design

- Make the current behavior observable before changing it.
- For repo operations, use `./bin/ask` as the default command surface; it forwards to `Infrastructure/bin/ask`.
- If an operation is unavailable via `./bin/ask`, state the exception and rationale.
- Prefer a narrow test or eval that would have caught the regression.
- Keep names and states consistent across native tools, skill output, and
  generated evidence.

## XP Lens For HE

- Story/value first: every execution slice names the user/operator value, risk
  reduction, or feedback-loop improvement it creates. If the value cannot be
  named, classify the work as `Later` or `Do Not Create`.
- Baby steps: prefer the smallest reversible slice that can teach something
  before adding broader structure.
- Feedback loops: every stage names the evidence that will change the next
  decision, such as a command, eval, CI signal, review finding, or user choice.
- Quality is not a control variable: do not weaken validation, evidence, or
  review gates to make closure easier.
- Accepted responsibility: every handoff names the owner/stage, unresolved
  assumptions, and the smallest next recovery step.
- Reflection: repeated friction becomes one durable improvement surface after
  the immediate issue is fixed.
- Continuous testing and integration: implementation handoffs record exact test,
  eval, and integration/CI status, or the blocker that prevents them.
- Release confidence: changed lifecycle skills must pass a set-level release
  eval lane with their adjacent route/work skills before near-complete plugin
  confidence is claimed.
- Respect: review and closure language stays evidence-first, concrete, and
  blameless.

## Stage Duties

- `he-strategy`: compress direction into the smallest feedback-producing next
  slice; do not produce strategy that cannot change a decision.
- `he-refactor`: stage migrations as baby steps with rollback and stop/pivot
  conditions before implementation.
- `he-linear-plan`: sequence `Now` work by story/value, risk reduction, and
  feedback value, not technical neatness alone.
- `he-plan`: define closure proof before implementation begins.
- `he-work`: ship one approved slice, run the smallest relevant gates, and
  record integration status.
- `he-eval-report`: verify the promised proof exists; do not invent late proof
  or mark missing evidence as success.
- `he-phase-work`: preserve sustainable cadence with bounded slack and
  stop rather than ritualize wakeups when evidence is stale.

## Red Signals

- A fix cannot name the exact failing command, comment, or artifact.
- A stage adds process without reducing future decision load.
- A handoff hides an unresolved blocker behind generic "follow-up" wording.
- A workflow asks agents to infer state that can be read from a command or file.
- A Linear plan creates work that has no stated story/value basis.
- A strategy, refactor, or plan does not name the next feedback-producing slice.
- A heartbeat continues after stale evidence, unclear redaction, or failed gates.
- A plugin confidence claim treats static plugin-eval budget failures as
  resolved without rooted runtime proof, observed usage, or an explicit
  exclusion.

## Slack Policy

Use `slack_policy` to state intentional tolerance:

```yaml
slack_policy:
  status: none|bounded|blocked
  reason: "<why slack exists>"
  limit: "<time, token, scope, or risk boundary>"
  recovery: "<how to tighten it later>"
```

Bounded slack is acceptable for exploratory stages. It is not acceptable for
merge readiness, security findings, failing CI, or unresolved review threads.

## Learning Loop

When the same issue recurs, fix the active issue first, then update one durable
surface so the route improves next time. Good destinations are skill wording,
contract examples, eval fixtures, validation wrappers, and high-traffic docs.
