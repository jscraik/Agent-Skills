# PR216 Testing Review

## Scope
- Base: `main` (`bac21b434`)
- Head: `codex/skill-factory-eval-hardening` (`5ce2db964`)
- Diff basis: `git diff main...HEAD`
- Reviewer focus: test coverage gaps, weak assertions, brittle tests, missing error-path coverage.

## Findings (Severity-ranked)

### 1) MEDIUM: Fallback run-id extraction and JSON-prefix parsing branches in Tessl live-private flow are not explicitly exercised
- Severity: medium
- Evidence:
  - Source branch points:
    - `Infrastructure/scripts/lib/ask/commands/evals.py:150` (`_parse_json_object_from_text`) includes prefix-skipping and object-only parse fallback.
    - `Infrastructure/scripts/lib/ask/commands/evals.py:166` (`_extract_tessl_eval_run_id`) includes multi-key lookup plus regex UUID fallback.
    - `Infrastructure/scripts/lib/ask/commands/evals.py:1728` consumes extracted run id to drive `tessl eval view` gating.
  - Test-coverage probe:
    - Command evidence: `rg -n "_extract_tessl_eval_run_id|_parse_json_object_from_text" Infrastructure/tests/test_ask_evals_command.py` returned no direct matches.
- Impacted behavior:
  - If Tessl emits non-canonical output (prefixed logs or plain-text UUID), the live-private gate can fail to retrieve or parse run IDs and may misclassify a valid run as blocked.
- Remediation:
  - Add targeted unit tests in `Infrastructure/tests/test_ask_evals_command.py` for:
    1. JSON with leading non-JSON text before `{`.
    2. Plain-text UUID extraction when JSON parsing fails.
    3. Payloads where run ID is under alternate keys (`data.id`, `evalRunId`, `runId`).
- Confidence: 0.78
- Validation ownership: introduced by current patch

## Strengths
- High-risk live-private readiness gate behavior is broadly covered (workspace validation, baseline comparisons, score thresholds, polling completion behavior).
- New contract-heavy surfaces in `package_contracts.py` are backed by substantial positive and negative tests in `Infrastructure/tests/test_ask_skills_package_contract.py`.
- Steering-uptake validator changes include explicit negative-path tests for unknown category and improvement types.

## Residual Risks
- The diff is very large (100+ files, 15k+ net insertions), so branch-level confidence is strongest in the primary modified Python modules and associated tests; documentation/artifact-only files were not revalidated semantically.
- Some parser fallbacks rely on tolerant behavior under malformed external CLI output, which typically regresses first when upstream output shape changes.

## Validation Evidence
- `git diff --name-only main...HEAD`
- `git diff --stat main...HEAD`
- `git diff --unified=0 main...HEAD -- Infrastructure/scripts/lib/ask/commands/evals.py`
- `git diff --unified=0 main...HEAD -- Infrastructure/tests/test_ask_evals_command.py`
- `rg -n "_extract_tessl_eval_run_id|_parse_json_object_from_text|_tessl_eval_view_has_complete_scores|_summarize_tessl_live_eval_view" Infrastructure/scripts/lib/ask/commands/evals.py`
- `rg -n "_extract_tessl_eval_run_id|_parse_json_object_from_text" Infrastructure/tests/test_ask_evals_command.py`

## Accountability Receipt
- status: completed_with_findings
- artifact_paths: [`artifacts/reviews/pr216-testing.md`]
- manifest_path: not_written_by_scope_single-artifact-request
- findings:
  - MEDIUM: unexercised fallback parsing branches for Tessl run-id extraction in live-private lane.
- failures_or_blockers: none
- improvement_opportunities:
  - Add compact unit tests for parser fallbacks and alternate run-id key extraction.
- strengths:
  - Strong coverage on primary happy/error paths for new live-private gating and package contracts.
- validation_evidence:
  - commands listed in “Validation Evidence”.
- next_action:
  - Add three focused parser fallback tests, then rerun `python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q`.

WROTE: artifacts/reviews/pr216-testing.md

