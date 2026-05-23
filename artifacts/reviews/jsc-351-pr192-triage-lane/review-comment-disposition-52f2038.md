PR #192 unresolved current review-thread audit (head 52f2038fc40ba67bd4ba393631d00cf92c86270d)

Scope and evidence
- Source: /private/tmp/pr192-reviewthreads.json (21 total threads, 15 unresolved + non-outdated).
- Live code checked at current workspace head for each referenced file/line.
- Local Memory CLI bootstrap/search blocked in this sandbox (cannot write ~/.local-memory/local-memory.pid).

Disposition summary
- valid: 6
- stale/already fixed: 4
- low-signal/simplification: 4
- requires owner decision: 1

thread 3293367014 | skill_discovery.py:267 | stale/already fixed
- Reason: current gate already includes system bridge fallback.
- Smallest change: none.
- Validate: python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py -q

thread 3293386644 | spec.md:187 | valid
- Reason: spec says --command-json but CLI requires --command.
- Smallest change: update spec row to --command shell text (or add CLI alias).
- Validate: rg -n "implicit-preview --command-json|implicit-preview --command" .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md Infrastructure/bin/ask

thread 3293386646 | goal.md:15 | valid
- Reason: lowercase docs/goals path.
- Smallest change: switch to Docs/goals path casing.
- Validate: rg -n "docs/goals/jsc-351-agent-skills-codex-abi-conformance" Docs/goals/jsc-351-agent-skills-codex-abi-conformance/goal.md

thread 3293386648 | receipts.jsonl:16 | valid
- Reason: lowercase docs/goals path in changed_files.
- Smallest change: normalize to Docs/goals path casing.
- Validate: rg -n "docs/goals/jsc-351-agent-skills-codex-abi-conformance" Docs/goals/jsc-351-agent-skills-codex-abi-conformance/receipts.jsonl

thread 3293386650 | state.yaml:45 | valid
- Reason: repeated lowercase docs/goals path references.
- Smallest change: normalize all docs/goals refs in this state file.
- Validate: rg -n "docs/goals/jsc-351-agent-skills-codex-abi-conformance" Docs/goals/jsc-351-agent-skills-codex-abi-conformance/state.yaml

thread 3293386655 | skill-doctor.v1.schema.json:26 | requires owner decision
- Reason: adds required next_command_decision while retaining v1 schema name.
- Smallest change: choose one path: optionalize field in v1 OR bump to v2 and migrate callers.
- Validate: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q

thread 3293386658 | skill-package.v1.schema.json:58 | valid
- Reason: compatibility_status compatible can pass with null core metadata.
- Smallest change: add conditional schema rule so compatible requires non-null required metadata.
- Validate: python3 -m pytest Infrastructure/tests/test_ask_skills_package_contract.py -q

thread 3293386660 | skills_impl.py:405 | low-signal/simplification
- Reason: one-source-of-truth refactor suggestion; no demonstrated bug.
- Smallest change: defer.
- Validate: none

thread 3293386662 | skills_impl.py:1330 | valid
- Reason: live_codex_invocation is emitted when user_runtime_ready true even if required runtime target failed.
- Smallest change: gate hint on required_runtime_ready or make hint runtime-target specific.
- Validate: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q -k "runtime_target or next_command_decision"

thread 3293386664 | skills_impl.py:2952 | low-signal/simplification
- Reason: asks for richer YAML parsing; current function is intentionally conservative and no failing contract case is shown.
- Smallest change: defer unless concrete failing openai.yaml sample appears.
- Validate: none

thread 3293386666 | skills_impl.py:6166 | valid
- Reason: pruning removes any first-level item matching bridge name; could delete user-owned directory/file.
- Smallest change: delete only generated aliases (marker/provenance/symlink-target check) before unlink/rmtree.
- Validate: python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q -k "prune_first_level_system_bridge"

thread 3293386668 | skills.py:135 | low-signal/simplification
- Reason: PLE0605 style-only issue, no behavior regression proven here.
- Smallest change: optional __all__ coercion cleanup in skills.py and repo.py.
- Validate: uv run --python 3.12 ruff check Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/scripts/lib/ask/commands/repo.py --select PLE0605

thread 3293386669 | test_ask_skills_package_contract.py:141 | low-signal/simplification
- Reason: test-helper dedup suggestion only.
- Smallest change: defer.
- Validate: none

thread 3293386670 | test_jsc351_codex_abi_schema_contracts.py:144 | stale/already fixed
- Reason: file no longer exists; equivalent oneOf enforcement exists in Infrastructure/tests/test_ask_skills_doctor.py.
- Smallest change: none.
- Validate: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q

thread 3293386672 | test_jsc351_codex_abi_schema_contracts.py:1095 | stale/already fixed
- Reason: file no longer exists; current guard in test_pr_changes_validation.py uses explicit SYSTEM_BRIDGE_HANDLES allow-list.
- Smallest change: none.
- Validate: python3 -m pytest Infrastructure/tests/test_pr_changes_validation.py -q

Requested focus topics
- skill_discovery system bridge visibility: fixed.
- implicit-preview command-json mismatch: valid.
- Docs/goals path casing: valid.
- skill-doctor v1 required-field compatibility: owner decision needed.
- skill-package compatible metadata invariant: valid.
- system-bridge empty command-handle path detection: stale as filed, intent already covered in current tests.

WROTE: artifacts/reviews/jsc-351-pr192-triage-lane/review-comment-disposition-52f2038.md
