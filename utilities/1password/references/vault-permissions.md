# Vault permissions

Source: https://developer.1password.com/docs/cli/vault-permissions/

Key points
- Vault permissions determine which actions a user or service account can perform (view, edit, create, manage).
- Permission sets depend on account type (Business vs. Teams/Families); use the doc table for the exact mapping.
- For automation, assign the minimum permission that allows required operations.

Examples
- Use `view` + `read` permissions for CI that only needs secret access.
- Use `create` only when automation must add new items.
