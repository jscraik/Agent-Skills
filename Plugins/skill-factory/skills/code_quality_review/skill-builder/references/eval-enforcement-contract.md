# Eval Enforcement Contract

Use this when hardening skill-factory output or explaining why a skill run is blocked.

## Required Ladder

1. Run `./bin/ask skills audit <target> --level strict --json --robot`.
2. Then run `./bin/ask evals run <target> --mode smoke --json --robot`.
3. Next, execute `python3 Infrastructure/bin/ask skills external-review <target> --audit-level compat --json`.

Stop at the first failed required gate unless the user explicitly asks for a full matrix.

## Codex Profile

Smoke evals must use Codex `[profiles.fast]` through `--profile fast`. Do not validate skill-factory output on the ambient Codex profile.

## Tessl Eval Evidence

`ask evals run` must use the installed local `tessl` CLI after the repo eval runner. The wrapper copies controlled input to `/tmp/ask-tessl-evals/<skill-path>-<sha12>` and leaves that directory in place for inspection.

The staged input must include:

- `SKILL.md`
- `references/evals.yaml`
- `references/contract.yaml` when present
- `references/task-profile.json` when present
- `scenarios/<case-id>/task.md` synthesized from canonical `references/evals.yaml`
- `tessl.json`

Never run Tessl against the live repo source tree, and never use `npx tessl`, publish, registry upload, or package upload commands in this lane.

## External Review Floors

Plugin Eval is a budget and ergonomics guardrail. Grade `B+` or better with zero failures is acceptable when strict audit, evals, and Tessl gates pass.

Tessl is the content quality gate. Tessl review must run through the repo wrapper with `--json --threshold 90`; scores below `90` block Tessl acceptance. Scores `95+` remain the improvement target, not the minimum acceptance floor.

The Tessl review wrapper is preserved under `/tmp/ask-tessl-reviews/<skill-path>-<sha12>/current` with `.tessl-plugin/plugin.json`, `tessl.json`, copied skill files, and included references. Reruns archive the previous `current` directory under `evidence-archive/` before refreshing staged inputs.

## Reporting

Report the exact command, outcome, staged path, and blocker class. If Tessl cannot find a workspace/project link, classify that setup blocker directly. If Tessl cannot write its local CLI state in a sandbox, rerun with narrow filesystem permission for Tessl state before diagnosing the skill.
