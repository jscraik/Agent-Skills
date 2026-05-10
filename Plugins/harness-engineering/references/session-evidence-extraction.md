# Session Evidence Extraction

Read when: `~/.agents/session-collector` evidence is used to improve HE
routing, skill context, refactor candidates, or `.harness` artifacts.

## Inventory Shape

Collector inventory should preserve enough context for another agent to
reproduce the evidence without reading the whole transcript:

```yaml
platform: codex|claude|cursor|unknown
file: "<source path or collector bundle path>"
size: 12345
ts: "YYYY-MM-DDTHH:MM:SSZ"
session: "<stable session id when present>"
cwd: "<working directory when present>"
branch: "<git branch when present>"
last_ts: "YYYY-MM-DDTHH:MM:SSZ"
match_count: 3
keyword_matches:
  - "he-plan"
  - "traceability"
_meta:
  parse_errors:
    - "<lossy parse note when present>"
```

Do not promote a row to workflow truth unless `cwd`, artifact path, branch, or
command evidence connects it to the current repo and slice.

## Extraction Modes

- `skeleton`: session id, repo, branch, timestamps, user asks, stage mentions,
  commands, artifact paths, validation outcomes, blocker labels, and completion
  signals.
- `errors`: command failures, exceptions, hook failures, permission/network
  blockers, validation failures, repeated exact error strings, and recovery
  attempts.
- `he-signals`: selected HE stages, folded-stage mentions, `.harness` paths,
  Linear identifiers, spec/plan/eval links, Project Brain references, and
  route-changing feedback.

Prefer the smallest mode that can answer the routing question. Use raw
transcript excerpts only when the normalized record cannot prove the claim.

## Promotion Rules

- Treat session evidence as supporting evidence, not tracker authority.
- Promote repeated failures only when at least two independent sessions share
  the same command family, artifact path family, or exact error signature.
- Keep broad labels such as `network`, `approval_required`, `permission`, and
  `timeout` as weak context until corroborated.
- Classify unknown `he-*` strings as `unmapped_signal` until
  `routing-map.json` admits them.
- Record `parse_errors` in the handoff when they affect confidence.

## Output Contract

When extraction affects a decision, include:

```yaml
session_evidence:
  source: "~/.agents/session-collector/<bundle-or-index>"
  mode: skeleton|errors|he-signals
  rows_examined: 0
  sessions_supporting: 0
  confidence: high|medium|low
  parse_errors_present: true|false
  decision_supported: "<route, repair, skillify, or no-op decision>"
  limits: "<what this evidence cannot prove>"
```
