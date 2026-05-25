# Adversarial Final Review - PU-007

## Verdict
- Recommendation: block PU-007 packaging until P1 is addressed.
- Reason: repo closeout can report commit readiness even when runtime evidence is invalid or stale, creating a false-success closeout claim path.

## Findings

### P1 - False-success: invalid runtime cards do not block closeout readiness
- Evidence:
  - Trigger: --changed mode with one or more malformed runtime cards under .harness/evidence/runtime-proof/**/runtime-card.json.
  - Execution path:
    - Runtime cards are scanned and invalid cards are detected (status = invalid): Infrastructure/scripts/lib/ask/commands/repo_impl.py:1309-1313.
    - repo_closeout computes blockers from changed-file detection, doctor blocking, sync, and strict diagnostic debt only; runtime evidence status is not considered: Infrastructure/scripts/lib/ask/commands/repo_impl.py:1354-1367.
    - commit_readiness.ready is therefore still true when no other blocker exists: Infrastructure/scripts/lib/ask/commands/repo_impl.py:1407-1411.
  - Failure outcome:
    - Closeout can return success while simultaneously reporting runtime_evidence.status = invalid, which invites a merge/closeout action on broken runtime-proof artifacts.
- Remediation suggestion:
  - Add runtime-evidence gating into blockers in repo_closeout for changed=true when runtime evidence is missing or invalid, or explicitly downgrade commit_readiness.ready when schema proof is not run and runtime evidence changed.

### P2 - Composition failure: changed-file intent vs global evidence scan causes stale-state poisoning
- Evidence:
  - Trigger: user changes one valid runtime card, while an unrelated old invalid card exists elsewhere under .harness/evidence/runtime-proof/.
  - Execution path:
    - Focused validation is scoped by changed paths and only adds the runtime-evidence validator when runtime-evidence files changed: Infrastructure/scripts/lib/ask/commands/repo_impl.py:1211-1218.
    - Runtime evidence summary ignores changed-file scope and scans the entire evidence root (rglob runtime-card.json): Infrastructure/scripts/lib/ask/commands/repo_impl.py:1304-1307.
    - Any unrelated invalid card flips aggregate status to invalid: Infrastructure/scripts/lib/ask/commands/repo_impl.py:1309-1313.
  - Failure outcome:
    - The closeout signal for the active change is contaminated by stale/unrelated artifacts, making readiness signals non-local and hard to trust for per-patch decisions.
- Remediation suggestion:
  - Report both changed_scope_status and workspace_scope_status separately; keep workspace-wide scan for observability, but use changed-scope status for patch-level readiness decisions.

## Residual risk (if shipped as-is)
- Human output shows runtime boundaries as not_checked_by_repo_closeout (Infrastructure/bin/ask:1089-1096), but this is advisory only and easy to overlook during fast closeout flows.
- The validator command is listed as not_run (Infrastructure/scripts/lib/ask/commands/repo_impl.py:1319-1322), so users may mistake discovery metadata for validated proof.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-007/adversarial-final-reviewer.md
