# Eval Enforcement Contract

Use this when hardening skill-factory output or explaining why a skill run is blocked.

## Required Ladder

0. Run `./bin/ask sdk start <target> --json --robot`.
1. Run `./bin/ask skills audit <target> --level strict --json --robot`.
2. Run `./bin/ask skills package verify <target> --json --robot`.
3. Run `./bin/ask sdk security risk-modes <target> --preview --json --robot`.
4. Run `./bin/ask sdk eval scenario-quality <target> --preview --json --robot`.
5. Run `./bin/ask sdk eval scorer-quality <target> --preview --json --robot`.
6. Run `./bin/ask sdk eval scorer-calibration <target> --preview --json --robot`.
7. Run `./bin/ask sdk eval run <target> --runner internal --mode smoke --codex-profile oss-local --json --robot`.
8. Run `./bin/ask sdk eval run <target> --runner internal --mode smoke --codex-profile oss-cloud --json --robot`.
9. Run `./bin/ask sdk eval tessl-local-proof --skill <target> --workspace jscraik --execute --json --robot`.
10. Run `./bin/ask evals run <target> --mode smoke --runner discovery-smoke --tessl-live-private --tessl-workspace jscraik --tessl-live-dry-run --json --robot`.
11. Run `./bin/ask sdk eval handoff-readiness --skill <target> --preview --json --robot`.
12. Next, execute `./bin/ask skills external-review <target> --audit-level compat --json --robot`.

Stop at the first failed required gate unless the user explicitly asks for a full matrix.

Score policy: oss-local is the 70-75 internal discovery band, oss-cloud is the
iterative path to >=90 internal success, and Tessl live-private is external
confirmation at >=90 and >= baseline. If Tessl finds basic skill-behavior,
format, scenario, rubric, judge, reference, security, or package-shape failures,
classify that as an upstream SDK pipeline defect and patch the deterministic
guardrail before rerunning from oss-local.

## Codex Profile

Quick smoke checks may use Codex `[profiles.fast]` through `--profile fast`, but they do not satisfy the `oss-local` or `oss-cloud` proof lanes. Do not validate skill-factory output on the ambient Codex profile.

The `oss-local` and `oss-cloud` lanes must use `codex exec --profile oss-local` and `codex exec --profile oss-cloud`, or an SDK receipt proving `codex_exec_invoked=true` and the matching `codex_profile`.

## Tessl Eval Evidence

Tessl live-private dry-run must use the installed local `tessl` CLI after the SDK deterministic and OSS proof lanes. The wrapper copies controlled input to `/tmp/ask-tessl-evals/<skill-path>-<sha12>` and leaves that directory in place for inspection.

The improve-skill Tessl lane uses the product workspace `jscraik`.
If an operator or older example supplies `skills-sdk`, `skills-sdk-lab`, or
`jscraik-private`, the wrapper blocks that stale alias and requires `jscraik`
before creating project identity,
scenario-generation staging, local proof, or live-private dry-run receipts.

Tessl local proof must be an execute receipt, not a preview receipt. Tessl dry-run handoff evidence must prove both the `--tessl-live-dry-run` command and `tessl_eval.dry_run=true` in the receipt payload.

The staged input must include:

- `SKILL.md`
- `references/evals.yaml`
- `references/contract.yaml` when present
- `references/task-profile.json` when present
- `evals/<case-id>/task.md` plus `evals/<case-id>/criteria.json` synthesized from canonical `references/evals.yaml`
- `tessl.json`

Never run Tessl against the live repo source tree, and never use `npx tessl`, publish, registry upload, or package upload commands in this lane.

## External Review Floors

Plugin Eval is a budget and ergonomics guardrail. Grade `B+` or better with zero failures is acceptable when strict audit, evals, and Tessl gates pass.

Tessl is the content quality gate. Tessl review must run through the repo wrapper with `--json --threshold 90`; scores below `90` block Tessl acceptance. Scores `95+` remain the improvement target, not the minimum acceptance floor.

The Tessl review wrapper is preserved under `/tmp/ask-tessl-reviews/<skill-path>-<sha12>/current` with `.tessl-plugin/plugin.json`, `tessl.json`, copied skill files, and included references. Reruns archive the previous `current` directory under `evidence-archive/` before refreshing staged inputs.

## Reporting

Report the exact command, outcome, staged path, and blocker class. If Tessl cannot find a workspace/project link, classify that setup blocker directly. If Tessl cannot write its local CLI state in a sandbox, rerun with narrow filesystem permission for Tessl state before diagnosing the skill.
