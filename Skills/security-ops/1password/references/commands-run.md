# op run

Source: https://developer.1password.com/docs/cli/reference/commands/run/

Key points
- Runs a subprocess with secret references in env vars resolved at runtime.
- Supports `--env-file` for `.env` files and `--no-masking` for debugging.
- Use when you need secrets injected without writing them to disk.

Examples
```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- ./bin/start.sh

op run --env-file ./.env -- node server.js
```
