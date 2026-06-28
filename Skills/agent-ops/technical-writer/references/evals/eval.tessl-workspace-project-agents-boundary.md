# eval.tessl-workspace-project-agents-boundary: Tessl Workspace Project And AGENTS Boundary

Knowledge claim: Technical-writer should keep Tessl workspace, Tessl project identity, private package visibility, eval history, and consuming-repository instruction context in separate documentation lanes.
Behavior under test: Runtime-lane docs boundary control.
Expected agent move: Writes an operator-facing patch that names `jscraik` as the workspace, names standalone and plugin-owned project identities such as `jscraik/technical-writer` and `jscraik/skill-factory`, states that eval runs attach to the project, preserves private-by-default visibility, and excludes `AGENTS.md` from staged Tessl plugin payload context.
Failure mode: Treats `jscraik` as a single shared project, copies `AGENTS.md` into skill references or Tessl rules, or claims registry publication/readiness from project-link or docs evidence.
Given: A Skills SDK runtime-lane correction needs to explain Tessl project history without blurring package visibility or agent instruction boundaries.
Should: Write `tessl-project-boundary.md`; separate workspace, project, private visibility, eval history, and `AGENTS.md` authority; and avoid publish-readiness claims.
Expected failure: Collapses workspace and project identity or treats `AGENTS.md` as staged skill/package context.
