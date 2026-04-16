# Validation and Checks

## Table of Contents
- [Repository checks](#repository-checks)
- [Config-sensitive checks](#config-sensitive-checks)
- [AI workflow checks](#ai-workflow-checks)
- [PR gate structure](#pr-gate-structure)
- [Authoring-family contract behavior](#authoring-family-contract-behavior)
- [Failure handling](#failure-handling)

## Repository checks
- `bash Infrastructure/scripts/verify-work.sh` (project-local default scope)
- `bash Infrastructure/scripts/verify-work.sh --workspace-governance` (explicit workspace scope)
- `bash Infrastructure/scripts/check_path_ownership_boundaries.sh` (blocks direct edits to runtime/projection surfaces including `.agents/**`, `Plugins/cache/**`, and `runtime/**`)
  - projection-refresh exception only: `PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 bash Infrastructure/scripts/check_path_ownership_boundaries.sh`
  - default scope is staged diff locally and base-ref diff in CI; override with `PATH_OWNERSHIP_GUARD_SCOPE`.
- `bash Infrastructure/scripts/sync_skills.sh`
- `python3 Infrastructure/scripts/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `just validate` (or `bash Infrastructure/scripts/validate_all.sh`)
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agent/PLANS.md`
- Use the repo-local wrapper above instead of the global `~/.codex` `verify-work` helper for this repository.
- Scope policy reference: [hook-governance-scope-defaults.md](/Docs/guides/hook-governance-scope-defaults.md).
- Path ownership policy: [14-path-ownership-boundaries.md](/Docs/agents/14-path-ownership-boundaries.md).

### Managed asset lifecycle baseline
- When work touches lifecycle metadata, packaged-skill inheritance, plugin manifests, or `docs/solutions/` governance:
  - Re-read [managed-asset-lifecycle.md](/Docs/reference/managed-asset-lifecycle.md) before editing.
  - Keep lifecycle truth in the authoritative in-file source, not a sidecar-first shadow registry.
  - Treat derived catalogs or indexes as stale until regenerated when they disagree with the authoritative source.
  - Use [skill-factory plugin manifest](/Plugins/skill-factory/.codex-plugin/plugin.json) as the phase-one plugin proof target and [skill-factory packaged skill-builder](/Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md) as the phase-one packaged-skill proof target. The `skill-builder`, `skill-creator`, `skill-installer`, and `plugin-creator` factory skills live in `Plugins/skill-factory/` and `Plugins/plugin-factory/` respectively.

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
See [CI Required Checks](/Docs/agents/12-ci-required-checks.md) for the complete dependency policy and workflow orchestration.

## Authoring-family contract behavior
`authoring-family-gate` invokes `bash Infrastructure/scripts/validate_skill_authoring_family.sh`.

CI local-memory policy:
- In PR CI, `SKILL_FAMILY_LOCAL_MEMORY_MODE` is set to `optional`.
- Expected behavior: local-memory preflight runs in warn-and-continue mode in CI, while remaining contract/eval/security checks continue to enforce pass/fail outcomes.
- Use `required` only in lanes where `local-memory` is guaranteed available.

That script enforces equivalent governance for:
- `Plugins/skill-factory/skills/*/skill-creator`
- `Plugins/skill-factory/skills/*/skill-installer`
- `Plugins/skill-factory/skills/*/skill-builder`
- `Plugins/plugin-factory/skills/*/plugin-creator`

Validation behavior includes:
- Contract/eval/security benchmark checks via `Infrastructure/scripts/validate_skill_authoring_family_benchmarks.py`.
- Contract/eval/prompt-injection/security fail criteria from `skill_gate.py` (`CONTRACT_*`, `EVALS_*`, `SEC_EVALS_*`, `PI_*`, `SCRIPT_SECURITY_*`, fail-fast workflow checks).
- OpenClaw security checks through `openclaw_skill_guard.py --mode both`.
- Structural eval coverage verification (smoke/release listing), with trusted-lane live eval execution only when explicitly enabled.

## Failure handling
- Stop at the first failed gate, fix, then rerun the minimal required check.