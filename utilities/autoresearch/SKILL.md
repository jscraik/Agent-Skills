---
name: autoresearch
description: "Analyze and improve this repo's skills and plugin packages through bounded experiment loops. Use this skill when users request autonomous research passes with hypothesis-validation-keep/discard decisions."
metadata:
  skill-type: team_automation
  lifecycle_state: incubating
  maturity: experimental
  owner: skill-factory
  review_cadence: monthly
  last_reviewed: 2026-04-14
  metadata_source: frontmatter
---

# Autoresearch

Run iterative, autonomous-style research loops against skill and plugin packages in this repository.
Boundary: this skill owns quality-improvement experiment cycles for `SKILL.md` packages and plugin bundles; it is not a generic feature implementation lane.

## When to use
- Primary triggers:
  - The user asks to "run autoresearch" or "autonomously improve" skills/plugins.
  - The user wants bounded loop execution: hypothesis, patch, validate, score, keep/discard.
  - The user wants overnight or multi-iteration improvement with durable artifacts.
- Non-triggers (route elsewhere):
  - One-off fixes without experiment loops.
  - Work that primarily changes product code outside skills/plugins.
  - Broad strategy brainstorming without concrete repository changes.

## Required inputs
- Assumptions:
  - At least one target path is provided or can be inferred.
  - The user accepts incremental, evidence-driven changes.
- Required inputs:
  - Target paths (skills and/or plugins).
  - Run tag (short lowercase label, e.g. `apr13-skill-loop`).
  - Stop condition (timebox, iteration cap, or manual stop only).
  - Success goal (examples: strict audit pass rate, reduced warnings, simplified structure).
  - Initial scope cap (start with 2-3 surfaces before broadening).
- Ask clarifying questions only for ambiguous risk boundaries or missing stop conditions.

## Deliverables
- `artifacts/autoresearch/<run-tag>-<timestamp>/results.tsv`
- `artifacts/autoresearch/<run-tag>-<timestamp>/journal.md`
- `artifacts/autoresearch/<run-tag>-<timestamp>/targets.txt`
- A final summary with:
  - kept vs discarded experiments,
  - validation evidence,
  - remaining risks and next hypotheses.

## Output contract
- For non-trivial summaries, include `schema_version`.
- Include run metadata: `run_tag`, `run_dir`, and `stop_condition`.
- Include decision totals: `kept`, `discarded`, `blocked`.
- Include command evidence as `[{command, outcome, note}]` with `outcome` in `pass|fail|blocked`.
- Include next actions as `next_hypotheses` so a follow-up run can start without re-triage.

## Constraints and safety
- Redact secrets/PII by default.
- Prefer offline-first workflows; require explicit user intent before network use.
- Edit canonical source paths only.
- Treat `plugins/cache/**` as mirrored output; do not edit cache paths.
- Destructive actions require explicit confirmation; prefer dry-run first.
- Keep each experiment to one clear hypothesis to preserve causality.

## Principles
- Baseline first, then iterate: do not evaluate improvements without baseline evidence.
- One hypothesis per iteration, one decision per iteration (`keep`, `discard`, `blocked`).
- Validation gates are mandatory and define decision quality.
- Favor simpler maintainable outcomes over marginal complexity-heavy gains.

## Workflow
1) Initialize run artifacts:
   - `bash utilities/autoresearch/scripts/init_run.sh --tag <tag> --targets "<path1,path2,...>"`
2) Capture baseline for each target using the matrix in `references/runbook.md`.
3) Loop on one hypothesis:
   - Apply minimal patch.
   - Run mandatory validations.
   - Compute iteration score and decision (`keep`/`discard`).
   - Record the result:
     - `python3 utilities/autoresearch/scripts/log_result.py --run-dir <run-dir> ...`
4) Keep only improvements that pass gates and improve score or quality with equal score and lower complexity.
5) Continue until stop condition is met.
6) Produce a concise findings summary and list exact commands run.

## Validation
- Fail fast: stop at the first failed gate for an iteration.
- Skill targets:
  - `python3 plugins/skill-factory/skills/skill-creator/scripts/quick_validate.py <skill-path>`
  - `./bin/ask skills audit <skill-path> --level strict --robot`
- Plugin targets:
  - `./bin/ask plugins harden <plugin-path> --robot`
- Mixed or broad changes:
  - `bash scripts/verify-work.sh --fast`
- Keep command-level outcomes in the run artifact.

## Gotchas
- Editing `plugins/cache/**` instead of canonical source paths causes ownership and sync failures.
- Running multi-change experiments makes keep/discard attribution unreliable.
- Forgetting to log discarded runs destroys research traceability.

## Failure mode
- If mandatory validations fail in an iteration, mark it `discard` (or `blocked` when a required command cannot run) and do not keep the patch.
- If workspace drift appears mid-run, stop immediately, record the blocker in `journal.md`, and request explicit user direction before continuing.

## See Also
| Skill | When to use |
|---|---|
| [[skill-creator]] | Create or reshape a single skill package before entering a loop. |
| [[plugin-builder]] | Harden or validate one plugin package outside a research loop. |
| [[code-review]] | Run an adversarial review pass on the final diff before accepting loop outcomes. |

**Topic map:** `[[agent-ops]]`

## Anti-patterns
- ❌ Treating "it feels better" as evidence without validation outcomes.
- ❌ Continuing unattended loops without explicit stop conditions.
- ❌ Keeping changes that fail mandatory validation gates.

## Examples
- Triggering prompt: "Run `autoresearch` for four iterations on `plugins/skill-factory/skills/skill-builder` and `utilities/autoresearch`, and keep only iterations that pass strict audit plus quick validate."
- Triggering prompt: "Set up a run tag for tonight's skill hardening pass, log each keep/discard decision, and give me a morning summary with blocker commands."
- Non-triggering prompt: "Fix one typo in `utilities/autoresearch/SKILL.md` and don't run any loop."
- Non-triggering prompt: "Update this repo's billing webhook retry logic."

## References
- `references/runbook.md` for setup, scoring, and decision policy.
- `references/contract.yaml` for machine-checkable behavior boundaries.
- `references/evals.yaml` for happy-path, edge, and pressure tests.
- `references/task-profile.json` when calibrating evaluation thresholds or posture defaults.
