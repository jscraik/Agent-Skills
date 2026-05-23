# PR #192 Governor Remediation At Head 52f2038

## Scope

This artifact records the governor's final disposition of current unresolved PR #192 review comments after comparing the subagent audit with the clean PR-head worktree at `52f2038fc40ba67bd4ba393631d00cf92c86270d`.

The subagent artifact `review-comment-disposition-52f2038.md` is preserved as input evidence. Two findings it marked stale were reclassified as valid in this worktree because `Infrastructure/tests/test_jsc351_codex_abi_schema_contracts.py` exists at the current PR head and covered the affected schema-contract checks.

## Final Disposition

| Thread Topic | Disposition | Remediation |
| --- | --- | --- |
| `implicit-preview --command-json` in the spec | valid | Updated the canonical spec command summary to use `--command <shell-command>`. |
| Lowercase `docs/goals` references | valid | Normalized goal, state, receipts, and implementation-note references to `Docs/goals`. |
| `next_command_decision` required in v1 doctor schema | valid compatibility risk | Kept the emitted field, but made it optional in `skill-doctor.v1.schema.json` and added schema compatibility tests. |
| Compatible package contract with null core metadata | valid | Added conditional schema requirements for compatible package contracts and test coverage for the rejection path. |
| Runtime invocation hint emitted for wrong runtime target | valid | Renamed `live_codex_invocation` to `live_runtime_invocation` and gated it on the required runtime readiness. |
| First-level system bridge alias pruning can delete user-owned paths | valid | Added generated-provenance checks and tests preserving unmarked user-owned first-level bridge directories. |
| `__all__` iterable style in facade modules | low-signal but safe | Coerced `_impl.__all__` to `list(...)` in `skills.py` and `repo.py`. |
| `oneOf` declared supported but not validated in local schema harness | valid in PR worktree | Added `allOf`, `if`, `then`, and `oneOf` support to the local schema harness used by JSC-351 contract tests. |
| Empty command-handle path allowed too broadly | valid in PR worktree | Replaced broad prefix detection with an explicit `SYSTEM_BRIDGE_HANDLES` allow-list. |
| Richer YAML parser helper / package test helper dedupe | low-signal | Deferred; no failing runtime contract was demonstrated, and broader helper churn is outside this review-remediation boundary. |
| `skill_discovery.py` system bridge visibility | stale/already fixed | No patch needed; current code already has system bridge fallback. |

## Validation Evidence

| Command | Outcome |
| --- | --- |
| `PYTHONPYCACHEPREFIX=/private/tmp/agent-skills-pycache /usr/bin/python3 -m py_compile Infrastructure/bin/ask Infrastructure/scripts/lib/ask/commands/skills_impl.py Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/scripts/lib/ask/commands/repo.py` | pass |
| `uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_ask_skills_package_contract.py -q` | pass: 8 passed |
| `uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q` | pass: 15 passed, 15 subtests passed |
| `uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q -k 'first_level_system_bridge or prune_first_level'` | pass: 4 passed, 36 deselected |
| `uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_ask_cli_impl.py -q -k 'skills_proof_json_contract or skills_proof_human_output'` | pass: 2 passed, 203 deselected |
| `uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_jsc351_codex_abi_schema_contracts.py -q` | pass: 98 passed, 666 subtests passed after schema harness and fixture remediation |
| `./bin/ask skills sync --scope workspace --projection rooted --plugin-cache-refresh skip --json --robot` | pass: synchronized rooted projection metadata with plugin cache refresh skipped |

## Governor Decision

This remediation is approved for a delivery-state commit and push to PR #192. No next implementation slice is approved until the pushed head is rechecked for PR checks, review-thread state, and Linear state, with stale or failed gates classified before further work.

WROTE: artifacts/reviews/jsc-351-pr192-triage-lane/governor-remediation-52f2038.md
