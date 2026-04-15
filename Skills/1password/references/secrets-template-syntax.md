# Secrets template syntax

Source: https://developer.1password.com/docs/cli/secrets-template-syntax/

Key points
- Use double-curly template syntax to embed secret references: `{{ op://vault/item/field }}`.
- Use `op inject` to replace template references with resolved secrets.
- In JSON templates, wrap secret references in single quotes to keep the JSON valid until injection.

Examples
```txt
DB_PASSWORD={{ op://app-prod/db/password }}

{"password": "'{{ op://app-prod/db/password }}'"}
```

Notes
- Template syntax supports whitespace inside the braces; keep the `op://` reference intact.
- Store templates (for example `.tpl`) in version control; store the resolved output outside version control.
