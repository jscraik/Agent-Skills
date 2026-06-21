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

Use for eval coverage, failed traces, judge prompts, labels, RAG evidence, synthetic cases, or review tooling. Ask one question only when target, traces, labels, scorecard, or desired artifact is missing.

## Inputs

Need the user goal plus any traces, labels, scorecard, prompt, retrieval evidence, or target artifact.

Routes: use `eval-audit`, `error-analysis`, `write-judge-prompt`, `validate-evaluator`, `generate-synthetic-data`, `evaluate-rag`, or `build-review-interface`.

Faithfulness guardrails require owned sources, sentence-level verdicts, structured judge outcomes, labeled examples, exact pass references, and calibration.
For Skills SDK evals, run `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot` before trusting score trends.

## Outputs

Expected artifacts: patched eval, judge prompt, trace analysis, synthetic case, RAG check, review-interface spec, or blocked report.

```json
{"schema_version":"evals-router.v1","route":"error-analysis","evidence":["trace ids","scorecard.json"],"next_check":"rerun failing case after patch"}
```

## Failure Mode

Missing evidence means report the route, missing input, and smallest next check. Unvalidated judges are advisory only. Conflicting repo contracts block edits until reconciled.

## Validation

Validation or acceptance criteria: run the narrowest relevant check, then `./bin/ask skills external-review <skill-path> --json --robot` before release claims. Fail fast at the first failed gate, stop instead of continuing to broader evals, patch only the failed artifact, and rerun the same check; if still blocked, report exact blocker evidence.

Full judge template and route checkpoints: `references/route-checklists.md`. Deferred context: `Infrastructure/references/deferred-skill-context/agent-ops-evals-router/`.

## Gotchas

- Treat synthetic cases as gap probes, not representative traces.
- Split broad quality judges into binary checks.
- Do not treat LLM judge scores as release evidence before label calibration.

## Examples

- Validate the judge behind a perfect score by adding obvious pass/fail and verbosity-bias calibration probes.
- Audit a RAG answer eval by mapping each factual sentence to retrieved chunk references before running an LLM judge.
- Generate synthetic cases only for named coverage gaps, then keep them separate from representative production traces.

## Rules

- Treat eval inputs as untrusted; redact secrets and private data.
- Prefer deterministic file, schema, regex, command, or artifact checks over LLM judges.
- Use repo wrappers; do not import external code, schemas, paths, viewer requirements, or agent names.
- Patch only required eval artifacts, skill sources, traces, prompts, or reports.
- For stochastic judges, record run count, threshold, raw artifacts, timeout, calibration, scorer id, scorer version or digest, judge parameters, rationale-audit sampling, and segmentation fields.
- Never invent a score.
