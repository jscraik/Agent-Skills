# Tessl Tile Scenario Contract

Use this contract when the requested output is a portable tile eval pack under
`<tile>/evals/`. These scenarios measure whether a skill changes agent
behavior in a one-shot, file-based harness.

## Harness Constraints

- The agent receives one task and then writes files in its workspace.
- No proprietary software, API keys, special accounts, or extra files are
  available unless the task inlines them.
- The task must be finishable in about 10 minutes.
- The agent cannot ask follow-up questions.
- The scorer sees only final workspace files, not chat logs, tool logs, or the
  agent's hidden process.
- The task should avoid large downloads and large generated outputs. If a
  necessary workflow may create files larger than 50 MB, require cleanup or mark
  the capability infeasible.

## Required Output Shape

```text
<tile>/evals/
├── instructions.json
├── summary.json
├── summary_infeasible.json
└── scenario-N/
    ├── task.md
    ├── criteria.json
    └── capability.txt
```

`scenario-N` folders are zero-indexed and sequential. Do not create folders for
infeasible capabilities.

## Instruction Inventory

Start by reading `SKILL.md` and referenced files under `references/`,
`scripts/`, and other package folders. Extract every instruction that directs
an agent to do or avoid a specific thing, including library choices, command
contracts, magic values, file formats, proprietary workflow knowledge, and
warnings.

`instructions.json` must list each instruction with:

- `instruction`: the behavior to test.
- `original_snippets`: source substrings with enough surrounding context.
- `relevant_when`: the scenario shape where the instruction matters.
- `why_given`: one of `reminder`, `new knowledge`, or `preference`.

Prefer scenario coverage for `preference` and `new knowledge` instructions
before generic reminders.

## Scenario Planning

Plan feasible scenarios before writing folders. Group related instructions into
cohesive real-world tasks that a capable baseline could solve in more than one
reasonable way, where the skill's guidance changes the likely answer.

Mark a capability infeasible when the harness cannot observe it from final
files, needs external accounts or unavailable software, requires large state, or
cannot fit the time budget. Record infeasible items in
`summary_infeasible.json` only.

## Scenario Files

`capability.txt` is a single short line naming the capability under test.

`task.md` is the user-visible task. It must be self-contained and actionable.
Inline any input files the agent needs. Do not reveal the hidden instruction,
rubric, criteria, fixture identity, eval harness, or exact expected answer.

`criteria.json` uses `type: weighted_checklist`. Checklist items must:

- sum to exactly 100;
- map to skill-specific instructions from `instructions.json`;
- be feasible to grade from final files;
- be binary or near-binary where possible;
- avoid generic completion, style, or quality checks unless the skill explicitly
  teaches them;
- avoid scoring skill-name mentions, source file paths, or copied rubric text.

## Summary Files

`summary.json` reports total feasible scenarios, instruction coverage,
coverage percentage, and reason distribution for `reminder`, `new knowledge`,
and `preference`.

`summary_infeasible.json` reports the number and reason for every infeasible
scenario idea.

## Validation Checklist

- Every `criteria.json` checklist sums to 100.
- Every criterion can point to an instruction in `instructions.json`.
- No criterion's hidden answer is copied into `task.md`.
- Scenario folders are sequential and contain exactly the required files.
- Input files are inlined in `task.md`; no task promises later setup.
- No task says it is an eval, simulation, fixture, criteria check, or hidden
  rubric exercise.
- Any process evidence needed for scoring is requested as an output artifact.
