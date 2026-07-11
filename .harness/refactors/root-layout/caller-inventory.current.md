# Repo Layout Caller Inventory

Generated from tracked repository files for the foundry/ and skills-sdk/
migration Phase 1 caller inventory.

## Summary

- Scanned files: 4486
- Skipped non-text or unreadable files: 440
- Files with legacy-root references: 1755
- Total legacy-root references: 17678

## Counts By Legacy Root

| Legacy root | References |
| --- | ---: |
| Docs/ | 847 |
| GOVERNANCE | 272 |
| Infrastructure/ | 5990 |
| Plugins/ | 2342 |
| Skills/ | 2805 |
| artifacts/ | 1284 |
| brand/ | 21 |
| docs-policy.json | 65 |
| plugins/ | 118 |
| scripts | 3799 |
| skills-system/ | 135 |

## Counts By Caller Category

| Category | References |
| --- | ---: |
| ask_cli_route | 1297 |
| ci_workflow | 293 |
| docs_reference_link | 8822 |
| external_operator_entrypoint | 68 |
| generated_artifact_input | 2292 |
| internal_python_import | 4129 |
| precommit_or_hook | 29 |
| runtime_projection_input | 691 |
| shell_command | 839 |
| tessl_staging_input | 191 |
| test_fixture | 3047 |
| unclassified | 2447 |

## Top Files

| File | References |
| --- | ---: |
| Infrastructure/GOVERNANCE/runtime-separation/path-consumers.yaml | 610 |
| Docs/plans/2026-04-14-feat-llm-wiki-runtime-pivot-plan.md | 410 |
| Infrastructure/tests/test_ask_cli_impl.py | 300 |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | 292 |
| Docs/plans/2026-03-10-feat-learning-preserving-skill-design-plan.md | 240 |
| Docs/goals/jsc-351-agent-skills-codex-abi-conformance/state.yaml | 216 |
| Docs/goals/jsc-351-agent-skills-codex-abi-conformance/receipts.jsonl | 209 |
| Docs/plans/2026-04-12-feat-product-factory-runtime-separation-plan.md | 202 |
| Infrastructure/tests/test_ask_evals_command.py | 184 |
| Infrastructure/scripts/testing/test_validate_all_runtime_separation_impl.py | 178 |
| Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/state.yaml | 174 |
| Docs/plans/2026-04-09-feat-skill-plugin-selection-gold-standard-upgrade-plan.md | 165 |
| Docs/skills-by-type.md | 161 |
| Docs/plans/2026-04-04-feat-skill-authoring-family-contract-rollout-plan.md | 160 |
| Infrastructure/GOVERNANCE/runtime-separation/readers.yaml | 159 |
| Docs/plans/2026-04-04-feat-skill-authoring-family-iteration-upgrade-plan.md | 151 |
| Infrastructure/scripts/validate_all_impl.sh | 149 |
| Docs/goals/jsc-391-agent-first-skills-sdk-scaffold-refactor/state.yaml | 137 |
| Infrastructure/scripts/lib/ask/command_metadata.py | 130 |
| Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh | 120 |
| Docs/skill-graphs/governance/inventory-policy.json | 119 |
| Docs/plans/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md | 112 |
| Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md | 112 |
| Docs/plans/2026-03-09-feat-skills-knowledge-graph-visual-interface-plan.md | 102 |
| Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/receipts.jsonl | 100 |
| Docs/plans/2026-03-29-fix-outstanding-onboarding-readiness-closeout-plan.md | 95 |
| Plugins/synaipse-harness/references/upstream/harness-engineering-context.yaml | 92 |
| Plugins/skill-factory/fixtures/budget-archive/2026-04-19/skills/code_quality_review/skill-builder/references/quality-tools.md | 88 |
| Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md | 86 |
| Infrastructure/scripts/lib/ask/commands/skills_impl.py | 78 |

## Migration Use

- Use the JSON artifact for exact file:line occurrences.
- Classify wrappers before moving a root.
- Regenerate this inventory after each migration bucket.
- Do not treat this inventory as behavior proof or hosted PR proof.
