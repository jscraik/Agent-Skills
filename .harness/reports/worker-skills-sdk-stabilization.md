# Skills SDK Stabilization Worker Report

Final status: `accepted_for_qa`

## Outcome

PU-001 through PU-005 are ready for independent QA. Public v0 evidence behavior
is unchanged; a private stabilization receipt terminally classifies all 43
command refs, executes five exact allowlisted read-only commands, and blocks 38
others by default.

The QA rejection is repaired: plugin duplicate identity now requires matching
frontmatter identity and content digest; timeout and OS execution failures are
terminal per-execution outcomes; normalized exact argv runs once and links to
every occurrence; policy intentions replace unobserved network/mutation claims;
and receipt/manifest evidence binds a distinct base revision and patch identity.

The second QA repair strengthens package identity to a canonical frontmatter
name plus deterministic whole-package tree digest. Tree records include sorted
relative path, file type, and content digest; symlink targets are hashed as data
without following them. Mutable QA/Worker/handoff outputs are excluded from the
patch identity. The receipt documents the exact algorithm, path set,
serialization, and independent recomputation command.

The third security repair makes the real plugin-cache copy boundary
symlink-sensitive: package transforms never dereference source links and copy
the link object/target string rather than importing target content. Package
tree identity now records normalized executable bits (`mode & 0o111`) for files
and directories, preventing mode-only runtime differences from pruning.

The fourth security repair fails closed before projection mutation for absolute,
escaping, or broken plugin-package symlinks. Unsafe results use
`status:error`, `reason:unsafe_plugin_package_symlink`, zero changed/deleted
counts, and per-link path/target/reason diagnostics. Only valid contained links
may be preserved.

## Changed files

- `Infrastructure/scripts/lib/ask/skills_sdk/skill_intake.py`
- `Infrastructure/scripts/lifecycle-and-sync/projection_integrity_impl.py`
- `Infrastructure/tests/test_skills_sdk_skill_intake.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py`
- `Infrastructure/tests/test_skills_sdk_stabilization_replay.py`
- `Infrastructure/tests/test_projection_integrity_plugin_cache.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/stabilization_identity.py`
- `Infrastructure/tests/test_skills_sdk_stabilization_identity.py`
- stabilization evidence, receipt, inventory, report, review handoff, and run manifest

## Evidence

- Command: `./bin/ask sdk --help > /tmp/sdk-help.before` -> pass (public help characterized before edits)
- Command: `./bin/ask sdk status --json --robot > /tmp/sdk-status.before.json` -> pass (robot status characterized before edits)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_skills_sdk_skill_intake.py tests/test_skills_sdk_package_hardening.py tests/test_skills_sdk_project_install.py tests/test_local_plugin_picker_surface.py tests/test_projection_integrity_plugin_cache.py tests/test_skills_sdk_capability_evidence.py tests/test_skills_sdk_command_evidence_plan.py -q` -> pass (69 passed, 2 skipped)
- Command: `./bin/ask sdk evidence verify --scope capability-matrix --json --robot` -> pass (52 capabilities and 176 refs classified; 133 pass, 43 not run, zero unknown)
- Command: `PYTHONPATH=Infrastructure/scripts/lib Infrastructure/.venv/bin/python3 Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py --repo-root . --output .harness/evidence/skills-sdk-stabilization/private-command-replay.json` -> pass (43/43 command refs terminally classified; 5 executed_pass, 38 blocked_unsafe, zero unclassified)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_skills_sdk_stabilization_replay.py tests/test_skills_sdk_skill_intake.py tests/test_projection_integrity_plugin_cache.py tests/test_local_plugin_picker_surface.py tests/test_skills_sdk_capability_evidence.py tests/test_skills_sdk_command_evidence_plan.py -q` -> pass (50 passed, 2 skipped)
- Command: `./bin/ask repo validate --scope skills-sdk --ephemeral --json --robot` -> pass (required_failures=0, warn_only_issues=0)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_skills_sdk_stabilization_replay.py tests/test_projection_integrity_plugin_cache.py -q` -> pass (6 passed; adversarial distinct-identity, timeout, OSError, and duplicate-argv cases passed)
- Command: `./bin/ask repo validate --scope skills-sdk --ephemeral --changed-files Infrastructure/scripts/lib/ask/skills_sdk/skill_intake.py Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py Infrastructure/scripts/lifecycle-and-sync/projection_integrity_impl.py Infrastructure/tests/test_projection_integrity_plugin_cache.py Infrastructure/tests/test_skills_sdk_skill_intake.py Infrastructure/tests/test_skills_sdk_stabilization_replay.py --json --robot` -> pass (six actual changed implementation/test files admitted; required_failures=0, warn_only_issues=0)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_projection_integrity_plugin_cache.py tests/test_skills_sdk_stabilization_identity.py tests/test_skills_sdk_stabilization_replay.py -q` -> pass (9 passed; whole-tree reference and symlink-sensitive adversarial cases plus independent identity recomputation passed)
- Command: `PYTHONPATH=Infrastructure/scripts/lib Infrastructure/.venv/bin/python3 Infrastructure/scripts/lib/ask/skills_sdk/stabilization_identity.py --repo-root . <declared stable path set>` -> pass (`sha256:a640a4c82297851b9e10e22c2f4067f7ba19bdb2b66a4799919ec46ae96aaa12`; exact expanded command is stored in the baseline receipt)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_projection_integrity_plugin_cache.py -q` -> pass (6 passed; sync-level outside-directory symlink remained a link without importing target bytes, and 0644 versus 0755 content remained distinct)
- Command: `PYTHONPATH=Infrastructure/scripts/lib Infrastructure/.venv/bin/python3 Infrastructure/scripts/lib/ask/skills_sdk/stabilization_identity.py --repo-root . <declared stable path set>` -> pass (`sha256:ad529c8855cdc8fed3bbb36daa78cdb2b1308c15422c486b865d674d6264011b`; supersedes the earlier identity after security repair)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_projection_integrity_plugin_cache.py -q` -> pass (7 passed, 5 subtests; outside directory/file, absolute, parent escape, and broken links fail closed with no projection; contained link succeeds)
- Command: `PYTHONPATH=Infrastructure/scripts/lib Infrastructure/.venv/bin/python3 Infrastructure/scripts/lib/ask/skills_sdk/stabilization_identity.py --repo-root . <declared stable path set>` -> pass (`sha256:8cc674b799d325aaa1031b2e87568282413b50922b5b2f62cb4c99e4b2a197b9`; supersedes the third-repair identity)
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests -q` -> blocked (collection error: `.skillsets/command-surface.json has no handle source_revision values`)
- Command: `./bin/ask repo closeout --changed --json --robot` -> blocked (isolated worktree workspace skill runtime projection is intentionally unsynced; no runtime projection mutation was authorized)

## Diagnostic debt and warnings

- Raw full-suite collection is blocked by obsolete generated command-surface metadata; the canonical Skills SDK gate passes and the stale tests were not edited.
- The public capability receipt intentionally remains `proof_mode: inventory_only`; the private replay receipt closes this stabilization proof lane without changing public behavior.
- The repeated mise tracked-config warning is environmental and did not fail focused tests.

## Rollback

Revert only the six implementation/test files in this dedicated worktree.
No live plugin cache, home runtime, primary dirty checkout, network service, or
external system was mutated.

## Excluded primary dirty state

The primary checkout and its existing `.gitignore`/untracked report state were
not edited or included.

## Not proven

Observed absence of network/filesystem mutation inside allowlisted command implementations,
raw full-suite collection, fresh QA acceptance,
Tessl, CircleCI, runtime migration, repository extraction, publication, and
retirement are not proven.

## Artifact accountability

- Receipt: `.harness/evidence/skills-sdk-stabilization/stabilization-baseline-receipt.json`
- Inventory: `.harness/evidence/skills-sdk-stabilization/command-service-rationalization-inventory.md`
- Private replay: `.harness/evidence/skills-sdk-stabilization/private-command-replay.json`
- Manifest: `artifacts/agent-runs/default-20260711T120000Z/manifest.json`

WROTE: /private/tmp/agent-skills-skills-sdk-stabilization/.harness/reports/worker-skills-sdk-stabilization.md
