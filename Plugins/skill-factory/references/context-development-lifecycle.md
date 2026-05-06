# Context Development Lifecycle

Use this when a skill change is meant to make agent behavior more reliable, not just satisfy a format check.

Treat every skill as a context package with a lifecycle:

1. Generate: capture the trigger, task shape, inputs, outputs, constraints, and source-of-truth references.
2. Test: run structural checks, strict audit, realistic routing/eval cases, and tool-backed smoke paths where available.
3. Distribute: refresh the relevant workspace, user, plugin, marketplace, or copied runtime surface when visibility matters.
4. Observe: record how future failures will surface through PR feedback, CodeRabbit/Codex findings, session-collector bundles, traces, validation logs, or plugin-eval reports.
5. Adapt: feed repeated failures back into the skill, reference, eval, or routing map instead of treating each fix as a one-off.

Minimum gate for skill hardening:

- name the lifecycle stage being changed;
- cite concrete evidence or a realistic scenario;
- add or update at least one validation/eval path when behavior changes;
- avoid copying raw transcripts, reviewer text, or logs into `SKILL.md`;
- leave a clear handoff for future observation or adaptation.

Consistency check for fuzzy context:

When a proposed skill, spec, or plan is vague enough that multiple agents could reasonably implement different things, compare independent interpretations before drafting durable instructions. If the interpretations diverge on objective, boundaries, risks, or done criteria, return to clarification instead of packaging the workflow.
