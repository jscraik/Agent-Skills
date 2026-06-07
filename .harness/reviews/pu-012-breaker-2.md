# PU-012 Breaker Pass 2 Review

## Accountability Receipt
- status: complete
- artifact_paths:
  - .harness/reviews/pu-012-breaker-2.md
  - artifacts/agent-runs/adversarial-reviewer-pu-012-breaker-2-20260606/manifest.json
- manifest_path: artifacts/agent-runs/adversarial-reviewer-pu-012-breaker-2-20260606/manifest.json
- findings:
  - High: PU-012 validation scope can stay green without exercising the new project-conformance commands.
  - Medium: Temp-worktree mise trust warnings are not classified as environment/tooling blockers, so validation can misreport setup noise as an SDK failure.
  - Medium: Project root identity is under-specified, so a relative or aliased root can be certified against the wrong tree.
- failures_or_blockers: none
- improvement_opportunities:
  - Add an explicit PU-012 validation slug or scope mapping, then assert it in the scope tests.
  - Define the validation environment contract for trusted mise config paths and state/cache dirs, and classify leftover warnings as blocked_environment.
  - Pin the project-root canonicalization rule to strict resolution and root-identity comparison.
- strengths:
  - The spec already avoids mutation and network access, which keeps the slice bounded.
  - The spec already points at temp-project coverage and schema-valid robot JSON output.
  - The spec already calls out the known mise temp-worktree warning class, which is the right place to close the loop.
- validation_evidence:
  - Reviewed the spec at /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md.
  - Reviewed the current validation scope router in /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/scripts/validate_all_impl.sh.
  - Reviewed the scope contract tests in /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/tests/test_skills_sdk_validation_scope.py.
  - Reviewed the existing project-root lifecycle contract in /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/scripts/lib/ask/skills_sdk/project_install.py and /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py.
- useful_findings:
  - The current skills-sdk scope only schedules skills-sdk-typed-artifacts, so PU-012 work can be omitted unless the validation router changes.
  - The current install and cleanup code already require strict, absolute, marker-backed project roots, so the spec should mirror that invariant instead of leaving identity implicit.
  - The spec's own note about mise trust paths shows the team already knows this is a validation-only concern, not an SDK capability failure.
- avoided_false_positive:
  - I did not treat the mise trust warning itself as an SDK defect; it is a setup/runtime-classification issue unless the spec says otherwise.
- evidence_quality: high. The gaps are visible in the spec text and in the existing validation/router contracts.
- followed_scope: yes. I only inspected the spec and the directly relevant validation, capability, install, and cleanup contracts.
- reusable_learning: temp worktrees need an explicit environment-blocker contract so trust-path noise does not get conflated with product behavior.
- coordinator_score: 8/10
- next_action: Tighten the spec with explicit validation-scope coverage, a setup-blocker rule for mise warnings, and a canonical project-root identity contract.
- artifacts:
  - .harness/reviews/pu-012-breaker-2.md
  - artifacts/agent-runs/adversarial-reviewer-pu-012-breaker-2-20260606/manifest.json

## Findings

### High: PU-012 can be marked complete without ever running PU-012 coverage
- Evidence:
  - Spec: FR-021 and the validation interface only say the skills-sdk scope must include PU-012 conformance coverage and that repo validate --scope=skills-sdk should include the PU-012 tests or validator entrypoint.
  - Spec: the same slice still points at skills-sdk-typed-artifacts only for validation scope.
  - Validation router: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/scripts/validate_all_impl.sh:260-328 still routes skills-sdk only to skills-sdk-typed-artifacts.
  - Scope test: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/tests/test_skills_sdk_validation_scope.py:37-44 still asserts only the typed-artifacts check for the dedicated scope.
- Why it matters:
  - A green repo validate --scope=skills-sdk can be claimed while the new project status/doctor surface is never scheduled, so the slice can look done without any proof that the new commands exist or work.
  - This is especially risky here because the slice is read-only and the only durable proof is validation; if the scheduler does not include PU-012, the spec can be satisfied on paper only.
- Concrete fix:
  - Add a dedicated PU-012 validation slug/check to validate_all_impl.sh, wire it into the skills-sdk scope, and add a scope test that fails until the PU-012 check is scheduled.
  - If the scope name is meant to stay broad, rewrite FR-021 and the interface row so the exact required check name is explicit instead of "or validator entrypoint".

### Medium: Mise trust warnings can be mistaken for SDK failures in the temp worktree
- Evidence:
  - Spec: the worktree setup note explicitly says the new worktree needs MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" plus repo-local MISE_STATE_DIR/MISE_CACHE_DIR/XDG state paths to avoid sandboxed mise trust and tracked-config warnings.
  - Spec: the validation boundary says validation commands must set trusted-config and state paths before classifying runtime setup failures.
  - Validation router: the current validation entrypoint probes mise/uv launchers and falls back between them, which means a trust warning can surface as a command-environment problem during validation rather than a product defect.
- Why it matters:
  - In this repo, that warning class is a known environment/setup issue, not evidence that the Skills SDK project-conformance feature is broken.
  - If the spec does not require the harness to classify that warning as blocked_environment or equivalent, the review lane can bounce between SDK failed and setup failed without a stable verdict.
- Concrete fix:
  - Add an explicit validation requirement that the PU-012 harness exports the trusted config/state/cache vars for the temp worktree before running checks.
  - Add a blocker taxonomy rule that any remaining mise trust or tracked-config warning is reported as environment/tooling blocked, not as a PU-012 conformance failure.

### Medium: Project-root identity is not pinned tightly enough to stop alias-based false positives
- Evidence:
  - Spec: FR-002 only says the command must refuse ambiguous or unsafe project roots, and the data contract describes project_root_identity only as a normalized identity for the inspected root.
  - Spec: the authority boundary forbids inferring authority from the cwd, but it does not say the root must be absolute, existing, and strictly resolved before inspection.
  - Existing lifecycle contract: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/scripts/lib/ask/skills_sdk/project_install.py:126-214 requires an explicit absolute path, strict resolution, and marker-backed project roots.
  - Existing cleanup contract: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py:246-276 compares the resolved receipt target root to the resolved --project-root.
- Why it matters:
  - A relative path, symlink alias, or moved checkout can be certified as healthy against the wrong tree if the implementation only normalizes strings instead of comparing canonical filesystem identity.
  - That creates a false positive where the receipt looks valid but it no longer proves the inspected project is the one that owns the lockfile and receipts.
- Concrete fix:
  - State that PU-012 status/doctor must require an absolute existing project root, resolve it strictly, and compare canonical resolved root identity against receipt and lockfile authority.
  - If the implementation intends a different identity scheme, define it in the spec now so the tests can lock it down.

## Residual Risks
- The spec still leaves the exact project-conformance schema file path and validator registration details to implementation judgment.
- The spec does not yet name a concrete capability-truth row id for the new surface, so the implementation could still hide the feature in a generic status summary unless that is pinned later.

## WROTE
WROTE: .harness/reviews/pu-012-breaker-2.md

