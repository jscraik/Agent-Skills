# SDK Pipeline Setup

Use this reference before scenario readiness, staging, or release claims for
Skills SDK eval work.

## Setup Checks

- Use the repo wrapper `./bin/ask`. If the wrapper is unavailable in a fresh
  checkout, run the repo bootstrap path before requiring SDK commands.
- Run `./bin/ask sdk status --json --robot` when the current SDK capability
  surface, matrix truth, or command availability matters.
- Keep cache and state paths writable in Codex sandboxes, for example
  `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache` and
  `XDG_CACHE_HOME=/private/tmp/agent-skills-xdg-cache`.

## Pipeline Lanes

Keep these lanes separate:

- Package shape: `./bin/ask skills package verify <skill-path> --json --robot`.
- Scenario quality: `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`.
- Deterministic or internal SDK eval: `./bin/ask sdk eval run ... --json --robot`.
- Tessl scenario preparation: `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot`.
- Tessl dry-run staging: `./bin/ask evals run <skill-path> --mode smoke --tessl-live-private --tessl-workspace <workspace> --tessl-live-dry-run --json --robot`.
- Live Tessl scoring: only after scenario count, scenario quality, run-budget,
  dry-run, and scenario-source gates pass.

Do not treat one lane as proof for another. Package verification proves local
shape and references; scenario-quality preview proves scenario contract quality;
SDK eval run proves only the selected runner/dataset; Tessl staging proves staged
payload shape; live scoring proves only the specific workspace run and model.

## Scenario Source Gate

Before Tessl dry-run or live scoring, require `scenario-sources.json` to show:

- skill-owned `references/evals.yaml` cases;
- reviewed generated fixtures from `references/evals/*.md` when present;
- at least 20 gold-standard structured scenarios for behavioral readiness;
- `structure_only: true` only when the package contract explicitly declares a
  package-shape exception.

## Lift Curation Gate

Use lift, not aggregate score, for curation:

```text
lift = with_context_score - baseline_score
```

Run retire decisions on the floor model. A scenario with near-zero lift on a
strong solver can still be valuable if the floor model needs the skill.

For weak or no lift:

- retire only when the skill prescription is universal competence and no
  skill-specific replacement exists;
- rewrite the task when task text leaked the technique;
- rewrite criteria when they grade universal competence instead of the
  skill-prescribed behavior.

For non-zero lift with with-context below 100%, classify the owner before
editing: unclear skill instruction, task mismatch, or criteria mismatch.
