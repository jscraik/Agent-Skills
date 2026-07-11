# Skills SDK Stabilization Modularity Compatibility - Independent QA

Final verdict: `accepted`

## Outcome

Independent QA could not disprove the repaired modularity extraction. The
focused `projection_mirror.py` module preserves the previously accepted
filesystem/security behavior and now routes orchestration dependencies through
the legacy compatibility API. Monkeypatches on
`projection_integrity_impl._sync_mirror_python` and
`projection_integrity_impl._prune_nested_duplicate_skill_identities` intercept
execution and control returned counts/logs without recursion or an alternate
bypass.

Before this fresh mutable QA report was written, every receipt-declared stable
path in the Git index matched both the worktree and its declared digest. The
index included `projection_mirror.py`; no `artifacts/agent-runs/**` path was
staged. Mutable QA/review outputs are intentionally excluded from stable patch
identity and may differ after this report update without invalidating it.

## Compatibility and recursion disproof

- Direct compatibility-wrapper probe patched `_sync_mirror_python` to `(77,
  88)` and duplicate pruning to `(['patched'], 9)`. With a projected `skills`
  directory present, the wrapper returned `(77, 97, [...])`; both mocks were
  called exactly once.
- Standard `sync_mirror` with the Python engine patched to `(17, 23)` returned
  `changed_files: 17`, `deleted_files: 23`, and called the compatibility seam
  once.
- Plugin-package `sync_mirror` with duplicate pruning patched to seven deletes
  returned `deleted_files: 7`, included `patched-prune`, and called the seam
  once.
- The call chain is finite: extracted orchestration calls an API compatibility
  wrapper; that wrapper calls the corresponding lower-level extracted function.
  The lower-level function does not call the orchestration wrapper again.
- The extracted module imports only standard-library dependencies and receives
  legacy helpers through the protocol/object boundary. Direct imports and all
  tests completed without circular-import or mutable-global failures.

## Prior behavior reverified

- Seven unsafe-symlink cases fail before projection mutation with zero
  changes/deletes and preserved sentinel; a valid contained link syncs and
  verifies.
- Whole-tree identity, executable mode distinction, true duplicate pruning,
  and preservation of distinct references/types/links/modes remain passing.
- README intake, replay timeout/OSError, exact-argv deduplication, and
  deny-by-default remain passing.
- Public SDK help and normalized status remain unchanged; public capability
  evidence remains schema v0 and inventory-only.
- Direct modularity validation and the explicit nine-file Skills SDK gate pass.
- Independent patch identity and generated replay digest match the receipt.
- QA performed no implementation or index mutation, live sync, network action,
  commit, push, or external mutation.

## Exact evidence

- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_projection_integrity_plugin_cache.py tests/test_skills_sdk_stabilization_identity.py -q` -> pass (10 passed, 5 subtests passed)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_skills_sdk_stabilization_identity.py tests/test_skills_sdk_stabilization_replay.py tests/test_skills_sdk_skill_intake.py tests/test_projection_integrity_plugin_cache.py tests/test_local_plugin_picker_surface.py tests/test_skills_sdk_capability_evidence.py tests/test_skills_sdk_command_evidence_plan.py -q` -> pass (61 passed, 2 skipped, 5 subtests passed)
- Command: `python3 Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py --changed-files Infrastructure/scripts/lifecycle-and-sync/projection_integrity_impl.py Infrastructure/scripts/lifecycle-and-sync/projection_mirror.py` -> pass (`ask_cli_modularity: lines=1873 max=1900`)
- Command: `./bin/ask repo validate --scope skills-sdk --ephemeral --changed-files Infrastructure/scripts/lib/ask/skills_sdk/skill_intake.py Infrastructure/scripts/lib/ask/skills_sdk/stabilization_identity.py Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py Infrastructure/scripts/lifecycle-and-sync/projection_integrity_impl.py Infrastructure/scripts/lifecycle-and-sync/projection_mirror.py Infrastructure/tests/test_projection_integrity_plugin_cache.py Infrastructure/tests/test_skills_sdk_skill_intake.py Infrastructure/tests/test_skills_sdk_stabilization_identity.py Infrastructure/tests/test_skills_sdk_stabilization_replay.py --json --robot` -> pass (all nine paths admitted, required_failures=0, warn_only_issues=0; unrelated checks skipped)
- Command: direct compatibility-wrapper monkeypatch probe -> pass (`_sync_mirror_python` and `_prune_nested_duplicate_skill_identities` each called once; patched counts/logs controlled result)
- Command: standard-sync monkeypatch regression probe -> pass (one interception; result changed=17, deleted=23)
- Command: plugin duplicate-prune monkeypatch regression probe -> pass (one interception; result deleted=7 with patched log)
- Command: seven-case unsafe-symlink parity matrix after compatibility repair -> pass (all attacks rejected before mutation; sentinel preserved; valid contained link synced and verified)
- Command: independent worktree and index stable-path digest comparison -> pass (no worktree mismatches, no index missing paths, no index digest mismatches; `projection_mirror.py` present)
- Command: independent patch-identity reconstruction -> pass (identity `sha256:13bb9ced63c819c7d12953de4d5c367721f3c0636620932594b57005ef2d3b29` matched)
- Command: independent generated replay worktree/index digest comparison -> pass (both matched declared digest)
- Command: `git diff --cached --name-only | rg 'artifacts/agent-runs'` -> pass (no output; no agent-run manifest staged)
- Command: `cmp -s /tmp/sdk-help.before /tmp/sdk-help.qa.compat` -> pass (public SDK help unchanged)
- Command: `cmp -s /tmp/status.before.norm /tmp/status.compat.norm` -> pass (normalized public SDK status unchanged)
- Command: `./bin/ask sdk evidence verify --scope capability-matrix --json --robot` -> pass (schema v0, 52 capabilities, 176 refs, 43 not run, zero unknown, `proof_mode: inventory_only`)
- Command: `git diff --check` -> pass (unstaged diff has no whitespace errors before report update)
- Command: `git diff --cached --check` -> pass (staged diff has no whitespace errors)

## Residual boundaries

- Raw full `pytest tests -q` remains blocked by pre-existing obsolete
  command-surface assertions.
- The canonical Skills SDK gate is narrow; focused suites remain the meaningful
  patch proof.
- Replay policy intent is not observed syscall absence.
- Transaction locking/concurrent source mutation, runtime install, live cache,
  Tessl, CircleCI, extraction, publication, hosted review, commit, merge, and
  release state remain unproven.
- Mutable QA report, Worker reports, review handoff, and run manifests are not
  part of stable patch identity; staging/commit decisions remain coordinator or
  human authority.

## Next step

The repaired modularity extraction may return to the coordinator for final
artifact reconciliation and human acceptance. No commit, push, live sync, or
external mutation is authorized by this QA result.

WROTE: /private/tmp/agent-skills-skills-sdk-stabilization/.harness/reports/qa-skills-sdk-stabilization.md
