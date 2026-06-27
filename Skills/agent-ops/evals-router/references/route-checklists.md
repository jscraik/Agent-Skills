# Route Checklists

## Judge Prompt Template

Criterion: pass iff every factual sentence is supported by an exact `source_references[]` entry.

Return JSON with `sentence_results[]`, `overall_verdict`, `failure_reason`, and `source_references[]`. Use `judge_pass` only when every factual sentence is supported; otherwise use `judge_semantic_fail`, `judge_parse_error`, or `judge_schema_error`.

## Route Checkpoints

- `eval-audit`: map each claim to cases; add or name the next missing realistic case.
- `validate-evaluator`: prove deterministic checks run before judges; require scorer id, version or digest, pass threshold, judge parameters, rationale audit, segmented analysis fields, and calibration probes for obvious correct, obvious wrong, verbosity bias, copied rubric text, skill-name mention, and evidence-lane overclaim.
- `generate-synthetic-data`: tie each synthetic case to a gap id and keep it separate from representative traces.
- `evaluate-rag`: verify retrieved chunks before judging answer support.

## Skills SDK Scorer Check

Run `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot` for SDK-owned skill evals. A blocked receipt means score trends are advisory until `references/evals.yaml` declares calibrated `scorer_quality` metadata.

Run `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot` when score trends, release claims, or live Tessl readiness depend on a judge/scorer. The bundle must include held-out labeled examples, TP/TN/FP/FN limits, threshold, scorer id, scorer version or digest, prompt version, model parameters, and raw scorer artifacts. A blocked receipt means the scorer metadata may be well shaped, but failure-catching behavior is not measured.

Run `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot` before quoting prior or current Tessl scores. The view artifact must come from `tessl eval view --json <run-id>` or a preserved repo evidence copy. A blocked receipt may still expose partial score math, but it is historical evidence only and must not be reported as a completed baseline.

Treat the Tessl score receipt as a feedback-loop gate, not only a score
formatter. A live handoff is blocked while `receipt.feedback_loop.status` is
`open`, including scenario-level baseline wins, incomplete baseline/usage
assessments, usage below the live handoff threshold, or no aggregate lift.
Every live Tessl regression must become an internal regression obligation, with
owner classification and rerun evidence, before the next live handoff claim.

## Skills SDK Scenario Runtime Lanes

For eval scenario behavioral proof, run the same Codex profile lanes used by the
Skills SDK judge path:

1. `codex exec --profile oss-local` in the read-only Codex profile sandbox.
2. `codex exec --profile oss-cloud` in the read-only Codex profile sandbox.

An SDK wrapper can stand in only when its receipt proves
`codex_exec_invoked=true` and the matching `codex_profile`. Do not treat
`./bin/ask evals run --runner codex`, discovery-smoke, or a generic ChatGPT
model result as oss-local or oss-cloud proof.
`codex exec --profile fast` is allowed for quick smoke tasks and checks only;
it does not satisfy either OSS promotion lane.

## Skills SDK Live Handoff Loop

Use this exact order for skill hardening before any live Tessl score is treated
as release evidence:

1. Run deterministic local gates first: `skills audit`, `sdk eval
   scenario-quality`, `sdk eval scorer-quality`, `sdk eval scorer-calibration`,
   and `sdk eval regression-plan` when previous Tessl or judge regressions
   exist.
2. Run the `oss-local` internal judge/scenario loop through
   `codex exec --profile oss-local` or a receipt that proves
   `codex_profile=oss-local`.
3. Patch `oss-local` failures by recording owner classification, failure mode,
   patch plan, retained regression artifact, and rerun commands.
4. Run the `oss-cloud` internal judge/scenario loop through
   `codex exec --profile oss-cloud` or a receipt that proves
   `codex_profile=oss-cloud`.
5. Patch `oss-cloud` failures with the same regression obligation shape.
6. Run Tessl local proof with an execute receipt, not a preview-only receipt.
7. Run Tessl live-private dry-run staging; the handoff receipt must prove both
   the `--tessl-live-dry-run` command and `tessl_eval.dry_run=true`.
8. Run live Tessl only after the deterministic gates, `oss-local`, `oss-cloud`,
   Tessl local proof, and Tessl dry-run pass for the current candidate, or an
   explicit blocker receipt explains why a lane was skipped.
9. Patch Tessl failures with the same regression obligation shape, then return
   to step 2 until all rubrics pass correctly.

`oss-local` is the cheap internal remediation judge, `oss-cloud` is the
higher-confidence internal judge, and Tessl is the external confirmation lane.
Do not spend live Tessl runs to discover failures that the internal judge loop
can surface first.
