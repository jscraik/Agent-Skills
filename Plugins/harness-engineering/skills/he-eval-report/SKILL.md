---
name: he-eval-report
description: "Generate HE eval and drift proof. Use when Linear or milestone closure needs validation."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Eval Report
## Philosophy
Implementation is not completion. Completion requires closure proof tied to the approved slice, the validation evidence, and the drift posture of the system after the change.
## When to Use
Use when after an HE implementation slice is complete and before recommending Linear parent issue, milestone, project, or execution-slice closure.
## Inputs
Completed implementation, selected execution slice, source harness artifacts under `.harness/{linear,refactors,decisions,core,strategy,triage,brainstorm,spec,plan,solutions}/`, validation output, diff, branch, PR, Linear identifiers, and any proof artifacts.
## Outputs
Write `.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<linear-parent-issue-or-milestone>-eval.md` when Linear context is known, or `.harness/evals/YYYY-MM-DD-<repo-name>-<linear-parent-issue-or-milestone>-eval.md` when no issue is known. Return schema_version when structured with evaluated_slice, validation_results, agentic_eval_validity, agent_native_scorecard when relevant, drift_validation, proof_artifacts, closure_recommendation, follow_up_work, core_adr_update_recommendation, blocked_by, and next_handoff. Apply Artifact Identity frontmatter from `Plugins/harness-engineering/references/artifact-routing-contract.md` so the eval shares the same `canonical_slug` as the Linear/spec/plan chain.
## Procedure
1. Resolve the stage context contract and identify exactly one evaluated slice; do not evaluate adjacent work.
2. Load the eval report contract, schema, template, drift taxonomy, Linear completion policy, and relevant source artifacts for the selected slice.
3. Classify source artifacts by content shape before path so mismatched titles, dates, or Linear identifiers become traceability findings.
4. Compare implementation against the Linear plan, refactor program, plugin HE spec, ADRs, core invariants, and proof artifacts.
5. Prove agentic eval validity before closure, including task validity, outcome validity, trajectory/process evidence, grader coverage, trial policy, side-effect authorization, and saturation or maintenance signal.
6. Apply agent-native audit and specialist-skill steering only when closure depends on those proof areas.
7. Run or explicitly block relevant validation gates; never invent passing results.
8. Generate and validate the report, then ask accept/challenge/rework before using `Complete` or `Complete with follow-up` as a Linear closure recommendation.
## Validation
Fail fast: stop at the first failed gate. Run `python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py <report-path>`, `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <report-path>`, and `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py <report-path>`; record exact command results. If the eval artifact is missing, incomplete, untraceable, or materially failing, closure recommendation must be `Blocked`, `Needs rework`, or `Unsafe to close`.
## Failure mode
If Linear identifiers, source artifacts, validation evidence, or the evaluated slice cannot be resolved, write the gap into the report, classify closure safety, and state the smallest repair before completion.
## Execution Boundaries
Eval reporting writes proof artifacts only. Do not close Linear work, update tracker status, or recommend closure from `Complete` classifications until accept/challenge/rework steering is complete.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- Missing validation is not a pass.
- Eval scope is the selected slice only; adjacent work belongs in follow-up classification.
## Constraints
Redact secrets. Preserve user edits. Do not remove important context for budget trimming; move deep context to references. Do not repeat the implementation spec, produce generic QA notes, rubber-stamp completion, or create Linear follow-ups for every observation.
## Anti-Patterns
- Recommending closure from implementation status alone.
- Marking unavailable validation as passing.
- Evaluating adjacent work outside the selected slice.
- Turning drift validation into vague architecture commentary.
- Creating issue noise for non-blocking or low-value observations.
## Examples
- "Generate the HE eval report for JSC-246 before we close the Linear parent."
- "The implementation is done; validate drift, proof artifacts, and whether this milestone is safe to close."
- "Use `he-eval-report` on this PR and tell me whether completion is blocked, needs rework, or complete with follow-up."
## Assets
Reference `assets/` only for skill packaging and browseability. Eval proof belongs in `.harness/evals/**`, PR evidence, validation logs, and Linear comments.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Agent-native audit scorecard: `Plugins/harness-engineering/references/agent-native-audit-scorecard.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Eval report contract: `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-contract.md`
- Eval report schema: `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-schema.json`
- Eval report template: `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-template.md`
- Drift taxonomy: `Plugins/harness-engineering/skills/he-eval-report/references/drift-taxonomy.md`
- Linear completion policy: `Plugins/harness-engineering/skills/he-eval-report/references/linear-completion-policy.md`
- Artifact identity: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Artifact classification: `Plugins/harness-engineering/references/artifact-classification-and-traceability.md`
- Local contract: `Plugins/harness-engineering/skills/he-eval-report/references/contract.yaml`
- Eval cases: `Plugins/harness-engineering/skills/he-eval-report/references/evals.yaml`
- Shared eval case projection: `Plugins/harness-engineering/references/he-eval-report-evals.yaml`
