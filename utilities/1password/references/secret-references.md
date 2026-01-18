# Secret References (overview)

Source: https://developer.1password.com/docs/cli/secret-references/

Key points
- Secret references are URIs that point to a vault, item, section, and field (names or IDs) and can replace plaintext secrets in env files, config files, or scripts.
- Resolve secret references at runtime with `op read`, `op run`, or `op inject`.
- Recommended: use service accounts to enforce least-privilege access to only required vaults.
- You can obtain secret references from the desktop app, the VS Code extension, via `op item get`, or by writing them using the documented syntax.

Examples
```bash
# Read a password to stdout
op read op://app-prod/db/password

# Write a private key to a file
op read --out-file ./key.pem "op://app-prod/server/ssh key?ssh-format=openssh"

# Inject into a template
op inject -i config.yml.tpl -o config.yml

# Run with env vars resolved
export DB_PASSWORD="op://app-prod/db/password"
op run -- printenv DB_PASSWORD
```
