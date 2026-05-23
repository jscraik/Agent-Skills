# PR #192 Triage — JSC-351 Delivery Lane

STATUS: recovered_by_coordinator_after_subagent_artifact_failure

## Live PR State

- PR: https://github.com/jscraik/Agent-Skills/pull/192
- Branch: `codex/jsc-351-abi-conformance`
- Head SHA: `975b8c5d986f11622aae2f0107ba72b5dfef525f`
- State: `OPEN`
- Draft: `true`
- Mergeability: `MERGEABLE` by GitHub field, but operationally blocked by failing checks.
- Review decision: none reported.
- Local branch upstream: `origin/codex/jsc-351-abi-conformance`
- Local unpushed commits at triage start: false.

## Check State

Failing:

- `pr-template`
- `security-scan`

Passing or successful status contexts observed:

- `ci/circleci: pr-pipeline`
- `CodeRabbit` status context
- `docs-test`
- `docs-lint`
- `skill-diagnostics`
- `Gitleaks (secrets scan)`
- `Artifact secrets pre-check`
- `Socket Security: Project Report`
- `Socket Security: Pull Request Alerts`
- `license/snyk (jscraik)`
- `security/snyk (jscraik)`
- `semgrep`
- `Trivy`

Pending or in progress during sampling:

- CodeQL `Analyze (javascript)`
- CodeQL `Analyze (python)`
- `Semgrep (SAST)`
- `graph-diff`
- `structure-gate`
- `Trivy (dependency CVE scan)`

Skipped by the Harness PR Pipeline after the failing gate:

- `linear-gate`
- `risk-policy-gate`
- `dependency-review`
- `actions-pinning`
- `consistency-drift-advisory`
- `consistency-drift-health`
- `lint`
- `typecheck`
- `test`
- `audit`
- `check`
- `memory`

## Review State

- CodeRabbit status context reports success.
- No actionable GitHub review comments or review decision were reported by the triage subagent.
- CodeRabbit success does not make the PR merge-ready while required checks fail.

## Known Validation Blockers

1. Question lifecycle contract cannot read plugin-factory README projection paths.
   - Evidence: validation logs report missing `.agents/plugins-runtime/cache/agent-skills-local/plugin-factory/README.md` and `Plugins/cache/agent-skills-local/plugin-factory/0.1.0/README.md`.
   - Classification: introduced by current patch until a clean-worktree repro proves otherwise.

2. Lifecycle readiness expects `imagegen` but discovers no tracked system skill.
   - Evidence: `test_repo_discovery_uses_tracked_system_skills_without_runtime_bridge` asserts `[] != ['imagegen']`.
   - Classification: introduced by current patch until a clean-worktree repro proves otherwise.

3. Projection integrity drift across plugin mirrors.
   - Evidence: projection integrity reports drift in `cache-harness-engineering`, `cache-plugin-factory`, and `cache-skill-factory`.
   - Classification: introduced by current patch until ownership is separated from unrelated dirty plugin work.

4. `SKILLSET_SOURCE_HASH_STALE` in hook changed-files mode.
   - Evidence: pre-commit/pre-push changed-files mode reports repeated `SKILLSET_SOURCE_HASH_STALE`.
   - Classification: possible unrelated dirty-worktree interaction or environment/tooling failure; requires controlled repro because hooks stash unstaged work before validating staged generated skillsets.

## Priority Remediation

1. Inspect failed remote checks:
   - `gh run view 26340255952 --repo jscraik/Agent-Skills --log-failed`
   - `gh run view 26340255954 --repo jscraik/Agent-Skills --log-failed`

2. Reproduce local blockers under controlled conditions:
   - Use the current PR branch.
   - Keep unrelated dirty work out of the repro path.
   - Determine whether staged `.skillsets` were generated from dirty canonical sources.

3. Decide whether projection drift belongs in this PR:
   - If yes, sync projections from the correct canonical source set and include the generated output intentionally.
   - If no, remove contaminated generated surfaces from the PR and regenerate only the JSC-351-owned artifacts.

4. Do not open another implementation slice until PR #192 has a clear remediation lane and the governor records updated delivery truth.

## Artifact Recovery Note

The `jsc351_pr192_triage_lane` subagent completed and returned live triage facts in its mailbox, but did not write the required file after one artifact-only follow-up. Per the review-swarm contract, the coordinator recovered the artifact from the subagent output and local PR checks.

WROTE: artifacts/reviews/jsc-351-pu006/pr192-triage.md
