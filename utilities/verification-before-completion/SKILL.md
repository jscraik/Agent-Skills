---
name: verification-before-completion
description: "Validate completion claims with fresh command evidence. Use when you are about to claim work is complete, fixed, or passing."
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
- `references/contract.yaml`
- `references/evals.yaml`

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
