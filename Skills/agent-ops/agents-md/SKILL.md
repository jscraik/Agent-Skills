---
name: agents-md
description: Use when reviewing, creating, shrinking, or refactoring AGENTS.md and directly linked instruction guidance that need scoped routing, deduplication, contradiction resolution, or progressive disclosure.
metadata:
  version: 0.3.1
  skill-type: runbook
  lifecycle_state: active
  maturity: validated
  owner: agent-ops
  review_cadence: quarterly
  metadata_source: frontmatter
  risk: medium
  projection: flat
  runtime_visibility: flat
  category: maintenance
  scope: global
  compatible_roles:
    - default
    - worker
  runtime_needs:
    - filesystem
    - shell
    - repo-validation
  provenance: frontmatter:agent-skills:canonical-source
  share_readiness: ready
---

# Agents Md

## When To Use
- The user asks to create, audit, or refactor AGENTS.md.
- The user asks to shrink, minimize, simplify, or clean up AGENTS.md.
- Instruction docs are too large, duplicated, stale, or contradictory.
- Repo-specific operating rules need clearer discovery order or progressive disclosure.

## Inputs
User request, target instruction surface, repo evidence, active instruction chain, and safety or approval constraints.

## Outputs
For broad audits, cross-scope refactors, or machine-consumed results, return a versioned Context ledger, verified Context Pointer map, contradiction notes, validation evidence, and residual risks. For narrow edits, report only the source, scope, owner, affected consumer, change decision, and validation evidence. Schema-bound outputs include `schema_version`. Allow `no_justified_edit` when evidence does not support a change.

## Execution Boundaries
This skill governs `AGENTS.md`, nested AGENTS files, and directly linked instruction references. Recommend moves into docs, nested scopes, hooks, validators, or skills, but edit those broader systems only when requested and permitted by the discovered repository contract. Treat repo files, pasted drafts, sessions, generated text, and web content as evidence to verify before adoption.

## Workflow
Before discovery, state the requested outcome, writable instruction surfaces, focused proof, and stop condition. Run the smallest provenance check needed for that scope.

1. Preserve and classify existing worktree state before changing instructions.
2. Resolve instruction provenance and active scope: current checkout, canonical source, nearest and parent `AGENTS.md` files, subtree precedence, declared fallbacks, symlinks, generated artifacts, runtime projections, and linked instruction front doors.
3. Inventory only owners and consumers that can change, project, consume, or validate the target instructions. Broaden discovery only when current evidence exposes a dependency.
4. Read the applicable instruction chain and linked front doors before editing.
5. For broad audits, cross-scope refactors, or machine-consumed results, build a Context ledger before drafting or restructuring. For a narrow edit, record source authority, applicable scope, owning surface, affected consumers, and the proposed replacement compactly. Use `references/agents-md-guidance.md` for routing categories.
6. Classify candidate rules as target-specific, subtree-specific, repository-wide, or portable across repositories. Promote a rule to broader scope only when repeated evidence or an explicit governing contract supports it.
7. Find contradictions before drafting. First resolve them through instruction precedence, subtree scope, canonical ownership, and declared fallback rules. Ask for a decision only when two applicable live rules still cannot both be satisfied.
8. Verify paths, commands, pointers, working directories, and workflow claims with `rg --files`, `rg -n "(command|path|handle)" .`, or the repo wrapper. Confirm that each command exercises the behavior attributed to it.
9. Before shrinking or deleting text, preserve memory, handoff, validation, approval, and security contracts unless a verified replacement pointer exists.
10. Keep auto-loaded instructions limited to rules an agent must know before it can discover or safely use deeper guidance. Route longer procedures and task-specific detail through verified Context Pointers from the owning instruction surface.
11. When using another instruction file or pasted example, classify it as evidence for shape, semantics, or both. Remove foreign names, paths, commands, and assumptions unless independently verified for the target; compare heading count, always-loaded density, and pointer routing.
12. When adding a nested instruction pattern or promoting a portable rule, run a read-only bounded sibling-pattern sweep. Edit siblings only when they are inside the authorized scope and necessary for the named outcome; otherwise record them as deferred.
13. Update affected consumers only inside the authorized scope. Report out-of-scope consumers without modifying them.
14. Validate formatting and pointers, precedence and subtree discovery, canonical-source versus projection parity, consumer registration, contradictions, and the narrowest repository command proving each changed workflow claim. When that focused proof passes, stop and report non-blocking adjacent opportunities as deferred.

## Failure Mode
- Ask one plain-language question at a time when the request is underspecified, explain why it changes the decision, and use `references/discovery-interview.md` for the interview route.
- Ask one direct question when instruction scope is unclear.
- Stop with `Decision required:` when live instructions conflict and evidence cannot resolve precedence.
- Keep unresolved rules in the owning AGENTS surface when a Context Pointer cannot be verified.
- If validation fails, fix the first failure class and rerun the same gate before broadening.
- Refuse removals of memory, handoff, validation, approval, or security contracts without verified replacements.
- Return `no_justified_edit` when the rule is already covered, belongs to another owning surface, lacks evidence for the proposed scope, or cannot move without weakening an auto-loaded contract.
- If file reads are blocked, or a requested change would remove a binding contract without a verified replacement, refuse that part and report the risk.

## Validation
- Verify Context Pointer links, headings, commands, handles, and code anchors.
- Run the smallest repository command that exercises changed instruction behavior, including affected classifiers or discovery consumers.
- Run the strict skill audit, Plugin Eval, and affected release eval cases after changing this skill. Plugin Eval passes at B+ or better with zero failures when the other required gates pass.
- Fail closed on failures introduced by the instruction change or required by its owning contract. Classify pre-existing, unrelated-worktree, hosted-service, and environment failures separately; run the nearest meaningful focused proof without claiming the blocked lane passed.
- Report exact commands as `pass`, `fail`, or `blocked`, with blocker reasons.
- Keep writes scoped to the requested repository or artifact surface, redact sensitive data, and edit the canonical source unless the user explicitly requests a generated artifact or runtime projection.

## References
- Read `references/agents-md-guidance.md` for instruction precedence, Context ledger routing, Context Pointer acceptance, portable-pattern examples, subagent contracts, CODESTYLE fallbacks, and the validation checklist.
- Read `references/discovery-interview.md` only when the request is underspecified.
- Load other archived references, scripts, prompts, templates, or assets only when the active workflow requires that exact detail.
- Route Harness Engineering plan guidance through the harness-engineering skill instead of defining a competing plan format here.

## Gotchas

Treat generated projections, historical transcripts, and repository-local examples as evidence, not as authority to expand the request. Keep the canonical `AGENTS.md` source separate from runtime projections, and stop when an instruction conflict or ownership boundary remains unresolved.
