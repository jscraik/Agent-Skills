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
  This is the platform-parity scenario gate and must include the same
  behavioral quality blockers used by Tessl dry-run/live-private staging.
- Deterministic or internal SDK eval: `./bin/ask sdk eval run ... --json --robot`.
- oss-local scenario proof: `codex exec --profile oss-local` in the read-only
  Codex profile sandbox, or an SDK receipt with `codex_exec_invoked=true` and
  `codex_profile=oss-local`.
- oss-cloud scenario proof: `codex exec --profile oss-cloud` in the read-only
  Codex profile sandbox, or an SDK receipt with `codex_exec_invoked=true` and
  `codex_profile=oss-cloud`.
- Fast smoke/check lane: `codex exec --profile fast` or a receipt in the
  `codex-fast-smoke` lane. This lane is useful for quick checks only and does
  not satisfy oss-local or oss-cloud promotion proof.
- Tessl local proof: `./bin/ask sdk eval tessl-local-proof --skill <skill-path>
  --workspace <workspace> --execute --json --robot`. Preview receipts do not
  satisfy the live handoff lane.
- Tessl scenario preparation: `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot`.
- Tessl dry-run staging: `./bin/ask evals run <skill-path> --mode smoke --tessl-live-private --tessl-workspace <workspace> --tessl-live-dry-run --json --robot`.
  Handoff readiness must verify both the command flag and a receipt payload with
  `tessl_eval.dry_run=true`.
- Live Tessl scoring: only after scenario count, scenario quality, run-budget,
  dry-run, scenario-source gates, and any prior Tessl feedback-loop obligations
  are closed.

Do not treat one lane as proof for another. Package verification proves local
shape and references; scenario-quality preview proves scenario contract quality;
SDK eval run proves only the selected runner/dataset; Tessl staging proves staged
payload shape; live scoring proves only the specific workspace run and model.
`./bin/ask evals run --runner codex` is not oss-local or oss-cloud proof unless
the durable receipt proves the matching Codex profile invocation.
Tessl local proof is required before dry-run/live handoff, but it does not
replace dry-run staging or live scoring.

## Live-To-Internal Feedback Loop

Treat `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill> --preview --json --robot`
as the handoff feedback-loop gate for every behavioral skill. A completed Tessl
run is not handoff-ready when the receipt reports:

- `feedback_loop.status: open`;
- any scenario-level baseline win;
- usage below the live handoff threshold;
- no aggregate lift over baseline;
- missing baseline or usage-spec assessments.

When the feedback loop is open, convert the live Tessl failure into repo-owned
internal evidence before another live run: preserve the view artifact, classify
each failing scenario owner as skill, task, criteria, or scorer, add or retain
equivalent internal regression cases, rerun the internal release gate, and only
then spend another live Tessl run.

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
