# Gold-Standard Hook Patterns

Read when: you want starter behaviors that feel production-ready without exceeding the March 2026 stable runtime contract.

## Table of Contents
- [Principles](#principles)
- [Recommended starter pack](#recommended-starter-pack)
- [Project vs user scope](#project-vs-user-scope)
- [Behavior patterns](#behavior-patterns)
- [Validation standard](#validation-standard)
- [What to avoid](#what-to-avoid)

## Principles
- Keep the pack small because hook latency compounds across every session and turn.
- Fail open on missing optional tooling because a transient local environment issue should not block all Codex work.
- Use explicit JSON outputs because structured control flow is easier to test than ad hoc stdout parsing.
- Make blocking behavior narrow and explainable because hooks should guide, not surprise.
- Keep policies local to the right config layer because repo policy and personal policy age differently.

## Recommended starter pack
For most repos, start with three hooks:

1. `SessionStart`
- Add a short repo-aware context string.
- Mention dirty worktree state, branch, and validation hints.
- Use `matcher: "^(startup|resume)$"` so the hook stays explicit.

2. `UserPromptSubmit`
- Block direct attempts to ignore system, developer, or repo instructions.
- Add small context for risky shortcut prompts such as skipping validation or using destructive commands.
- Keep this narrow so normal prompts are unaffected.

3. `Stop`
- Prevent clearly incomplete final responses.
- Catch draft markers, unresolved checklist items, and validation-skipped claims without reasons.
- Respect `stop_hook_active` so the hook does not trap the session in a retry loop.

## Project vs user scope
Prefer project scope when:
- validation rules differ by repo;
- startup context depends on repo layout;
- the hook pack would be noisy in unrelated repos.

Prefer user scope when:
- the rule is personal and durable across all repos;
- the same safety guardrails genuinely apply everywhere;
- you want one global starter pack in `~/.codex`.

Do not install the same pack in both places unless you intentionally want duplicate execution.

## Behavior patterns
`SessionStart`
- good pattern: infer nearest scoped repo root from `cwd`, then emit concise context and warnings
- bad pattern: dump long build docs or policy essays into `additionalContext`

`UserPromptSubmit`
- good pattern: block prompt-injection phrasing and annotate risky shortcut language
- bad pattern: try to lint or rewrite the entire user prompt

`Stop`
- good pattern: block only on obvious incompleteness with a one-shot corrective reason
- bad pattern: block stylistic differences or subjective tone choices

## Validation standard
Minimum:
- `zsh -n` every hook script
- `jq .` the generated `hooks.json`
- dry-run one representative payload per enabled event

Better:
- rerun the `Stop` dry-run with `stop_hook_active: true` to prove it does not re-block
- test one harmless prompt and one policy-violating prompt through `UserPromptSubmit`
- test `SessionStart` on both a repo directory and a non-repo directory

## What to avoid
- unsupported `prompt`, `agent`, or `async` hooks sold as stable;
- relative command paths inside `hooks.json`;
- giant `SessionStart.additionalContext` strings;
- `Stop` logic that blocks because tests were skipped even when a valid reason is present;
- hook scripts that assume one package manager or repo shape without checking.
