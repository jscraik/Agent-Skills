# Evaluation Harness

## Goal

Evaluate skills as auditable capability packages. A release-readiness claim must
map from source text to scenarios, deterministic checks, trace evidence,
baseline comparison, and a clear pass/fail/blocked decision.

## Claim-To-Evidence Flow

1. Extract explicit claims from SKILL.md, references/contract.yaml, and workflow
   references into references/evals.yaml.
2. Map each claim to at least one scenario through claim_ids.
3. Keep activation checks separate from execution checks:
   - activation: should-trigger, should-not-trigger, and ambiguous-routing cases
   - execution: artifacts, commands, validation, safety, and recovery behavior
4. Compare mature release suites against a declared baseline such as
   previous_version, no_skill, or neutral_repo_baseline.
5. Grade deterministic evidence first, then use semantic review only for quality
   dimensions that cannot be checked mechanically.
6. Preserve machine evidence in JSON artifacts and render the human report from
   an MDX source when a rich report is useful.
7. Export saved run summaries into deterministic macro-eval events before
   doing population-level discovery or clustering.

## Canonical Inputs

- references/evals.yaml: scenario, claim, baseline, and report metadata.
- Infrastructure/templates/evals.yaml: starter template for new eval suites.
- Infrastructure/templates/eval-report.mdx: MDX source template for human eval
  reports backed by machine-readable result data.
- `./bin/ask evals macro-report --json --robot`: deterministic macro-eval
  exporter for saved skill eval summaries.

## Required Scenario Families

- happy: normal in-scope activation and execution.
- edge: missing inputs, ambiguous ownership, stale state, or partial context.
- negative: adjacent work where the skill must not activate.
- pressure: prompt injection, validation bypass, unsafe command, or false
  completion pressure.

## Hard Gates

Hard gates cap release status even when the weighted score looks acceptable:

- no false completion claim
- no validation bypass
- no unsafe command or destructive action outside the approval path
- no missing required artifact
- no unresolved source/projection ownership confusion
- no unredacted secret or raw private telemetry export
- no release claim without version, evaluator version, scenario version, and
  report hash

## Reporting

Human-readable reports should be authored as MDX when the report includes
tables, score vectors, trace panels, or implementation notes. MDX keeps the
report diffable for agents while allowing reusable React components for humans.
When a report is copied out of the template directory, copy or bundle the
declared component module with it; a missing component import is a blocked
report lane, not a successful eval.
The MDX report is not the source of truth for pass/fail status; the JSON
scorecard, release manifest, traces, and staged eval artifacts remain canonical.

## Macro-Eval Export

Run `./bin/ask evals macro-report --json --robot` after smoke or release evals
have produced saved `summary.json` artifacts. The command writes:

- `.harness/archive/2026-08-15-artifact-retirement/infrastructure-artifacts/evals/macro/macro-eval-events.jsonl`
- `.harness/archive/2026-08-15-artifact-retirement/infrastructure-artifacts/evals/macro/macro-eval-report.json`
- `.harness/archive/2026-08-15-artifact-retirement/infrastructure-artifacts/evals/macro/macro-eval-report.mdx`
- `.harness/archive/2026-08-15-artifact-retirement/infrastructure-artifacts/evals/macro/components/eval-report.tsx`

Each JSONL row is one eval case with deterministic labels for `case_type`,
`run_outcome`, `eval_finding`, and `behavior_pattern`. This is the stable input
for later macro discovery, notebooks, or dashboards. The exporter does not claim
BERTopic, AgentTrace, or semantic clustering; it creates the compact evidence
corpus those layers can consume.

## No-Skill Lift Gates

Use `baseline_type: no_skill` when a case should prove that loading the skill
changes the result. The runner executes the same case again without prepending
skill context and records `baseline_comparisons`, `skill_lift`,
`is_beneficial`, and `baseline_regression` in the case summary.
`no_skill` baselines are executable for skill-prepended cases; pair this
baseline with `prepend_skill: true` so the runner has a real skill-enabled run
to compare against the no-skill control.

Add these budgets only when the no-skill control is expected to lose:

```yaml
prepend_skill: true
baseline_type: no_skill
budgets:
  require_skill_lift: true
  min_skill_lift: 1
```

`require_skill_lift` fails the case when the skill-enabled run does not beat the
no-skill baseline. `min_skill_lift` fails the case when the numeric lift is below
the requested threshold. Do not add these budgets to generic acceptance cases
where a capable base model could reasonably pass without the skill; those cases
should still record a baseline or use a neutral baseline decision instead.

## Run Record Template

| Date | Scope | Checks run | Result | Follow-up |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | baseline | claim extraction + scenario matrix + gates | pass/fail/blocked | link to issue/PR |
