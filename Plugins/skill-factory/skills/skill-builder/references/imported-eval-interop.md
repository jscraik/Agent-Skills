# Imported Eval Interop (Skillgrade-style)

Use this guide when `install-distribute` imports a skill package that already contains an evaluation contract such as `eval.yaml`, grader scripts, or rubric files.

## Goal

Preserve upstream evaluation semantics while enforcing skill-builder gold gates.

## Detection

Treat a package as upstream-eval-aware when one or more of these are present:

- `eval.yaml`
- `graders/` scripts
- rubric files referenced from eval config

## Preservation Rules

- Keep upstream eval files intact during install or upgrade.
- Do not rewrite upstream `eval.yaml` into `Infrastructure/references/evals.yaml`.
- Add compatibility overlays for gold validation without mutating upstream evaluation intent.

## Skillgrade Baseline Semantics (from upstream refs)

- Trial presets:
  - smoke: quick signal
  - reliable: stronger confidence
  - regression: high-confidence regression check
- CI threshold behavior:
  - threshold controls CI pass/fail behavior; preserve source defaults unless user overrides.
- Grader composition:
  - deterministic and LLM rubric graders can be combined with weighted scoring.
- Grader output contract:
  - required: `score` (0.0 to 1.0), `details`
  - optional: `checks[]`
  - stdout should contain only final JSON result.

## Dual-Grade Reporting Contract

For each imported skill report:

- `gold_grade`: pass or warn or fail (quick_validate, skill_gate, analyze, openclaw)
- `upstream_grade`: pass or warn or fail (upstream evaluator checks when available)
- `interop_actions`: list of compatibility overlays or no-op preservation
- `decision`: pass or warn or fail with next fix

## Recommended Install Flow

1. Run deconflict full-scan against installed operational skills.
2. Run an artifact-uplift pass across incoming `Infrastructure/references/`, `assets/`, and `agents/` to capture reusable improvements for overlapping installed skills.
3. Install skill package without rewriting upstream eval files.
4. Run gold validators.
5. Run upstream-grade checks when evaluator tooling is available.
6. Emit a combined summary with both grades and next actions.
