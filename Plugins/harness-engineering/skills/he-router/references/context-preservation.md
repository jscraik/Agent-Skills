# Harness Engineering Router Context Preservation

Keep these longer-form router rules out of the active trigger body while preserving
the prior operating contract for audit and future restoration.

- Prior compact frontmatter:

```yaml
description: "Use when ambiguous, mixed, or folded-alias HE requests need the correct stage."
```

- Choose one Harness Engineering lifecycle stage.
- Use the user request, artifact state, and Linear evidence as the routing source.
- Prefer the smallest stage that safely unblocks the user.
- Keep routing separate from implementation.
- Parse direct `he-*` stage names, artifact state, lifecycle words, and risk words before broad keyword matches.
- Translate folded stage names through `Plugins/harness-engineering/references/folded-skill-context.md` before selecting a stage.
- Apply the deterministic decision order in `Plugins/harness-engineering/references/deterministic-stage-routing.md`.
- Pick exactly one stage from `Plugins/harness-engineering/references/routing-map.json`.
- Route domain-language conflicts through `Plugins/harness-engineering/references/domain-model-routing.md`.
- Route QA or feedback sessions through `Plugins/harness-engineering/references/qa-intake-routing.md`.
- Route prior-session or repeated-failure requests through `Plugins/harness-engineering/references/session-evidence-contract.md`.
- Route coverage-gap and skillify-candidate evidence to `he-improve` for triage before any new skill package is proposed.
- Return `schema_version: 1` when structured output is requested, plus `selected_stage`, `matched_rule`, `confidence`, `rationale`, `recommended_next_step`, and `missing_input` when blocked.
- Select exactly one primary stage.
- Do not implement product code.
- Do not select `he-work` for review, PR, go/no-go, failing test, root-cause, TDD, browser-polish, optimization, or stale-branch cleanup requests.
- Redact secrets and sensitive data.
- Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.
- Do not treat ambiguous review or failing-test language as implementation work.
- Do not create a plan when a spec is missing.
- Do not route stale-branch cleanup through feature work.
- Do not invent Linear state when the issue status is absent.
- Never drop required context for brevity; move it into references or deferred context and link it here.
- Ensure the selected stage exists in the HE stage set, the recommendation is stage-specific, and conflict cases obey deterministic routing before broad keyword matches.
- Fail fast when the selected stage is absent from the routing map, required artifact evidence is missing, or lifecycle cues conflict; stop at the first failed gate and report the blocker.
- If required evidence is missing, return `confidence: blocked` with exactly one `missing_input`; do not guess a stage.
- `review`, `PR`, `go/no-go`, and `failing test` requests are not implementation requests.
- Linear issue references are routing evidence, not a substitute for artifact checks.
- Session evidence requests need prior-session or repeated-failure context before choosing a stage.
- Collector `he-*` path fragments and bundle names are evidence labels, not valid stage invocations, until they match the routing map.
