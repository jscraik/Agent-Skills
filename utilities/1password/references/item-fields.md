# Item fields

Source: https://developer.1password.com/docs/cli/item-fields/

Built-in field types
- `otp` (one-time password), `conception` (date), `expiration` (date), `monthYear` (month+year).
- `email`, `url`, `phone`.
- `file` (document/file reference).
- `sshKey` (SSH keys).

Custom field types
- `string` (text), `concealed` (password), `email`, `url`, `phone`, `date`, and `monthYear`.

Examples
```bash
# Inspect the fields for a login item type
op item template login | jq '.fields[] | {label, type}'
```

Notes
- Built-in fields vary by item type (login, password, document, server, etc.).
- Use `op item template` (or `op item create --template`) to see the field layout for a given item type before writing JSON.
