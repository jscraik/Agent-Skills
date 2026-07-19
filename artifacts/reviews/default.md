# PR #345 Candidate `db50255` Independent QA Disproof

schema_version: qa-proof/v1
status: rejected
agent_id: 019f753b-4f48-7c30-858b-1831cdd94631
candidate: db50255eb80917362b9a8d60e3fcc72b70ba041b
candidate_worktree: /private/tmp/agent-skills-jsc389-approved-auth-stream

## Scope

Independent, immutable-commit review of PR #345 candidate `db50255eb80917362b9a8d60e3fcc72b70ba041b`. I inspected only its parent/diff and relevant runtime/schema contracts. I did not edit, stage, commit, push, create or update a PR, mutate hosted reviews, or run a provider-backed eval or judge.

## Verdict

Reject the candidate as a complete closeout of the six findings. Four contract repairs are substantiated locally, but two high-impact defects remain:

1. **P1 — the claimed approved cloud-auth path is still only shape-checked.** `is_opaque_env_reference` accepts any FIFO whose trailing components are `.codex/.env`; it does not require that the path equals `Path.home() / ".codex" / ".env"` or another explicit allowlisted operator reference. Because `_approved_cloud_auth_fact` takes `SKILLS_SDK_OSS_CLOUD_ENV_FILE` directly and `_cloud_catalog_fact` repeats the same predicate, an arbitrary temporary `.../.codex/.env` FIFO is admitted and reaches the catalog-runner boundary. The parent commit `5a55b745` introduced the weaker basename/parent predicate; `db50255` does not modify it.

2. **P1 — the typed receipt reader still accepts an unordered completed A/B receipt.** The candidate makes the JSON Schema require `command_variant_labels == ["A", "B"]` and ordered top-level `variant_results`, but `validate_ab_run_receipt` delegates to `AbRunReceipt`, whose completed validators use set equality / `exact_variant_labels`. An otherwise valid receipt with labels `["B", "A"]` and both runtime gates/results reversed is accepted by the typed reader, while the authoritative JSON Schema rejects it. This contradicts the candidate's stated ordered-A/B receipt contract and leaves a public reader bypass.

## Six-Finding Matrix

| Hosted finding | Independent result | Evidence |
| --- | --- | --- |
| Cloud approved opaque env path (parent P1) | **Not disproved; persists.** | Arbitrary temporary `.../.codex/.env` FIFO produced `auth=pass` and `catalog=pass` through a fake non-provider runner. |
| Blocked receipts require top-level blockers | **Disproved.** | The v1 JSON Schema has a root-required `blockers` field and a `status=blocked` `minItems: 1` conditional; focused schema test passes. |
| Completed receipt proves side effects | **Disproved.** | Both schema and `validate_run_receipt_status` require mutation, provider, network, and Codex-exec side-effect flags for `completed`; focused schema test passes. |
| Judge schema accepts versioned `ex_` identifiers | **Disproved.** | Both judge schemas accept `^(?:ex_[a-z0-9]{16}|[0-9a-f]{16})$`; focused test passes. |
| `--output-last-message` binds to receipt path | **Disproved.** | Candidate's guard requires exactly one flag and an adjacent matching value; focused test rejects forged/multiple path cases. |
| Exact ordered A/B labels | **Partially fixed; not disproved overall.** | JSON Schema rejects reversed A/B order, but the typed reader accepts the same reversed completed receipt. |

## Scope And Churn

`db50255` changes seven files only: the two judge schemas, the v1 run schema, two Skills SDK contract modules, and two focused tests. The diff is coherent with the named receipt-contract work and has no whitespace errors. I found no unrelated churn.

## Exact Evidence

Command: `git -C /private/tmp/agent-skills-jsc389-approved-auth-stream status --short --branch` -> pass (candidate checkout was clean on `codex/jsc-389-approved-auth-stream`, ahead of `origin/main` by two commits)

Command: `git -C /private/tmp/agent-skills-jsc389-approved-auth-stream rev-parse HEAD` -> pass (`db50255eb80917362b9a8d60e3fcc72b70ba041b`)

Command: `git -C /private/tmp/agent-skills-jsc389-approved-auth-stream diff --no-ext-diff --check db50255eb80917362b9a8d60e3fcc72b70ba041b^ db50255eb80917362b9a8d60e3fcc72b70ba041b` -> pass (no whitespace errors)

Command: `XDG_CACHE_HOME=/private/tmp/codex-xdg-cache XDG_STATE_HOME=/private/tmp/codex-xdg-state PYTHONDONTWRITEBYTECODE=1 bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_skills_sdk_auth_stream_identity.py tests/test_skills_sdk_ab_argv_binding.py tests/test_skills_sdk_schema_spine.py tests/test_skills_sdk_ab_run.py tests/test_skills_sdk_ab_judge.py tests/test_skills_sdk_ab_judge_score.py` -> pass (202 passed, 89 subtests passed)

Command: `XDG_CACHE_HOME=/private/tmp/codex-xdg-cache XDG_STATE_HOME=/private/tmp/codex-xdg-state PYTHONDONTWRITEBYTECODE=1 bash Infrastructure/scripts/run-infrastructure-python.sh - <<'PY' ... validate_ab_run_receipt(reversed_completed_receipt); schema_validation.validate_payload_against_schema(reversed_completed_receipt, ...) ... PY` -> pass (typed reader accepted the reversed completed receipt; JSON Schema returned `fail`)

Command: `XDG_CACHE_HOME=/private/tmp/codex-xdg-cache XDG_STATE_HOME=/private/tmp/codex-xdg-state PYTHONDONTWRITEBYTECODE=1 bash Infrastructure/scripts/run-infrastructure-python.sh - <<'PY' ... create arbitrary temporary .codex/.env FIFO; _approved_cloud_auth_fact(...); _cloud_catalog_fact(..., fake_runner) ... PY` -> pass (`arbitrary_dot_codex_fifo_auth=pass`; `arbitrary_dot_codex_fifo_catalog=pass`; no provider or judge invoked)

## Limitations

This is local deterministic contract evidence only. It does not prove hosted review-thread state, current CI, mergeability, provider availability, cloud credential validity, actual Codex execution, a provider-backed eval/judge result, or release readiness.

WROTE: artifacts/reviews/default.md
