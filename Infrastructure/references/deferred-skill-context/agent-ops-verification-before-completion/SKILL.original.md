---
name: verification-before-completion
description: "Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing."
metadata:
  skill-type: code_quality_review
---

# Verification Before Completion

## Table of Contents
- [Usage triggers](#usage-triggers)
- [Required context and assumptions](#required-context-and-assumptions)
- [Deliverables and results](#deliverables-and-results)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Constraints and safety](#constraints-and-safety)
- [Philosophy](#philosophy)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowering execution style](#empowering-execution-style)
- [Examples](#examples)
- [References](#references)

## Usage triggers
Use this skill when you are about to:
- Say a fix works.
- Say tests pass.
- Open a PR or merge based on test/build claims.

Do not use as a replacement for debugging root cause.

## Required context and assumptions
- Claim you intend to make.
- Exact command(s) that prove the claim.
- Relevant repo/test/build context.

## Deliverables and results
- Verified claim with command evidence.
- Blocked status if verification fails or is missing.
- Clear next action when blocked.

## Standards snapshot (March 2026)
- Fresh command evidence beats memory, intuition, or prior CI snapshots.
- Verify the exact claim being made, not a nearby weaker claim.
- Prefer the smallest command that proves the claim while still covering the real risk.
- If evidence is incomplete, downgrade the claim instead of stretching the interpretation.

## Failure mode
If no fresh command can prove the claim, the claim is blocked by definition and must be rewritten or deferred.

## Workflow
1. **State the claim** (for example: "tests pass").
2. **Map claim to command** that can prove it.
3. **Run command fresh** in current context.
4. **Read output fully** (exit code + failures + warnings).
5. **Decide**:
   - If evidence proves claim: report success with evidence.
   - If not: report actual status and next step.
6. **Only then** proceed to completion/PR/merge language.

## Validation
Fail fast: **stop at the first failed gate** and do not proceed.

Required gates:
1. Verification command identified.
2. Verification command executed now (not stale).
3. Output confirms the specific claim.
4. If any gate fails, claim must be blocked or revised.

## Anti-patterns
- "Should pass" / "probably fixed" language without fresh output.
- Relying on old CI runs or prior terminal output.
- Claiming success from partial checks.
- Skipping verification because change "looks small."
- **NEVER** claim completion from memory or stale output.
- **DO NOT** continue to PR/merge language when a gate failed.
- **DON'T** paraphrase missing evidence as if the command ran.

## Constraints and safety
- Redact secrets/tokens/PII from shared logs.
- Never fabricate or paraphrase missing verification evidence.
- Keep verification scoped to requested claim.
- Avoid mutating follow-up steps until the verification claim is settled.

## Philosophy
- Evidence before assertions.
- Trust output, not intuition.
- Accuracy is faster than rework.
- Why trust this method? It converts assumptions into verifiable facts.
- What tradeoff is acceptable: extra command time now or rollback time later?
- Which claim is highest-risk and should be verified first?

## Variation and adaptation
- Vary verification depth by risk: different checks for hotfixes, releases, and refactors.
- Adapt evidence format to audience context-specific needs (brief summary vs detailed command log).
- Customize gate ordering when one claim depends on another result.
- Avoid repetitive generic checklists when a targeted sequence is safer.
- Use different blocking language depending on confidence and impact.

## Empowering execution style
- You are capable of setting a high reliability bar with clear evidence.
- This workflow unlocks confident decision-making under pressure.
- Explore efficient verification strategies while keeping assertions honest.
- Enable fast collaboration by making status explicit and reproducible.

## Examples
- "Before I open this PR, verify lint and tests are green."
- "Confirm this hotfix really resolves the failing test."

## References
- `Infrastructure/references/contract.yaml`
- `Infrastructure/references/evals.yaml`

## See Also

| Skill | When to use together |
|---|---|
| [[he-fix-bugs]] | Run first to find root cause; use this skill to prove the fix worked |
| [[he-tdd]] | Write failing tests before fixing; this skill verifies they now pass |
| [[gh-workflow]] | Gate PR merges: verification must pass before PR language is used |
| [[evals-router]] | Verify LLM eval pipelines pass before claiming eval work is complete |

**Topic map:** [[agent-ops]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## When to use
- Use this skill when you are about to claim a fix works, tests pass, a task is complete, or a PR is ready based on local verification.
- Do not use it as a substitute for root-cause analysis; use it after implementation or debugging to validate the exact claim.

## Required inputs
- The exact completion claim you intend to make.
- The fresh command or check that can prove that claim in the current repo state.
- Enough repo context to interpret the result correctly, including scope and any relevant warnings.

## Deliverables
- A verified claim tied to fresh command evidence, or an explicit blocked status if the evidence does not support the claim.
- The exact validation command used, the observed result, and the next safest action when validation fails.
