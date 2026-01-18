# Secret reference syntax

Source: https://developer.1password.com/docs/cli/secret-reference-syntax/

Syntax
- `op://<vault>/<item>/<section>/<field>` for a field value.
- `op://<vault>/<item>/<section>/<file>` to reference a document/file attachment (file name goes in the field position).

Rules
- Item, section, and field labels are case-insensitive; vault names are case-sensitive.
- Only plain alphanumerics and these symbols are supported in the path: `. _ - @`.
- For unsupported characters, use the vault/item/field IDs instead of names.
- If the reference includes whitespace or special characters, wrap the whole reference in quotes.
- You can embed environment variables in references (for example `${ENV_VAR}`) and `op run` will expand them.

Examples
```bash
# Field value
op read op://Finance/Stripe/login/password

# Field attribute
op read "op://Finance/Stripe/login/password?attribute=title"

# File attachment content
op read "op://Ops/Certificates/Prod TLS/cert.pem?attribute=content"
```

Query parameters
- Use `?attribute=<name>` (or `?attr=<name>`) to fetch a specific attribute.
- Common field attributes: type, value, title, id, purpose, otp.
- Common file attributes: content, size, id, name, type.
- For SSH private keys, use `?ssh-format=openssh` to control format.
