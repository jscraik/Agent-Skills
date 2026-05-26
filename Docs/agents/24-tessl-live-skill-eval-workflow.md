# Tessl Live Skill Eval Workflow

## Purpose

Use this workflow when an operator explicitly asks for live Tessl evidence for a
skill, or asks to use Tessl's scenario-generation skill to improve the local
eval suite.

This is a controlled staging workflow. It is not a registry-publish workflow.
Agents must keep the live repository source, Tessl tool install state, generated
scenario drafts, and final canonical eval cases separate.

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

Use --dry-run first when proving the package shape:

    ./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --dry-run --json --robot

The command writes a stable evidence directory:

    /tmp/ask-tessl-scenario-generation/<skill-path>-<sha12>/
      scenario-generation-brief.md
      target-tile/
        tile.json
        tessl.json
        SKILL.md
        references/
      tool-project/
        tessl.json
        .tessl/tiles/tessl-labs/tessl-skill-eval-scenarios/

target-tile is the disposable tile-shaped input for scenario creation.
tool-project is the only place where the Tessl scenario tile may be installed.
The installed tile is pinned as tessl-labs/tessl-skill-eval-scenarios@0.1.0.

After the command succeeds, open scenario-generation-brief.md. It points to the
installed Tessl scenario skill and its workflow reference. Follow that skill
inside the staged directory and write generated scenarios under:

    /tmp/ask-tessl-scenario-generation/<skill-path>-<sha12>/target-tile/evals/

## Scenario Review

Generated Tessl scenarios are drafts. Before importing anything into canonical
repo state, review every scenario for:

- direct coverage of actual skill instructions
- self-contained task setup
- no instruction leakage from the rubric into task.md
- no reliance on hidden files, local credentials, network-only behavior, or
  proprietary software
- criteria that are file-observable, binary where possible, and total 100
- realistic timeout and output size
- non-duplication with existing references/evals.yaml cases

Only after review should an agent translate useful generated cases into the
canonical skill eval source:

    <skill-path>/references/evals.yaml

Do not commit target-tile/evals/ directly.

## Live Private Eval

Use this command only when the operator asks for live private Tessl evidence:

    ./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --json --robot

Start with a dry run when proving shape:

    ./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --tessl-live-dry-run --json --robot

The wrapper stages a private tile under:

    /tmp/ask-tessl-live/<skill-path>-<sha12>/
      tile.json
      tessl.json
      SKILL.md
      references/
      evals/<case-id>/task.md
      evals/<case-id>/criteria.json

The staged tile.json must use:

    {
      "name": "<workspace>/<tile-name>",
      "version": "<SKILL.md metadata.version>",
      "private": true,
      "skills": {
        "<tile-name>": {
          "path": "SKILL.md"
        }
      }
    }

The wrapper reads the Tessl tile version from SKILL.md frontmatter, preferring
metadata.version and falling back to a top-level version field. This value must
be valid SemVer. Do not run live private Tessl evals for a changed skill until
the canonical SKILL.md version represents the behavior being evaluated.

Tessl tile evals attach to a Tessl project using that same
<workspace>/<tile-name> identity. If Tessl reports a missing or inaccessible
project, create, link, or repair the project for the staged lane before
rerunning:

    tessl project create --workspace <workspace> <tile-name>
    tessl project link --workspace <workspace>
    tessl project repair --workspace <workspace>

## Reading Results

Treat Tessl scores as evidence, not proof by themselves.

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
- Live scenario tool install, if run, installed only into tool-project.
- Root tessl.json, .tessl/, .codex/, .mcp.json, AGENTS.md, and CLAUDE.md were
  not modified by Tessl setup.
- Generated scenarios were reviewed before canonical import.
- The staged tile.json version matches the canonical SKILL.md frontmatter
  version for the skill behavior being evaluated.
- Focused Python tests for the wrapper passed.
- The exact command outcomes and staged paths were reported.
