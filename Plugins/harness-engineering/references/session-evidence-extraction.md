# Session Evidence Extraction

Read when: `~/.agents/session-collector` evidence is used to improve HE
routing, skill context, refactor candidates, or `.harness` artifacts.

## Inventory Shape

Collector inventory should preserve enough context for another agent to
reproduce the evidence without reading the whole transcript. The session
collector is the extraction layer; HE is the interpretation layer. Prefer the
collector's normalized public output before raw transcript, rollout, OTEL, hook,
or tool payload files.

```yaml
platform: codex|claude|cursor|unknown
file: "<source path or collector bundle path>"
size: 12345
ts: "YYYY-MM-DDTHH:MM:SSZ"
session: "<stable public session fingerprint when present>"
codex_provenance:
  status: found|not_found|blocked|not_applicable
  source: session_collector_public|session_collector_sensitive|manual|not_available
  he_trace_id: "<hetrace_* or not_available>"
  redaction_status: safe_summary|sensitive_local_only|blocked|unknown
  session_id_status: hash_only|raw_local|not_available
  thread_id_status: hash_only|raw_local|not_available
  session_tree_id_status: hash_only|raw_local|not_available
  turn_id_status: hash_only|raw_local|not_available
  otel_trace_id_status: hash_only|raw_local|not_available
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
command evidence connects it to the current repo and slice. Public extraction
rows should use hashed identifiers or presence flags. Raw Codex IDs and local
paths belong only in sensitive local provenance output.

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

## Provenance Reading Order

1. Public session-collector output and its provenance_records.
2. Sensitive session-collector provenance output only when local inspection is
   needed and allowed.
3. Raw Codex rollout, transcript, OTEL, or hook payload files only when the
   collector evidence is missing or blocked.
4. Manual reconstruction only when collector and raw local sources are not
   available; mark confidence low unless corroborated.

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
  codex_provenance_status: found|not_found|blocked|not_applicable
  he_trace_id: "<hetrace_* or not_available>"
  redaction_status: safe_summary|sensitive_local_only|blocked|unknown
  parse_errors_present: true|false
  decision_supported: "<route, repair, skillify, or no-op decision>"
  limits: "<what this evidence cannot prove>"
```

Session evidence can prove correlation and freshness. It cannot prove current
repo truth, test success, PR readiness, or Linear closure without separate live
evidence.

## References

- Read for Codex provenance vocabulary and public/local redaction boundaries:
  codex-provenance-contract.md.
- Read for PR-facing safety trace requirements:
  pr-safety-trace-contract.md.
