# KnowledgeOS Handoff Conversion

Use this reference when converting handoff eval scenarios from
`~/dev/knowledge-OS/exports/evals/references/evals/*.md` into SDK-owned eval
assets.

## Source Shape

KnowledgeOS handoff eval markdown commonly contains:

- title: `eval.<family>.<slug>: <name>`;
- `Promotion status`;
- `Proof route`;
- `Fixture path`;
- `Knowledge claim`;
- `Behavior under test`;
- `Failure mode`;
- `Expected agent move`;
- `Skill lift before failure`;
- `Skill lift after behavior`;
- `Observable delta`;
- `Given`;
- `Should`;
- `Expected failure`;
- `Bad answer patterns`;
- `Good answer patterns`.

Treat the handoff file as a portable reproduction contract, not as canonical SDK
ownership proof.

## SDK Mapping

Map the handoff into `references/evals.yaml` as follows:

- `id`: stable slug from the source filename without `.md`.
- `name`: title after the colon, converted to a concise human name.
- `category`: choose one of the runner-supported SDK categories:
  `happy`, `negative`, `pressure`, or `edge`.
- `eval_modes`: usually `[smoke, release]` for promoted or candidate
  behavior scenarios.
- `should_trigger`: `true` when the target skill should handle the task.
- `realistic`: `true` unless the handoff explicitly says the case is
  synthetic-only.
- `why_realistic`: derive from `Behavior under test` and the operator
  pressure described by `Given`.
- `unit`: compact behavior family, for example `CI truth`,
  `merge readiness`, `architecture proof`, or `claim lineage`.
- `given`: copy or lightly compress the `Given` line.
- `should`: copy or lightly compress the `Should` line.
- `prompt`: write a realistic user-facing task that creates the situation
  without copying `Expected agent move`, `Expected failure`, or answer
  patterns into visible task text.
- `acceptance`: convert `Expected agent move`, `Observable delta`, and
  `Good answer patterns` into scorer-visible expected signals.

Preserve `Knowledge claim`, `Failure mode`, `Expected failure`, bad/good
patterns, source file path, fixture path, and promotion status as evidence notes
in a reviewed fixture under `references/evals/*.md` when the detail is too large
for `references/evals.yaml`.

## Review Rules

- Do not import raw handoff text without review against
  `gold-scenario-contract.md`.
- Do not vendor KnowledgeOS validation-workspace-only fixtures into SDK-ready
  exports unless the target skill owns and reviews them.
- Do not claim the scenario is staged, live-ready, or installed just because the
  handoff export exists.
- Keep proof lanes separate: KnowledgeOS export structure, SDK canonical import,
  SDK scenario-quality, Tessl staging, live scoring, CI state, review state, and
  merge readiness are different evidence.
- Avoid task leakage: `Expected agent move`, `Expected failure`, and answer
  pattern text belong in hidden expected behavior or acceptance metadata, not in
  user-visible `prompt`.

## Batch Conversion Checklist

- Handoff files must have unique SDK ids.
- SDK categories must be runner-supported: `happy`, `negative`, `pressure`,
  or `edge`.
- Converted cases include the original fixture path in evidence metadata
  or a reviewed fixture file.
- Each converted case preserves the failure mode and observable delta.
- Baseline failure paths are plausible before skill context is added.
- No converted prompt exposes hidden answer patterns or fixture paths.
- Scenario-source proof later records the origin as KnowledgeOS handoff plus
  reviewed SDK import, not raw generated output.
