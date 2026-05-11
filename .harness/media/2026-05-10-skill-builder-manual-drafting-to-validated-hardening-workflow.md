# Skill Builder: From Manual Drafting -> Validated Hardening Workflow

## Purpose

Review media artifact for the skill-builder hardening patch that folded a large Codex-harness review and media workflow into durable skill behavior without bloating the entrypoint.

## Image Generation & Persistence Evidence

- `$imagegen` invoked: yes
- generated-image cache source path: `~/.codex/generated_images/019e1292-3f9d-7db2-99d6-2d16ecee653a/ig_0f920b1b6326cbef016a00e3e1f0248191a2b8a1d34ce49ed4.png`
- repository `.harness/media/` PNG path: `.harness/media/2026-05-10-skill-builder-manual-drafting-to-validated-hardening-workflow.png`
- prompt metadata path: `.harness/media/2026-05-10-skill-builder-manual-drafting-to-validated-hardening-workflow-prompt.md`
- sidecar path: `.harness/media/2026-05-10-skill-builder-manual-drafting-to-validated-hardening-workflow.md`
- repository PNG existence verification: pass
- persistence method: cache-copy
- final user-facing text after imagegen permitted: no, active image tool contract forbids narrative text after generation
- residual risk: image text may need deterministic overlay review; cache-copy persistence is verified.

## Bespoke Framing

- skill name: skill-builder
- original state: manual drafting and prompt-carried hardening rules
- target state: validated Skill Factory hardening workflow with routed reference detail
- main weakness: long review/media workflow was not durable without risking entrypoint bloat
- main improvement: compact entrypoint plus routed hardening workflow reference, eval updates, contract updates, and measured validator evidence
- validation evidence: strict audit pass; OpenClaw pass; OpenAI format pass; progressive disclosure pass; Plugin Eval A/95 with invoke-cost warning; smoke eval fail
- artifact impact: `SKILL.md`, `agents/openai.yaml`, `contract.yaml`, `evals.yaml`, `references/harness-hardening-workflow.md`, media prompt metadata, media sidecar
- confidence movement: 68% -> 82%, capped by failed smoke evals

## Prompt Summary

See prompt metadata for the full image prompt.

## Linked Context

Skill under review: `Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md`
