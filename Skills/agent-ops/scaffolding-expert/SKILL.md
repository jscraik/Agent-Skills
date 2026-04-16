---
name: scaffolding-expert
description: "Use when users ask how to scaffold or re-scaffold a repo: this skill chooses the right tier (`lite|growth|strict`), audits drift/conflict from file evidence, and returns minimal-change remediation aligned to the user's `~/dev` git-project style."
metadata:
  skill-type: runbook
---

# Scaffolding Expert

Decision and audit guidance for project scaffolding so teams avoid both under-structure and over-structure while preserving the user's existing operating style.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints and safety](#constraints-and-safety)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [Examples](#examples)
- [See Also](#see-also)
- [References](#references)

## When to use

Use this skill when work involves:
- choosing scaffold depth for a new repo or major rewrite;
- auditing an existing repo for scaffolding drift, overlap, or conflict;
- reconciling mixed workflow conventions (for example, package-manager drift, duplicate validation entrypoints, shell-policy mismatch);
- proposing minimal-change remediation that improves maintainability and accountability.

Do not use this skill for:
- ordinary feature implementation with no scaffolding/governance impact;
- full platform migration plans unrelated to scaffold structure.

## Required inputs

- target repo path and primary stack lane(s): `npm`, `bash`, `uv-python`, or mixed;
- project shape signals: team size, release cadence, compliance pressure, blast radius, expected lifespan;
- existing scaffold signals: instruction files, environment contracts, validation scripts, CI check policy files;
- workspace style root (default `~/dev`) when recommendations should align to the user's established `.git` project patterns;
- execution posture: assessment-only or implementation-ready recommendations.

If inputs are missing, default to assessment-only and report assumptions explicitly.

## Deliverables

- recommended scaffold tier (`lite`, `growth`, or `strict`) with evidence;
- style-profile summary derived from `~/dev` git projects (or explicit reason the scan was skipped);
- drift/conflict audit summary with exact file-path findings;
- minimal remediation plan ordered by dependency and risk;
- lane-specific validation commands and expected pass criteria;
- structured recommendation output including `schema_version` when schema-bound output is requested.

## Philosophy

- Prefer the smallest scaffold that satisfies real operational risk.
- Canonical source first: one owner per policy surface, projections second.
- Separate required control points from optional convenience automation.
- Avoid introducing framework/process overhead that the repo cannot sustainably maintain.

## Workflow

1. Intake and scope the scaffold surface.
- Do map instruction precedence (`AGENTS.md` and deeper scoped overrides) before proposing structure changes because precedence mistakes create invalid scaffolding decisions.
- Do identify canonical routing docs and validation entrypoints before drafting changes because remediation must target source-of-truth surfaces.

2. Profile the user's project style from local git repos.
- Do run `bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev` when the request expects the user's usual style because this captures recurring control-plane conventions across `.git` projects.
- Do use `Infrastructure/references/jamie-dev-style-signals.md` to interpret profile output because counts alone are not a recommendation.
- Do state any scan limitations (missing `fd`/`jq`, inaccessible root, or intentionally skipped scan) because unresolved context changes confidence.

3. Classify scaffold tier.
- Do use `Infrastructure/references/scaffold-tier-matrix.md` because it converts risk and complexity into a defensible tier.
- Do score by risk, complexity, multi-surface requirements, and team operating model because tier drift usually starts with implicit assumptions.

4. Audit drift and conflict.
- Do use `Infrastructure/references/drift-conflict-audit.md` because it keeps findings comparable across repos.
- Do capture concrete drift types such as duplicate ownership, conflicting scripts, CI parity gaps, and environment contract drift because remediation ordering depends on drift class.
- Do cross-check drift findings against the style profile because established workspace conventions may explain an apparent mismatch.

5. Recommend minimal-change remediation.
- Do fix highest-leverage blockers first (entrypoint ambiguity, validation drift, contract conflicts) because early fixes reduce rework and false negatives.
- Do preserve stable conventions unless they conflict with declared canonical policy because forced standardization often increases operator burden.
- Do call out where recommendations intentionally follow the user's observed style because that protects team adoption.

6. Route to lane-specific guidance.
- Do apply [[npm-workflow-discipline]] for npm dependency and script contracts because lockfile/install semantics need deterministic policy.
- Do apply [[bash-hygiene]] for shell and hook hygiene because interpreter and quoting drift is a common scaffold breakage.
- Do apply [[uv-python-project-setup]] for Python environment and lockfile flows because `uv` contracts are stronger than ad hoc virtualenv guidance.
- Do use [[context7]] for version-sensitive dependency/API questions because external library behavior can drift quickly.

7. Produce recommendation package.
- Do provide tier decision, style-profile summary, audit findings, remediation order, and validation ladder because users need both diagnosis and execution path.
- Do use template formats in `Infrastructure/references/recommendation-templates.md` because stable output contracts improve downstream automation.

## Validation

Run the smallest relevant checks first, then broaden:

```bash
# Workspace-style profile (recommended when personal style alignment matters)
bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev

# Optional when repository provides these wrappers
bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required
bash Infrastructure/scripts/validation-and-linting/verify-work.sh --fast
```

Lane checks are in `Infrastructure/references/validation-lanes.md`; apply only the lanes touched by the recommendation.

Fail-fast policy:
- stop at first blocking mismatch;
- report exact blocker evidence;
- continue only after the blocker is addressed.

## Constraints and safety

- Redact secrets, tokens, and private internal data by default.
- Do not recommend destructive operations unless explicitly requested.
- Do not introduce mixed package-manager or interpreter policies.
- Keep `SKILL.md` concise; move deep matrices/examples to `Infrastructure/references/`.
- Keep recommendations actionable with command-accurate validation.

## Anti-patterns

- Over-scaffolding small or short-lived projects.
- Multiple canonical owners for the same control surface.
- Validation entrypoints that disagree with CI required checks.
- Shell scripts mixing `sh` and Bash semantics without explicit intent.
- Python dependency flows that bypass `uv` lock/sync guarantees.
- Recommending governance controls with no operator maintenance path.

## Failure mode

- If the repo path is unknown, return an intake checklist instead of guessing.
- If tier signals are contradictory, recommend the lower-risk tier and state the unresolved signals.
- If policy files conflict, stop and surface the contradiction before proposing implementation.

## Gotchas

- Teams often optimize for immediate speed and accidentally choose `strict` scaffolds they cannot maintain.
- CI check-name parity drift causes repeated PR friction even when code is correct.
- Generated tooling docs can appear healthy while the underlying contract scripts drift.
- Environment contracts are frequently copied across repos without adapting stack-specific commands.

## Examples

- "Should this repo stay lightweight or adopt full preflight/verify/check-parity governance?"
- "Audit this monorepo for scaffolding conflicts after we mixed npm scripts with pnpm docs."
- "We have `.codex/environments/environment.toml` and `Infrastructure/scripts/check-environment.sh` drift; what is the minimal correction path?"
- "Use how I normally scaffold repos in `~/dev` and tell me what tier and controls this new project should adopt."

## See Also

| Skill | When to use together |
|---|---|
| [[npm-workflow-discipline]] | Lockfile discipline and script contract normalization |
| [[bash-hygiene]] | Shell-policy and quoting/interpreter hardening |
| [[uv-python-project-setup]] | uv-managed Python project and execution contract setup |
| [[context7]] | External docs grounding for version-sensitive dependencies |

**Topic map:** [[agent-ops]]

## References

- `Infrastructure/references/scaffold-tier-matrix.md`
  Read when: you need the tier scoring model and escalation/de-escalation rules.
- `Infrastructure/references/jamie-dev-style-signals.md`
  Read when: you need the `~/dev` style-profile scan contract and interpretation guidance.
- `Infrastructure/references/drift-conflict-audit.md`
  Read when: you are collecting file-level drift evidence and need consistent severity surfaces.
- `Infrastructure/references/validation-lanes.md`
  Read when: you need lane-specific command ladders and pass criteria.
- `Infrastructure/references/recommendation-templates.md`
  Read when: you need structured response payload templates (`schema_version` outputs).
- `Infrastructure/references/examples.md`
  Read when: you need canonical scenario patterns before writing recommendations.
- `Infrastructure/references/contract.yaml`
  Read when: you need machine-checkable boundaries, inputs, and non-goals.
- `Infrastructure/references/evals.yaml`
  Read when: you need trigger and non-trigger test cases for release/smoke validation.
- `Infrastructure/references/task-profile.json`
  Read when: you need evaluation thresholds and delegation posture metadata.
