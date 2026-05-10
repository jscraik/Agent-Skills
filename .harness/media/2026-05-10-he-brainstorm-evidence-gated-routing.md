# HE Brainstorm: From Synthetic Eval Drift -> Evidence-Gated Ambiguity Routing

## Purpose

Review media sidecar for the he-brainstorm hardening pass. The intended image
would explain the actual transformation from synthetic eval drift and implicit
brainstorm boundaries into evidence-gated ambiguity routing.

## Image Generation & Persistence Evidence

- `$imagegen` invoked: blocked
- generated-image cache source path: blocked; active image tool does not expose
  a discoverable cache path or native output path in its callable schema
- repository `.harness/media/` PNG path: blocked; no PNG was written
- prompt metadata path:
  `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-brainstorm-evidence-gated-routing-prompt.md`
- sidecar path:
  `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-brainstorm-evidence-gated-routing.md`
- repository PNG existence verification: blocked
- persistence method: blocked
- final user-facing text after imagegen permitted: no, per active image tool
  contract forbidding post-generation text
- residual risk: direct generation was not invoked because the requested
  persistence proof cannot be completed with the active tool contract.

## Bespoke Framing

- skill name: he-brainstorm
- original state: synthetic eval drift and implicit brainstorm boundaries
- target state: evidence-gated ambiguity routing
- main weakness: missing eval realism declarations and weakly contextualized
  eval prompts, plus implicit anti-trigger/safety/failure boundaries
- main improvement: validator-clean evals and explicit brainstorm routing,
  safety, failure, output, and confidence contract
- validation evidence: strict audit pass, strict-audit security gate pass,
  OpenClaw pass through strict audit, OpenAI format lint pass, progressive
  disclosure lint pass, markdownlint pass, Vale pass, lychee pass, Plugin Eval
  B/91 with invoke/deferred-cost warnings; direct `skill_gate.py` and post-patch
  smoke/release evals blocked by Codex usage-limit guard
- artifact impact: canonical `SKILL.md`, `references/evals.yaml`, and markdown
  references changed; generated runtime handle left untouched
- confidence movement: 78% -> 88%, capped by blocked post-patch smoke evals

## Prompt Summary

See prompt metadata:
`/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-brainstorm-evidence-gated-routing-prompt.md`.

## Linked Context

- Skill package:
  `/Users/jamiecraik/dev/agent-skills/Plugins/harness-engineering/skills/he-brainstorm`
- Runtime handle:
  `/Users/jamiecraik/dev/agent-skills/.agents/skills/he-brainstorm/SKILL.md`
