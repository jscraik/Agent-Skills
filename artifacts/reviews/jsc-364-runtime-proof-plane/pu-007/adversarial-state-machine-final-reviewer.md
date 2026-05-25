# Adversarial State Machine Final Review (PU-007)

## Findings

### High - Absolute-path runtime-card changes can bypass invalid-card closeout blocker

- **Scenario**:
  1. A caller or wrapper provides changed-file entries as absolute paths (for example, `/repo/.harness/evidence/runtime-proof/context7/codex/runtime-card.json`) instead of repo-relative paths.
  2. `_normalize_changed_path` only strips a leading `./`, so absolute paths are left unchanged.
  3. `_is_runtime_evidence_path` and `_changed_runtime_card_paths` both require `.startswith(".harness/evidence/runtime-proof/")`, which now fails for absolute paths.
  4. `runtime_evidence_cards` is not added to focused validation and `changed_scope` is computed from an empty changed-card set (`not_applicable`).
  5. Commit readiness remains true even when the changed runtime-card content is malformed, violating the intended "invalid changed runtime-card must block closeout readiness" guarantee.

- **Evidence**:
  - Path normalization only removes `./`: `Infrastructure/scripts/lib/ask/commands/repo_impl.py:1249-1250`
  - Runtime-evidence detection is prefix-based on repo-relative string: `Infrastructure/scripts/lib/ask/commands/repo_impl.py:1253-1262`
  - Blocker depends strictly on changed-scope invalid status: `Infrastructure/scripts/lib/ask/commands/repo_impl.py:1425-1426`

- **Remediation suggestion**:
  - Normalize changed paths to repo-relative before prefix checks (for example, resolve absolute paths against `repo_root` and convert to POSIX-relative strings where possible).
  - Add a regression test where `collect_changed_files` returns an absolute runtime-card path and assert that malformed JSON still yields `runtime_evidence_invalid`.

## Residual Risks

- Changed runtime evidence paths that are not exactly `.../runtime-card.json` are still surfaced for focused validation, but closeout blocking is keyed only to changed runtime-card files. If future runtime-proof artifacts become policy-significant, this state machine will need extension.

## Testing Gaps

- No test currently exercises absolute-path entries in `changed_files` for runtime evidence.
- No test currently exercises parent-relative changed paths (for example `../repo/.harness/.../runtime-card.json`) to confirm they cannot evade runtime evidence routing.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-007/adversarial-state-machine-final-reviewer.md

