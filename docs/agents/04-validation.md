# Validation and Checks

## Table of Contents
- [Repository checks](#repository-checks)
- [Config-sensitive checks](#config-sensitive-checks)
- [AI workflow checks](#ai-workflow-checks)
- [PR gate structure](#pr-gate-structure)
- [Authoring-family contract behavior](#authoring-family-contract-behavior)
- [Failure handling](#failure-handling)

## Repository checks
- `bash scripts/verify-work.sh`
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- `just validate` (or `bash scripts/validate_all.sh`)
- `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- Use the repo-local wrapper above instead of the global `~/.codex` `verify-work` helper for this repository.

### Managed asset lifecycle baseline
- When work touches lifecycle metadata, packaged-skill inheritance, plugin manifests, or `docs/solutions/` governance:
  - Re-read [managed-asset-lifecycle.md](/Users/jamiecraik/dev/Agent-Skills/docs/reference/managed-asset-lifecycle.md) before editing.
  - Keep lifecycle truth in the authoritative in-file source, not a sidecar-first shadow registry.
  - Treat derived catalogs or indexes as stale until regenerated when they disagree with the authoritative source.
  - Use [compound-engineering-router plugin manifest](/Users/jamiecraik/dev/Agent-Skills/plugins/compound-engineering-router/.codex-plugin/plugin.json) as the phase-one plugin proof target and [compound-engineering-router packaged skill](/Users/jamiecraik/dev/Agent-Skills/plugins/compound-engineering-router/skills/compound-engineering-router/SKILL.md) as the phase-one packaged-skill proof target.

## Config-sensitive checks
- For edits to `package.json`, CI workflows, `settings.json`, or similar config files:
  - Run applicable lint/test/typecheck gates before commit.
  - Confirm pass status explicitly in handoff notes.
- For implementation work, run separate implementation and verification workflows.
- Require `codex review --uncommitted` before merge.

## AI workflow checks
- Ensure `README.md`, `AGENTS.md`, and linked docs agree on commands and scope.
- Prefer repository-root commands over guessed defaults.

## PR gate structure
See [CI Required Checks](/docs/agents/12-ci-required-checks.md) for the complete dependency policy and workflow orchestration.

## Authoring-family contract behavior
`authoring-family-gate` invokes `bash scripts/validate_skill_authoring_family.sh`.

CI local-memory policy:
- In PR CI, `SKILL_FAMILY_LOCAL_MEMORY_MODE` is set to `optional`.
- Expected behavior: local-memory preflight runs in warn-and-continue mode in CI, while remaining contract/eval/security checks continue to enforce pass/fail outcomes.
- Use `required` only in lanes where `local-memory` is guaranteed available.

That script enforces equivalent governance for:
- `utilities/skill-builder`
- `skills-system/skill-creator`
- `skills-system/skill-installer`
- `skills-system/plugin-creator`

Validation behavior includes:
- Contract/eval/security benchmark checks via `scripts/validate_skill_authoring_family_benchmarks.py`.
- Contract/eval/prompt-injection/security fail criteria from `skill_gate.py` (`CONTRACT_*`, `EVALS_*`, `SEC_EVALS_*`, `PI_*`, `SCRIPT_SECURITY_*`, fail-fast workflow checks).
- OpenClaw security checks through `openclaw_skill_guard.py --mode both`.
- Structural eval coverage verification (smoke/release listing), with trusted-lane live eval execution only when explicitly enabled.

## Failure handling
- Stop at the first failed gate, fix, then rerun the minimal required check.
