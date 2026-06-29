---
name: evals-router
description: "Use when evaluating LLM or RAG outputs: audit eval coverage, analyze failed traces, write binary judge prompts, validate judges against labels, generate targeted synthetic cases, evaluate retrieval quality, or plan review tooling. Do not use for ordinary software test implementation."
metadata:
  version: "1.0.0"
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-06-16:canonical-source
  review_cadence: quarterly
  metadata_source: frontmatter
---

# Evals Router

Route LLM/RAG eval work to the smallest proof-producing path.

## When To Use

Use for eval coverage, failed traces, judge prompts, labels, RAG evidence, synthetic cases, or review tooling. Do not use for ordinary software test implementation.

## Inputs

Need the user goal plus any traces, labels, scorecard, prompt, retrieval evidence, or target artifact.

Ask one question only when the target, evidence, scorecard, or desired artifact is missing.

## Outputs

Expected artifacts: patched eval, judge prompt, trace analysis, synthetic case, RAG check, review-interface spec, or blocked report.

Artifact shapes:

- eval-audit: `claim_id -> case_id|gap_id`
- error-analysis: `trace_id | failure_mode | owner | rerun_command`
- evaluate-rag: `sentence_id -> supported chunk_ref | unsupported`

## Procedure

1. Choose one route and one proof method from the table below.
2. Confirm the required evidence exists before editing prompts, judges, or eval data. If it is missing, stop with a blocked report naming the missing file, label set, trace, chunk, or score receipt.
3. Produce the smallest checkable artifact: claim-to-case map, trace failure table, binary judge prompt, calibration bundle, synthetic case file, sentence-support map, or review schema.
4. Run the route check. If it fails, patch only the failed prompt, case, judge, retrieval evidence, or report section; rerun that same check before widening scope.
5. For Skills SDK score trends, Tessl score history, or judge release claims, run the scorer commands in Validation and use references/route-checklists.md before trusting the score.

Route checks:

- eval-audit: scorecard plus eval files -> claim-to-case map -> pass when every claim maps to a case or named gap.
- error-analysis: failing traces plus latest run command -> failure-mode table with owner -> pass when one patched failure has rerun evidence.
- write-judge-prompt: criterion plus labels -> binary prompt with strict JSON -> pass when pass and fail labels produce expected verdicts.
- validate-evaluator: scorer config plus labeled probes -> calibration receipt -> pass when obvious, bias, copied-rubric, skill-name, and evidence-lane probes match expected verdicts.
- generate-synthetic-data: named coverage gap -> separated synthetic cases -> pass when every case has a gap id and no production-trace claim.
- evaluate-rag: answer plus retrieved chunks -> sentence-support map -> pass when every factual sentence has chunk support or an unsupported verdict.
- build-review-interface: reviewer workflow goal -> field list, verdict schema, export format -> pass when another reviewer can record a verdict without extra fields.

Capsules: use `references/knowledge-capsule.manifest.yaml` to pick one capsule, `references/source-context.yaml` for provenance, and `references/evals.yaml` for KnowledgeOS scenario IDs.

## Failure Mode

Missing evidence blocks the route until the report names the missing input and smallest next check. Unvalidated judges are advisory only. Conflicting repo contracts block edits.

## Validation

Run the narrowest relevant check first. For this skill package, use:

1. `./bin/ask skills package verify <skill-path> --json --robot`
2. `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot`
3. `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot`
4. `./bin/ask skills external-review <skill-path> --json --robot` before release claims

Fail fast: stop at the first failed gate; do not proceed. If blocked, report exact blocker evidence and the nearest meaningful fallback.

Detailed route checkpoints, judge audit fields, scorer checks, and capsule routing live in references/route-checklists.md and references/knowledge-capsule-routing.md.

## Gotchas

- Treat synthetic cases as gap probes, not representative traces.
- Split broad quality judges into binary checks.
- Do not treat LLM judge scores as release evidence before label calibration.

## Examples

- Request: "This RAG answer looks plausible but may hallucinate." Route: evaluate-rag. Evidence: retrieved chunks plus answer sentences. Next check: sentence support map before any judge.
  Artifact: sentence s1 -> chunk-07 -> supported; sentence s2 -> no chunk -> unsupported, so fail or rewrite s2.
- Request: "The judge gives everything 100%." Route: validate-evaluator. Evidence: labeled pass/fail cases. Next check: obvious wrong, verbosity-bias, and copied-rubric probes.
- Request: "We need more edge cases for tool failures." Route: generate-synthetic-data. Evidence: named gap id. Next check: keep generated cases separate from production traces.
- Judge prompt template:

~~~text
Grade one binary criterion.
Criterion: PASS iff every factual sentence in answer_text has exact support in source_references.
Return JSON: {"sentence_results":[{"sentence_id":"s1","verdict":"supported|unsupported|not_factual","source_refs":["chunk-07"],"reason":"..."}],"overall_verdict":"judge_pass|judge_semantic_fail|judge_parse_error|judge_schema_error","failure_reason":""}
Use judge_pass only when every factual sentence is supported.
~~~

- SDK scorer command: ./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot. For release-impacting scorers, follow with ./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot.

## Rules

- Redact secrets and private data from eval inputs.
- Prefer deterministic file, schema, regex, command, or artifact checks over LLM judges.
- Use repo wrappers; do not import external code, schemas, paths, viewer requirements, or agent names.
- For stochastic judges, record the audit fields named in references/route-checklists.md.
- Require held-out calibration before using a judge or scorer as behavioral proof.
- Never invent a score.
