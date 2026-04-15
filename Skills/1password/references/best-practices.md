# CLI best practices

Source: https://developer.1password.com/docs/cli/best-practices/

Key points
- Prefer secret references and `op run`/`op inject` over plaintext secrets.
- Use least-privilege vault access, ideally via service accounts.
- Avoid persisting session tokens in shared environments; prefer service account tokens.
- Rotate credentials regularly and keep templates in source control.

Examples
- Store `app.env.tpl` in repo and generate `app.env` at runtime with `op inject`.
- Use a service account token in CI instead of an interactive session.
