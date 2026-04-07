---
name: skill-creator
description: Author new Codex skill scaffolds with contract-ready starter files and explicit lifecycle handoff metadata. Use this skill when users need new-skill creation or scaffold-bound edits before hardening, packaging, or installation work.
metadata:
  short-description: Create first-pass skill scaffolds with clear handoff
---

# Skill Creator

Create the first usable version of a skill using the unified **Agent Skills Kit (`ask`)** CLI, then hand off non-trivial lifecycle work to `skill-builder`.

## When to use

Use this skill when the user asks to:
- create a brand-new skill from scratch;
- complete a just-generated scaffold;
- produce an initial starter package before deeper optimization.

Do not use this skill as primary owner when the request is mainly about:
- eval or routing hardening across existing skills;
- release-quality benchmarking and comparative rounds;
- install/import distribution workflows;
- plugin packaging or marketplace policy.

Handoffs:
- to `skill-builder` for lifecycle hardening and comparative eval work;
- to `skill-installer` for downstream install/import;
- to `plugin-builder` when the deliverable boundary is a plugin package.

## Inputs

Collect the minimum required inputs before drafting files:
- skill goal and target outcomes;
- trigger contexts and non-triggers;
- intended location (default `${CODEX_HOME:-$HOME/.codex}/skills`);
- required bundled resources (`scripts/`, `references/`, `assets/`);
- constraints from user policy, tool access, or repo conventions.

If scope is broad, narrow first pass to 2-3 focused surfaces and defer the rest to handoff.

Destination guardrail:
- confirm the destination path before first write, even when using the default `${CODEX_HOME:-$HOME/.codex}/skills`.

## Outputs

Produce a starter package that another agent can execute without guessing:
- `SKILL.md` with clear triggering description and bounded procedure;
- `agents/openai.yaml` aligned with the skill contract;
- starter resource files in `scripts/`, `references/`, or `assets/` only when needed;
- for non-trivial starter work, `references/handoff-package.md` in the target skill.

Output contract notes:
- keep machine-checkable artifacts versioned when schema-bound;
- include `schema_version` fields in structured artifacts that define strict contracts.

For non-trivial handoff-ready starters, also include:
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json` (when intended for operational graph participation)
- `references/handoff-package.md` copied from `references/handoff-package-template.md` and filled with concrete scope, blockers, and next actions.

## Philosophy

Starter-authoring should optimize for clarity, portability, and clean ownership transfer:
- Codex is already capable, so include only high-signal instructions;
- prefer reusable resources over repeating implementation details in chat;
- write for the next maintainer, not only the current run;
- keep first pass small, explicit, and easy to validate.

## Constraints

- Keep frontmatter canonical: required keys are `name` and `description`; optional official keys are `license`, `compatibility`, `allowed-tools`, and `metadata`.
- Do not invent extra top-level frontmatter keys.
- Ensure `description` is action-oriented and routing-strong.
- Never expose secrets, tokens, private keys, or personal data in examples or generated files.
- Redact sensitive strings by default when showing logs, manifests, commands, or sample outputs.
- Keep references one level deep from `SKILL.md`; avoid deeply nested discovery trees.
- Prefer deterministic script usage over speculative manual steps when a helper script exists.

## Procedure

1. Clarify scope and collect concrete trigger examples.
2. Derive the smallest reusable package (`scripts`, `references`, `assets`) from those examples.
3. Initialize or complete the scaffold via the unified CLI (`ask skills init`).
4. Fill `SKILL.md` and `agents/openai.yaml` with bounded, role-correct guidance.
5. Add or update contract/eval artifacts for non-trivial starters.
6. Run validation gates, including `ask skills audit` and smoke eval execution, and fix failures.
7. If lifecycle hardening is needed, create `references/handoff-package.md` and hand off to `skill-builder`.

Primary command:

```bash
# Initialize a new skill scaffold
bin/ask skills init <skill-name> --category <category> --description "..."
```

## Anti-Patterns

Avoid these common failures:
- building full lifecycle gates in `skill-creator` instead of handing off;
- writing long narrative docs instead of concrete starter assets;
- mixing plugin packaging behavior into standalone starter authoring;
- shipping non-trivial starters without handoff artifact and contract/eval files;
- leaving placeholder text like `todo` in final skill outputs.

## Examples

- When the user asks: "Can you build a starter skill for incident postmortems and include a references template?"
- When the user says: "I need a first-pass scaffold for a new cloud provider CLI."
- When the user asks: "Please create the initial skill package now and include a handoff artifact for hardening."

## Validation

Run gates in order and fail fast: stop at the first failed gate, fix it, then rerun from that gate onward.

```bash
# Structural and Security Audit
bin/ask skills audit <path/to/skill-folder> --level strict

# Full Repository Health
bin/ask repo validate --ephemeral
```

Family gate note:
- `scripts/validate_skill_authoring_family.sh` defaults to structural contract/security checks (smoke+release case listing).
- Live Codex smoke+release execution is trusted-lane only with `SKILL_FAMILY_LIVE_EVALS=1 SKILL_FAMILY_LIVE_EVALS_TRUSTED=1`.

## See Also

| Skill | When to use together |
|---|---|
| [[skill-builder]] | Lifecycle hardening, comparative eval rounds, and release-quality contract upgrades |
| [[skill-installer]] | Installing already-valid skills into Codex environments |
| [[cli-spec]] | Consult the technical contract for the ask CLI |

**Topic map:** [[agent-ops]]
