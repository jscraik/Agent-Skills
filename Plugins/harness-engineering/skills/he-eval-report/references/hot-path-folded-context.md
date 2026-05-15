# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active he-eval-report entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded Philosophy

Implementation is not completion. This skill writes closure proof for exactly
one approved Harness Engineering slice, with evidence for validation, drift,
side effects, traceability, generated media when relevant, and Linear closure
safety. Higher-priority instructions, command boundaries, and local `AGENTS.md`
guidance remain binding.

## Folded When Not to Use

- Do not use for implementation planning, code review, strategy, or reframe
  design; hand off to the matching HE skill.
- Do not use to close Linear, post external comments, publish, delete, approve,
  or update trackers. This skill may recommend after proof, not mutate external
  state.
- Do not recommend closure from implementation status, missing validation,
  source existence, or generated media prompts without persisted artifacts.

## Folded Outputs

Write one report at `.harness/evals/YYYY-MM-DD-JSC-###-<repo>-<issue-or-milestone>-eval.md`
when Linear context is known, or `.harness/evals/YYYY-MM-DD-<repo>-<issue-or-milestone>-eval.md`
otherwise. Include Artifact Identity frontmatter from
`Plugins/harness-engineering/references/artifact-routing-contract.md` and return
`schema_version`, evaluated slice, validation results, drift validation, proof
artifacts, closure recommendation, follow-up work, blockers, git staging
status, staged paths, Codex provenance status, PR safety trace status, next
handoff, and confidence.
Non-trivial reports also include the BLUF review surface so the closure
recommendation, blocker consequence, and next action are visible before proof
detail.

## Folded Preconditions

- Resolve exactly one evaluated slice; classify source artifacts by content
  shape before trusting titles, dates, or Linear identifiers.
- Load only the local contract, schema, template, drift taxonomy, Linear
  completion policy, and source artifacts needed for the slice.
- Start with 2-3 focused surfaces; widen only when closure depends on broader
  release, security, runtime, or media-persistence evidence.

## Folded Procedure

1. If asked to close work from implementation status alone, stop and classify
   closure as blocked until report, validation, drift proof, and
   accept/challenge/rework steering are complete.
2. Compare implementation against the approved Linear plan, reframe program,
   plugin HE spec, ADRs, core invariants, source-prompt coverage limits, and
   proof artifacts.
3. Prove agentic eval validity: task, outcome, trajectory/process evidence,
   grader coverage, trial policy, side-effect authorization, and saturation or
   maintenance signal.
4. Apply first-principles, XP, gate-selection, plugin-hook capability,
   domain-model, source-prompt, agent-native, and specialist-skill checks only
   when they are relevant to closure.
5. When media generation is closure evidence, require a repository media path,
   source generated-image cache path if available, prompt metadata path,
   sidecar path, and file-existence verification. A prompt alone is not proof.
6. Run or explicitly block relevant validation gates; never invent passing
   results.
7. When closure claims cite session, Codex, collector, rollout, transcript, or
   telemetry evidence, classify Codex provenance and redaction status from the
   session collector before recommending closure.
8. Apply the BLUF review contract to non-trivial eval reports so the closure
   recommendation, proof blocker, follow-up decision, and next action are
   scannable before detailed evidence.
9. Apply the visual reference contract when proof spans multiple gates,
   artifacts, media files, validation outputs, or non-linear drift decisions;
   prefer gate matrices and evidence-chain diagrams.
10. Generate and validate the report, apply the git staging contract for the
   report and any current-turn proof artifacts, then ask accept/challenge/rework before
   using `Complete` or `Complete with follow-up` as a Linear closure
   recommendation.

## Folded Validation

Run these from the repo root and record exact `pass|fail|blocked` outcomes.
Use each command with the report path argument:
- `python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py`
- `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py`
- `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py`

For skill-package edits, also run strict skill audit, OpenClaw, OpenAI format,
progressive-disclosure lint, Plugin Eval, focused script tests, and smoke or
release eval listing/execution when available. Missing proof is `not-run` or
`blocked`, never `pass`. Fail fast: stop at the first failed gate, fix or
classify it, then rerun before proceeding to broader gates.

## Folded Evidence Requirements

- Every closure claim must link to observed command output, diff/PR evidence,
  source artifacts, Linear identifiers, report paths, or media files.
- Provenance can support correlation and freshness only. It cannot prove tests
  passed, implementation correctness, Linear updates, PR readiness, or closure
  safety without separate evidence.
- PR-bound eval summaries must use a public-safe HE trace ID and hashed or
  presence-only provenance identifiers.
- Runtime, hook, MCP, CI, Linear, generated-image, and validator claims require
  fresh observed output.
- Media persistence is complete only when the `.harness/media/` PNG exists and
  a sidecar records purpose, source cache path, repository path, prompt metadata,
  linked context, and validation notes.

## Folded Accessibility Requirements

Keep reports scannable in plain Markdown. Avoid color-only status, giant tables
without surrounding prose, image-only proof, or conclusions that require reading
unlinked logs.

## Folded Confidence Reporting

Tie confidence to direct evidence, validator results, runtime proof, media
persistence proof where relevant, and remaining unknowns. Cap confidence when
strict audit, smoke/release evals, Plugin Eval, runtime visibility, Linear proof,
or media persistence is failed or blocked.

## Folded Examples

- "Generate the HE eval report for JSC-246 before closing the Linear parent."
- "Validate drift, proof artifacts, and whether this milestone is safe to close."
- "The slice generated media; prove the cache image was copied to `.harness/media/`."

## Folded References

- Read when writing reports: `references/eval-report-contract.md`,
  `references/eval-report-template.md`, `references/eval-report-schema.json`.
- Read when classifying drift or Linear closure: `references/drift-taxonomy.md`,
  `references/linear-completion-policy.md`.
- Read when validating local contract/evals: `references/contract.yaml`,
  `references/evals.yaml`.
- Read when report scanability/No-Fog structure matters:
  `../../references/bluf-review-contract.md`.
- Read when evidence chains, gate matrices, visual proof, screenshots, or
  generated media need persistence rules:
  `../../references/visual-reference-contract.md`.
- Read when session collector, Codex provenance, trace IDs, or PR safety trace
  supports a closure claim:
  `../../references/codex-provenance-contract.md`,
  `../../references/pr-safety-trace-contract.md`.
- Read when closure proof could be mistaken for live tracker mutation:
  `../../references/closure-mutation-contract.md`.
- Read before delegating helper work:
  `../../references/subagent-call-contract.md`.
- Read shared HE contracts only when the selected slice needs them:
  `Plugins/harness-engineering/references/deferred-context-index.md`.

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
