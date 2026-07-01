# Repo Layout Caller Inventory

Generated from tracked repository files for the foundry/ and skills-sdk/
migration Phase 1 caller inventory.

## Summary

- Scanned files: 10340
- Skipped non-text files: 722
- Files with legacy-root references: 1615
- Total legacy-root references: 14404
- Excluded generated/evidence references: 113258

## Counts By Legacy Root

| Legacy root | References |
| --- | ---: |
| Docs/ | 740 |
| GOVERNANCE | 215 |
| Infrastructure/ | 4909 |
| Plugins/ | 2231 |
| Skills/ | 2597 |
| brand/ | 21 |
| docs-policy.json | 64 |
| plugins/ | 125 |
| scripts | 3379 |
| skills-system/ | 123 |

## Counts By Caller Category

| Category | References |
| --- | ---: |
| ask_cli_route | 889 |
| ci_workflow | 147 |
| docs_reference_link | 7211 |
| external_operator_entrypoint | 68 |
| internal_python_import | 3382 |
| precommit_or_hook | 16 |
| runtime_projection_input | 486 |
| shell_command | 687 |
| tessl_staging_input | 186 |
| test_fixture | 2500 |
| unclassified | 2337 |

## Top Files

| File | References |
| --- | ---: |
| Infrastructure/GOVERNANCE/runtime-separation/path-consumers.yaml | 426 |
| Docs/plans/2026-04-14-feat-llm-wiki-runtime-pivot-plan.md | 337 |
| Infrastructure/tests/test_ask_cli_impl.py | 295 |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | 264 |
| Docs/plans/2026-04-12-feat-product-factory-runtime-separation-plan.md | 182 |
| Infrastructure/scripts/testing/test_validate_all_runtime_separation_impl.py | 174 |
| Docs/plans/2026-03-10-feat-learning-preserving-skill-design-plan.md | 172 |
| Docs/goals/jsc-351-agent-skills-codex-abi-conformance/state.yaml | 170 |
| Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/state.yaml | 164 |
| Docs/skills-by-type.md | 161 |
| Docs/plans/2026-04-04-feat-skill-authoring-family-contract-rollout-plan.md | 160 |
| Infrastructure/GOVERNANCE/runtime-separation/readers.yaml | 159 |
| Docs/plans/2026-04-09-feat-skill-plugin-selection-gold-standard-upgrade-plan.md | 142 |
| Docs/plans/2026-04-04-feat-skill-authoring-family-iteration-upgrade-plan.md | 138 |
| Infrastructure/tests/test_ask_evals_command.py | 125 |
| Infrastructure/scripts/validate_all_impl.sh | 122 |
| Docs/skill-graphs/governance/inventory-policy.json | 119 |
| Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh | 118 |
| Docs/plans/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md | 112 |
| Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md | 103 |
| Infrastructure/scripts/lib/ask/command_metadata.py | 103 |
| Plugins/synaipse-harness/references/upstream/harness-engineering-context.yaml | 88 |
| Docs/goals/jsc-391-agent-first-skills-sdk-scaffold-refactor/state.yaml | 83 |
| Docs/plans/2026-05-06-feat-agent-first-golden-path-product-compression-plan.md | 74 |
| Docs/plans/2026-04-05-feat-skill-authoring-family-gold-standard-upgrade-plan.md | 73 |
| Plugins/skill-factory/references/skill-builder/skill-quality-baseline.json | 73 |
| Infrastructure/scripts/migrations/legacy/move-docs-layout.sh | 71 |
| Plugins/skill-factory/fixtures/budget-archive/2026-04-19/skills/code_quality_review/skill-builder/references/skill-quality-baseline.json | 71 |
| Plugins/skill-factory/fixtures/budget-archive/2026-04-21/skills/code_quality_review/skill-builder/references/skill-quality-baseline.json | 71 |
| Plugins/skill-factory/skills/code_quality_review/skill-builder/references/skill-quality-baseline.json | 71 |

## Migration Use

- Use the JSON artifact for exact file:line occurrences.
- Classify wrappers before moving a root.
- Regenerate this inventory after each migration bucket.
- Do not treat this inventory as behavior proof or hosted PR proof.
