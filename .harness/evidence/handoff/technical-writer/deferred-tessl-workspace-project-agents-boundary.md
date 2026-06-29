# Deferred Tessl Workspace Project And AGENTS Boundary Scenario

Status: deferred from current Tessl-comparable scenario universe.

Reason: the current Tessl score receipt records 32 scenarios and does not
include either `tessl-workspace-project-agents-boundary` or
`generated-eval.tessl-workspace-project-agents-boundary`. Keeping this
scenario in `references/evals.yaml` or as `references/evals/eval.*.md`
would make the SDK expect 34 scenarios and would make OSS/Tessl evidence
incomparable to the recorded Tessl score receipt.

Knowledge claim: Technical-writer should keep Tessl workspace, Tessl project
identity, private package visibility, eval history, and consuming-repository
instruction context in separate documentation lanes.

Behavior under test: Runtime-lane docs boundary control.

Expected agent move: Writes an operator-facing patch that names `jscraik` as
the workspace, names standalone and plugin-owned project identities such as
`jscraik/technical-writer` and `jscraik/skill-factory`, states that eval runs
attach to the project, preserves private-by-default visibility, and excludes
`AGENTS.md` from staged Tessl plugin payload context.

Failure mode: Treats `jscraik` as a single shared project, copies
`AGENTS.md` into skill references or Tessl rules, or claims registry
publication/readiness from project-link or docs evidence.

Given: A Skills SDK runtime-lane correction needs to explain Tessl project
history without blurring package visibility or agent instruction boundaries.

Should: Write `tessl-project-boundary.md`; separate workspace, project,
private visibility, eval history, and `AGENTS.md` authority; and avoid
publish-readiness claims.

Expected failure: Collapses workspace and project identity or treats
`AGENTS.md` as staged skill/package context.

Reactivation rule: only move this back into `references/evals.yaml` or
`references/evals/eval.*.md` when the staged Tessl source receipt and Tessl
score receipt include the matching scenario paths.
