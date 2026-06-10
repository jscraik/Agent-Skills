# CodeRabbit Review

## Review Command
- coderabbit review --agent --base main --files Infrastructure/config/skills-sdk/capability-matrix.v1.json Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py artifacts/recommended-skills-sdk-pipeline.html

## Findings

### Medium: Generated pipeline HTML points the repo marketplace root at the wrong path
- artifacts/recommended-skills-sdk-pipeline.html:2787
- Impact: the new "Canonical Marketplace Files" card tells readers to use repo .agents/plugins/marketplace.json, but the repo-level marketplace manifest used throughout the codebase and tests is Plugins/marketplace.json. That makes the generated guidance internally inconsistent and risks sending follow-up work toward the wrong root.
- Evidence: [artifacts/recommended-skills-sdk-pipeline.html:2787](/Users/jamiecraik/dev/agent-skills/artifacts/recommended-skills-sdk-pipeline.html#L2787) says repo .agents/plugins/marketplace.json; [Infrastructure/tests/test_ask_plugins_commands.py:104-110](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_plugins_commands.py#L104) documents and writes the repository-level Plugins/marketplace.json.
- Minimal fix: change the HTML card to refer to Plugins/marketplace.json for the repo root, and keep ~/.agents/plugins/marketplace.json only for the personal/home root.
- Validation ownership: introduced by current patch.

## Rejected or Unconfirmed
- No other confirmed findings from the edited Python validator or capability matrix after targeted validation.

## Validation
- python3 -m pytest -q Infrastructure/tests/test_skills_sdk_capability_status.py passed.
- python3 -m pytest -q Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_local_plugin_picker_surface.py failed in the local-plugin picker suite, but the failures were in pre-existing dirty-tree surfaces unrelated to the three edited files.
- coderabbit review --agent --base main --files Infrastructure/config/skills-sdk/capability-matrix.v1.json Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py artifacts/recommended-skills-sdk-pipeline.html produced no readable structured output in this environment, so the source-based validation above was used for confirmation.

## Accountability Receipt
- status: complete
- artifact_paths:
  - artifacts/reviews/coderabbit.md
  - artifacts/agent-runs/coderabbit-20260608T204500Z/manifest.json
- manifest_path: artifacts/agent-runs/coderabbit-20260608T204500Z/manifest.json
- findings:
  - severity: medium
    file:line: artifacts/recommended-skills-sdk-pipeline.html:2787
    impact: repo-level marketplace guidance points at the wrong root
    remediation: replace .agents/plugins/marketplace.json with Plugins/marketplace.json
    confidence: high
    validation_ownership: introduced by current patch
- failures_or_blockers:
  - coderabbit review --agent produced no readable review text in this environment
  - broader plugin-picker tests failed on unrelated dirty worktree drift
- improvement_opportunities:
  - keep generated docs aligned with the canonical repo marketplace path naming
  - consider a small assertion test for the rendered HTML marketplace path strings
- strengths:
  - the capability-status validator update is internally consistent and the targeted matrix test passes
  - the patch cleanly separates local plugin readiness from remote marketplace scope
- validation_evidence:
  - Infrastructure/tests/test_skills_sdk_capability_status.py passed
  - current-patch source inspection matched the repo-level marketplace convention in Infrastructure/tests/test_ask_plugins_commands.py
- useful_findings:
  - the repo marketplace path convention is Plugins/marketplace.json
- avoided_false_positive:
  - did not treat unrelated failures in Infrastructure/tests/test_local_plugin_picker_surface.py as patch regressions
- evidence_quality:
  - medium-high
- followed_scope:
  - yes
- reusable_learning:
  - repo-local marketplace guidance must stay consistent with the write path used in the plugin command tests
- coordinator_score:
  - 8/10

WROTE: artifacts/reviews/coderabbit.md
