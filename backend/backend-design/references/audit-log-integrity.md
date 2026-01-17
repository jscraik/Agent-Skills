# Audit Log Integrity and Tamper Evidence

## Immutability
- Use append-only storage for audit events.
- Prevent updates/deletes except by privileged compliance workflow.

## Tamper Evidence
- Hash chain each event to the previous event hash.
- Store periodic signed checkpoints.
- Optionally use WORM storage for long-term retention.

## Access Controls
- Read access limited to compliance roles.
- Separate storage from primary OLTP DB when possible.
