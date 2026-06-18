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

## Gold Gate

- The scenario describes a real maintainer task or realistic operator pressure.
- The right skill materially improves the answer; a strong baseline should have a plausible failure path.
- The visible task does not include the exact expected answer, scoring mechanics, hidden criteria, or fixture path.
- Acceptance does not score skill-name mentions, provenance-only file paths, or generic quality language as the main proof.
- Criteria are observable or judge-calibrated, with one assertion per criterion.
- Each behavioral skill has at least 20 gold-standard scenarios before live Tessl readiness.
- A behavioral set should include at least 4 generic SDK structure/layout cases, 8 bespoke happy or edge cases, 4 negative or should-not-trigger cases, and 4 pressure, adversarial, or regression cases.

## Run Budget Gate

Use the operator-provided workspace limit of 300 live Tessl runs unless Tessl reports a different operator-approved limit. Preserve a 20-run remediation reserve.

Preferred preflight:

    tessl eval list --json --workspace <workspace> --limit 300

If the limit or remaining capacity cannot be verified, block nonessential live scoring and continue with internal evals, dry-run staging, and scenario review. Record the blocker in the skill contract or run report.

## Anti-Easy Findings

Flag a scenario before live scoring when:

- Long expected-answer text appears in the visible task, given, should, or prompt.
- Baseline ties or beats the skill run.
- Acceptance is keyword-only or provenance-only.
- The task tells the agent which skill, fixture, criteria, or rubric to use.
- The scenario only checks package shape while claiming behavioral readiness.
- Criteria can be satisfied by copying file paths or saying "validate evidence" without making the domain decision.
