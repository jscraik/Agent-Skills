# Route Checklists

## Judge Prompt Template

Criterion: pass iff every factual sentence is supported by an exact `source_references[]` entry.

Return JSON with `sentence_results[]`, `overall_verdict`, `failure_reason`, and `source_references[]`. Use `judge_pass` only when every factual sentence is supported; otherwise use `judge_semantic_fail`, `judge_parse_error`, or `judge_schema_error`.

## Route Checkpoints

- `eval-audit`: map each claim to cases; add or name the next missing realistic case.
- `generate-synthetic-data`: tie each synthetic case to a gap id and keep it separate from representative traces.
- `evaluate-rag`: verify retrieved chunks before judging answer support.
