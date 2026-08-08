# Tessl Live Skill Eval Workflow

## Purpose

Use this workflow when an operator explicitly asks for live Tessl evidence for a
skill, or asks to use Tessl's scenario-generation skill to improve the local
eval suite.

This is a controlled staging workflow. It is not a registry-publish workflow.
Agents must keep the live repository source, Tessl tool install state, generated
scenario drafts, and final canonical eval cases separate.

Every create or update cycle that will use live Tessl scoring must run the
scenario-prep lane before the live-private lane, unless the work is explicitly a
structure-only package check. The live-private lane consumes only reviewed
canonical skill assets; it does not generate scenarios during scoring.
When `SKILL.md`, core references, behavior claims, triggers, constraints, or
output contracts change, review scenario drift before live scoring: classify
existing scenarios as keep, update, remove, or add, then update canonical eval
assets before staging Tessl.
For behavioral skills, declare 5 to 10 gold-standard structured scenarios and
target 8. Use generic SDK structure/layout scenarios for package shape and
bespoke skill-specific scenarios for behavior; do not pad the set with
duplicated, weak, or self-referential cases. Author and repair that set through
`oss-local`, run the same case ids through `oss-cloud`, and preserve those exact
ids through Tessl dry-run and external evaluation. Any addition, removal, or
substitution returns the candidate to `oss-local`.

Use a separate development-pool policy to improve the skill without changing
the Tessl comparison denominator. The default policy is 20 cases for the local
development pool, the fixed release eight plus 2 rotating growth cases for the
10-case cloud challenge pool, and the unchanged release eight for Tessl. The
cloud challenge cases must come from the local pool. Changes to release case
ids, criteria, rubric, scorer version, or package identity create a new
baseline version; do not report that score as uplift against the prior set.

Keep the model families independent across proof lanes: `oss-local` uses
`qwen3.5:9b-mlx`, `oss-cloud` uses `deepseek-v4-flash:cloud`, and Tessl external uses
`deepseek-v4-flash`. Every eval receipt must carry the declared execution model,
family, provider, and identity source. A model change starts a new baseline for
that lane. Do not average scores across model families; compare each lane to its
own prior baseline and use cross-lane agreement or disagreement as portability
evidence. Configuration identity alone is not provider-invocation proof.

Use `evals-router` for scenario quality review. The route must verify the
assertion contract before changing the skill: each scenario needs a realistic
user-facing condition, one primary failure mode, a comparator expectation
against no-skill or baseline behavior, deterministic checks where possible, and
a weak-eval critique. Scenarios that only prove trigger words, filenames,
generic phrases, or rubric copying are not gold-standard scenarios.

Before scenario scoring, run Tessl's skill review lane when activation,
best-practice quality, or static score is in doubt. Use the repo wrapper when a
wrapper exists; otherwise run the native CLI only against a temporary copied
skill directory, not the live repo source. `tessl skill review --optimize` may
suggest or apply edits, but accepted changes must be transferred back to the
canonical skill source and revalidated through the SDK gates below. Do not use a
private live eval score, static review score, or GitHub badge score as a
substitute for the scenario-based readiness gate.

## Hard Boundaries

- Use the installed native tessl CLI only.
- Do not use npx tessl.
- Do not run Tessl commands from the repository root unless the wrapper command
  is the command being executed.
- Do not run tessl publish, tessl tile publish, tessl skill publish,
  tessl tile pack, registry upload, or package upload commands.
- Do not point Tessl at the live skill source tree.
- Do not copy generated scenarios into canonical files before review.
- Do not print workspace API tokens or shell-expanded environment contents.

## Scenario-Generation Prep

Use this command to prepare a disposable workspace for Tessl's public scenario
skill:

    ./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot

Staging-only is the default and does not install the scenario-generation tile.
Use `--execute` only after the staged brief has been reviewed and the operator
has explicitly authorized the temporary Tessl install:

    ./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --execute --json --robot

The command writes a stable evidence directory:

    /tmp/ask-tessl-scenario-generation/<skill-path>-<sha12>/
      scenario-generation-brief.md
      target-tile/
        .tessl-plugin/plugin.json
        tessl.json
        skills/<skill-name>/SKILL.md
        skills/<skill-name>/references/
      tool-project/
        tessl.json
        .tessl/tiles/tessl-labs/tessl-skill-eval-scenarios/

target-tile is the disposable plugin-shaped input for scenario creation.
tool-project is the only place where the Tessl scenario tile may be installed.
The installed tile is pinned as tessl-labs/tessl-skill-eval-scenarios@0.1.0.
The wrapper stops at preparation and install; it does not generate scenario
files by itself. On rerun, the wrapper archives prior target-tile, tool-project,
and generated scenario evidence under evidence-archive/ before refreshing the
current staging inputs.

When `--execute` is selected, setup also stages the private plugin at the
stable `/tmp/ask-tessl-evals/<skill-path>-<sha12>/` path used by the later live
evaluator and links the Tessl project from that directory. The `target-tile/`
directory remains the scenario-generator input only. This separation is
required because Tessl records the absolute source directory in a project
binding; linking the target tile instead makes a valid project-link receipt
unusable for the subsequent live run.

Treat every Registry tile used by this workflow as a dependency, not as a
trusted fact source. Before installing or relying on a Registry tile, record the
exact package id and version or commit-specific source, publisher or workspace,
local install command, and any visible quality, impact, and security signals. A
high review score, successful install, or Registry listing is candidate evidence
only; it does not replace local lint/review, scenario-quality, target-repo
validation, or live score comparison. High or critical security warnings block
use until inspected and explicitly accepted by the operator.

If the approved environment stream was sourced and `TESSL_WORKSPACE_API_TOKEN`
is present, but `tessl project repair --json` still returns
`Please authenticate with Tessl to continue`, classify the result as
`blocked_auth` for the native Tessl CLI session. Do not keep retrying token
export advice, do not print token values, and do not delete the staged
`/tmp/ask-tessl-scenario-generation/**` evidence. The next required action is
a Tessl CLI login/session repair outside the package staging lane.

After the command succeeds, open scenario-generation-brief.md. It points to the
installed Tessl scenario skill and its workflow reference. Follow that skill
inside the staged directory and write instructions.json, summary.json,
summary_infeasible.json, and sequential scenario folders under:

    /tmp/ask-tessl-scenario-generation/<skill-path>-<sha12>/target-tile/evals/

## Scenario Review

Generated Tessl scenarios are drafts. Before importing anything into canonical
repo state, review every scenario for:

- direct coverage of actual skill instructions
- self-contained task setup
- a plausible no-skill failure mode, so the scenario can show skill lift rather
  than merely general agent competence
- a clear comparator expectation: no-skill, previous-skill, wrong-skill, or
  local-owner baseline should plausibly miss the required behavior
- no instruction leakage from the rubric into task.md
- no exact expected-answer text copied into task.md, given, should, or the
  user prompt
- no task wording that names the exact skill-specific concepts being scored
  unless those concepts are user-facing domain language
- no scoring-mechanics language such as Tessl, fixture, generated scenario,
  rubric, criteria, hidden expected behavior, or "use this skill"
- no reliance on hidden files, local credentials, network-only behavior, or
  proprietary software
- criteria that are file-observable, binary where possible, and test one
  assertion each
- a difficulty tag and anti-easy note describing why a strong baseline might
  still fail
- realistic timeout and output size
- non-duplication with existing references/evals.yaml cases

Only after review should an agent translate useful generated cases into the
canonical skill eval sources:

    <skill-path>/references/evals.yaml
    <skill-path>/references/evals/*.md

Use `references/evals.yaml` for the skill-owned case index and
`references/evals/*.md` for reviewed generated fixture evidence. Do not commit
target-tile/evals/ directly.

After any skill change, run a scenario drift review even when no new scenarios
were generated. Compare the changed skill contract with `references/evals.yaml`,
`references/evals/*.md`, and any knowledge capsules that provide eval evidence.
For each affected scenario, record the decision as keep, update, remove, or add.
Do not carry stale scenarios into live Tessl scoring just because they passed
before the skill changed.

## Live Private Eval

Use this command only when the operator asks for live private Tessl evidence:

    ./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --json --robot

Start with a dry run when proving shape:

    ./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --tessl-live-dry-run --json --robot

The dry-run route is not a shortcut around the SDK sequence. Before it stages
the payload, the shared admission check requires current receipts for
mechanical validation, security risk modes, scenario quality, scorer quality,
scorer calibration, deterministic local gates, `oss-local`, `oss-cloud`, and
executed Tessl-local proof. Record the successful dry-run receipt, then run
`sdk eval handoff-readiness --preview` before an actual live Tessl submission.

Project setup is a separate, explicit side-effect lane. Run
`./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --execute --json --robot`
only with operator authority. It records a candidate-bound
`.harness/evidence/tessl-project-links/<skill>/<candidate-digest>.json` receipt.
The live evaluator only reads that receipt; it never repairs, relinks, updates,
or creates a Tessl project as a side effect of scoring.

The wrapper stages a private plugin package under:

    /tmp/ask-tessl-evals/<skill-path>-<sha12>/
      .tessl-plugin/plugin.json
      tessl.json
      skills/<skill-name>/SKILL.md
      skills/<skill-name>/references/
      scenario-sources.json
      evals/<case-id>/task.md
      evals/<case-id>/criteria.json
      evidence-archive/<timestamp>-live-private/   # only after reruns

Root `evals/` must sit beside `.tessl-plugin/` in the staged plugin root.
`.tessl-plugin/plugin.json` must use the workspace-prefixed package name,
preserve `private: true`, and declare a real skill path, for example:

    {
      "name": "<workspace>/<plugin-name>",
      "version": "<SKILL.md metadata.version>",
      "description": "Private live eval plugin for <skill-name>.",
      "private": true,
      "skills": "./skills/"
    }

`.tessl-plugin/plugin.json` is the only live-private package manifest. Do not
stage `tile.json` as a compatibility fallback, and do not point plugin
`skills` at a missing directory, a root that does not contain a discoverable
`SKILL.md`, or a live repo path outside the staged package.

The staged `scenario-sources.json` records how many cases came from
`references/evals.yaml` and how many reviewed generated cases came from
`references/evals/*.md`. For normal skill create/update work, a live-private run
is blocked when reviewed generated scenarios are missing. Use the structure-only
exception only for package-shape checks that are not claiming behavioral skill
readiness.

For behavioral skill readiness, the live-private staging gate requires 5 to 10
gold-standard structured scenarios, with 8 as the target. Counts outside that
range are blocker evidence, and the staged ids must exactly match both OSS proof
lanes.

Before running live Tessl, check the workspace run budget. Treat any
operator-provided cap as binding unless Tessl reports a different
operator-approved limit, and preserve at least 20 runs as a remediation reserve.
Use the installed Tessl CLI's supported list/filter surface; do not require a
fixed list-window flag. A typical preflight is:

    tessl eval list --json --workspace <workspace>

If the preflight fails or remaining capacity is unknown, block nonessential live
scoring. Continue with SDK scenario generation, internal evals, dry-run staging,
and scenario quality review until capacity is confirmed. Record the blocker and
the fallback evidence in the skill contract or run report.

The wrapper reads the Tessl tile version from SKILL.md frontmatter, preferring
metadata.version and falling back to a top-level version field. This value must
be valid SemVer. Do not run live private Tessl evals for a changed skill until
the canonical SKILL.md version represents the behavior being evaluated.

For plugin-owned skills under `Plugins/<plugin-id>/skills/**`, `<tile-name>`
is the plugin id rather than the leaf skill directory. For example,
`Plugins/skill-factory/skills/skill-factory-router` stages as
`<workspace>/skill-factory` while the plugin manifest exposes the surviving
Skill Factory skill entries.

Tessl plugin evals attach to a Tessl project using that same
`<workspace>/<plugin-name>` identity. The wrapper must check that staged project
link before running live evals, relink an existing project first, and create the
project only when the relink path proves it does not already exist:

    ./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --execute --json --robot

The raw Tessl project commands are vendor-reference material only. Do not run
them directly from a live-eval lane: the wrapper's project-setup receipt is the
required boundary between project mutation and scoring.

## Reading Results

Treat Tessl scores as evidence, not proof by themselves.

- A live-private command is not green merely because `tessl eval run`
  completed. The wrapper must inspect `tessl eval view --json <run-id>` and
  compare usage-spec results against baseline before reporting readiness.
- Before quoting prior or current Tessl scores, preserve the
  `tessl eval view --json <run-id>` artifact and run
  `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot`.
  Memory summaries, screenshots, and chat history are provenance only. A
  blocked receipt may expose partial score math, but it is not a completed
  baseline.
- If both usage-spec and baseline are 100%, classify the run as
  pass_but_non_discriminative for improvement evidence. The skill may be
  correct, but the scenario set did not prove uplift. Tighten scenarios before
  using the run as improvement proof.
- Interpret Tessl's Improvement card as a ratio. A score of 100% and baseline
  of 100% displays as 1x, meaning no observed uplift over baseline.
- If `tessl eval view --json <run-id>` reports `failureReason.code` as
  `EVAL_QUOTA_EXCEEDED`, classify the live-private lane as
  `blocked_environment`. Do not submit another live eval until the quota reset
  or quota increase is available; use dry-run staging and local scenario
  quality gates only.
- If the live run would exceed the operator-approved workspace budget or consume
  the 20-run reserve, classify the lane as `blocked_environment` for live
  scoring and continue with dry-run/local validation only.
- The live-private readiness gate is: usage-spec score is at least 90% and is
  not below the baseline score. A 95%+ score remains the improvement target.
  A lower score, lower baseline comparison, or
  missing viewable score summary is a failed or blocked gate, not a pass.
- If the score UI shows an in-progress or lower live score, that live score is
  the active readiness lane even if local Tessl review or Plugin Eval produced a
  higher static score.
- If with-context scores exceed baseline, inspect which criteria improved and
  decide whether to preserve the current skill behavior.
- If with-context scores are below baseline, inspect failing scenarios before
  strengthening the skill. A worse score can mean the skill is misleading, too
  broad, stale, or giving the agent extra instructions that conflict with the
  task.
- First check whether the with-context solution directory contains the expected
  durable artifacts. For Goal Governor, missing or marker-light
  `goal-governor-output.yaml` files are skill-contract failures: harden the
  output contract and canonical eval prompt before adding new behavior.
- If a scenario is weak or infeasible, improve or remove the scenario before
  making skill changes.
- Record the Tessl run ID, staged path, command, and blocker or score summary in
  the implementation notes or closeout evidence.

When a private eval exposes regressions, use this improvement loop:

1. Export or inspect the per-scenario details before editing the skill.
2. Separate scenario weakness from skill weakness. Fix scenario wording only when
   the task or rubric is impossible, leaky, or not file-observable.
3. For real skill misses, patch the canonical skill source and references, not
   the staged Tessl directory.
4. Preserve negative-trigger boundaries. If a non-governed review or one-file fix
   improves without Goal Governor, make the skill opt out instead of broadening
   its trigger.
5. Rerun local audit and discovery smoke before any second live private eval.
6. Start a new private Tessl run only after local proof passes; keep the old run
   ID as before/after evidence.

For Goal Governor specifically, prioritize these failure classes in order:
ordinary-review false positives, missing `goal-governor-output.yaml`, missing
exact markers, and then scenario coverage gaps. Marker fixes belong in
`SKILL.md`, `references/goal-contract.md`, `references/markers.md`, or the
specific canonical eval case that needs file-visible wording.

## Agent Checklist

Before claiming completion:

- prepare-tessl-scenarios --dry-run passed for the target skill when using
  scenario generation.
- For every create/update skill flow that will run live Tessl, bespoke generated
  scenarios were prepared, reviewed, and imported before live scoring, unless
  `references/contract.yaml` explicitly declares a structure-only exception.
- Scenario drift was reviewed after the latest skill change, and stale, weak, or
  obsolete scenarios were updated, removed, or replaced before live scoring.
- Live scenario tool install, if run, installed only into tool-project.
- Root tessl.json, .tessl/, .codex/, .mcp.json, AGENTS.md, and CLAUDE.md were
  not modified by Tessl setup.
- Generated scenarios were reviewed before canonical import.
- The live staged `scenario-sources.json` shows both skill-owned eval cases and
  reviewed generated fixture cases for non-structure runs.
- The live staged `scenario-sources.json` shows 5 to 10 gold-standard structured
  scenarios, targets 8, and carries the same ids proven by `oss-local` and
  `oss-cloud`.
- OSS receipts name the execution model, family, provider, and identity source;
  the Qwen local and DeepSeek cloud provider lanes are distinct.
- When `oss-local` uses bounded qwen shards, every shard contains at most two
  cases and `ask sdk eval aggregate-shards` passes over repo-owned shard
  receipts with one package, dataset, rubric, profile, and exact release-set
  identity before `oss-cloud` or Tessl runs.
- Tessl workspace run capacity was checked or explicitly estimated, with the
  operator-approved limit and 20-run remediation reserve preserved.
- The staged `.tessl-plugin/plugin.json` version matches the canonical SKILL.md frontmatter
  version for the skill behavior being evaluated.
- Focused Python tests for the wrapper passed.
- The exact command outcomes and staged paths were reported.
