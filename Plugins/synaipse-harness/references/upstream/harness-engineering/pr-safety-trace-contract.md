# PR Safety Trace Contract

Read when: preparing, reviewing, or reconciling an HE-authored pull request,
handoff, GitHub comment, or PR-ready artifact that cites .harness evidence,
Linear state, validation output, session evidence, or Codex provenance.

## Purpose

A PR safety trace gives reviewers a safe audit trail for the work without
publishing raw local telemetry. It should let a reviewer see which Linear issue,
spec, plan, validation, review, eval, reconcile report, and Codex provenance
support the PR. It should also say what the trace does not prove so provenance
does not become false confidence.

## Required Public Block

Every HE-authored PR should include a compact public block shaped like this
when the repository PR template has room for it:

    ## Harness Engineering Trace

    | Field | Value |
    |---|---|
    | HE Trace ID | hetrace_YYYYMMDD_target_hash |
    | Linear Issue | JSC-123 or not_applicable |
    | Spec Artifact | .harness/specs/... or not_applicable |
    | Plan Artifact | .harness/plan/... or not_applicable |
    | Review Artifact | .harness/review/... or not_applicable |
    | Eval Artifact | .harness/evals/... or not_applicable |
    | Reconcile Artifact | .harness/reconcile/... or not_applicable |
    | Validation Evidence | listed in Testing section |
    | Provenance Source | session_collector_public |
    | Provenance Status | found |
    | Codex Session | hash:<short-hash> or not_available |
    | Codex Thread | hash:<short-hash> or not_available |
    | Codex Turns | <n> hashed turn ids or not_available |
    | OTEL Trace | hash:<short-hash> or not_available |
    | Redaction Status | safe_summary |
    | Sensitive Evidence | local-only, not included in PR |

    ### Safety Notes

    - Raw Codex session IDs, thread IDs, turn IDs, transcript paths, rollout
      paths, trace bundle paths, prompts, responses, tool payloads, and
      telemetry contents are intentionally excluded from this PR.
    - Validation evidence is listed separately and is not inferred from
      provenance.
    - Missing, blocked, or stale provenance is treated as a review signal.

If the repository PR template cannot accept a dedicated section, include the
same fields under the closest evidence, testing, risk, or review section without
renaming or removing template sections.

PR-facing evidence locations must be public URLs, repo-relative artifact paths,
artifact IDs, or hash-only tokens. Absolute local filesystem paths belong only
in local-sensitive artifacts.

## Local Artifact Shape

When a richer local mapping is needed, write a local HE artifact instead of
pasting raw data into the PR:

    {
      "schema_version": 1,
      "artifact_type": "he-pr-safety-trace",
      "he_trace_id": "hetrace_YYYYMMDD_target_hash",
      "linear_issue": "JSC-123",
      "pr": "https://github.com/org/repo/pull/123",
      "spec": ".harness/specs/example.md",
      "plan": ".harness/plan/example.md",
      "validation": {
        "commands": [
          {"command": "python3 -m pytest", "status": "pass"}
        ]
      },
      "codex_provenance": {
        "source": "session_collector_public",
        "status": "found",
        "redaction_status": "safe_summary",
        "thread_id_status": "hash_only",
        "turn_id_status": "hash_only",
        "transcript_path_status": "present_hash_only",
        "rollout_path_status": "present_hash_only",
        "evidence_freshness": "current",
        "proves": [
          "A Codex session was correlated with this work.",
          "Collector evidence exists for local inspection."
        ],
        "does_not_prove": [
          "Tests passed.",
          "The implementation is correct.",
          "Linear was updated.",
          "The PR is ready to merge."
        ]
      }
    }

If raw mappings are stored locally, mark the artifact
redaction_status: sensitive_local_only and do not publish it.

## Review Rules

- The public PR trace must include HE Trace ID, Provenance Source,
  Provenance Status, and Redaction Status when provenance is claimed.
- The trace must identify validation as separate evidence; never imply tests
  passed because provenance exists.
- not_found, blocked, and not_applicable are valid statuses. Missing fields are
  not.
- Raw local Codex IDs, transcript paths, rollout paths, trace bundles, prompt
  contents, response contents, tool payloads, and telemetry payloads are review
  blockers for public PR text unless the repository is explicitly local-only and
  the user authorized publication.

## Handoff Rule

If a PR is not created yet, HE handoff should still provide the safe trace block
or state the exact blocker. Future PR creation should copy the safe block, not
reconstruct it from raw local evidence.
