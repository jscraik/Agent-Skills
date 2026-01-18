# Secrets in scripts

Source: https://developer.1password.com/docs/cli/secrets-scripts/

Key points
- Prefer secret references + `op run`, `op read`, or `op inject` to avoid plaintext secrets in scripts.
- Four supported approaches: direct `op read`, `op run` with environment variables, `op inject` for templates/config, and shell plugins.

Examples
```bash
# Direct read in a script
DB_PASSWORD="$(op read op://app-prod/db/password)"

# Env vars + op run
export DB_PASSWORD="op://app-prod/db/password"
op run -- ./bin/start.sh

# Template injection
op inject -i app.env.tpl -o app.env

# Shell plugin
op plugin run -- wrangler whoami
```

Notes
- If a variable is referenced in the same command that calls `op run`, your shell expands first. Export it before `op run`, or use a subshell expansion pattern.
