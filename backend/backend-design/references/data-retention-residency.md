# Data Retention and Residency Checklist

## Retention
- Define per-data-class retention periods (user data, logs, model inputs/outputs).
- Define deletion SLA (e.g., 30 days) and audit evidence of deletion.
- For model inputs/outputs, document storage policy and opt-out controls.

## Residency
- Specify storage region(s) and transfer mechanisms.
- If multi-region, define replication and failover boundaries.
- Document cross-border transfer rules and user notice requirements.

## LLM/Frontier Model Considerations
- Document provider retention policy and user-configurable retention.
- Redact or minimize sensitive data prior to model calls.
- Store prompts/outputs only when required for audit or replay.
