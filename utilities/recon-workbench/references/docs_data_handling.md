# Data handling and redaction

Summary from `docs/reference/DATA_HANDLING.md`.

## Principles
- Collect only what is necessary to answer the goal.
- Avoid capturing credentials, personal data, or customer content.
- Redact secrets before sharing outputs.

## Redaction workflow
- Identify sensitive fields (tokens, cookies, auth headers, user identifiers).
- Replace with stable placeholders (e.g., REDACTED_TOKEN_1).
- Record the redaction method in the report.

## Retention
- Keep raw artifacts only as long as needed.
- Prefer derived summaries for long-term storage.
- Encrypt/restrict access to raw artifacts if required.
