---
name: skill-builder
description: Analyze and harden Codex skills and plugin packages for contract quality, eval coverage, and safety compliance. Use this skill when an existing package is approaching release and needs evidence-backed validation.
metadata:
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  last_reviewed: 2026-04-19
  metadata_source: frontmatter
---

# Skill Builder

Use this skill to harden an already-created skill package before release.

## When to use
- Quality or safety review for an existing skill or plugin package.
- Evals/contract/task-profile corrections before shipping.
- Benchmark-driven comparison against a baseline.

## Do not use
- First-draft scaffolding: route to `[[skill-creator]]`.
- Install/import and runtime visibility work: route to `[[skill-installer]]`.

## Core Philosophy
- Keep changes minimal, reversible, and evidence-backed.
- Prefer deterministic validation before narrative conclusions.
- Preserve required context by relocating depth to `references/`, never by deleting it.

## Core workflow
1. Confirm target path and intended mode (`audit` or `improve`).
2. Validate required artifacts first: `references/contract.yaml`, `references/evals.yaml`, `references/task-profile.json`.
3. Run deterministic validation gates before proposing edits.
4. Apply minimal fixes with explicit evidence.
5. Return machine-checkable output with blockers and risks.

## Required output contract
Provide:
- `schema_version`
- `mode`
- `target_path`
- `findings`
- `changes`
- `validation_evidence` with `pass|fail|blocked`
- `risks`

## Progressive disclosure policy
Never drop required context. Preserve context by relocating detailed guidance to `references/` and linking it from this file.

Read when:
- running family validation or benchmark gates: [validation checklist](./references/workflows-and-validation.md)
- selecting eval structure and comparison mode: [eval guidance](./references/evals-v2-migration.md)
- handling security and pressure-test expectations: [security checks](./references/security-checks.md)

## Anti-Patterns to Avoid
- Expanding scope beyond skill-quality hardening.
- Claiming pass status without command evidence.
- Removing context instead of relocating it to `references/`.

## Constraints
- Keep edits minimal and reversible.
- Report exact command outcomes.
- Treat secrets and credentials as sensitive; redact by default.
