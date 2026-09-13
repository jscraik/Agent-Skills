---
schema_version: 1
plan_id: agents-guidance-reconciliation-20260912
status: complete
owner: agent-skills
---

# Reconcile agent instruction guidance

This plan fixes seven reviewed instruction defects so agents can finish authorized
work without obsolete approval steps, registry dependencies, or misleading
validation commands. Changes stay in repository guidance, the agents-md package,
and the existing PM report validator and tests. Existing unrelated edits remain
untouched. Failed checks remain visible before the final handoff.

## Source and scope

Source: Jamie's September 12 review and explicit request to implement all seven
findings. Official model guidance:
https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices

Baseline: `51309064aebf7b087d16b03537855bce6de8850e`, branch
`codex/telos-runtime-owner`, with 50 pre-existing changed entries.
No remote, runtime installation, global configuration, or unrelated source edits.
The current global policy remains the authority; this work repairs its local
references rather than copying it into every AGENTS file.

## Context ledger and checklist

| ID | Owner and consumer | Change and acceptance |
| --- | --- | --- |
| F1 | Docs instruction router and role guide | Resolve precedence before asking; authorized policy edits need no duplicate confirmation. |
| F2 | Tooling guide; shell users | Use the configured non-login shell and explicit Bash scripts. |
| F3 | agents-md guidance; generated instruction drafts | Artifacts and probe agents are conditional on the selected contract or uncertain runtime health. |
| F4 | agents-md fallback; repos without local style | Route to the verified CODESTYLE.md file, not its sibling directory. |
| F5 | Testing guide; local validation callers | Run checks selected by the change; synchronize only within an authorized projection scope; distinguish audit from repair. |
| F6 | Validation and testing guides; reviewers | Select uncommitted, base, or commit review scope to cover the actual candidate. |
| F7 | PM guide and report validator; report authors | Preserve v1 selection evidence without consulting the retired home role registry. |

- [x] PU-1: Implement F1, F2, F5, F6 in linked guidance.
- [x] PU-2: Implement F3 and F4 in agents-md and affected eval cases.
- [x] PU-3: Update F7 validator, docs, and test producers; prove accepted and rejected inputs through the public validator and CLI.
- [x] PU-4: Run focused tests, instruction-pointer checks, skill checks, and applicable aggregate validation.
- [x] PU-5: Record outcomes, remaining blockers, and the bounded sibling sweep.

## Validation strategy

Run the PM report regression through the public validator and CLI, using isolated
fixtures. Run the PM delivery tests to retain delivery gates. Inspect review help
and sync help rather than invoking reviews or modifying runtime projections.
Run strict source audit, Plugin Eval, and affected release cases for agents-md;
report unavailable runtime/model execution separately. Use repository docs/prose
and aggregate checks without repairing unrelated dirty-worktree failures.

## Rollback and stop conditions

Rollback only this task's hunks; preserve earlier changes in shared files. Stop
affected actions for a permission denial, an unresolved ownership collision, or
an unavailable required check. Do not waive validation, substitute a source check
for runtime proof, or reduce the seven-finding scope. No commit or remote action
is needed for this local handoff.

## Evidence

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest tests/test_thread_report_dispatch_guards.py scripts/testing/test_validate_thread_pm_delivery.py -q`
-> pass (19 tests, 32 subtests). Fixtures isolate required repo files; the
validator accepts selection evidence without home lookup and rejects missing,
placeholder, empty, and incorrectly typed selection fields. CLI tests exercise
exit codes and JSON results. No pre-patch red run was captured.

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m ruff check scripts/validation-and-linting/validate_thread_report.py tests/test_thread_report_dispatch_guards.py scripts/testing/test_validate_thread_pm_delivery.py`
-> pass.

Command: `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
-> pass (209 files, zero errors after fixing two introduced relative links).

Command: `codex review --help` -> pass; confirms uncommitted, base, and commit scopes.
Command: `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh --help`
-> pass; confirms workspace scope and projection/index mutation.
Command: `git diff --check` -> pass.

Command: `./bin/ask skills audit Skills/agent-ops/agents-md --level strict --source-only --json --robot`
-> pass, with an existing stale-rubric warning. Source-only proof does not prove
model behavior or runtime promotion.
Command: `./bin/plugin-eval analyze Skills/agent-ops/agents-md --format json`
-> pass (A, score 100, zero failures; static analysis, no observed usage).

Concurrent writer completed: the other task supplied the F3/F4 source fixes,
corrected fallback eval, mailbox eval, and model-documentation audit route.
Those changes were verified before this task resumed package repair. This task
preserved that work and added the missing claims, case-specific expected
behavior, analytic quality rubric, and canonical heading structure.

Aggregate command: `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`.
First run failed on introduced link errors (now fixed), overdue aidevcon review
cadence, and unrelated plugin projection drift. The preflight also reports a
local Harness 0.15.0 versus required 0.15.3 mismatch as advisory. A second run
finished with two unrelated failures: aidevcon review cadence and plugin
projection drift. Its docs lint passed. No sync, dependency install, or
review-date renewal is authorized by those failures. Later ledger edits were
validated separately; this aggregate run does not prove those later edits.

Command: `vale --minAlertLevel error Skills/agent-ops/agents-md/references/agents-md-guidance.md Docs/agents/README.md Docs/agents/07a-role-governance.md Docs/agents/02-tooling-policy.md Docs/agents/04-validation.md Docs/agents/10-agent-testing-gates.md Docs/agents/26-pm-thread-coordination.md .harness/plan/2026-09-12-agents-guidance-reconciliation.md`
-> pass (zero findings across eight files).

## September 12 follow-up repair

Factory decision: IMPROVE_EXISTING. The outcome is verified instruction
guidance; the rejected assumption is that source changes or static scores alone
prove model behavior. Repair existing package contracts and evals, preserve the
dirty worktree, and require focused behavioral evidence. Do not create a new
skill or promote runtime or hosted readiness from local results.

Command: `./bin/ask skills package verify Skills/agent-ops/agents-md --json --robot`
-> pass after adding claims, case-specific expected behavior, the quality
rubric, and canonical H2 routing. Initial failures exposed those omissions.

Command: `python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json`
-> pass; refreshed generated source hashes from canonical packages.

Command: `bash Infrastructure/scripts/lifecycle-and-sync/sync_projection_trees.sh plugin-caches --format json`
-> pass with bounded host approval after sandbox denial. The previous three
repository-local plugin mirrors were archived at
`/private/tmp/agents-guidance-plugin-mirrors-20260912T1858.tgz` before replacement.
Command: `python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope plugin-caches --format text`
-> pass for all three mirrors. No user-home install or config mutation occurred.

Command: `python3 Plugins/plugin-factory/scripts/plugin-builder/plugin_builder.pyw validate Plugins/aidevcon`
-> pass. Monthly review checked manifest ownership and paths, README package
identity, all bundled outline/quote/transcript files for non-empty presence, and
the harness-engineering talk skill's grounding and inert-source rules. No
hook, MCP, app, Python, or shell implementation files were found. Retained
incubating/experimental and UNLICENSED status; renewed last_reviewed only after
this bounded package review. This is not a complete transcript accuracy,
copyright, upstream freshness, or installed runtime review.

Behavioral evals: sandbox network access failed even after a network grant;
bounded host approval enabled execution. The five-case 60-second suite timed
out without final output. A 180-second single-case retry passed
`edge-codestyle-global-fallback`; subsequent outcomes are recorded below.
Evidence: `.tmp/agent-skills-artifacts/skills/agents-md/20260912-195543-730999/workflow-closeout.json`.

The post-repair aggregate run completed with one failure: the unrelated dirty
`Skills/agent-ops/alignment-checkpoint/SKILL.md` lacks `## Gotchas`. Catalog,
context budget, projection integrity, family/schema, Python design, and runtime
separation checks all passed. No edits were made to alignment-checkpoint.
Log root: `/var/folders/tl/6bt8_lsn31b2j3sc_q5yr05c0000gn/T/agent-skills-validate-all.RAyTOM`.

Command: `./bin/ask evals run Skills/agent-ops/agents-md --mode release --case edge-codestyle-global-fallback --skip-tessl --timeout-seconds 180 --no-dashboard --json --robot`
-> pass (one case).

Command: `./bin/ask evals run Skills/agent-ops/agents-md --mode release --case edge-subagent-contract-full --case edge-subagent-mailbox-contract --case edge-model-documentation-audit --case edge-missing-exact-model-docs --skip-tessl --timeout-seconds 240 --no-dashboard --json --robot`
-> blocked (mailbox passed; three cases hit the default 60-second per-case
limit). Evidence: `.tmp/agent-skills-artifacts/skills/agents-md/20260912-195750-529395/workflow-closeout.json`.

Command: `./bin/ask evals run Skills/agent-ops/agents-md --mode release --case edge-subagent-contract-full --case edge-model-documentation-audit --case edge-missing-exact-model-docs --skip-tessl --timeout-seconds 600 --no-dashboard --json --robot`
-> fail (artifact contract and missing exact-model docs passed; semantic audit
hit a scorer false negative). Evidence:
`.tmp/agent-skills-artifacts/skills/agents-md/20260912-200134-036198/workflow-closeout.json`.
The observed response correctly stated that diff checks cannot validate
unchanged committed instructions. The scorer recognized only uncommitted or
diff-only wording. Added diff-check/staged synonyms; a managed-Python regex
probe accepted the actual response and rejected two answers without coverage
analysis. Three inspection-heavy cases now declare timeout_sec 180; acceptance
requirements and model selection remain unchanged.

Command: `./bin/ask skills audit Skills/agent-ops/agents-md --level strict --source-only --json --robot`
-> pass after correcting claim-schema source, claim_type, and evidence fields.
The historical task-profile rubric remains an advisory warning, not a changed
or renewed calibration claim.
Command: `./bin/plugin-eval analyze Skills/agent-ops/agents-md --format json`
-> pass (A/100, zero failures).
Command: `python3 Infrastructure/scripts/lifecycle-and-sync/route_skillset.py --skill-set skill-factory --task 'Repair skill package quality and audit evals' --json`
-> pass (skill-builder selected).
Command: `python3 Infrastructure/scripts/validation-and-linting/check_plugin_active_archive_links.py`
-> pass.
Command: `python3 Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py`
-> pass.
Command: `python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection flat --json`
-> pass.

Command: `./bin/ask evals run Skills/agent-ops/agents-md --mode release --case edge-model-documentation-audit --skip-tessl --timeout-seconds 240 --no-dashboard --json --robot`
-> pass after scorer repair. Evidence:
`.tmp/agent-skills-artifacts/skills/agents-md/20260912-200630-055287/workflow-closeout.json`.

All five targeted behavioral cases have passing evidence across the focused
runs. This is not an all-case release-suite pass: only the five affected
behavioral cases were run, and static contract fields were checked for all 24
cases. Tessl distribution, publication, and user-home installation were not
selected.

## Alignment-checkpoint heading follow-up

Jamie explicitly authorized the remaining heading repair. Moved the unchanged
warning that a checkpoint is not implementation or deployment proof from
Validation into Gotchas. Preserved all other existing changes and refreshed
generated manifests with the owning generator.

Command: `bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict`
-> pass (107 files, zero errors, three existing advisory warnings).
Command: `vale --minAlertLevel error Skills/agent-ops/alignment-checkpoint/SKILL.md`
-> pass.
Command: `./bin/ask skills audit Skills/agent-ops/alignment-checkpoint --level strict --source-only --json --robot`
-> pass (existing realism and stale-rubric warnings remain advisory).
Command: `./bin/ask skills package verify Skills/agent-ops/alignment-checkpoint --json --robot`
-> pass before and after relocation.
Command: `python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json`
-> pass.
Command: `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
-> pass, zero required failures and zero warn-only issues. The preflight's
installed Harness version advisory remains separate. Successful ephemeral
aggregate logs are automatically removed by the wrapper.

Command: `./bin/ask evals run Skills/agent-ops/alignment-checkpoint --mode release --case happy-explicit --case edge-validation --skip-tessl --timeout-seconds 180 --no-dashboard --json --robot`
-> fail: happy-explicit passed; edge-validation reported unexpected selection.
The negative response continued ordinary validation without a checkpoint and
linked the repaired skill file. The detector uses broad skill-name/path text
matching, so this is an apparent selection-detector false positive, not proof
that the checkpoint behavior activated. No evaluator code was changed.
Evidence: `.tmp/agent-skills-artifacts/skills/alignment-checkpoint/20260912-201145-103462/workflow-closeout.json`.

The heading blocker is resolved. The detector follow-up below closes the
remaining local validation finding; no all-evals or release-readiness claim is
made.

## Selection detector follow-up

Jamie explicitly authorized fixing the negative-case false positive. The
detector now ignores diagnostic/tool-output skill mentions, reads assistant
message events instead of serialized event blobs, and requires exact structured
skill identity. Activation wording cannot match a skill-file path or a longer
skill name; applying a supplied skill remains a valid activation statement.
No positive evidence remains unknown rather than being labeled activation.
The negative case has a bounded 180-second timeout for repository inspection.

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh ../Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals_assertions.py`
-> fail before repair (file/tool mentions and similar-name identities were
misclassified), then pass (four tests including positive/negative subcases).
Additional path/similar-name regressions also failed before their boundary fix
and passed afterward.
Command: `bash Infrastructure/scripts/run-infrastructure-python.sh ../Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals_runner_selection.py`
-> pass (one test).
The original failed response and JSONL artifacts were replayed through the
public detector and negative assertion; pass, selection unknown and no false
activation failure. The tests preserve real explicit and structured activation.

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m ruff check ../Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals_assertions.py`
-> pass. Direct Ruff checking of the existing assertions module fails on F405
wildcard-import findings: 143 at HEAD versus 140 after repair. No suppression
or unrelated import refactor was added. The aggregate program-design gate passes.
The initial pytest invocation could not collect this plugin test path; direct
execution uses the file's existing unittest entrypoint.

Command: `./bin/ask evals run Skills/agent-ops/alignment-checkpoint --mode release --case happy-explicit --case edge-validation --skip-tessl --timeout-seconds 300 --no-dashboard --json --robot`
-> pass, both cases. Evidence:
`.tmp/agent-skills-artifacts/skills/alignment-checkpoint/20260912-202002-146303/workflow-closeout.json`.
The preceding attempt exposed the unsupported applying phrase and a negative
case timeout; those were repaired without weakening selection assertions.

Command: `bash Infrastructure/scripts/lifecycle-and-sync/sync_projection_trees.sh plugin-caches --format text`
-> pass with bounded host approval after canonical source changes.
Command: `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
-> pass after the final detector adjustment, zero required failures and zero
warn-only issues. All selected local repairs and focused acceptance checks are
complete. Runtime/release lanes remain separate. The direct-Ruff debt was
subsequently repaired below.

## Explicit-import cleanup

Jamie authorized the remaining wildcard-import lint cleanup. Replaced the
assertion module's wildcard import with explicit dependencies. A module-level
attribute forwarder preserves the existing core re-export interface used by
the runner; missing names still raise AttributeError. No detector semantics
or eval expectations changed.

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m ruff check ../Plugins/skill-factory/scripts/skill-builder/run_skill_evals_assertions.py ../Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals_assertions.py`
-> pass, zero findings (previously 140 F405 findings in the assertion module).
Command: `bash Infrastructure/scripts/run-infrastructure-python.sh ../Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals_assertions.py`
-> pass, five tests; covers detector behavior and every existing core re-export
identity plus unknown-name rejection.
Command: `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
-> pass after explicit-import cleanup, zero required failures and zero
warn-only issues.
Command: `bash Infrastructure/scripts/run-infrastructure-python.sh ../Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals_runner_selection.py`
-> pass, one test.
Command: `./bin/ask evals run --help` -> pass through the public CLI.
Command: `bash Infrastructure/scripts/lifecycle-and-sync/sync_projection_trees.sh plugin-caches --format text`
-> pass with bounded host approval.
