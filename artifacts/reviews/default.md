# Agent Skills PR #313 Post-Merge Follow-Up QA Disproof

schema_version: qa-proof/v1
status: accepted_with_broader_suite_gap
agent_id: 019f3468-2091-7bb2-bd5e-ecad35647e4d
repo: /Users/jamiecraik/dev/agent-skills
branch: codex/pr313-postmerge-review-followups

## Scope

Independent QA Disproof lane for the Project PM canary. I inspected the real branch output and tried to disprove the two Worker claims:

- schema blocks pass/review intake-review receipts when package-security-signature evidence is missing or null, while preserving the blocked null route.
- local-score blocks the impact lane when scenario-quality emits suite-level blockers or blocked status even when row-level `blocked_count` is 0.

I did not edit implementation files.

## Repo Contract Read

- Read `AGENTS.md`.
- Read `CODESTYLE.md`.
- Read `Docs/agents/19-high-signal-steering-feedback.md`.
- Read `Docs/agents/04-validation.md`.
- Read `artifacts/AGENTS.md`.

Key applied constraints: use repo wrappers, keep local proof separate from hosted PR/review truth, treat review output as bounded evidence, and report exact command outcomes.

## Branch And Dirty State

Command: `git status --short --branch --untracked-files=all` -> pass (branch `codex/pr313-postmerge-review-followups`; five intended implementation/test files modified; two Worker handoff JSON files untracked)

Changed files inspected:

- `Infrastructure/config/schemas/skills-sdk/skill-intake-review-receipt.v0.schema.json`
- `Infrastructure/scripts/lib/ask/skills_sdk/local_score.py`
- `Infrastructure/tests/test_skills_sdk_schema_spine.py`
- `Infrastructure/tests/test_skills_sdk_skill_intake_review.py`
- `Infrastructure/tests/test_skills_sdk_local_score.py`

Worker handoffs inspected:

- `.harness/reports/worker-handoffs/pr313-postmerge-review-followups/worker-01-skill-intake-review-receipt.json`
- `.harness/reports/worker-handoffs/pr313-postmerge-review-followups/worker-02-local-score.json`

## Findings

### No Blocking Defect Found In Focused Patch

The schema now has `package_security_signature_receipt` in top-level `required`, requires the package-security signature schema for `status: pass` and `status: review`, and permits only `null` for `status: blocked`.

The local-score impact lane now combines row-level blocked count, suite-level blocker count, and receipt status before allowing impact to pass.

### P3: Focused Tests Are Narrower Than The Full Disproof Matrix

The checked-in regression tests cover the main review/null schema case and the suite-level local-score blocker. They do not explicitly encode every disproof probe I ran manually, especially missing signature for review, missing/null signature for pass, and positive acceptance for blocked/null.

This is not a rejection because the current schema behavior passed those probes. It is an advisory: if this PR follow-up becomes the durable guardrail, the manual probes should be converted into unit tests so future changes cannot regress the matrix invisibly.

### Broader Suite Gap Remains

The full `tests.test_skills_sdk_skill_intake_review` suite still fails five tests because the current `valid_skill` fixture is blocked by an intake quarantine issue involving `README.md`. This matches the Worker handoff boundary that the full skill-intake review suite is not green.

I did not prove this failure is pre-existing by checking out/running the base branch in this QA lane. The current diff does not modify the fixture or the production intake quarantine path that emits that blocker, but the evidence here only proves the broader suite is still failing on the current branch.

## Deterministic Checks

Command: `sed -n '1,220p' AGENTS.md` -> pass (repo operating contract read)
Command: `sed -n '1,240p' CODESTYLE.md` -> pass (first codestyle section read)
Command: `sed -n '241,520p' CODESTYLE.md` -> pass (remaining codestyle section read)
Command: `sed -n '1,260p' Docs/agents/19-high-signal-steering-feedback.md` -> pass (steering uptake/systemic scope contract read)
Command: `sed -n '1,260p' Docs/agents/04-validation.md` -> pass (repo validation contract read)
Command: `git diff -- Infrastructure/config/schemas/skills-sdk/skill-intake-review-receipt.v0.schema.json` -> pass (schema diff inspected)
Command: `git diff -- Infrastructure/scripts/lib/ask/skills_sdk/local_score.py` -> pass (local-score diff inspected)
Command: `jq '.' .harness/reports/worker-handoffs/pr313-postmerge-review-followups/worker-01-skill-intake-review-receipt.json` -> pass (Worker 01 handoff inspected)
Command: `jq '.' .harness/reports/worker-handoffs/pr313-postmerge-review-followups/worker-02-local-score.json` -> pass (Worker 02 handoff inspected)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache PYTHONPATH=/Users/jamiecraik/dev/agent-skills/Infrastructure/tests bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_schema_spine.TestSkillsSdkSchemaSpine.test_skill_intake_review_receipt_schema_rejects_review_without_package_signature` -> pass (1 test OK)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache PYTHONPATH=/Users/jamiecraik/dev/agent-skills/Infrastructure/tests bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_skill_intake_review.TestSkillsSdkSkillIntakeReview.test_schema_fixture_consumes_risk_mode_receipt` -> pass (1 test OK)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_local_score.TestSkillsSdkLocalScore.test_builder_honors_suite_level_scenario_quality_blockers` -> pass (1 test OK)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_local_score` -> pass (7 tests OK)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache PYTHONPATH=/Users/jamiecraik/dev/agent-skills/Infrastructure/tests bash Infrastructure/scripts/run-infrastructure-python.sh - <<'PY' ... PY` -> pass (manual matrix rejected review missing signature, review null signature, pass missing signature, pass null signature; accepted blocked null signature; verified local-score suite blocker blocks impact)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache PYTHONPATH=/Users/jamiecraik/dev/agent-skills/Infrastructure/tests bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_schema_spine` -> pass (96 tests OK)
Command: `XDG_CACHE_HOME=/tmp/agent-skills-test-cache XDG_STATE_HOME=/tmp/agent-skills-test-state MISE_CACHE_DIR=/tmp/agent-skills-test-mise-cache MISE_STATE_DIR=/tmp/agent-skills-test-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/tmp/agent-skills-test-uv-cache PYTHONPATH=/Users/jamiecraik/dev/agent-skills/Infrastructure/tests bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_skill_intake_review` -> fail (27 tests ran; 5 failures remain around `valid_skill` being blocked by intake quarantine, including `approved_top_level_paths` evidence for `README.md`)
Command: `git diff --check` -> pass (no whitespace errors reported)

## Decision

accept_with_advisory

I could not disprove the focused Worker fixes. The implementation satisfies the two review-thread concerns in local deterministic proof.

Do not claim the broader skill-intake review suite is green. Do not claim hosted GitHub review threads are resolved. Do not claim PR readiness, mergeability, cleanup safety, release readiness, or project completion from this QA lane.

## Claims Boundary

Proves:

- Current branch schema rejects pass/review receipts when `package_security_signature_receipt` is missing or null.
- Current branch schema still accepts the blocked/null route.
- Current branch local-score impact lane blocks suite-level scenario-quality blockers even when row-level `blocked_count` is 0.
- Focused schema/local-score tests pass locally through the repo Infrastructure wrapper.
- Full schema spine suite passes locally.

Does not prove:

- Hosted PR #313 review-thread resolution.
- Any new PR is ready, green, mergeable, reviewed, or safe to clean up.
- Full skill-intake review suite health.
- Base-branch/pre-existing classification for the remaining skill-intake review failures.
- Linear, CircleCI, CodeRabbit, or external tracker state.
- Project completion.

WROTE: artifacts/reviews/default.md
