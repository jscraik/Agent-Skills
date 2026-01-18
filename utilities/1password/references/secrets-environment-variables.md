# Secrets in environment variables

Source: https://developer.1password.com/docs/cli/secrets-environment-variables/

Key points
- Use secret references instead of plaintext values in environment variables.
- Use `op run` to resolve secret references and run a command with those values injected.
- Avoid committing resolved `.env` files; keep templates in source control and generate resolved files at runtime.

Examples
```bash
# Resolve env vars already exported
export DB_PASSWORD="op://app-prod/db/password"
op run -- printenv DB_PASSWORD

# Resolve a .env file
op run --env-file ./config/.env -- node server.js
```

Notes
- If the shell expands variables before `op run`, export them first or use a subshell pattern so `op run` can resolve the references.
