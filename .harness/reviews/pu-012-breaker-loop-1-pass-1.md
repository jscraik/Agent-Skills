# PU-012 Adversarial Review

Verdict: findings present. The spec is close, but a few acceptance holes still let an implementation claim success without proving the strongest project-root safety and runtime identity rules.

## Findings

### High: The spec still leaves broad but marked roots underspecified.
- Evidence:
  - .harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:112-116 requires the root to be absolute, existing, strictly resolved, marker-backed, and inside the intended boundary.
  - The same spec at 143-145 only names missing, relative, nonexistent, ambiguous, symlink-escaping, or unsafe roots, but never defines the unsafe floor.
  - The validation plan at 344-376 only exercises relative, nonexistent, symlink alias, and symlink escape cases.
  - Existing install safety already rejects filesystem root, home, and the live repo target in Infrastructure/scripts/lib/ask/skills_sdk/project_install.py:126-214.
- Why it matters:
  - An implementation can still treat a marked broad tree such as /tmp, $HOME, or even the live repo checkout as project managed if it only checks for a marker and a resolved path. That turns a read-only conformance command into an arbitrary filesystem audit and can make a dangerous root look accepted.
- Concrete fix:
  - Name the forbidden root classes explicitly in the spec, or require the project-conformance command to reuse the same root resolver as install/cleanup, including the filesystem-root, home-directory, and live-repo refusals.
  - Add a negative VAC case for a marked broad root and for the live repo root.
- Confidence: 0.86
- Validation ownership: human

### Medium: Canonical identity drift after a move is mentioned, but never forced by acceptance.
- Evidence:
  - The strict identity rule in .harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:116-117 explicitly mentions moved checkouts and receipt roots whose canonical identity differs from the supplied root.
  - The validation plan at 350-376 does not include a moved-checkout or bind-mount style case; it only checks relative paths, nonexistent paths, symlink aliases, and symlink escapes.
- Why it matters:
  - A project can be relocated or rebound after install without changing the visible path string. If the implementation only proves "the path exists and has a marker", it can still report cleanup readiness for the wrong tree.
- Concrete fix:
  - Add a fixture that represents a path whose canonical identity changed after a move or bind mount, then require blocked conformance before any lockfile or receipt inspection.
  - Make the acceptance text assert the emitted project_root_identity matches the canonical resolved root, not just the input string.
- Confidence: 0.78
- Validation ownership: human

### Medium: Empty marked projects are allowed, but the missing-lockfile status is still ambiguous.
- Evidence:
  - SA-001 in .harness/specs/2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate-spec.md:48 says an empty marked project with no lockfile should still report SDK-managed and no installed skills.
  - FR-005 at 146-147 separately requires the command to validate skills.lock.json when present and classify missing lockfile states.
  - The top-level data contract at 193-197 and the conformance rules at 217-223 do not define which lockfile_status values are legal for the "empty but healthy" case.
- Why it matters:
  - The implementation can pick a blocked or fail classification for the no-lockfile case and still satisfy the rest of the spec, or it can silently treat "no lockfile" as healthy without proving which branch was intended. Either way, the empty-project path can look green while the lockfile semantics drift underneath it.
- Concrete fix:
  - Define the exact lockfile_status enum for the empty-marked-project path and state whether conformance should be pass, warn, fail, or blocked when no lockfile exists yet.
  - Add a dedicated acceptance test for SA-001 that asserts the missing-lockfile branch explicitly rather than only checking "no installed skills."
- Confidence: 0.64
- Validation ownership: human

## Accountability Receipt

- status: findings
- artifact_paths:
  - .harness/reviews/pu-012-breaker-loop-1-pass-1.md
- findings:
  - high: broad-but-marked project roots are not concretely excluded
  - medium: moved-checkout canonical identity drift is not exercised
  - medium: empty-marked-project lockfile semantics are ambiguous
- failures_or_blockers:
  - none
- improvement_opportunities:
  - tighten the root-safety floor by naming the forbidden roots explicitly
  - add a canonical-identity drift fixture
  - define the empty-project lockfile branch unambiguously
- strengths:
  - the spec already requires explicit --project-root refusal
  - the spec already requires launch-time mise env setup for validation
  - the spec already calls for a first-class project_conformance capability row
- validation_evidence:
  - spec review only; no runtime tests were executed
  - supporting repo contracts reviewed: Infrastructure/scripts/lib/ask/skills_sdk/project_install.py, Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py, Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py, Infrastructure/scripts/validate_all_impl.sh, Infrastructure/tests/test_skills_sdk_validation_scope.py, Infrastructure/tests/test_skills_sdk_capability_status.py
- next_action:
  - update the spec acceptance language and validation matrix so a future implementation cannot pass without proving root-safety floor, canonical identity drift handling, and empty-project lockfile semantics
- useful_findings:
  - root-safety floor needs explicit forbidden roots
  - moved-checkout identity drift needs a dedicated acceptance case
  - empty-project semantics need a defined lockfile classification
- avoided_false_positive:
  - did not flag the validation-scope router because the spec already requires an explicit PU-012 slug/check
  - did not flag wrapper parity as a blocker because the spec intentionally allows a flat-verb fallback
  - did not treat mise trust warnings as a spec defect; those were handled as launch-time environment noise
- evidence_quality:
  - medium-high; line references came directly from the spec and nearby repo contracts, but no implementation run was needed for this review
- followed_scope:
  - reviewed only the PU-012 spec plus the minimum related contracts needed to judge project-root refusal, mise launch env, validation scope, strict identity, and capability-truth exposure
- reusable_learning:
  - when a spec mentions unsafe roots, pin the forbidden root classes explicitly and add a fixture for each one
  - when canonical identity is part of the contract, add a moved-checkout or bind-mount test, not just symlink and relative-path cases
- coordinator_score: 8

WROTE: .harness/reviews/pu-012-breaker-loop-1-pass-1.md
