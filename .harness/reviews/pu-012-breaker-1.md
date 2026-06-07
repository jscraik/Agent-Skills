# PU-012 Breaker Review

## Findings

### High: A missing `--project-root` acceptance case leaves room for implicit cwd fallback
- **Evidence:** `.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:111`, `:137-139`, `:163-165`, `:298-299`, `:312-334`
- **Impact:** The spec bans inferring authority from the current working directory, but none of the acceptance criteria or validation commands prove that `status` or `doctor` fail closed when `--project-root` is omitted. A future implementation could silently inspect the launch cwd, pass the listed happy-path fixtures, and still report conformance for the wrong project root.
- **Why it matters:** That is exactly the kind of false-positive adoption signal the gate is supposed to prevent. It can also hide root-selection bugs until after agents trust the wrong lockfile and receipt set.
- **Concrete fix:** Add an explicit acceptance case and validation command for both `project status` and `project doctor` with `--project-root` omitted. The expected result should be a guided error, no filesystem reads beyond argument parsing, and no fallback to cwd or parent discovery.
- **Confidence:** 92/100
- **Validation ownership:** Spec gap

### Medium: The required mise runtime setup is described, but the validation plan does not actually inject it
- **Evidence:** `.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:89`, `:286`, `:306`, `:312-319`
- **Impact:** The spec correctly separates sandbox setup warnings from SDK behavior, but the concrete validation commands are bare invocations. In a temp worktree with a repo `.mise.toml`, those commands can emit trust or tracked-config warnings before the SDK code even runs, and the spec never bakes the required `MISE_TRUSTED_CONFIG_PATHS`, `MISE_STATE_DIR`, `MISE_CACHE_DIR`, and `XDG_STATE_HOME` values into the actual command examples.
- **Why it matters:** This leaves the gate vulnerable to misclassifying environment noise as a Skills SDK failure, which is the recurring issue the spec says to avoid. It also makes the validation plan non-reproducible unless the operator remembers the surrounding shell setup from the prose sections.
- **Concrete fix:** Wrap every temp-worktree validation command in the required launch-time environment block, or centralize the env setup in a repo wrapper that the spec can point to unambiguously. The env block should be part of the validation command text, not only prose guidance.
- **Confidence:** 89/100
- **Validation ownership:** Spec gap

### Medium: `ask sdk status` can satisfy the spec with prose, not a first-class machine-readable capability row
- **Evidence:** `.harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:82`, `:154`, `:166`, `:236`; `Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py:25-54`, `:89-139`; `Infrastructure/tests/test_skills_sdk_capability_status.py:64-77`
- **Impact:** The spec says project conformance must be visible in capability truth, but it never names a row id, schema field, or validation rule for that new capability. The existing capability-status contract only accepts the current fixed id set, so an implementation can still pass the current tests by tucking project-conformance evidence into notes or source-artifact prose instead of making it a real machine-checkable row.
- **Why it matters:** If project conformance is not a first-class capability row, `ask sdk status` can keep looking green while the project-health gate stays invisible to downstream automation.
- **Concrete fix:** Reserve an explicit capability id/row for project conformance, update `capability-matrix.v1.json` and the capability-status validation to require it, and add a test that asserts the row is present with read-only evidence and `mutation_performed: false`.
- **Confidence:** 84/100
- **Validation ownership:** Spec gap

## Accountability Receipt

- **status:** complete
- **artifact_paths:**
  - `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-1.md`
- **manifest_path:** `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/artifacts/agent-runs/adversarial-reviewer-019e9dc5-cc3b-7481-bc30-40ff038ea4f2/manifest.json`
- **findings_count:** 3
- **failures_or_blockers:** none
- **improvement_opportunities:**
  - Add explicit negative acceptance for omitted `--project-root`.
  - Bake temp-worktree mise env setup into the validation commands themselves.
  - Define the project-conformance capability row as a machine-readable status contract.
- **strengths:**
  - The spec does clearly fence off mutation, network access, and workspace-wide scanning.
  - It also calls out the mise trust versus tracked-config distinction, which is the right failure class to guard.
- **validation_evidence:** static review of the spec plus the existing capability-status contract and tests; no source code changes were made.
- **next_action:** tighten the spec acceptance matrix so the implementation cannot pass by relying on cwd fallback, shell startup warnings, or free-text capability notes.
- **useful_findings:**
  - Missing `--project-root` coverage is the easiest path to a false positive.
  - Validation examples need the mise env block as executable text, not just prose.
  - Capability truth needs a named row, not only an evidence note.
- **avoided_false_positive:** I did not flag the mise warnings themselves as a Skills SDK bug; the issue is that the spec does not fully operationalize the runtime setup needed to suppress or separate them.
- **evidence_quality:** High for the acceptance-hole and validation-environment gaps; medium-high for the capability-row underspecification because the contract can still be tightened in a few different ways.
- **followed_scope:** reviewed only the PU-012 spec and the directly relevant Skills SDK contracts/tests needed to judge it.
- **reusable_learning:** temp-worktree validation should encode shell setup in the command surface whenever mise trust and tracked-config state are separate concerns.
- **coordinator_score:** 8/10

WROTE: /private/tmp/agent-skills-skills-sdk-pu-012-project-conformance/.harness/reviews/pu-012-breaker-1.md
