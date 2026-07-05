# improve-agent-native OSS Repair Packaging Triage

schema_version: oss-repair-packaging-triage/v1

## Scope

- PM source thread: 019f0314-ba59-7a00-ab78-9bd3174d1d03
- Execution report thread: 019f2458-ad2a-76e1-8c74-052484d452ed
- Branch/worktree: codex/improve-native-oss-eval-repair-package in /Users/jamiecraik/dev/agent-skills
- Current gate being packaged: oss-cloud-release-eval
- Boundary: Tessl dry-run, Tessl live, publish, release, PR #306/shared scenario registry work, SkillsBar local score work, and fresh qwen or oss-cloud reruns are out of scope.

## Evidence Basis

- Thread report: .harness/reports/thread-replies/019f2458-ad2a-76e1-8c74-052484d452ed/latest.json
- OSS-cloud release ledger: .harness/evidence/handoff/improve-agent-native/oss-cloud-release-ledger.json
- OSS local/cloud release comparison: .harness/evidence/handoff/improve-agent-native/oss-cloud-release-comparison.json
- Scenario-quality repair evidence: .harness/evidence/handoff/improve-agent-native/scenario-quality-after-oss-cloud-coherence-guardrail-criteria.json
- PM delivery receipt: .harness/reports/thread-replies/019f2458-ad2a-76e1-8c74-052484d452ed/pm-delivery.json

## Dirty Triage Table

| Bucket | Include in this slice | Files or patterns | Reason |
| --- | --- | --- | --- |
| Intended source changes | yes | Skills/agent-ops/improve-agent-native/references/evals.yaml; Skills/agent-ops/improve-agent-native/references/eval-scenarios.json | Skill-owned eval criteria were repaired to remove brittle generated wording and align OSS-local/OSS-cloud behavior. |
| OSS proof-set source | yes | Infrastructure/config/skills-sdk/oss-minimum-proof-sets.v1.json; Infrastructure/scripts/validation-and-linting/build_oss_minimum_*.py; Infrastructure/tests/test_oss_minimum_*.py | Encodes Jamie's 15+5 policy, shard planning, minimum proof receipts, and local/cloud comparison behavior. |
| Scenario-quality ratchet | yes | Infrastructure/scripts/lib/ask/skills_sdk/release_rubric_checks.py; Infrastructure/scripts/lib/ask/skills_sdk/tessl_eval_quality.py; Infrastructure/tests/test_skills_sdk_scenario_quality.py; Infrastructure/tests/test_skills_sdk_tessl_eval_quality.py | Blocks repeat failures from phrase-only negative boundary assertions and comma-list expected_signal checks, and keeps output-format instructions from being misclassified as semantic answer leakage. |
| Generated source-of-truth artifacts | yes, bounded | .harness/evidence/handoff/improve-agent-native/oss-cloud-release-ledger.json; oss-cloud-release-comparison.json; oss-cloud-release-shard-plan.json; qwen-oss-local-full-release-ledger.json | Captures the OSS release-eval lane evidence that this package is closing. |
| Validation/evidence artifacts | yes, bounded | selected scenario-quality-after-oss-cloud-*.json; oss-cloud-delta-classification-20260704.json; package/scorer/audit receipts after qwen smoke when referenced by report | Keeps the evidence trail for the criteria repairs and stage comparison. |
| PM handoff artifacts | yes | latest.json; pm-delivery.json; oss-repair-packaging-triage.md | Provides the reviewable closeout artifact for this packaging lane. |
| Learning/steering artifacts | yes, bounded | .harness/memory/LEARNINGS.md; .harness/quality/steering-uptake.md | Includes OSS eval lessons and steering uptake rows that explain deterministic ratchets. |
| Local-only/temp eval artifacts | no | Infrastructure/artifacts/evals/closeouts/20260703T*.json | Raw closeout exports are local runtime evidence. The committed lane uses summarized handoff receipts instead. |
| SkillsBar local score work | no | local-score schema/source/tests; .harness/evidence/skills-sdk/local-score/** | Explicit PM boundary says no SkillsBar local score work in this lane. |
| Package security lane | no | package-security-signature schema/source/tests | Separate security lane, not part of OSS local/cloud eval repair packaging. |
| Risk-mode/API command drift | no | risk-mode-taxonomy, sdk_security, command_metadata, ask command files unless separately proven | Separate dirty buckets; not needed to package the OSS evidence. The bounded tessl_eval_quality change is included above because focused tests proved it is required by the scenario-quality ratchet. |
| PR #306/shared scenario registry | no | .harness/research/2026-07-03-skills-sdk-shared-scenario-registry-design.md | Explicit PM boundary excludes PR #306/shared scenario registry work. |
| Codex-agent eval work | no | codex/agents/evals/workflow-guardrail-candidates/** | Separate repo/control-plane lane. |
| Unrelated thread reports | no | .harness/reports/thread-replies/019f2871-*/**; 019f2c2b-*/** | Other execution-thread reports are not part of this OSS package. |

## Validation Plan

- Focused regression tests for the OSS minimum proof-set helpers and scenario-quality ratchets.
- Scenario-quality preview for Skills/agent-ops/improve-agent-native.
- Thread report validation and PM delivery validation.
- Steering uptake validation because this slice carries steering/learning rows.
- Targeted git diff whitespace check for the intended staged slice.

## Boundary Statement

This package records OSS local/cloud release-eval evidence only. It does not prove Tessl dry-run, Tessl live, publish, release, or registry readiness.
