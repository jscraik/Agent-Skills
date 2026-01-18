# 1Password CLI environment variables

Source: https://developer.1password.com/docs/cli/environment-variables/

Key variables
- `OP_CONNECT_HOST` and `OP_CONNECT_TOKEN` configure access to a 1Password Connect server.
- `OP_SERVICE_ACCOUNT_TOKEN` authenticates a service account (for automation).
- `OP_SESSION_<account>` stores a signed-in session token for a specific account shorthand.
- `OP_DEVICE`, `OP_INTEGRATION_NAME`, and `OP_LOG_LEVEL` set device name, integration name, and log verbosity.
- `OP_FORMAT` controls output format (for example JSON).
- `OP_READ_TIMEOUT` sets read timeouts; `OP_TRACE` enables tracing.

Examples
```bash
# Connect server usage
export OP_CONNECT_HOST="https://connect.example.com"
export OP_CONNECT_TOKEN="<token>"
op vault list

# Service account usage
export OP_SERVICE_ACCOUNT_TOKEN="<token>"
op item list --vault "Prod"
```

Notes
- Prefer service account tokens for CI/automation; avoid persistent session tokens in shared environments.
