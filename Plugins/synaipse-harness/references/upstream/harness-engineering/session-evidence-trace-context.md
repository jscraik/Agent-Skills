# Session Evidence Trace Context

Read when: using `~/.agents/session-collector/`, archived Codex sessions, prior
run evidence, PR conversation evidence, or local memory to inform an HE stage.

## Purpose

Session evidence is only useful when future agents can trace where it came from,
which repo state it describes, and whether it matches the current slice.

## Pre-Resolve Before Use

Resolve as much of this context as possible before drawing conclusions:

- current working directory;
- repository name and absolute path;
- branch name and upstream, if available;
- PR number or URL, if available;
- Linear project, milestone, parent issue, and sub-issues, if available;
- selected `.harness` artifact chain;
- session evidence bundle path or source identifier;
- evidence time range;
- redaction or sensitivity status.
- Codex provenance status when the evidence comes from Codex sessions,
  transcripts, rollout files, OTEL traces, or hook/tool events;
- public he_trace_id when the evidence will feed a PR, handoff, eval, or
  reconcile report.

If a value cannot be resolved, record `unknown` with the inspection method and
whether the gap blocks the stage.

## Trust Rules

- Treat session evidence as historical evidence, not current repo truth.
- Prefer session-collector public provenance records before inspecting raw
  Codex rollout, transcript, OTEL, or hook payload files.
- Re-check live files, git state, Linear state, or PR state when the conclusion
  affects scope, validation, closure, or mutation.
- Do not mix evidence from different repos, branches, PRs, or Linear parents
  without a traceability warning.
- If session evidence conflicts with current artifacts, classify the conflict
  before writing or recommending work.
- Public HE artifacts may include hashes, presence flags, redaction status, and
  the HE trace ID. Keep raw thread IDs, turn IDs, transcript paths, rollout
  paths, trace bundles, prompts, responses, tool payloads, and telemetry
  contents in local-sensitive artifacts only.

## Output Fields

```yaml
session_evidence_status: used|none_found|blocked|not_applicable
session_evidence_source: "<path, collector id, memory file, or not_applicable>"
session_evidence_repo: "<repo name/path or unknown>"
session_evidence_branch: "<branch or unknown>"
session_evidence_pr: "<PR URL/number or unknown>"
session_evidence_linear: "<project/milestone/issue or unknown>"
session_evidence_time_range: "<range or unknown>"
session_evidence_currentness: current|historical|mixed|unknown
session_evidence_trace_blocker: yes|no
codex_provenance:
  status: found|not_found|blocked|not_applicable
  source: session_collector_public|session_collector_sensitive|manual|not_available
  he_trace_id: "<hetrace_* or not_available>"
  redaction_status: safe_summary|sensitive_local_only|blocked|unknown
  evidence_freshness: current|historical|mixed|unknown
  proves:
    - "<what this provenance supports>"
  does_not_prove:
    - "<what still needs live repo/tracker/validation evidence>"
```

## Anti-Patterns

- Using session excerpts without repo, branch, or artifact identity.
- Treating prior-run conclusions as live validation evidence.
- Letting collector path labels replace source artifact or Linear traceability.
- Pasting raw Codex local identifiers or transcript/rollout paths into PR text.
- Treating a telemetry trace ID as proof that tests passed or work is ready to
  merge.

## References

- Read for Codex-specific fields, redaction rules, and proof limits:
  codex-provenance-contract.md.
- Read for PR-facing trace shape and public/sensitive split:
  pr-safety-trace-contract.md.
