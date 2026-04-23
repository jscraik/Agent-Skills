# Superpowers Skill Gap Audit (2026-02-22)

## Table of Contents
- [Scope](#scope)
- [Inventory summary](#inventory-summary)
- [Direct overlaps](#direct-overlaps)
- [Missing-by-name skills and recommended action](#missing-by-name-skills-and-recommended-action)
- [High-impact improvements for existing skills](#high-impact-improvements-for-existing-skills)
- [Recommended rollout order](#recommended-rollout-order)

## Scope
Compared:
- `/Users/jamiecraik/dev/Infrastructure/config/codex/Plugins/marketplaces/superpowers-dev/skills`
- `/Users/jamiecraik/dev/agent-skills`

Method:
- Name-level diff (`SKILL.md` folder names)
- Manual semantic mapping to existing local skills

## Inventory summary
- Superpowers skills: **14**
- Local skills in `/Users/jamiecraik/dev/agent-skills`: **121**
- Direct name overlap: **2**
- Missing by name: **12**

## Direct overlaps
1. `brainstorming`
2. `systematic-debugging`

## Missing-by-name skills and recommended action
| Superpowers skill | Local equivalent today | Recommendation |
|---|---|---|
| `writing-skills` | `skill-builder` | **Do not import directly**. Keep `skill-builder` as canonical for Codex; optionally backport selected TDD-for-skills examples. |
| `using-superpowers` | AGENTS + system behavior | **Do not import**. It is Codex-specific and conflicts with current Codex skill-invocation model. |
| `writing-plans` | `product-spec`, `tech-spec`, `backend-engineer` | Add lightweight generic `writing-plans` skill or expand `product-spec` with an execution-handoff mode. |
| `executing-plans` | partial via existing planning skills | Add dedicated execution-mode skill for plan runbooks with checkpoints and blocker handling. |
| `test-driven-development` | none (explicit) | Add a first-class TDD skill (high value). |
| `verification-before-completion` | partial patterns spread across skills | Add a global verification gate skill (high value). |
| `requesting-code-review` | partial in `gh-workflow` | Add focused pre-merge review-request pattern (or add mode to `gh-workflow`). |
| `receiving-code-review` | partial in `gh-workflow` | Add focused feedback-intake/triage pattern (or add mode to `gh-workflow`). |
| `finishing-a-development-branch` | partial in `gh-workflow` / release flows | Add end-of-branch closure skill (merge/PR/keep/discard options + cleanup). |
| `using-git-worktrees` | none (explicit) | Add worktree setup/cleanup skill (high value for safe branch isolation). |
| `subagent-driven-development` | none (explicit) | Add only if you want parallel/subagent orchestration by default. Must be adapted to your single-threaded repo policy. |
| `dispatching-parallel-agents` | `automate-github-issues` (domain-specific) | Add generalized variant only if you want broader multi-agent orchestration. Must include strict independence checks. |

## High-impact improvements for existing skills
1. `/Users/jamiecraik/dev/agent-skills/Skills/systematic-debugging/SKILL.md` currently references missing skills:
   - `superpowers:test-driven-development`
   - `superpowers:verification-before-completion`

   **Action:** either create those skills locally or update references to local canonical alternatives.

2. `/Users/jamiecraik/dev/agent-skills/github/gh-workflow/SKILL.md` can absorb two explicit modes:
   - `requesting-code-review`
   - `receiving-code-review`

3. Add a single reusable “verification gate” checklist and link it from major implementation skills.

## Recommended rollout order
1. `test-driven-development`
2. `verification-before-completion`
3. `using-git-worktrees`
4. `writing-plans`
5. `executing-plans`
6. Review lifecycle (`requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch`)
7. Optional orchestration (`subagent-driven-development`, `dispatching-parallel-agents`) after policy alignment
