# Skill Builder Repair Policy

Use this reference when a skill-builder run needs deeper repair doctrine after
the entrypoint has selected the package and failing gate.

## Philosophy

Prefer one evidence-backed repair over broad rewriting. A score is useful only
when the artifact, command, baseline, and failed contract are preserved.

## First-Principles Gate

- Desired outcome: repair an existing skill through the Skills SDK proof ladder
  without replacing release evidence with prose.
- User-specific constraints: use repo wrappers, keep oss-local before
  oss-cloud, keep Tessl live as confirmation only, and record lessons as
  guardrails.
- Rejected copied assumption: a better SKILL.md alone proves release readiness.
- Fundamental constraints: existing skill source is canonical; each failed gate
  owns the next patch; warnings must be repaired before promotion.
- Smallest effective mechanism: patch the smallest failed skill, reference,
  eval, or validator surface that changes the failing gate.
- Artifact decision: IMPROVE_EXISTING.
- Rejected alternatives: rewriting the whole skill, running Tessl live before
  SDK receipts, or ignoring scenario drift.
- Evidence required: factory gate receipt, package verify receipt,
  scenario-quality receipt, and oss-local receipt before oss-cloud.
- Validation proof: rerun the failed gate after each repair.
- Stop or pivot condition: after three flat repair loops, stop with
  `blocker_notes` and classify the owning gate.

## Repair Map

- Repeated guidance: delete the duplicate `SKILL.md` sentence; rerun the same
  score gate.
- Vague validation: add `Command: ... -> pass|fail|blocked`; audit or release
  status must be `success`.
- Missing recovery: add the named failed-gate branch; rerun that gate.
- Weak eval or reference: patch cited `references/**`; package verify must keep
  `reference_quality:true`, including invocable Markdown reference headings and
  vendored KnowledgeOS capsule bodies.
- Unsafe request: emit `Safety Verdict:` and make no edits.
- Package handle: keep package-specific details in
  `references/package-specific-repairs.md`.
- Tessl or KnowledgeOS capsule handling: load
  `Plugins/skill-factory/references/tessl-knowledgeos-capsule.md` only when the
  target change depends on Tessl plugin layout, registry/install behavior,
  review/eval proof, MCP packaging, workspace/project setup, security policy,
  or Skills SDK handoff patterns.

## Tessl And Scenario Policy

Before any live-private Tessl score for a created, updated, installed,
refactored, or skillified candidate, run `./bin/ask sdk start <skill-path>
--json --robot`, then the SDK proof ladder in order:

1. strict audit
2. package verify
3. security risk-modes
4. scenario-quality
5. scorer-quality
6. scorer-calibration
7. oss-local
8. oss-cloud
9. Tessl local proof with `--execute`
10. Tessl live-private dry-run
11. handoff-readiness

The improve-skill Tessl lanes use the product workspace `jscraik`, and every
staged plugin starts `private: true` until a separate publish lane changes
visibility. Treat oss-local as the 70-75 internal discovery band, oss-cloud as
the iterative path to at least 90 internal success, and Tessl live as external
confirmation at at least 90 and at least baseline.

For scenario prep, use sdk-scenario-generator with the installed Tessl scenario
skill to generate bespoke scenarios for the exact skill, review them, and
import useful cases into canonical skill assets. The live-private lane must
stage both `references/evals.yaml` skill-owned cases and reviewed generated
scenarios from `references/evals/*.md`; structure-only package checks are the
only explicit exception.

After every skill change, review scenario drift before live scoring. Compare
changed triggers, constraints, outputs, references, and behavior claims with
`references/evals.yaml` and `references/evals/*.md`, then classify scenarios as
keep, update, add, or remove.

Before live Tessl scoring, bump the skill or plugin package version whenever
the staged package changed since the previous live run. Identical retry runs may
reuse the same version, but changed SKILL.md, scenarios, contract, or
runtime-context references must not be scored under the previous tile version.

Behavioral skills need at least 20 gold-standard structured scenarios before
live Tessl readiness scoring. Generic structure/layout scenarios can prove SDK
shape, but bespoke scenarios must prove the skill-specific behavior. Do not pad
the count with duplicate, weak, or scoring-mechanics scenarios.

Before any live Tessl run, check the workspace run budget. Treat 300 live eval
runs as the operator-provided limit unless Tessl reports a different
operator-approved limit, and preserve a 20-run remediation reserve. If capacity
is unknown or below reserve, use dry-run/local gates instead of burning a live
run.
