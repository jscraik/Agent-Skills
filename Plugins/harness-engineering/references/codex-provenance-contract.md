# Codex Provenance Contract

Read when: HE artifacts, reviews, eval reports, reconcile reports, phase loops,
or PR handoffs cite Codex session evidence, session-collector output, rollout
records, transcript paths, OpenTelemetry traces, tool-call evidence, or prior
run provenance.

## Purpose

Codex provenance connects HE work to the execution evidence that produced or
reviewed it without leaking local runtime data. The session collector owns raw
extraction and privacy normalization. Harness Engineering owns interpretation:
what the provenance supports, what it does not support, whether the evidence is
fresh enough for the current decision, and what safe summary may appear in a PR
or public artifact.

## Source Order

Use the safest normalized source that can answer the question:

1. Public session-collector output, including provenance_records.
2. Sensitive session-collector provenance output only for local inspection when
   allowed.
3. Raw Codex rollout, transcript, OTEL, or hook payload files only when the
   collector evidence is missing, blocked, or explicitly insufficient.
4. Manual provenance only when no collector source is available; mark the
   limits plainly.

Do not make HE skills independently scrape raw Codex runtime files when a
collector artifact can provide the same answer.

## Public Trace Rule

Public PRs and public HE artifacts get a safe HE Trace ID (he_trace_id) plus hashed or
presence-only provenance identifiers. Local sensitive artifacts may keep the
raw mapping only when marked sensitive_local_only.

Recommended public identifier:

    hetrace_<YYYYMMDD>_<issue-or-repo>_<short-random-or-hash>

The he_trace_id is a Harness Engineering correlation ID. It is not a Codex
session ID, thread ID, turn ID, transcript path, rollout path, or OTEL trace ID.
The public Provenance Source should name session_collector_public,
session_collector_sensitive, manual, not_available, or the blocked source class.

## Output Shape

When provenance affects a decision, include this shape or an equivalent
Artifact Identity-compatible field set:

    codex_provenance:
      status: found|not_found|blocked|not_applicable
      source: session_collector_public|session_collector_sensitive|manual|not_available
      he_trace_id: "<hetrace_* or not_available>"
      collector_output: "<path-or-unknown>"
      sensitive_output: "<path-or-not_used>"
      redaction_status: safe_summary|sensitive_local_only|blocked|unknown
      session_id_status: hash_only|raw_local|not_available
      thread_id_status: hash_only|raw_local|not_available
      session_tree_id_status: hash_only|raw_local|not_available
      turn_id_status: hash_only|raw_local|not_available
      otel_trace_id_status: hash_only|raw_local|not_available
      rollout_path_status: present_hash_only|raw_local|not_available
      transcript_path_status: present_hash_only|raw_local|not_available
      evidence_freshness: current|historical|mixed|unknown
      proves:
        - "<what this provenance supports>"
      does_not_prove:
        - "<what still needs live repo/tracker/validation evidence>"

Use not_applicable when the artifact has no dependency on prior Codex
execution evidence. Use not_found when the collector was checked and did not
provide usable provenance. Use blocked when the collector or sensitive output
cannot be inspected safely.

## PR-Safe Fields

These may appear in PR bodies and public summaries:

- he_trace_id;
- collector output filename or artifact label, when it does not expose private
  local paths;
- provenance status and source;
- redaction status;
- hash-only session, thread, turn, and OTEL trace fingerprints;
- counts such as 3 hashed turn ids;
- presence flags such as transcript evidence present locally;
- explicit proves and does_not_prove statements.
- PR-facing evidence locations only when they are public URLs, repo-relative
  artifact paths, artifact IDs, or hash-only tokens.

## Local-Only Fields

These must not appear in public PR bodies, public GitHub comments, or public HE
artifacts by default:

- raw Codex session IDs, thread IDs, session tree IDs, turn IDs, and tool-call
  IDs;
- raw OTEL trace IDs when they can correlate across private telemetry systems;
- raw transcript paths, rollout paths, rollout trace bundle paths, and local
  sensitive provenance paths;
- prompts, responses, tool inputs, tool outputs, terminal output copied from
  traces, and telemetry payload contents;
- local usernames, machine-specific absolute paths, or secrets unless already
  part of a deliberate local-sensitive artifact.

If raw values are needed, write or reference a local artifact marked
redaction_status: sensitive_local_only and keep it out of PR text.

## What Provenance Proves

Codex provenance can support:

- a Codex execution, review, or validation session was correlated with the work;
- the collector saw session/thread/turn/trace evidence for the work;
- local sensitive evidence exists for Jamie to inspect;
- evidence is current, historical, mixed, or unknown relative to the slice;
- an artifact, PR, or Linear issue has a traceable execution context.

## What Provenance Does Not Prove

Codex provenance does not prove by itself:

- tests passed;
- the current repo diff matches the cited run;
- the implementation is correct;
- Linear was updated;
- PR review threads are resolved;
- CI is green;
- the PR is ready to merge;
- raw transcript contents are safe to publish.

Always keep validation, repo state, tracker state, PR state, and review findings
as separate proof surfaces.

## Confidence Rules

- Cap confidence when provenance is missing, stale, manually reconstructed, or
  sourced from raw fallback rather than collector output.
- Treat safe_summary as publishable but incomplete: it proves correlation, not
  correctness.
- Treat sensitive_local_only as inspectable by Jamie, not sharable by default.
- If provenance conflicts with live repo, PR, Linear, or validation evidence,
  classify the conflict before continuing.

## Anti-Patterns

- Pasting raw local transcript or rollout paths into PRs.
- Calling an he_trace_id a Codex session ID.
- Treating OTEL trace IDs as proof of test success.
- Treating collector hashes as enough evidence to close Linear.
- Letting every HE skill invent its own raw Codex parser.
- Hiding missing provenance instead of recording not_found or blocked.
