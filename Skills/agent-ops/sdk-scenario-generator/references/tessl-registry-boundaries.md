# Tessl Registry Boundaries

Use this reference when scenario generation touches Tessl tiles, Registry
publication, workspace sharing, installation, or repo-local tile rollout.

## Package Model

- Tessl treats context as packaged dependencies: docs, steering/rules, and
  skills can be bundled into tiles.
- The current manifest naming contract is `plugin.json`.
- Tile identity comes from `plugin.json` `name` in `workspace/tile-name`
  form, not from the GitHub repository name.
- A tile must contain at least one context surface such as `docs`,
  `steering`, or `skills`.
- When `describes` is present for package documentation, `docs` is required.
- `README.md` is Registry presentation content; do not assume it is loaded as
  agent context unless the tile also declares docs, rules, or skills.

## Evidence Lanes

Keep these lanes separate in scenarios, rubrics, and readiness summaries:

- Local package shape: `tessl skill lint` or `tessl tile lint`.
- Local skill review: `tessl skill review`.
- Scenario effectiveness: `tessl scenario ...` and `tessl eval ...` outputs.
- Repo-local install state: `tessl install file:...` plus `tessl.json`.
- Registry publication state: published workspace/tile version.
- Workspace access: membership and private/public visibility.
- Local code/test truth in the repository using the installed context.

Do not claim that one lane proves another. For example, local lint does not
prove a Registry version is current; Registry review metadata does not prove the
context works in the target repo; and repo-local tile presence does not prove
workspace publication or installability.

## Distribution Choices

Use repo-local tiles when the context belongs to one codebase and should travel
through normal source review. Use Registry tiles when the context is reusable
across repositories or teams, needs workspace access control, or needs versioned
updates independent of code changes.

Public publication is an explicit decision. Public tiles use `private: false`
and may not be reversible to private after publication. Default scenario
guidance should prefer private publication or repo-local tiles until the user has
approved public distribution.

## Scenario Implications

- Scenario tasks should not ask agents to publish, make public, add workspace
  members, or burn live eval capacity unless the user task explicitly authorizes
  that action.
- Registry scores and review signals are candidate-selection evidence. They do
  not replace local validation or representative scenario evals.
- If publishing readiness is under review, require `plugin.json` identity,
  semantic version intent, privacy choice, lint/review evidence, scenario eval
  evidence when skill effectiveness matters, and workspace access proof for
  private distribution.
- If repo-local rollout is under review, require the tile directory and the
  `tessl.json` file-source entry as separate artifacts.
