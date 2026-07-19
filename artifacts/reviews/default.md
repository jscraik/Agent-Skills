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

---

# JSC-468 CI Repair Adversarial Review

schema_version: adversarial-ci-review/v1
status: changes_requested
agent_id: 019f7b91-c82b-7a12-a6fe-5d8938afa0df
mode: read_only

## Scope

Reviewed the in-progress CI repair for the `audit`, `check`, and `lint` PR
failures. I inspected the current candidate diff, the previously proposed
single-commit CI remedy `140ca1b6c`, the maintained validation router, and the
canonical manifest generator. I made no source, workflow, skill, Git, hosted,
package-manager, or external-eval mutation.

## Findings

### P1 — New regression test is not in a CI-owned execution path

`Infrastructure/tests/test_pr_pipeline_validation_dependencies.py` is a useful
unit test, but no PR job currently selects it. `scripts/validate_all_impl.sh`
limits `--scope=test` to `skill-lifecycle-tests`, `skill-authoring-family`,
`skill-graph-profiles`, and `gotcha-store` (lines 305-310). The only selected
pytest targets in
`Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh`
are enumerated at lines 584-598, and this file is absent. The test therefore
does not ratchet a future removal of `uv` from the workflow.

Minimal remediation: add this exact test to a maintained CI test command, or
move the assertion into an existing validator that `audit`/`check` already run.
Prove both the direct test and its canonical CI-owned caller path.

### P2 — Test accepts unsafe ordering and an unspecified Python runtime

`_uses_python_setup` in
`Infrastructure/tests/test_pr_pipeline_validation_dependencies.py:32-37` only
checks for an `actions/setup-python` action, while `_installs_uv` at lines 40-46
only checks that some step contains `uv`. Neither asserts a `python-version:
"3.12"` nor that setup and installation precede the `repo validate` step. A
workflow that installs `uv` after validation, or uses Python 3.11, would pass
the test even though `Infrastructure/pyproject.toml:5` and
`Infrastructure/uv.lock:3` require `>=3.12`.

Minimal remediation: derive step indexes and assert, per scope, pinned Python
3.12 setup < uv install < validation command.

### P2 — Added CI tool version bypasses the repository tool pin

The candidate uses `python -m pip install --upgrade pip uv pyyaml pytest
jsonschema` in `.github/workflows/pr-pipeline.yml:538` and `:555`.
`.mise.toml:5` declares the repository's `uv` version as `0.11.3`; the new
unqualified `uv` install can change independently of the repo tool contract.
This is not a root package-manager contract, but it is a CI toolchain
reproducibility and supply-chain drift risk.

Minimal remediation: install the repository-approved `uv` version (or a
SHA-pinned `setup-uv` action admitted by the existing action-pinning policy),
then update the test to assert the chosen mechanism.

### P3 — Two unrelated heading-level edits should be removed

The progressive-disclosure repair requires `## Gotchas`; it does not require
changing `### Anti-Patterns`. The candidate also promotes that heading in
`Skills/agent-ops/improve-codebase-architecture/SKILL.md:116` and
`Skills/agent-ops/testing/SKILL.md:129`. Both strict package audits pass, so
this is not a correctness blocker, but restoring the two headings to their
original nesting keeps the approved repair minimal.

### Confirmed non-finding — Full manifest rewrite is generator-owned

The manifest change is broad because each row records `source_revision`.
`Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py:113-122`
writes every root manifest and the generated rows now bind to the current
candidate revision. The repository explicitly identifies manifests as generated
and forbids hand edits in
`Docs/specs/2026-04-24-feat-context-budgeted-skill-trees-spec.md:912`.
Retain the complete generator output after reviewing it; do not trim it to the
two edited skills.

## Evidence

Command: `git show --format= 140ca1b6c | git apply --check --verbose` -> pass (the proposed CI commit applies cleanly to the current workflow surface)

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_pr_pipeline_validation_dependencies.py --disable-warnings --maxfail=1` -> pass (the new test passes locally, but static routing evidence shows CI does not select it)

Command: `bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict` -> pass (the two required H2 Gotchas headings are now accepted; three unrelated warnings remain)

Command: `./bin/ask skills audit Skills/agent-ops/improve-codebase-architecture --level strict --json --robot` -> pass (the candidate skill shape is accepted)

Command: `./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot` -> pass (the candidate skill shape is accepted)

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh scripts/validation-and-linting/check_context_budget.py --projection rooted --json` -> fail (14 stale `SKILLSET_SOURCE_HASH_STALE` rows plus one local runtime-exposure finding before the candidate generator output; the 14 source paths match `origin/main`)

Command: `git diff --quiet origin/main -- Skills/agent-ops/agents-md/SKILL.md Skills/agent-ops/autoreview/SKILL.md Skills/agent-ops/evals-router/SKILL.md Skills/agent-ops/goal-governor/SKILL.md Skills/agent-ops/improve-agent-native/SKILL.md Skills/agent-ops/improve-codebase-architecture/SKILL.md Skills/agent-ops/pr-green-sweep/SKILL.md Skills/agent-ops/simplify/SKILL.md Skills/agent-ops/technical-writer/SKILL.md Skills/agent-ops/testing/SKILL.md Skills/agent-ops/ubiquitous-language/SKILL.md Plugins/aidevcon/skills/talk-podjarny-skills-are-the-new-code/SKILL.md Plugins/aidevcon/skills/talk-tal-skills-security/SKILL.md Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md` -> pass (all 14 stale source paths were unchanged from `origin/main` before the approved repair)

## Boundary

No Tessl, provider-backed, cloud, or other live external evaluation was run.
This review does not prove hosted CI, hosted review state, mergeability, or the
future post-push check results.

WROTE: artifacts/reviews/default.md
