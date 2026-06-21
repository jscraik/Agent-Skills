# Eval Improvement Contract

Use this reference when scenario generation or scenario review involves an
eval-driven improvement loop for a Tessl tile or a codebase context pack.

## Inputs To Preserve

Capture the scenario name, criterion name, max score, baseline score,
with-context score, aggregate scenario delta, relevant `criteria.json`, and the
context files that could teach or confuse the behavior.

For tile evals, inspect `skills/**/SKILL.md`, `rules/**/*.md`, and
`docs/**/*.md`. For codebase evals, inspect the target repo's context files
such as `AGENTS.md`, `CLAUDE.md`, Copilot instructions, or rule files.

## Bucket Classifier

- Bucket A, working: with-context score is at least 80% of max and materially
  better than baseline. Preserve this behavior.
- Bucket B, tile gap: baseline and with-context are both below 80%. Add the
  missing tile or context guidance if the criterion is valid.
- Bucket C, redundant: baseline is already at least 80%. Flag the criterion as
  low-lift and ask whether to remove, harden, or keep it as a sanity check.
- Bucket D, regression: with-context is lower than baseline. Investigate first;
  look for confusing, contradictory, overly broad, or recently added guidance.

Bucket D outranks Bucket B. A regression means context is making the agent worse,
so adding more instructions may deepen the problem unless the contradiction is
understood.

## Fix Protocol

For each Bucket B or D item:

1. State what the rubric wants.
2. State what the current tile or context says.
3. State the gap, contradiction, or ambiguity.
4. Show the proposed file edit before applying it when the user asks to preview
   changes.
5. Apply the smallest targeted edit.
6. Lint or validate the changed tile or context pack.
7. Commit only changed files after approval.
8. Rerun the same eval lane and compare before versus after.

For tile evals, `tessl tile lint <tile-path>` proves local package shape only.
It does not prove scenario improvement. `tessl eval run ./evals/ --workspace
<workspace>` plus `tessl eval compare ./evals/ --breakdown --workspace
<workspace>` provide the rerun evidence.

## Consistency Audit

Before fixing regressions, scan all relevant tile files for contradictions, not
only the criterion named in the failure. Common causes include retry counts,
backoff timing, abort-versus-continue behavior, authentication recovery,
optional-versus-required flow steps, and command or file ownership conflicts.

When a consistency audit is the task output, produce `contradiction_report.md`
with every contradiction found, files involved, verbatim conflicting statements,
why they conflict, and a severity note for likely agent confusion or regression.

## Anti-Patterns

- Fixing a Bucket D regression by adding unrelated guidance before finding the
  confusing instruction.
- Treating a local lint pass as proof that eval scores improved.
- Committing unrelated files or generated noise.
- Rewriting working sections and causing Bucket A regressions.
- Removing redundant Bucket C criteria without user approval.
