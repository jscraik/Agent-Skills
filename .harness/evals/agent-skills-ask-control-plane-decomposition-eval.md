---
schema_version: 1
artifact_id: agent-skills-ask-control-plane-decomposition-eval
artifact_type: he-eval-report
type: he-eval-report
canonical_slug: agent-skills-ask-control-plane-decomposition
title: Agent Skills Ask Control Plane Decomposition Eval
harness_stage: he-eval-report
status: plan_ask_005_complete_linear_resolved
date: 2026-05-08
traceability_required: true
origin: .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
linear_issue: JSC-284
linear_status: complete
linear_milestone: Command surface and ask reliability
---

# Agent Skills Ask Control Plane Decomposition Eval

## Status

`plan_ask_005_complete_linear_resolved`

Focused blocker repair, repo-wide doctor cleanup, and the `PLAN-ASK-003`
plugin-cache service extraction are complete and reviewed. `PLAN-ASK-004` has
produced the proof taxonomy ADR and completed its required end-of-phase
simplify, he-fix-bugs, and he-code-review loop. `PLAN-ASK-005` closure evidence
is complete locally. Live Linear refresh later succeeded through issue fetches,
closure proof was posted to `JSC-284`, and `JSC-284` through `JSC-287` are Done.

## Scope

- Plan: `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
- Linear parent: `JSC-284`
- Current slice: `PLAN-ASK-005` closure eval and traceability
- Code movement into extracted services: complete and reviewed
- Decision artifact: `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-284` |
| Child issues | `JSC-285`, `JSC-286`, `JSC-287` |
| Project | `agent-skills` |
| Milestone | `Command surface and ask reliability` |
| Status | Done |
| Closure proof | Linear comment `a54b9452-af8c-4498-bbba-ed61f92bd773` |

## Live Linear Refresh

Resolved.

- Earlier attempt: `mcp__codex_apps__linear._research` returned `INVALID_ARGUMENT`
  with MCP error `Tool research not found`.
- Resolution: `mcp__codex_apps__linear._fetch` verified `JSC-284`, `JSC-285`,
  `JSC-286`, and `JSC-287` as `Done`.
- Closure mutation: `JSC-285`, `JSC-286`, `JSC-287`, then `JSC-284` were moved to
  `Done`.
- Closure proof: comment `a54b9452-af8c-4498-bbba-ed61f92bd773` posted to
  `JSC-284`.
- Plan handling: `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
  now records `linear_status: linear_resolved_done` and
  `linear_delta_status: resolved_live_fetch_done`.

## Responsibility Map

| Current surface | Current file | Intended future home | Movement status |
| --- | --- | --- | --- |
| Skill listing, resolution, sync orchestration | `Infrastructure/scripts/lib/ask/commands/skills.py` | keep command adapter thin; extract domain services only after gates pass | command adapter still owns orchestration |
| Catalog projection refresh | `Infrastructure/scripts/lib/ask/commands/skills.py` | catalog/projection service | not started |
| Local plugin cache replacement and command-handle duplicate pruning | `Infrastructure/scripts/lib/ask/services/plugin_cache.py` | plugin-cache service | extracted |
| Shared local plugin marketplace/copy/materialization helpers | `Infrastructure/scripts/lib/ask/services/plugin_sources.py` | neutral plugin source helper service | extracted |
| Home plugin source mirror refresh | `Infrastructure/scripts/lib/ask/commands/skills.py` plus `plugin_sources.py` helpers | plugin mirror service or plugin-cache-adjacent service | behavior fixed; orchestration not extracted |
| Command-handle ownership and reports | `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` | remain canonical command-surface source | not moved |

## Bug Fixed Before Refactor

### Home plugin mirror pruned copied source skills

Fact:

- `test_sync_skills_user_scope_replaces_local_plugin_mirror_copies` reproduced a
  missing `home/plugins/harness-engineering/skills/he-heartbeat/SKILL.md` after
  user-scope sync.
- `_refresh_home_plugin_mirrors` copied the plugin source and then called
  `_prune_command_handle_skill_entries`, which is intended for runtime cache
  duplicate prevention.

Interpretation:

- `~/plugins/<plugin>` is a source mirror for marketplace `source.path`
  resolution, not a runtime picker cache. Pruning command-handle-owned skills
  from that mirror makes the copied plugin incomplete.

Patch:

- Removed command-handle duplicate pruning from `_refresh_home_plugin_mirrors`.
- Left pruning behavior intact for `_replace_plugin_cache_copy`, which handles
  repo-local runtime cache copies.

### Local plugin picker expected surface was stale

Fact:

- `Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md` exists.
- `.skillsets/harness-engineering/manifest.jsonl` contains `he-phase-heartbeat`.
- `test_local_plugins_expose_all_expected_skills_at_first_level` failed because
  `EXPECTED_SOURCE_PLUGIN_SKILLS["harness-engineering"]` did not include it.

Patch:

- Added `he-phase-heartbeat` to the expected harness-engineering plugin source
  skill set in `Infrastructure/tests/test_local_plugin_picker_surface.py`.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `./bin/ask skills resolve he-work --json` | pass | Resolved canonical `Plugins/harness-engineering/skills/he-work/SKILL.md`. |
| `./bin/ask skills resolve he-spec --json` | pass | Resolved canonical `Plugins/harness-engineering/skills/he-spec/SKILL.md`; latest closure trace `4935af2f-98d2-4811-9dd0-7519366143b7`. |
| `./bin/ask skills list --json` | pass | Runtime list readable; policy identity `8c69fbfa81b89658`; latest closure trace `8dc6a05a-92f3-47c9-b937-b1c43604fd8b`. |
| `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json` | pass | Rooted projection dry-run validation passed after extraction and review fixes; 219 planned writes, 6 planned deletes, 1 symlink; command surface has 95 handles; latest closure trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`. |
| `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q` | pass | 9 passed after expected-surface updates for `he-phase-heartbeat` and `he-eval-report`, plus `he-eval-report` OpenAI metadata. |
| `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q` | pass | 25 passed in 3.77s after home mirror pruning fix. |
| `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py Infrastructure/tests/test_ask_skills_sync_security.py Infrastructure/tests/test_skill_scope_precedence.py -q` | pass | 41 passed in 3.78s after service extraction and review fixes. |
| `PYTHONPATH=Infrastructure/scripts/lib python3 -c "import ask.services.plugin_cache; print('ok')"` | pass | Direct service import works without relying on `commands/skills.py` path side effects. |
| `bash -lc '! rg -n -e "ask\\.commands" -e "from ask\\.commands" -e "import .*commands" Infrastructure/scripts/lib/ask/services >/dev/null'` | pass | No matches found; check expects `rg` no-match behavior and returns a passing assertion. |
| `python3 -m py_compile Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/scripts/lib/ask/commands/plugins.py Infrastructure/scripts/lib/ask/services/plugin_cache.py Infrastructure/scripts/lib/ask/services/plugin_sources.py Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py` | pass | Python compile check passed for changed command/service modules and runtime-budget validator. |
| `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` | pass | Latest run after plan/eval updates: `scanned_files=177 errors=0 warnings=0`. |
| `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md` | pass | Traceability lint passes for the spec artifact. |
| `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md` | pass | Traceability lint passes for the plan artifact. |
| `rg -n "structural audit is not outcome proof\|selection policy changes\|default-visible promotion gates\|reachability\|structural\|quality\|outcome\|experimental\|latent\|structurally-valid\|reachable\|outcome-proven\|trusted\|default-visible\|deprecated" .harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md` | pass | ADR contains required proof levels, lifecycle states, and non-enforcement language. |
| `./bin/ask repo doctor-catalog --json --robot` | pass | Catalog parity resolved; canonical count 21. |
| `./bin/ask runtime budget --json --robot` | pass | Runtime budget within policy; curated `agents-sdk` collision explicitly baselined and no unresolved scope collisions remain. |
| `./bin/ask repo doctor --json --robot` | pass | `blocking: false`; catalog parity, runtime budget, projection sync, and command handles pass. Latest closure trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e`. Repo surface retains non-blocking diagnostic debt. |

## End-of-Phase Review Loop

| Review lane | Result | Action taken |
| --- | --- | --- |
| `simplify` | One medium simplification finding: the curated `agents-sdk` runtime-budget baseline used exact version/hash paths and would drift on plugin cache version changes. | Fixed by normalizing curated cache collision keys to `Plugins/cache/openai-curated/<plugin>/skills/<skill>` and adding rotating-version regression coverage. |
| `he-fix-bugs` | No blocking bug/regression findings. Residual test-gap note: home mirror and plugin source helper behavior should remain covered through sync integration tests. | Preserved `test_ask_skills_sync_security.py` coverage that verifies copied source skills remain present after sync, including `he-heartbeat`. |
| `he-code-review` | Two medium findings: plan/eval Linear status contradiction and fragile runtime-budget baseline path matching. | Fixed the initial plan/eval status contradiction, then superseded it after live Linear fetches resolved closure; fixed runtime-budget baseline normalization and regression tests. |

## PLAN-ASK-004 Proof Taxonomy ADR

| Requirement | Evidence | Status |
| --- | --- | --- |
| ADR exists and is linked from this eval | `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md` | complete |
| Defines proof levels | ADR defines `reachability`, `structural`, `quality`, and `outcome` | complete |
| Defines lifecycle states | ADR defines `experimental`, `latent`, `structurally-valid`, `reachable`, `outcome-proven`, `trusted`, `default-visible`, and `deprecated` | complete |
| Says structural audit is not outcome proof | ADR explicitly states structural audit is not outcome proof | complete |
| Keeps enforcement outside this slice | ADR excludes selection policy changes, command behavior changes, promotion gates, proof schema changes, metadata migration, and global glossary edits | complete |
| Checks terms against `UBIQUITOUS_LANGUAGE.md` | Existing glossary covers canonical source, runtime projection, generated command handle, visible runtime surface, advanced repo discovery, strict audit, and policy identity; new proof terms are kept ADR-local | complete |

## PLAN-ASK-004 End-of-Phase Review Loop

| Review lane | Result | Action taken |
| --- | --- | --- |
| `simplify` | No actionable simplification finding. The ADR is short, uses one taxonomy table and one lifecycle table, and does not duplicate the global glossary. Subagent dispatch was attempted but returned only an instruction acknowledgment, so it is not counted as review evidence. | No patch required. |
| `he-fix-bugs` | No blocker found. Required acceptance terms are present; the ADR does not mutate `UBIQUITOUS_LANGUAGE.md`, command behavior, selection policy, or promotion gates. Subagent dispatch was attempted but returned only an instruction acknowledgment, so it is not counted as review evidence. | No patch required. |
| `he-code-review` | No readiness blocker found. Traceability is coherent: `JSC-287` -> `SA-ASK-007` -> `PLAN-ASK-004` -> ADR/eval evidence. Linear closure completed (see Lines 52–61: live fetch and closure mutation completed). | No patch required. |

## Resolved Blockers

### Catalog parity drift

- Former severity: blocker
- Resolution: projection-refresh lane regenerated the catalog/runtime surfaces.
- Evidence: `repo doctor-catalog` passes with canonical count `21`.
- Projection churn reviewed: tracked changes are limited to `SKILL.md` and
  `.skillsets/**`; runtime projection/cache churn was generated by the repo
  sync lane, not hand-edited source.

### Runtime budget scope collision

- Former severity: blocker
- Resolution: explicitly baselined only the curated `agents-sdk` same-scope
  collision.
- Collision:
  - `Plugins/cache/openai-curated/cloudflare/6807e4de/skills/agents-sdk`
  - `Plugins/cache/openai-curated/openai-developers/f812c146/skills/agents-sdk`
- Evidence: `runtime budget` passes with no `unresolved_scope_collisions`; the
  curated pair is reported as `baselined_scope_collisions`.
- Guardrail: unrelated same-scope collisions still fail runtime-budget
  validation.

## Decomposition Gate Decision

`PLAN-ASK-003` implementation, `PLAN-ASK-004` proof ADR, and `PLAN-ASK-005`
local closure eval are complete.

Current baseline after service extraction:

1. `./bin/ask skills resolve he-spec --json` passes; trace
   `4935af2f-98d2-4811-9dd0-7519366143b7`.
2. `./bin/ask skills list --json` passes; trace
   `8dc6a05a-92f3-47c9-b937-b1c43604fd8b`.
3. `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`
   passes; trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`. Preserves
   `plugin_cache_writes`, `logs`, `validation_status: pass`, command surface
   `95` handles, and mutation counts `219` writes, `6` deletes, `1` symlink.
4. `./bin/ask repo doctor --json --robot` passes with `blocking: false`; trace
   `5954fd8e-642d-4fc6-8d9b-b723cff7269e`.

## PLAN-ASK-005 Closure Traceability

| Closure requirement | Evidence | Status |
| --- | --- | --- |
| Responsibility map present | `Responsibility Map` section maps command adapter, plugin cache service, plugin source helpers, home mirror behavior, and command-surface ownership. | complete |
| Before/after command evidence present | `Validation` and `Decomposition Gate Decision` sections record current command traces and preserved fields. Earlier baseline traces are retained in this artifact history and plan gate notes. | complete |
| Changed files list present | `Changed Files For This Slice` below records HE-slice files separately from broader dirty worktree surfaces. | complete |
| Plugin cache field/log comparison present | `Decomposition Gate Decision` records preserved `plugin_cache_writes`, `logs`, `validation_status`, command handles, and mutation counts. | complete |
| Repo doctor blocker classification present | Validation records `blocking: false` with repo-surface diagnostic debt classified as non-blocking. | complete |
| Rollback conditions checked | No rollback condition hit for PLAN-ASK-003, PLAN-ASK-004, or PLAN-ASK-005. Linear closure completed (see Lines 52–61: live fetch and closure mutation completed). | complete |
| Linear traceability table present | `Linear Traceability` below maps `JSC-284` through `JSC-287` to plan units and evidence. | complete |
| Later extraction phases not started | Catalog/projection extraction, proof enforcement, routing/improvement extraction, and tool-resolution extraction remain out of scope and were not started. | complete |

## Changed Files For This Slice

HE-slice files intentionally changed or created:

- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
- `Infrastructure/scripts/lib/ask/commands/plugins.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lib/ask/services/__init__.py`
- `Infrastructure/scripts/lib/ask/services/plugin_cache.py`
- `Infrastructure/scripts/lib/ask/services/plugin_sources.py`
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
- `Infrastructure/tests/test_local_plugin_picker_surface.py`
- `Infrastructure/tests/test_ask_skills_sync_security.py`
- `Infrastructure/tests/test_skill_scope_precedence.py`
- `Plugins/harness-engineering/skills/he-eval-report/agents/openai.yaml`

Projection/generated or broader pre-existing dirty surfaces are present in the
worktree and must be reviewed separately before any commit staging. This eval
does not claim ownership of unrelated `.harness/linear`, `.harness/review`,
`.harness/specs`, `.skillsets/**`, `SKILL.md`, route-skillset, or plugin-doc
churn unless the final commit stage explicitly selects them.

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs |
| --- | --- |
| `JSC-284` | `SA-ASK-001` through `SA-ASK-015` |
| `JSC-285` | `SA-ASK-001`, `SA-ASK-002`, `SA-ASK-010` |
| `JSC-286` | `SA-ASK-003`, `SA-ASK-004`, `SA-ASK-005`, `SA-ASK-006`, `SA-ASK-009`, `SA-ASK-010`, `SA-ASK-011`, `SA-ASK-012`, `SA-ASK-013` |
| `JSC-287` | `SA-ASK-007` |

## Linear Traceability

| Linear issue | Local evidence | Closure status |
| --- | --- | --- |
| `JSC-284` | Parent slice has PLAN-ASK-001 through PLAN-ASK-005 evidence in this eval and plan. | Done in Linear |
| `JSC-285` | Responsibility map and baseline gate evidence recorded. | Done in Linear |
| `JSC-286` | Plugin-cache service extraction, focused tests, dry-run parity, and review-loop fixes recorded. | Done in Linear |
| `JSC-287` | Proof taxonomy ADR exists and PLAN-ASK-004 review loop recorded. | Done in Linear |

## Rollback Conditions

No rollback condition was hit for the local plan units.

- No unexpected robot JSON drift was observed in the closure gate.
- Plugin cache root layout and dry-run fields remained stable.
- Service-layer command imports were checked with `rg` and remain absent.
- Later extraction phases did not start.
- Linear status mutation happened only after live issue fetches verified tracker
  identity and state.

## Next Gate

Local closure evidence and Linear closure are complete. The next gate is
selected-file review before any final local commit that claims tracker closure.

## Commit Status

No commit created.

Reason:

- The user has not requested a local commit for this phase in the active turn.
- Linear closure is complete, but no local commit was requested in the active
  turn and the worktree still contains broader generated/projection churn.
