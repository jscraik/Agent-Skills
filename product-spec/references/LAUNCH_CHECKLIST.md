# Launch Readiness Checklist (solo-dev friendly)

> Rule: RNIA — if N/A, say why in 1–2 lines and who accepted the risk.

## Readiness basics
- [ ] PRD and Tech Spec approved
- [ ] ORR checklist completed; residual risks accepted
- [ ] Owners for launch + rollback identified

## Rollout plan
- [ ] Rollout strategy: flag | canary | phased | big-bang (justify)
- [ ] Success criteria during rollout (live metrics + time window)
- [ ] Abort criteria + who can pull the kill-switch
- [ ] Communications plan (status channel, cadence)

## Monitoring & alerts
- [ ] Dashboards for KPIs and guardrails linked
- [ ] Alerts enabled for availability/latency/error rate (or N/A with reason)
- [ ] Pager/on-call path verified

## Backward/forward compatibility
- [ ] API compatibility checked (clients/consumers)
- [ ] Data migration safe to rollback or dual-read/write plan exists

## Testing & verification
- [ ] Smoke tests defined for post-deploy
- [ ] Rollback procedure tested/dry-run
- [ ] Feature flag default/initial state documented

## Security & access
- [ ] Secrets/config for launch validated
- [ ] Access controls for new surfaces (roles, scopes) set
- [ ] Audit/log redaction verified for sensitive fields

## Dependencies
- [ ] External dependencies available and within rate/SLA
- [ ] Feature toggles/entitlements coordinated with upstream/downstream systems

## Post-launch
- [ ] Monitoring window + staffing (who watches, when)
- [ ] Post-launch review scheduled (time box)
- [ ] Data collection plan for KPIs and guardrails

## Residual risks & approvals
- [ ] Residual risks listed with owners
- [ ] Approver names recorded (even if just you)
