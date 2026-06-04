---
name: sy-improve
description: "Improves SynAIpse Harness skill-package artifacts by rewriting vague skill descriptions, fixing failing eval assertions, updating stage contracts, tightening references, and rerunning the failed check. Use when a SynAIpse skill needs improvement, a stage description is too vague, an eval is failing, or audit, Tessl, plugin-eval, or stage-review feedback identifies a package fix."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: none
  runtime_visibility: hidden
---
# SynAIpse Harness Improve

## Philosophy

Turn a specific quality finding into the smallest durable source change, then
prove that the same gate no longer reports the issue.

## When to Use

Use this skill when a SynAIpse skill needs improvement, a stage description is too vague, an eval is failing, a contract is missing fields, or audit output, Tessl review, plugin-eval feedback, or stage-review feedback identifies a skill, plugin, reference, contract, or eval that needs fixing. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-router` hands off to `sy-improve`.

## Inputs

Collect only the inputs needed to reproduce and fix the quality finding:

- exact finding text, score, failed assertion, or reviewer comment
- source path to the affected `SKILL.md`, `references/evals.yaml`, contract, fixture, or plugin metadata
- failed command, such as `./bin/ask skills audit <skill-path> --level strict --json --robot`, `plugin-eval analyze <plugin-path> --format json`, or `./bin/ask skills external-review <skill-path> --audit-level compat --skip-plugin-eval --json --robot`
- approved scope, non-goals, and current worktree status

## Procedure

1. Quote and classify the finding before editing:
   - Record `git status --short --branch`.
   - Quote the failing audit code, Tessl score reason, plugin-eval finding, or reviewer comment.
   - Classify the mechanism as `description_trigger_gap`, `abstract_procedure`, `eval_schema_gap`, `contract_gap`, `reference_drift`, or `security_boundary_gap`.
2. Choose the smallest canonical source file:
   - Edit `SKILL.md` for trigger wording, workflow clarity, examples, constraints, or actionability.
   - Edit `references/evals.yaml` for scenario coverage, schema, assertions, or prompt-injection cases.
   - Edit `references/contract.yaml` for required fields, boundaries, output shape, or observability.
   - Do not edit generated projections or runtime cache copies unless the user explicitly asks.
3. Apply the narrow improvement:
   - Rewrite vague descriptions with concrete verbs and natural trigger phrases.
   - Replace abstract procedure steps with exact commands, paths, field names, and fail-fast branches.
   - Keep unrelated cleanup out of scope and preserve user-owned dirty work.
4. Rerun proof in order:
   - First rerun the exact failed command from the finding.
   - Then run the nearest adjacent gate: `./bin/ask skills audit <skill-path> --level strict --json --robot`, `plugin-eval analyze <plugin-path> --format json`, or `./bin/ask skills external-review <skill-path> --audit-level compat --skip-plugin-eval --json --robot`.
   - If the same finding remains, stop, record `given`, `expected`, `actual`, `reproduce_command`, and return to step 2.
5. Report the durable improvement:
   - Name the source file changed, the finding fixed, the validation commands rerun, and any related cleanup intentionally skipped.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-improve`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `improvement_patch`: the concrete stage deliverable
- `evidence_checked`: current evidence read during this stage
- `validation`: exact command outcomes as `pass`, `fail`, or `blocked`
- `open_risks`: remaining risks or unproven lanes
- `next_stage`: recommended next SynAIpse stage, or `none`

## Execution Boundaries

Do not mutate trackers, PRs, external services, or protected files unless the
user gave that authority in the current task. This stage cannot claim CI,
review, tracker, merge, deployment, or closure readiness unless that lane was
checked in the same run.

## Constraints

Redact secrets and sensitive data by default. Do not expose tokens, credentials,
private session contents, or local-only telemetry. Prefer exact evidence over
confidence.

## Validation

Fail fast: stop at the first failed required gate and do not proceed to later
claims or external readiness. Say which evidence was read and which lanes were
not checked. Local files do not prove CI, review threads, tracker state, PR
mergeability, or deployment readiness.

## Failure Mode

If the next action depends on authority, destructive behavior, external writes,
publication, or closure proof, stop and ask for that missing input. If only a
minor detail is missing, proceed with a named assumption and mark it as
changeable.

## Examples

Input: "Use sy-improve for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-improve
target: JSC-244
decision: "Improve Tessl score"
deliverable:
  finding: "description and body were too generic"
  fix: "added decision matrix method and concrete example"
  validation: "pass: ./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-improve --audit-level compat --skip-plugin-eval --json --robot"
evidence_checked:
  - "current local context read in this run"
validation:
  - "blocked: PR, CI, review, and tracker state were not checked in this run"
open_risks:
  - "external readiness is unknown until live PR and tracker state are refreshed"
next_stage: sy-reconcile
~~~

## Gotchas

- Yesterday's proof is context, not current evidence.
- Do not patch around an evaluator; fix the mechanism it identified.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Editing runtime cache output when canonical plugin source exists.
- Expanding into unrelated refactors while fixing one quality finding.

## References

This skill is self-contained for normal quality-fix work. Open optional repo
references only when the finding names contract, eval, benchmark, or source
provenance details:

- `references/contract.yaml`: compact stage contract.
- `references/evals.yaml`: strict audit and Tessl scenario coverage.
- `references/task-profile.json`: family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root`: preserved source
  material from the imported replacement package.
