# SynAIpse Harness Router Context Preservation

Keep these older router rules out of the entrypoint while preserving audit value.

- Choose one SynAIpse Harness lifecycle stage.
- Use request text, artifact state, and Linear evidence as routing source.
- Prefer the smallest stage that safely unblocks the user.
- Keep routing separate from implementation.
- Parse direct `sy-*` stage names, artifact state, lifecycle words, and risk
  words before broad keyword matches.
- Translate folded names through
  `Plugins/synaipse-harness/references/folded-skill-context.md`.
- Apply
  `Plugins/synaipse-harness/references/deterministic-stage-routing.md`.
- Pick exactly one stage from
  `Plugins/synaipse-harness/references/routing-map.json`.
- Route domain-language conflicts through
  `Plugins/synaipse-harness/references/domain-model-routing.md`.
- Route QA or feedback sessions through
  `Plugins/synaipse-harness/references/qa-intake-routing.md`.
- Route prior-session or repeated-failure requests through
  `Plugins/synaipse-harness/references/session-evidence-contract.md`.
- Route coverage-gap and skillify-candidate evidence to `sy-improve` before
  any new skill package is proposed.
- Structured output includes `schema_version`, `selected_stage` or `blocker`,
  `matched_rule`, `confidence`, `recommended_next_step`, and `missing_input`
  when blocked.
- Select exactly one primary stage and do not implement product code.
- Never select `sy-work` for review, PR, go/no-go, failing-test, root-cause,
  TDD, browser-polish, optimization, or stale-branch cleanup requests.
- Redact secrets and sensitive data.
- Move budget-trimmed context to references and index it in
  `Plugins/synaipse-harness/references/deferred-context-index.md`.
- Do not treat ambiguous review or failing-test language as implementation work.
- Do not create a plan when a spec is missing.
- Do not route stale-branch cleanup through feature work.
- Do not invent Linear state when the issue status is absent.
- Ensure the selected stage exists in the SynAIpse stage set, the recommendation is
  stage-specific, and conflict cases obey deterministic routing before broad
  keyword matches.
- Fail fast when the selected stage is absent from the routing map, required
  artifact evidence is missing, or lifecycle cues conflict; stop at the first
  failed gate and report the blocker.
- If required evidence is missing, return `confidence: blocked` with exactly
  one `missing_input`; do not guess.
- `review`, `PR`, `go/no-go`, and `failing test` are not implementation
  requests.
- Linear references are routing evidence, not substitutes for artifact checks.
- Session evidence requests need prior-session or repeated-failure context
  before choosing a stage.
- Collector `sy-*` path fragments and bundle names are evidence labels, not
  valid stage invocations, until they match the routing map.
