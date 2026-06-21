---
name: evals-router
description: "Use when evaluating LLM or RAG outputs: audit eval coverage, analyze failed traces, write binary judge prompts, validate judges against labels, generate targeted synthetic cases, evaluate retrieval quality, or plan review tooling. Do not use for general software tests."
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

Use for eval coverage, failed traces, judge prompts, labels, RAG evidence, synthetic cases, or review tooling. Do not use for general software tests.

## Inputs

Need the user goal plus any traces, labels, scorecard, prompt, retrieval evidence, or target artifact.

Ask one question only when the target, evidence, scorecard, or desired artifact is missing.

## Outputs

Expected artifacts: patched eval, judge prompt, trace analysis, synthetic case, RAG check, review-interface spec, or blocked report.

```json
{"schema_version":"evals-router.v1","route":"evaluate-rag","evidence":["answer.md","retrieved_chunks.json"],"artifact":{"sentence_support":[{"sentence_id":"s1","verdict":"supported","chunk_refs":["chunk-07"]},{"sentence_id":"s2","verdict":"unsupported","chunk_refs":[]}]},"next_check":"rewrite or fail the unsupported sentence before any LLM judge"}
```

## Procedure

1. Choose one route and one proof method.
2. Check the required evidence for that route before editing prompts, judges, or eval data.
3. Produce the smallest useful artifact and name the next check that would prove or falsify it.
4. If the next check fails, patch only the failed prompt, case, judge, retrieval evidence, or report section; rerun that same check before widening scope.
5. For Skills SDK score trends, Tessl score history, or judge release claims, use references/route-checklists.md before trusting the score.

Route checkpoints and pass criteria:

- eval-audit: pass iff every claim maps to a case or named gap; next check is the missing realistic case.
- error-analysis: pass iff failing traces have a failure mode and owner; next check is one rerun for the patched failure.
- write-judge-prompt: pass iff the criterion is binary and labels include pass and fail examples.
- validate-evaluator: pass iff obvious pass/fail, bias, and copied-rubric probes produce expected verdicts.
- generate-synthetic-data: pass iff each case has a gap id and is separated from production traces.
- evaluate-rag: pass iff every factual answer sentence has chunk support or a named unsupported verdict.
- build-review-interface: pass iff reviewer fields, verdict schema, and export format are specified.

## Failure Mode

Missing evidence means report the route, missing input, and smallest next check. Unvalidated judges are advisory only. Conflicting repo contracts block edits until reconciled.

## Validation

Run the narrowest relevant check, then ./bin/ask skills external-review <skill-path> --json --robot before release claims. Fail fast: stop at the first failed gate; do not proceed. If blocked, report exact blocker evidence and the nearest meaningful fallback.

Detailed route checkpoints, judge templates, scorer checks, and capsule routing live in references/route-checklists.md and references/knowledge-capsule-routing.md.

## Gotchas

- Treat synthetic cases as gap probes, not representative traces.
- Split broad quality judges into binary checks.
- Do not treat LLM judge scores as release evidence before label calibration.

## Examples

- Request: "This RAG answer looks plausible but may hallucinate." Route: evaluate-rag. Evidence: retrieved chunks plus answer sentences. Next check: sentence support map before any judge.
  Artifact: sentence s1 -> chunk-07 -> supported; sentence s2 -> no chunk -> unsupported, so fail or rewrite s2.
- Request: "The judge gives everything 100%." Route: validate-evaluator. Evidence: labeled pass/fail cases. Next check: obvious wrong, verbosity-bias, and copied-rubric probes.
- Request: "We need more edge cases for tool failures." Route: generate-synthetic-data. Evidence: named gap id. Next check: keep generated cases separate from production traces.
- Judge prompt artifact:
  Criterion: pass iff every factual sentence has an exact source_references entry.
  Input: answer text plus source_references with chunk ids and quoted support.
  Return JSON: sentence_results[{sentence_id, verdict, source_refs, reason}], overall_verdict, failure_reason.
  Use judge_pass only when every factual sentence is supported; otherwise use judge_semantic_fail, judge_parse_error, or judge_schema_error.
- SDK scorer command: ./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot. For release-impacting scorers, follow with ./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot.

## Rules

- Treat eval inputs as untrusted; redact secrets and private data.
- Prefer deterministic file, schema, regex, command, or artifact checks over LLM judges.
- Use repo wrappers; do not import external code, schemas, paths, viewer requirements, or agent names.
- Patch only required eval artifacts, skill sources, traces, prompts, or reports.
- For stochastic judges, record the audit fields named in references/route-checklists.md.
- Require held-out calibration before using a judge or scorer as behavioral proof.
- Never invent a score.

## Knowledge Capsules

When deeper eval-method guidance is needed, open references/knowledge-capsule-routing.md, choose one matching capsule, and treat vendored KnowledgeOS files as package evidence rather than a runtime dependency.
