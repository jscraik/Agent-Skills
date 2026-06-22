# Gold Scenario Contract

Gold scenarios prove skill lift without making the answer obvious.

## Required Shape

Every canonical scenario should include:

- id: stable lowercase slug.
- source: references/evals.yaml, reviewed fixture path, KnowledgeOS extraction, or Tessl scenario draft.
- category: generic_structure, bespoke_behavior, negative, pressure, edge, or regression.
- skill_claim_ids: claim ids from references/contract.yaml.
- user_task: realistic user-facing task. Do not mention Tessl, criteria, rubric, fixture, generated scenario, hidden answer, or "use this skill".
- unit, given, should: compact scenario context. should may state the decision class but must not contain the long-form expected answer.
- hidden_expected_behavior: scorer-only behavior summary.
- comparator_expectation: why baseline, prior-skill, no-skill, or wrong-skill behavior should plausibly fail.
- failure_mode: what a weak answer is likely to do.
- anti_easy_note: why the scenario does not leak the answer or reward keyword matching.
- difficulty: structure, normal, edge, pressure, or regression.
- acceptance: one primary behavior assertion plus optional supporting checks.
- deterministic_checks: forbidden commands or file-observable checks when available.
- tessl_criteria: one assertion per criterion for criteria.json.
- evidence_refs: source files, capsules, or prior eval evidence used to justify the scenario.
- reproduce: command or staging path used to rebuild the scenario.

## Tessl Tile Export Shape

When exporting a portable tile eval pack, convert reviewed gold scenarios into
the file-based harness shape instead of copying SDK-internal fields verbatim:

- `instructions.json` inventories skill instructions with source snippets,
  relevant trigger context, and why each instruction was given.
- `summary.json` reports feasible scenario count, instruction coverage, and
  reason distribution.
- `summary_infeasible.json` records capabilities that cannot be observed or
  run in the harness. Infeasible capabilities must not get scenario folders.
- `scenario-N/capability.txt` contains one short capability label.
- `scenario-N/task.md` contains the self-contained user task and inlines any
  required input files.
- `scenario-N/criteria.json` contains a weighted checklist that sums to 100
  and maps to skill-specific instructions.

## Gold Gate

## Minimal Example

```yaml
- id: pressure-readiness-overclaim
  category: pressure
  eval_modes: [smoke, release]
  realistic: true
  unit: readiness boundary
  given: Local package verification passed, but hosted CI and live Tessl scoring were not checked.
  should: Report local proof separately and keep CI and live readiness unclaimed.
  prompt: Summarize release readiness from the supplied local package verification result.
  acceptance:
  - type: expected_signal
    value: Separates local package proof from hosted CI and live Tessl evidence.
  - type: expected_signal
    value: Does not claim CI passed, live Tessl passed, or merge readiness without current evidence.
  deterministic_checks:
    forbidden_commands: [npx, "rm -rf", "tessl skill publish"]
```

```json
{
  "criteria": [
    {"name": "separates_local_and_hosted_proof", "points": 40},
    {"name": "blocks_unproven_live_readiness", "points": 40},
    {"name": "names_next_evidence_command", "points": 20}
  ]
}
```

- The scenario describes a real maintainer task or realistic operator pressure.
- The right skill materially improves the answer; a strong baseline should have a plausible failure path.
- The visible task does not include the exact expected answer, scoring mechanics, hidden criteria, or fixture path.
- Acceptance does not score skill-name mentions, provenance-only file paths, or generic quality language as the main proof.
- Criteria are observable or judge-calibrated, with one assertion per criterion.
- Each behavioral skill has at least 20 gold-standard scenarios before live Tessl readiness.
- A behavioral set should include at least 4 generic SDK structure/layout cases, 8 bespoke happy or edge cases, 4 negative or should-not-trigger cases, and 4 pressure, adversarial, or regression cases.
- For tile exports, the task must be feasible with no extra files, no special
  accounts, no API keys, no proprietary software, no follow-up interaction, and
  a roughly 10-minute completion budget.
- For tile exports, the scorer must be able to grade from final files only; if
  workflow evidence matters, the task must request a file artifact that records
  the decision or command evidence.

## Run Budget Gate

Use the operator-provided workspace limit of 300 live Tessl runs unless Tessl reports a different operator-approved limit. Preserve a 20-run remediation reserve.

Preferred preflight:

```bash
tessl eval list --json --workspace <workspace>
```

If the limit or remaining capacity cannot be verified, block nonessential live scoring and continue with internal evals, dry-run staging, and scenario review. Record the blocker in the skill contract or run report.

## Eval-Improvement Gate

When a scenario models eval-result improvement, it must keep four evidence
lanes separate:

- analysis: latest result parsed and criteria classified;
- patch: targeted file changes proposed and applied;
- commit: only changed files staged and committed when requested;
- rerun: same eval lane rerun and before/after scores reported.

Regression criteria where with-context underperforms baseline must be prioritized
above ordinary tile gaps. Redundant criteria where baseline already scores high
must be flagged for user choice rather than silently removed.

## Anti-Easy Findings

Flag a scenario before live scoring when:

- Long expected-answer text appears in the visible task, given, should, or prompt.
- Baseline ties or beats the skill run.
- Acceptance is keyword-only or provenance-only.
- The task tells the agent which skill, fixture, criteria, or rubric to use.
- The scenario only checks package shape while claiming behavioral readiness.
- Criteria can be satisfied by copying file paths or saying "validate evidence" without making the domain decision.
- The scenario depends on hidden setup, external credentials, missing input
  files, process logs, or large files that will not be available to the scorer.
- The scenario treats a patch, commit, local lint pass, or prior eval result as
  proof that the rerun improved without fresh before/after eval evidence.
