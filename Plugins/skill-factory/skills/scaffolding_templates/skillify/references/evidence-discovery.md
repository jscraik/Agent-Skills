# Skillify Evidence Discovery

Use this reference when the user asks to find repeated workflows worth packaging, not only when they already provide a workflow.

## Evidence Order

Use available evidence in this order:

1. Recent Codex sessions and task summaries from the local session collector.
2. Codex memories and rollout summaries, including durable memory-extension notes, to find patterns repeated across sessions.
3. Project Brain surfaces in the active repo, especially `.harness/knowledge/**`, `.harness/decisions/**`, and `.harness/review-log.md` when present.
4. Project-local Obsidian or markdown vaults when the repo declares one; use them as graph/viewer or knowledge context unless the repo explicitly makes them canonical.
5. Chronicle only when enabled and relevant, for discovery of recent work outside Codex; verify important details against the source system before packaging.
6. Existing skills, custom agents, and automations, so the result extends or reuses what already exists before creating a duplicate.

## Local Surfaces

- Session collector: `~/.agents/session-collector`; preferred bundle outputs include `skillify-candidates.json`, `skill-invocation-summary.json`, `skill-proof-candidates.json`, `skill-refactor-handoffs.json`, and `project-evidence.json`.
- OTel collector: `~/.agents/otel-collector`; use `data/processed/stats.json`, `/stats`, and telemetry confidence as freshness and observability context, not as the sole authority for packaging.
- Observability stack: `~/.agents/observability-stack`; use only for local runtime evidence and correlation.
- Memory extensions: prefer fresh persisted Codex memory under `~/.codex/memories/extensions/`; `~/dev/configs/codex/memories_extensions/` is a legacy projection mirror useful for archived Chronicle instructions and resources.
- Project Brain: inspect `.harness/knowledge/**`, `.harness/decisions/**`, `.harness/review-log.md`, and repo docs that describe Project Brain indexing. Treat decision records as higher authority than knowledge summaries when both exist.
- Project-local Obsidian or vault roots: inspect only when the repo declares or contains a vault, `.obsidian`, topic-map, or wiki/graph surface. Obsidian is usually a viewer over markdown links, not a canonical writer; verify claims against repo source, decisions, commands, or task artifacts before packaging.
- Existing Codex config assets: inspect skills, custom agents, and automations before creating a new package.

## Candidate Criteria

Only act on a candidate when it:

- occurred at least twice, or is clearly likely to recur and costly to repeat;
- has stable inputs, a repeatable procedure, and a clear output or stopping condition;
- would materially improve speed, quality, consistency, or reliability;
- is not already adequately covered by an existing skill, custom agent, automation, validator, or doc.

## Smallest Form

- Skill: reusable workflow or playbook that should be invoked on demand.
- Custom subagent: bounded specialist role or investigation task suitable for delegation.
- Automation: scheduled or recurring check, report, reminder, or monitor.
- Skip: work that is too one-off, ambiguous, sensitive, poorly evidenced, or already covered.
- Extend existing: existing skill, agent, automation, script, or validator covers the lane but needs a narrow improvement.

## Required Shortlist

Before creating anything, produce a compact shortlist with:

- repeated workflow
- supporting evidence and dates
- frequency and confidence
- recommended form: skill, subagent, automation, extend existing, or skip
- why it is or is not worth creating

Then create only high-confidence missing items. Keep them narrow, practical, source-aware, and easy to validate.

## Blocked Discovery Output

If command access, source files, memories, telemetry, Project Brain, or vault
surfaces cannot be read, return a blocker instead of an invented shortlist. The
blocker still needs to preserve the discovery map so the next agent knows which
surfaces matter:

- session collector and `skillify-candidates.json` or adjacent bundles;
- Codex memories, rollout summaries, and memory-extension notes;
- Project Brain surfaces such as `.harness/knowledge/**`,
  `.harness/decisions/**`, and `.harness/review-log.md`;
- project-local Obsidian, markdown vault, wiki, or graph surfaces when declared
  by the repo;
- OTel, telemetry, or observability surfaces when requested;
- existing skills, custom agents, automations, docs, scripts, validators, and
  hooks that might already cover the candidate.

For each unavailable source class, state the permission, command output, path, or
artifact needed to unblock verification. Do not collapse blocked discovery into
generic "enable shell" guidance when the user named specific evidence surfaces.

## Closeout

Finish with what was created or extended, what was deliberately skipped, and what needs more evidence before packaging.
