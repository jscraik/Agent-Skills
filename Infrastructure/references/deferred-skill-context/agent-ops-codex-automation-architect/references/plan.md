# Codex Automation Architect Plan

## Table of Contents
- [Objectives](#objectives)
- [Scope](#scope)
- [Implementation steps](#implementation-steps)
- [Validation](#validation)
- [Known hard blockers](#known-hard-blockers)

## Objectives
- Build a gold-standard Codex automation skill (March 30, 2026 baseline).
- Support creation plus review/merge of existing automations.
- Enforce safe operation under strict approval/sandbox policies.

## Scope
- In scope:
  - automation design/consolidation
  - freshness checks via OpenAI docs MCP + `codexRepo` MCP + Context7 MCP
  - blocker remediation and permission mapping
  - RRULE design guardrails (timezone, `count` vs `until`, `wkst`)
  - headless multi-runner validation guidance
- Out of scope:
  - unrelated app feature coding
  - unsafe escalation tactics

## Implementation steps
1. Scaffold skill layout and resources.
2. Author SKILL workflow and constraints.
3. Configure MCP dependencies in `agents/openai.yaml`.
4. Add contract/evals/headless matrix references.
5. Run quality gates and report score.

## Validation
- `quick_validate.py`
- `skill_gate.py`
- `analyze_skill.py`
- optional: `run_skill_evals.py` multi-runner

## Known hard blockers
- `git commit` rejected when `AskForApproval=Never`.
  - Fallback: patch-only output + deferred commit in approved run.
