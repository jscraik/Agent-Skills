---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-1-plan-technical-review
artifact_type: he-code-review
canonical_slug: agent-skills-first-principles-factory-gate-phase-1-plan
title: First-Principles Factory Gate Phase 1 Plan Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-09
traceability_required: false
target: .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md
risk: medium
ui: false
---

# First-Principles Factory Gate Phase 1 Plan Technical Review

## Review Scope

Target reviewed:

- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`

Supporting evidence checked:

- `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec.md`
- `.harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-technical-review.md`
- `.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`
- `.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md`
- `../codex/codex-rs/hooks/src/schema.rs`
- `../codex/codex-rs/hooks/src/engine/output_parser.rs`
- `../codex/codex-rs/core-plugins/src/loader.rs`
- `../codex/codex-rs/core-plugins/src/manifest.rs`
- `../codex/codex-rs/hooks/src/engine/mod_tests.rs`

This review checks whether the deepened plan is technically executable as a
Phase 1 implementation contract. It does not approve Phase 2 schema work,
Phase 3 validator work, Phase 4 MCP/app/eval work, or Linear mutation.

## Findings

No P0, P1, or P2 blockers found.

### Resolved P2-001: Hook output needed Codex schema proof, not only JSON proof

Initial plan wording said the hook scripts should preserve their current JSON
output shape and focused tests should assert `additionalContext`. Cross-checking
the live Codex hook parser showed that `SessionStartHookSpecificOutputWire`
requires `hookSpecificOutput.hookEventName` before the runtime can parse the
same object and extract `additionalContext`.

Fix applied to the plan: Phase 1 now requires both factory hook scripts to emit
`hookSpecificOutput.hookEventName: "SessionStart"` and requires the focused test
to assert that field. This keeps the change inside Phase 1 because it corrects
the existing `SessionStart` hook runtime contract rather than adding a new
feature.

### P3-001: Router behavior remains partly human-reviewed

The plan correctly treats router changes as instruction-surface changes rather
than executable route logic. The remaining loophole is that a future edit could
weaken router wording while focused hook tests still pass. The deepened plan
mitigates this by making manual router diff inspection required closeout
evidence and by carrying shared fragments into the hook tests.

Remediation status: accepted for Phase 1. Add executable router behavior tests
only if a later phase introduces a machine-readable routing contract.

### P3-002: Focused tests prove hook context, not full factory quality

The focused hook contract test can prove that bundled hooks emit the new
first-principles context and preserve existing context. It cannot prove that
future skills/plugins are materially better. The plan names this boundary and
keeps the missing eval artifact as future readiness work.

Remediation status: accepted for Phase 1. The later eval artifact should cover
before/after output quality and artifact-selection behavior.

### P3-003: Broad validation may report unrelated repository warnings

The changed-file authoring-family gate can surface existing warnings or
unrelated dirty-tree issues. The plan mitigates this by running focused tests
first and requiring exact blocker text if broad validation fails for unrelated
reasons.

Remediation status: accepted. Do not expand Phase 1 to fix unrelated warnings
unless they directly invalidate the changed files.

## Loopholes Checked

| Loophole | Result |
| --- | --- |
| Plan accidentally enables or assumes `plugin_hooks` globally | Not present. The plan relies on direct script execution for tests and advisory hook context only. |
| Plan turns Phase 1 into schema or validator enforcement | Not present. Schema, strict/warn validation, and eval enforcement are explicitly deferred. |
| Plan edits generated projections or runtime mirrors | Not present. `.agents/**` and `.skillsets/**` are explicitly out of scope. |
| Plan loses existing factory hook context | Mitigated. Focused tests must assert old routing and hook-contract fragments remain. |
| Plan claims full factory-governor readiness | Not present. Completion definition preserves the missing eval artifact as future readiness work. |
| Plan leaves implementation wording too ambiguous | Mitigated by file-level wording targets and hook/test fragment contracts. |
| Plan tests JSON that Codex runtime would reject | Fixed. Plan now requires `hookSpecificOutput.hookEventName: "SessionStart"`, matching live Codex schema/parser behavior. |
| Plan requires network or external service access | Not present. Planned commands are local repository validation commands. |
| Plan creates Linear state drift | Not present. Linear mutation is explicitly out of scope. |

## Technical Verdict

Pass for `he-work` Phase 1 implementation.

The plan is now specific enough for a small source change: add one compact gate
to each factory router, mirror it in the existing bundled `SessionStart` hook
context, make the hook output match the live Codex `SessionStart` schema, extend
the focused hook contract test, and validate locally. The plan does not close
the full first-principles factory-governor initiative; it deliberately leaves
schema, enforcement, MCP/app surfaces, and eval proof to later phases.

## Required Closeout Evidence

The implementation closeout should report exact outcomes for:

```bash
python3 -m py_compile \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py

python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q

git diff --check

bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  Plugins/skill-factory/skills/skill-factory-router/SKILL.md \
  Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py
```

It should also state whether any extra files appeared in `git diff --name-only`
and whether they are unrelated dirty work or Phase 2 drift.

## Confidence Loop Result

This review was re-run after the Codex source cross-check exposed the missing
`hookEventName` requirement. With that fix added to the plan, the remaining
risks are accepted Phase 1 limits rather than factual loopholes:

- Runtime loading is still feature-gated by `plugin_hooks`, so hooks remain an
  advisory portability layer with router/test fallback.
- Router behavior remains instruction-surface behavior, so manual diff review
  remains required.
- Full output-quality proof remains deferred to the later eval artifact.
