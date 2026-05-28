# SkillOpt Skills SDK Implementation Record

Date: 2026-05-28

## Scope

Implemented the first bounded skill-optimization contract slice from
`.harness/research/audits/2026-05-28-skillopt-skills-sdk-gap-analysis.md`.

This record exists so future audit, PR triage, and Skills SDK planning can
trace what moved from recommendation to executable repo contract.

## Implemented

- Added `skill-optimization-contract.v1` as the declarative contract for
  trainable skill behavior.
- Exposed optimization readiness through `./bin/ask skills package ... --json
  --robot`.
- Added optimization readiness to package contract progressive-disclosure and
  agent-contract payloads.
- Made reference-contract command declarations satisfy the SDK package
  `commands` field when the command does not appear directly in `SKILL.md`.
- Added unit coverage for valid and incomplete optimization contracts.
- Updated `autoresearch` as the first real consumer:
  - train / selection / held-out test split roles;
  - bounded edit policy;
  - rejected-edit buffer;
  - anti-cheat protected paths;
  - best-candidate and promotion evidence;
  - reviewed canonical promotion.

## Decisions

- Skill optimization is optional. A package without `optimization.enabled`
  remains valid and reports `optimization_status: not_declared`.
- Optimization is not runtime proof. Passing the contract proves shape and
  governance only; it does not prove candidate quality, held-out
  generalization, or anti-cheat success.
- The first public contract is deliberately small: target artifact, optimizer
  mode, roles, split visibility, edit budget, acceptance gate, anti-cheat,
  evidence, and promotion.
- Canonical `SKILL.md` edits stay review-gated. Optimizers may produce
  candidate artifacts, not silently rewrite canonical source.

## Files Changed By This Slice

- `Infrastructure/config/schemas/skill-optimization-contract.v1.schema.json`
- `Infrastructure/config/schemas/skill-package-readiness.v1.schema.json`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `Infrastructure/tests/test_ask_skills_package_contract.py`
- `Skills/agent-ops/autoresearch/SKILL.md`
- `Skills/agent-ops/autoresearch/references/contract.yaml`
- `Skills/agent-ops/autoresearch/references/evals.yaml`
- `.harness/research/audits/2026-05-28-skillopt-skills-sdk-implementation-record.md`

## Validation Evidence

- Command: `python3 -m unittest Infrastructure.tests.test_ask_skills_package_contract`
  - Result: pass
  - Evidence: 22 tests ran successfully.
- Command: `./bin/ask skills package autoresearch --json --robot > /tmp/autoresearch-package.json && jq '{status, skill_status: .data.skill_package.status, readiness: .data.skill_package.package_contract.readiness_level, workflow_status: .data.skill_package.package_contract.sdk_contract.values.workflow_contract.status, optimization_status: .data.skill_package.package_contract.sdk_contract.values.optimization_contract.status, optimization_mode: .data.skill_package.package_contract.sdk_contract.values.optimization_contract.optimizer_mode, sdk_missing: .data.skill_package.package_contract.sdk_contract.required_fields.missing, blockers: .data.skill_package.gate_summary.blocked_reasons}' /tmp/autoresearch-package.json`
  - Result: pass
  - Evidence: `skill_status=pass`, `readiness=share_ready`,
    `optimization_status=pass`, `optimization_mode=bounded_patch`,
    `sdk_missing=[]`, `blockers=[]`.

## Remaining Follow-Up

- Add an optimizer runner or adapter later. This patch only creates the package
  contract and first consumer policy.
- Decide whether `ask skills package` should validate optimization contract
  payloads against the JSON Schema directly, beyond the current deterministic
  readiness checks.
- Add real train / selection / held-out datasets when a concrete SkillOpt or
  evo-style run is scheduled; current split paths define roles and boundaries
  but do not claim datasets exist.
- Extend dashboards or review artifacts to surface optimization status next to
  workflow and package readiness.
