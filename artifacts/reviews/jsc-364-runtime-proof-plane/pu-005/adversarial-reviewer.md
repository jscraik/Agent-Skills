# PU-005 Adversarial Review

## Scope
- Reviewer: adversarial-reviewer subagent.
- Diff reviewed before remediation: PU-005 Codex preview source identity and truncation hardening.
- Artifact note: the subagent returned the finding in mailbox completion but did not write this file; the coordinator transcribed the finding and accepted remediation to preserve the required artifact trail.

## Severity-Ranked Findings

### High: False-success path: skills codex-preview reported pass without checking source identity

**Status:** accepted and fixed.

**Evidence:**
- Infrastructure/bin/ask:541 routed skills codex-preview directly to skills_commands.skills_codex_preview.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py:2577 previously ignored repo_root and emitted a static status pass command list.
- Infrastructure/scripts/lib/ask/services/codex_preview.py:306 and Infrastructure/scripts/lib/ask/services/codex_preview.py:321 show the actual preview builders compute source identity and downgrade status to partial when blockers exist.

**Risk:** An agent could treat the command-family index as green preview proof even when Codex source identity or live-runtime fidelity checks were blocked.

**Remediation applied:** skills_codex_preview now derives status, source_identity, source_basis, and blocked_checks from build_codex_load_preview, and emits not_a_validation_result: true so the command remains a discovery index rather than proof.

## Residual Risks
- Downstream validators still need to consume truncation.status instead of legacy warning text; this remains a later integration-boundary risk.

## Post-Fix Evidence
- python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q -> pass (23 passed).
- ./bin/ask skills codex-preview --json --robot -> pass and now emits status partial, not_a_validation_result true, source_identity, source_basis, and blocked_checks.
- The new failing-path test covers blocked source identity behavior for the command-family index.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/adversarial-reviewer.md
