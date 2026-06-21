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
