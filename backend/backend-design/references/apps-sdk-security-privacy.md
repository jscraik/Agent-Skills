# Apps SDK: Security and Privacy (Condensed)

## Principles
- Least privilege, explicit consent, defense in depth.
- Validate inputs server-side; keep audit logs.

## Data handling
- Avoid secrets in responses.
- Redact PII in logs.
- Define retention and deletion policies.

## Prompt injection
- Treat model inputs as untrusted.
- Require confirmations for destructive actions.
