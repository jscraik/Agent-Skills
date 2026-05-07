# XP Operating Contract

Harness Engineering favors simple, evidence-backed improvement loops. This
contract keeps staged work close to the failing behavior and prevents ceremony
from replacing working software.

## Simple Design

- Make the current behavior observable before changing it.
- For repo operations, use `./bin/ask` (stable wrapper to `Infrastructure/bin/ask`) as the default command surface.
- If an operation is unavailable via `./bin/ask`, explicitly note the exception and rationale.
- Prefer a narrow test or eval that would have caught the regression.
- Keep names and states consistent across native tools, skill output, and
  generated evidence.

## Red Signals

- A fix cannot name the exact failing command, comment, or artifact.
- A stage adds process without reducing future decision load.
- A handoff hides an unresolved blocker behind generic "follow-up" wording.
- A workflow asks agents to infer state that can be read from a command or file.

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
