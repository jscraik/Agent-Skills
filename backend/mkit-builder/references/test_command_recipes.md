# Test Command Recipes (TS SDK + FastMCP)

Use these commands for quick verification. Adapt paths/ports to your project.

## TypeScript SDK

Build and run:

```bash
npm run build
node dist/index.js
```

Inspector:

```bash
npx @modelcontextprotocol/inspector
```

Manual tool call (JSON-RPC over HTTP):

```bash
curl -s -X POST http://localhost:3000/mcp \
  -H 'Content-Type: application/json' \
  -H 'MCP-Protocol-Version: 2025-11-25' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## FastMCP

Run server (example):

```bash
python -m your_server_module
```

Inspector:

```bash
npx @modelcontextprotocol/inspector
```

Manual tool call:

```bash
curl -s -X POST http://localhost:3000/mcp \
  -H 'Content-Type: application/json' \
  -H 'MCP-Protocol-Version: 2025-11-25' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Auth0 Token Debug (HTTP)

```bash
# Replace with your domain and client
curl -s https://YOUR_TENANT_DOMAIN/.well-known/openid-configuration
```

```bash
# Verify token audience locally (JWT decode)
python - <<'PY'
import jwt
import sys

token = sys.argv[1]
print(jwt.decode(token, options={"verify_signature": False}))
PY
```
