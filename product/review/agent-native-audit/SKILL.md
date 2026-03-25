---
name: agent-native-audit
description: Audit a repository, workflow, or feature against agent-native operating principles and return evidence-backed gaps plus remediation priorities. Use when a user asks whether agents can realistically discover, execute, verify, and maintain a workflow end to end.
metadata:
  skill-type: product_verification
---

# Agent-Native Audit

Merged with preserved upstream audit guidance from `EveryInc/compound-engineering-plugin` at pinned ref `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`; see [`artifacts/agent-native-audit-merge-import-2026-03-23.txt`](../../../artifacts/agent-native-audit-merge-import-2026-03-23.txt) for provenance and hashes.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Deep-Dive Playbook](#deep-dive-playbook)
- [Validation](#validation)
- [Gotchas](#gotchas)
- [Anti-patterns](#anti-patterns)
- [See also](#see-also)

## When to use

Use this skill when:
- a repo or feature needs an agent-native audit;
- a workflow appears to rely on hidden human knowledge, UI-only actions, or undocumented setup;
- you need a structured review of whether an agent can discover, execute, and verify a task safely.
- you want a scored principle-by-principle agent-native review and remediation priorities.

Do not use this skill when:
- the user only wants a normal code review;
- the task is a narrow bug fix with an already-known root cause;
- the work is purely visual polish with no workflow or automation implications.

## Required inputs

- audit target:
  - repository path,
  - feature path, or
  - workflow surface;
- the intended agent task or user journey;
- any constraints around auth, approvals, deployment, or validation.

## Deliverables

- a short principle-based audit with evidence;
- prioritized findings grouped by severity or operational risk;
- concrete remediation steps that move the workflow toward agent-native parity;
- residual risks or unknowns that still require human decisions.
- when requested, a scored scorecard or principle-specific audit using the preserved deep-dive playbook.

## Failure mode

- If the target surface is too vague to audit, stop and narrow the scope first.
- If the workflow depends on inaccessible external systems, audit the visible boundary and mark the missing layer as an evidence gap.
- If the request is actually asking for implementation, switch to the relevant build or review skill after the audit framing is complete.

## Philosophy

- Agent-native means an agent can find the path, execute the path, and verify the result without hidden tribal knowledge.
- Missing documentation, hidden credentials, and manual-only checkpoints are design defects, not incidental friction.
- The audit should create a sharper next step, not just a critique.

## Workflow

1. Define the user-visible workflow or operating surface being audited.
2. Inspect discovery surfaces:
   - `AGENTS.md`,
   - README/docs,
   - skill or automation entrypoints,
   - validation commands,
   - auth/bootstrap instructions.
3. Evaluate the workflow against core principles:
   - discoverable entrypoint;
   - executable steps;
   - deterministic verification;
   - safe escalation boundaries;
   - portable state and artifacts;
   - minimal human-only knowledge.
4. Capture evidence for each gap with file or command references.
5. Recommend the smallest fixes that remove the highest-friction agent blockers first.

## Deep-Dive Playbook

- Use `references/upstream-playbook.md` when the user wants a full scored architecture review instead of the default concise blocker audit.
- Read that playbook when you need:
  - an 8-principle scorecard;
  - a principle-specific audit such as action parity, tools as primitives, shared workspace, or capability discovery;
  - a heavier parallelized audit plan with separate workstreams per principle.
- Keep this `SKILL.md` as the routing wrapper and preserve the detailed scoring doctrine in the reference instead of inflating the wrapper.

## Validation

- Every finding should point to concrete evidence, not inference alone.
- Every recommendation should name the specific artifact or workflow surface to change.
- If evidence is partial, label the finding as a bounded risk rather than a confirmed defect.

## Gotchas

- A workflow can look agent-friendly in docs but still hide manual-only setup in scripts or external tooling.
- Audit findings should stay tied to the named task; avoid drifting into a general platform critique unless the user asked for that.
- If the user asks for a comprehensive scored audit and you only run the lightweight wrapper flow, switch to `references/upstream-playbook.md` before responding.

## Anti-patterns

- Treating vague “this feels manual” impressions as findings without evidence.
- Mixing architectural critique with unrelated style preferences.
- Recommending large rewrites when a missing instruction, script, or validation step would remove the blocker.
- Collapsing the scored upstream audit doctrine into a vague summary instead of routing to the preserved deep-dive reference.

## See Also

| Skill | When to use together |
|---|---|
| [[agents-md]] | Tighten repo instructions after finding discoverability gaps |
| [[codex-home-audit]] | Audit the Codex home surface instead of a single repo |
| [[check-pr]] | Review a specific pull request after identifying agent-native risks |
| [[gh-workflow]] | Land follow-up fixes through the GitHub workflow |

**Topic map:** [[agent-ops]]
