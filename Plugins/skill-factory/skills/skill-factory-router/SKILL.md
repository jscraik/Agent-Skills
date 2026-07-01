---
name: skill-factory-router
description: "Analyzes Codex skill-management requests, selects the workflow lane, and returns selected_lane, mode, next_step, and blockers. Use when the user says create a skill, add/update/fix/review a skill, install/sync/list skills, choose a workflow, or merge/retire a skill."
metadata:
  version: "1.0.0"
  skill-type: team_automation
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-05-28:canonical-source
  share_readiness: ready
  review_cadence: quarterly
  last_reviewed: "2026-05-28"
  metadata_source: frontmatter
  compatible_roles: default, worker, skill-inspector
  runtime_needs: repo-owned skill source path; Skill Factory skill inventory; ./bin/ask skills external-review
---

# Skill Factory Router

Select the smallest durable Skill Factory workflow for a Codex skill-management request, then return a read-only routing handoff before loading deeper instructions.

## When To Use

- The user asks to create, capture, improve, audit, refactor, install, sync, list, prove, or route a Codex skill.
- The request names skill work but the correct Skill Factory lane is not already certain.
- The request depends on Tessl, Plugin Eval, validation, runtime, installation, package visibility, or session evidence and needs the correct owner lane before action.

Do not use this router to execute the downstream lane. Route plugin package lifecycle work to plugin-factory. Route system creator and installer work to the system lanes instead of copying those bodies into Skill Factory.

Example requests that should trigger this router:

- "Create a skill from this workflow and tell me which lane owns it."
- "This skill is failing package proof; route the smallest hardening workflow."
- "Should this be skill-refactor, skillify, or the system skill creator?"

Start with the smallest package boundary that can answer the routing question. Inspect the target request, target skill, and one evidence handle before expanding to broader package or runtime state.

## Inputs

- User request or named target skill.
- Current authority boundary: read-only routing, approved edit, install or sync, eval execution, package publication, or review-only.
- Available evidence handle when routing depends on Tessl, Plugin Eval, validation, runtime, review, or session artifacts.

If target, lane, write authority, or validation requirement is missing, ask one plain-language question. Load references/discovery-interview.md only when that ambiguity cannot be resolved from the user request.

## Outputs

Return one YAML handoff:

    schema_version: 1
    selected_lane: .system/skill-creator|skillify|skill-factory-router|skill-refactor|.system/skill-installer
    mode: create|capture|harden|analyze|install
    rationale: <one sentence tied to the request shape>
    next_step: <specific skill or system lane to load next>
    first_principles_check:
      required: true|false
      result: skill|docs|script|hook|validator|rule|answer|not_checked
    blocked_by: null

Expected artifacts: no source edits from this router. Downstream lanes own review reports, eval artifacts, package outputs, runtime evidence, commits, and publication receipts.

## Workflow

1. Match the request to this routing table. Explicit lane names win unless the user names multiple lanes or asks for an unsafe action.
2. For create, draft, or new SKILL.md requests, select .system/skill-creator with mode create.
3. For skillify, save this process as a skill, or make reusable guidance requests, select skillify with mode capture.
4. For fix, improve, raise Tessl score, repair evals, or reduce token cost requests, select the Skill Factory hardening workflow with mode harden.
5. For failing-skill, duplicate comparison, merge, or retire requests, select skill-refactor with mode analyze.
6. For install, list, sync, or prove Codex can see a skill requests, select .system/skill-installer with mode install.
7. For copy or fork the system skill creator or installer requests, block the fork and route to the matching system lane.
8. For major new-skill or broad-rewrite requests, decide whether the durable answer is a skill, docs, script, hook, validator, rule, or direct answer.
9. Return the handoff and stop unless the user explicitly asks this router to execute the selected lane.

Use Infrastructure/references/first-principles-factory-gate.md for the first-principles factory gate before routing create, harden, refactor, or skillify work.
For .system/skill-creator or .system/skill-installer, attach Skill Factory references or eval contracts; do not fork the system skill body. Apply the context-disposition policy: move important still-valid context to references and discard stale, duplicated, unsafe, superseded, or low-signal text.

## Failure Mode

- No single lane fits: set blocked_by to the ambiguity and ask the smallest routing question.
- The request asks this router to mutate source, install, sync, publish, or run downstream proof before lane selection: block and name the downstream owner.
- The request would resurrect retired flat command handles, generated aliases, or projection-only manifest rows: block and route to canonical source repair.
- The request treats plugin-cache visibility, command-surface rows, flat skill symlinks, and runtime picker visibility as the same proof surface: block and separate the lanes.
- Claim environment, auth, runtime, Tessl, plugin cache, command surface, or Codex picker state only from current-turn evidence.

## Gotchas

- Execution boundaries matter: this router selects the lane only. Downstream skills own edits, sync, evals, install proof, and publication proof.
- Do not treat a route decision, plugin-cache row, or picker projection as proof that the selected skill passed validation.

## Execution Boundaries

- This router produces a lane handoff only; it does not edit source, install skills, sync projections, publish packages, or run downstream eval proof.
- Downstream lanes own source edits, runtime sync, external review, Tessl evals, package outputs, and publication receipts.

### Anti-Patterns To Avoid

- Do not mutate skill source while routing; return the lane handoff first.
- Do not fork .system/skill-creator or .system/skill-installer when the correct answer is to load the preserved system lane.
- Do not collapse install, projection, Tessl, Plugin Eval, and Registry evidence into one status.
- Do not route ordinary app debugging, CI repair, or repo refactors into Skill Factory only because the word "skill" appears nearby.

### Variation

Adapt the handoff to the request shape. Creation asks need a first-principles check, hardening asks need the failing proof lane, refactor asks need duplicate or retirement evidence, and install asks need runtime visibility boundaries.

## Validation

- Keep routing read-only unless the user explicitly asks this router to execute a selected lane.
- Downstream lanes own source edits, runtime sync, external review, Tessl evals, packaging, publishing, and install proof.
- A route decision is not proof that a skill is installed, visible in Codex, passing evals, or safe to publish.
- Runtime picker visibility depends on regenerated projections and local sync, not only canonical source edits.
- Redact secrets, tokens, PII, and sensitive local paths.
- Stop at the first failed required gate, classify it, and do not sync, commit, publish, or install until it is fixed or explicitly blocked.
- bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
- ./bin/ask skills external-review Plugins/skill-factory/skills/skill-factory-router --audit-level compat --json

## References

Load only the reference needed for the selected routing question:

Read when: choose exactly one reference below after the routing question is known.

- Read when validating the router contract or output shape: [references/contract.yaml](references/contract.yaml)
- Read when checking routing eval coverage or Tessl cases: [references/evals.yaml](references/evals.yaml)
- Read when tuning evaluator thresholds: [references/task-profile.json](references/task-profile.json)
- Read when the target, lane, write authority, or validation need is ambiguous: [references/discovery-interview.md](references/discovery-interview.md)
- Read when lane policy or first-principles routing is disputed: [references/routing-policy.md](references/routing-policy.md)
