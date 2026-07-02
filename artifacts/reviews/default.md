# PR #301 Green Sweep Review-Thread Repair

STATUS: blocked_policy_or_approval

PR: https://github.com/jscraik/Agent-Skills/pull/301
Latest pushed head: 97c4ba5f402a1ebf909b0c2c32c86bcf3774bbf7
Commit created: 97c4ba5f4 fix: preserve tessl fallback signals

## What Changed

- Patched `TesslRegistrySnapshot.impactMetric` so a Tessl registry payload with only `scenarioCount` and no `impactScore` returns nil, preserving the local impact signal.
- Patched `TesslRegistrySnapshot.securitySignal` so clean strings such as `no issues`, `clean`, or `clear` classify as Passed before the issue/fail/flag substring branch.

## Evidence

- Command: `PYTHONPYCACHEPREFIX=/private/tmp/pr301-pycache python3 -m py_compile Infrastructure/scripts/validation-and-linting/run_oss_local_smoke.py Infrastructure/scripts/validation-and-linting/check_oss_local_smoke_output.py Infrastructure/scripts/validation-and-linting/validate_skills_sdk_release_ratchets.py Infrastructure/scripts/testing/test_validate_skills_sdk_release_ratchets.py` -> pass.
- Command: `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/pr301-pycache python3 -m pytest -q Infrastructure/scripts/testing/test_validate_skills_sdk_release_ratchets.py Infrastructure/tests/test_oss_local_smoke_output_check.py` -> pass, 25 passed.
- Command: `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json` -> pass.
- Command: `CLANG_MODULE_CACHE_PATH=/private/tmp/improve-agent-native-menubar-clang-cache xcrun swiftc -parse Prototypes/improve-agent-native-menubar/Sources/ImproveAgentNativeMenuBar/App.swift` -> pass.
- Command: `git diff --check` -> pass.
- Command: `git commit -m "fix: preserve tessl fallback signals"` -> pass, created 97c4ba5f4.
- Command: `GIT_TERMINAL_PROMPT=0 git push origin HEAD:codex/qwen-local-eval-guardrails` -> pass, pushed 497f4de21..97c4ba5f4.
- Command: `gh pr checks 301 --repo jscraik/Agent-Skills --watch=false` -> blocked in latest poll only by pending Semgrep (SAST) and Semgrep OSS; no failure observed.
- Command: `gh api graphql resolveReviewThread ...` -> blocked by tenant policy denying review-thread mutation without explicit user approval.

## Remaining Blockers

- GitHub review-thread mutation needs explicit PM/user approval or a supported resolver path.
- PR #301 still had Semgrep (SAST) and Semgrep OSS pending in the latest hosted-check poll.
- GraphQL still reported one live unresolved App.swift review thread after the source patch.
- Primary checkout remains dirty and was not used or cleaned.

---

# Qwen OSS-Local Case Repair Review

STATUS: blocked_runtime

Thread report: `.harness/reports/thread-replies/019f2458-ad2a-76e1-8c74-052484d452ed/latest.json`
Current gate: `oss-local-qwen-behavior-eval`
Focused case: `happy-agents-md-audit`

## Owner Classification

The original completed failure was owned by scenario criteria, not skill behavior:

- The prompt asked to audit AGENTS.md files in "a repo" without naming the current working repository as the target.
- The qwen response therefore asked for the missing target repository.
- Several `expected_signal` criteria scored boilerplate wording such as "Semantically covers the scenario-specific evidence and decision signals" instead of observable output obligations.

The current blocker after the scenario repair is runtime/runner completion:

- The focused qwen run now creates only `prompt.txt`.
- No `scorecard.json`, Codex final answer, stdout, or stderr artifact was emitted for the latest run.

## Files Changed

- `Skills/agent-ops/improve-agent-native/references/evals.yaml`
- `Infrastructure/scripts/lib/ask/skills_sdk/tessl_eval_quality.py`
- `Infrastructure/tests/test_skills_sdk_tessl_eval_quality.py`
- `.harness/reports/thread-replies/019f2458-ad2a-76e1-8c74-052484d452ed/latest.json`

## Evidence

- Command: `sed -n '1,160p' Infrastructure/artifacts/skills/improve-agent-native/20260702-222317-856935/01-happy-agents-md-audit/codex/final.txt` -> pass. Evidence: qwen asked which target repository to audit.
- Command: `apply_patch Skills/agent-ops/improve-agent-native/references/evals.yaml` -> pass. Evidence: scenario now names the current working repository and removes scorer-boilerplate expected-signal wording.
- Command: `apply_patch Infrastructure/scripts/lib/ask/skills_sdk/tessl_eval_quality.py Infrastructure/tests/test_skills_sdk_tessl_eval_quality.py` -> pass. Evidence: added `scorer_boilerplate_expected_signal` rule and regression test.
- Command: `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/qwen-case-pycache PYTHONPATH=/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_skills_sdk_tessl_eval_quality.py::test_expected_signal_rejects_scorer_boilerplate` -> pass, 1 passed.
- Command: `PYTHONPYCACHEPREFIX=/private/tmp/qwen-case-pycache python3 -m py_compile Infrastructure/scripts/lib/ask/skills_sdk/tessl_eval_quality.py` -> pass.
- Command: `XDG_CACHE_HOME=/private/tmp/agent-skills-xdg-cache XDG_STATE_HOME=/private/tmp/agent-skills-xdg-state MISE_CACHE_DIR=/private/tmp/agent-skills-mise-cache MISE_STATE_DIR=/private/tmp/agent-skills-mise-state MISE_TRUSTED_CONFIG_PATHS=/Users/jamiecraik/dev/agent-skills/.mise.toml UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache ./bin/ask sdk eval run Skills/agent-ops/improve-agent-native --runner internal --mode smoke --codex-profile oss-local --timeout-seconds 45 --case happy-agents-md-audit --json --robot; code=$?; echo ASK_EXIT:$code; exit $code` -> blocked. Evidence: artifact directory `Infrastructure/artifacts/skills/improve-agent-native/20260702-223706-917494` contains `prompt.txt` only; `scorecard.json` is missing.
- Command: `python3 Infrastructure/scripts/validation-and-linting/validate_thread_report.py .harness/reports/thread-replies/019f2458-ad2a-76e1-8c74-052484d452ed/latest.json --json` -> pass.

## Next Step

Continue in the runner/runtime lane for this same focused case. Do not broaden to oss-local release eval, oss-cloud, Tessl dry-run, or Tessl live until `happy-agents-md-audit` produces a scorecard receipt.
