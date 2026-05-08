---
name: he-eval-report
description: "WHAT: Generate post-implementation HE eval and drift reports before Linear closure. Use when completed work needs proof against the approved slice, validation gates, routing, architecture, context, governance, and moat invariants."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Eval Report
## Philosophy
Implementation is not completion. Completion requires closure proof tied to the approved slice, the validation evidence, and the drift posture of the system after the change.
## When to Use
Use after an HE implementation slice is complete and before recommending Linear parent issue, milestone, project, or execution-slice closure.
## Inputs
Completed implementation, selected execution slice, source harness artifacts under `.harness/{linear,refactors,decisions,core,strategy,triage,brainstorm,spec,plan,solutions}/`, validation output, diff, branch, PR, Linear identifiers, and any proof artifacts.
## Outputs
Write `.harness/evals/<repo-name>-<linear-parent-issue-or-milestone>-eval.md` and return schema_version when structured with evaluated_slice, validation_results, agentic_eval_validity, agent_native_scorecard when relevant, drift_validation, proof_artifacts, closure_recommendation, follow_up_work, core_adr_update_recommendation, blocked_by, and next_handoff. Apply Artifact Identity frontmatter from `Plugins/harness-engineering/references/artifact-routing-contract.md` so the eval shares the same `canonical_slug` as the Linear/spec/plan chain.
## Procedure
Identify the evaluated slice first; do not evaluate unrelated work. Load the eval report contract, template, drift taxonomy, and Linear completion policy. Compare implementation against Linear plan, refactor program, plugin HE spec, ADRs, and core invariants. Prove agentic eval validity before closure: task validity, outcome validity, trajectory/process evidence, grader coverage, trial policy, authorization validation for side-effectual actions, and saturation or maintenance signal. Run or explicitly block relevant validation gates; never invent passing results. Generate the report, validate it with `scripts/validate_eval_report.py`, gather corrections when the user challenges the evidence, and only then recommend Linear status changes.
## Validation
Fail fast: stop at the first failed gate. Run `python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py <report-path>`, `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <report-path>`, and `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py <report-path>`; record exact command results. If the eval artifact is missing, incomplete, untraceable, or materially failing, closure recommendation must be `Blocked`, `Needs rework`, or `Unsafe to close`.
## Failure mode
If Linear identifiers, source artifacts, validation evidence, or the evaluated slice cannot be resolved, write the gap into the report, classify closure safety, and state the smallest repair before completion.
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
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Eval report contract: `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-contract.md`
- Eval report template: `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-template.md`
- Drift taxonomy: `Plugins/harness-engineering/skills/he-eval-report/references/drift-taxonomy.md`
- Linear completion policy: `Plugins/harness-engineering/skills/he-eval-report/references/linear-completion-policy.md`
- Artifact identity: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Local contract: `Plugins/harness-engineering/skills/he-eval-report/references/contract.yaml`
- Eval cases: `Plugins/harness-engineering/skills/he-eval-report/references/evals.yaml`
- Shared eval case projection: `Plugins/harness-engineering/references/he-eval-report-evals.yaml`
