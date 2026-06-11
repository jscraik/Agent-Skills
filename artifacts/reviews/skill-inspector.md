schema_version: 1
review_scope: "current diff for synaipse lifecycle SDK shape"
target_skills:
  - "Plugins/synaipse-harness"
  - "Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py"
  - "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json"
findings:
  - severity: high
    file: "[Plugins/synaipse-harness/.codex-plugin/plugin.json](/Users/jamiecraik/dev/agent-skills/Plugins/synaipse-harness/.codex-plugin/plugin.json#L33)"
    evidence: "The plugin manifest still points skills at ./skills/, but find Plugins/synaipse-harness/skills -maxdepth 2 -mindepth 1 only returns .DS_Store, and git diff --name-status -- Plugins/synaipse-harness/skills shows only deletions for the old sy-* directories."
    impacted_behavior: "The plugin advertises a stage-based skill surface, but no shipped stage skill directories are present in the current tree, so routing cannot load the 12-stage lifecycle."
    remediation: "Restore or add the replacement stage skill directories before merging, and verify the package root contains the expected skill sources."
    confidence: high
  - severity: high
    file: "[Plugins/synaipse-harness/references/routing-map.json](/Users/jamiecraik/dev/agent-skills/Plugins/synaipse-harness/references/routing-map.json#L5)"
    evidence: "The README and routing map both publish sy-spec (README.md:34, routing-map.json:11), but the requested SDK shape calls for sy-slice-spec, and no sy-slice-spec directory exists under Plugins/synaipse-harness/skills/."
    impacted_behavior: "Consumers that follow the requested 12-stage contract will not find the slice-spec stage, so stage selection and handoff routing diverge from the expected SDK shape."
    remediation: "Rename or alias the stage consistently to sy-slice-spec across the skill tree, routing map, and docs, then regenerate any derived metadata."
    confidence: high
severity_summary:
  high: 2
  medium: 0
  low: 0
validation_evidence:
  - command: "git diff --name-status -- Plugins/synaipse-harness/skills"
    outcome: "pass"
    evidence: "Only deletions are present for the prior sy-* stage directories."
  - command: "find Plugins/synaipse-harness/skills -maxdepth 2 -mindepth 1"
    outcome: "pass"
    evidence: "No stage skill directories exist in the current tree."
  - command: "python3 -m pytest -q Infrastructure/tests/test_skills_sdk_review_plan.py"
    outcome: "pass"
    evidence: "13 passed, 15 subtests passed in 0.50s."
blocked_items: []
recommended_actions:
  - "Restore the skill-tree additions or rename the deleted stage tree in the same patch so the package contains executable stage sources."
  - "Replace every sy-spec reference with sy-slice-spec, or introduce an explicit compatibility alias if backward compatibility is required."
  - "Re-run the package validator after the stage tree is restored."
go_no_go: no_go
accountability_receipt:
  status: complete
  artifact_paths:
    - "artifacts/reviews/skill-inspector.md"
    - "artifacts/agent-runs/skill-inspector-20260608-01/manifest.json"
  findings:
    - "Stage skill directories were removed without visible replacements."
    - "The published stage name still says sy-spec instead of the requested sy-slice-spec."
  failures_or_blockers: []
  improvement_opportunities:
    - "Keep rename/migration patches paired so routing docs and executable skill directories move together."
    - "Add a quick tree-existence check to the review path before relying on manifest or docs changes."
  strengths:
    - "Targeted review-plan schema tests passed, so the findings stay scoped to the SDK shape issue."
    - "The package manifest and routing docs make the intended stage surface easy to inspect."
  validation_evidence:
    - "git diff --name-status -- Plugins/synaipse-harness/skills"
    - "find Plugins/synaipse-harness/skills -maxdepth 2 -mindepth 1"
    - "python3 -m pytest -q Infrastructure/tests/test_skills_sdk_review_plan.py"
  next_action: "Restore the stage tree and align the stage name before merging."
manifest_path: "artifacts/agent-runs/skill-inspector-20260608-01/manifest.json"
WROTE: artifacts/reviews/skill-inspector.md
