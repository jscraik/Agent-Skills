# Feature Flagging and Gradual Rollout

## Principles
- Default off for high-risk tools.
- Targeted rollout by tenant, role, or percentage.
- Capture metrics and error rates before widening rollout.

## Safeguards
- Kill switch for immediate rollback.
- Audit logging for flag changes.
