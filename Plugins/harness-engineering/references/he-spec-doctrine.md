# he-spec Retained Doctrine

Read when: the compact `he-spec` entrypoint is not enough.

## Core Job

`he-spec` creates the Harness Engineering WHAT contract before `he-plan` decides HOW. A good spec removes behavior ambiguity, records boundaries, defines acceptance IDs, and makes failure plus observability explicit enough that planning does not invent product behavior.

## Source Grounding

Use the strongest available source and record source-parity: active Linear issue, current tracked spec, brainstorm, QA report, UI source or parent spec, normalized session evidence, matching repo specs, then raw feature description.

When multiple artifacts exist, distinguish the current active artifact from the latest dated artifact. If they conflict, stop or record the contradiction before planning handoff.

## Session Evidence

Fresh 2026-05-02 collector evidence showed 431 sessions in seven days, strong `harness-engineering` signal, repeated HE stages, and validation/tool-call patterns useful for grounding. Use `~/.agents/session-collector` output to summarize decisions, blockers, gates, and project hints. Do not copy raw transcripts or sensitive identifiers.

## Codex Mode Lessons

Live Codex Plan Mode separates discoverable facts from preference/tradeoff questions and requires exploration before asking. It also keeps `update_plan` separate from durable artifacts. `he-spec` should follow both rules.

## Agent Skills Kit Spec Pattern

Strong local specs include schema/status/risk/depth/UI frontmatter, mode decision, baseline, Linear contract, boundary, domain model, lifecycle/interfaces, invariants, failure, observability, acceptance matrix, Linear traceability, first slice, and `he-plan` handoff.

## Compression Recovery

When the source evidence says a prior cockpit, golden-path, or agent-native plan
left too much visible surface, write a recovery spec instead of another broad
architecture spec. The recovery spec must promote compression from guidance to
blocking acceptance: first-contact help budget, agent catalog budget, standalone
command admission, docs deletion budget, fresh-agent eval, ablation proof, and
evidence-backed north-star metrics. Do not let additive compatibility, metadata,
or classification count as product compression.
