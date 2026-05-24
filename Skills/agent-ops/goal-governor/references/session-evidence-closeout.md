# Session Evidence Closeout

Read when Goal Governor uses session-collector, OTEL, generated bundles, PR,
review, tracker, or other live-delivery evidence.

## Evidence Anchors

- `/Users/jamiecraik/.agents/session-collector/README.md` says the collector
  reads OTEL raw events, Codex rollout sessions, and optional project roots, then
  emits privacy-safe project evidence, validation summaries, evidence gaps,
  tool attribution, subagent lifecycle summaries, and skill-refactor handoffs.
- Session-collector bundle manifests keep `goal-events.json` unavailable until
  a real producer exists and mark inferred subagent lifecycle as
  `native_lifecycle_available: false`.
- The trust-boundary closeout table separates local code/tests, generated
  bundles, GitHub PR and mergeability, CI, review threads, and Linear state.
- `agent-knowledge.json` remediation rules require artifact-first completion,
  one narrow retry for missing artifacts, blocker classification, and closing
  consumed agents.

## Truth Lanes

Do not collapse delivery evidence into a single ready/not-ready claim. Report
these lanes separately when they matter:

- `local_validation`: exact local commands and outcomes from the current
  checkout.
- `generated_artifacts`: bundle/schema/receipt artifacts that exist locally,
  including freshness and shareability limits.
- `remote_pr_checks`: GitHub or CI status for the latest pushed head only.
- `review_threads`: live CodeRabbit/Codex/GitHub review state for the latest
  head, separate from local fixes.
- `tracker_state`: Linear or other tracker state checked live, with local
  planned IDs preserved when generated bundles use them.
- `merge_readiness`: branch protection, approvals, required checks, unresolved
  threads, and draft/merge state checked live.

## Closeout Rules

1. Prefer bounded collector artifacts over raw transcripts. Use raw sessions
   only when the bundle cannot answer the question.
2. Treat `native_lifecycle_available: false` as a limit, not as proof that no
   agents ran.
3. Treat stale, missing, claim-only, disappearing, environment-blocked, or
   inferred evidence as recovery input before Worker implementation or closeout.
4. If reviewers or agents were asked to write artifacts, completion requires
   verifying every expected artifact exists and is non-empty.
5. If an expected artifact is missing, retry once with an artifact-only
   follow-up; after that, mark the coverage gap explicitly.
6. Classify approval, permission, network, missing-file, timeout, git-state,
   lint, test, and environment blockers separately from code findings.
7. Close consumed child agents after their outputs are verified or their
   coverage gaps are recorded.

## Output Shape

When using these surfaces, include a `truth_lanes` block in the Goal Governor
output contract and keep every lane at `pass`, `fail`, `blocked`, or
`unknown`. A lane can be `unknown` only when the relevant live source was not
available or not in scope for the current governed action.
