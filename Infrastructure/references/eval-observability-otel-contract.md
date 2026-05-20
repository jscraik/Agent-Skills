# Eval Observability OTel Contract

Use this contract when adapting OpenTelemetry-style observability patterns into
Agent Skills Kit's own local eval package.

## Purpose

Make eval traces easier to inspect, compare, label, and turn into datasets
without confusing telemetry export health with skill correctness.

## Source Status

- External inspiration supplied in chat: Braintrust OpenTelemetry logging guide.
  Use it as a pattern source only, not as a product integration target.
- Local corroborating evidence: existing eval artifacts already capture
  codex_events.jsonl, stdout.txt, stderr.txt, result.json, summaries,
  and scorecards under Infrastructure/artifacts/skills/**.
- Local caution evidence: historical eval stderr includes an OpenTelemetry
  export error to http://127.0.0.1:4318/v1/logs, proving exporter failures can
  appear during eval runs and must be classified separately from skill behavior.
- Do not wire Braintrust credentials, packages, projects, endpoints, or export
  flows from this contract. If a future task explicitly asks for a Braintrust
  integration, treat that as a separate external-dependency design.

## Policy

OTel-inspired tracing belongs in evals as a repo-owned observability lane, not
as the default pass/fail source of truth and not as a dependency on Braintrust.

Use it to:

- record eval run, case, model, attempt, tool-call, and scorer spans in the
  local eval package;
- correlate local codex_events.jsonl with local trace summaries;
- build datasets from real failed or interesting eval traces;
- debug multi-step agent behavior, tool calls, retries, and latency;
- support later human labeling and custom scorer work.

Do not use it to:

- replace local deterministic checks;
- replace codex exec --json traces;
- replace strict audit, Plugin Eval, Tessl, Snyk, or discovery-smoke lanes;
- require Braintrust credentials for any skill eval;
- mark a skill failed only because telemetry export failed;
- upload secrets, private URLs, raw credentials, or sensitive repo data.

## Lane Semantics

| Lane | Required by default | Failure classification | Release effect |
| --- | --- | --- | --- |
| local eval artifacts | yes | skill/eval failure or blocker | can block |
| codex exec --json trace | release live-runner cases | live-runner failure or blocker | can block |
| OTel local collector export | no | blocked_eval_observability or warning | advisory unless explicitly required |
| Braintrust export | no | not supported by this local package contract | out of scope |
| dataset/scorer creation from traces | no | blocked_labeling_or_dataset | advisory until required by a named eval program |

## Minimum Span Model

When implemented, use stable names and redacted attributes:

- eval run span: skill, run id, runner, mode, branch/SHA, artifact root;
- eval case span: case id, category, expected trigger, mode, attempt;
- model call span: model id, sandbox/profile, status, token usage when
  available, final-output schema status;
- tool/command span: command family, result status, duration, redacted error
  class, artifact path;
- scorer span: check id, check type, pass/fail/blocked, evidence path;
- export span: exporter target, status, retry count, blocker class.

Do not attach raw prompts, completions, stdout, stderr, secrets, private URLs,
or full file contents by default. Store raw evidence locally and attach only
repo-relative artifact paths or redacted summaries unless an explicit privacy
review allows richer export.

## Environment Contract

OTel-compatible local export must be opt-in through explicit configuration such
as environment variables or CLI flags. Missing collector, no network, or
exporter timeout should produce a classified observability blocker or warning,
not a skill failure. Missing Braintrust credentials must not be reported as a
blocker because Braintrust is not part of this package contract.

Recommended first-class status values:

- not_configured
- exported
- blocked_missing_collector
- blocked_network
- blocked_export_error
- redacted

## Implementation Sequence

1. Preserve current local artifact generation as the canonical evidence source.
2. Add an eval observability summary object to local result/scorecard artifacts.
3. Add repo-owned OTel-style span emission behind an explicit opt-in flag or
   environment toggle.
4. Add redaction tests before allowing any non-local export target.
5. Keep Braintrust integration out of scope unless Jamie explicitly starts a
   separate external integration lane.
6. Add dataset/scorer workflows only after real failed traces exist and a human
   labeling loop is defined.

## Acceptance Criteria

- Local evals still run without Braintrust, OTel collector, network, or external
  credentials.
- Exporter failure is reported separately from skill failure.
- Result artifacts include enough local paths to reconstruct what would have
  been exported.
- Redaction tests cover raw prompt/output, environment variables, tokens,
  private URLs, and full stderr/stdout capture.
- Release-readiness reports can show observability as not_configured, exported,
  or blocked without changing deterministic gate outcomes.

## Validation

Use focused tests before any live export:

- unit test result schema includes observability status without requiring export;
- unit test exporter failure maps to observability blocker, not eval failure;
- unit test redaction removes secrets and private data from span attributes;
- smoke test with export disabled proves default local eval behavior is
  unchanged.

## Open Questions

- Should Cloud evals and local codex exec evals use the same trace id format?
- Which traces are safe to export externally versus local-only?
- Should dataset creation be manual, scheduled, or tied to release eval
  failures only?
