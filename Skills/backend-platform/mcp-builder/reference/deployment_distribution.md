# Deployment & Distribution

Use this for packaging and deployment choices (local, remote dev, and production).

## A) Local Server Distribution (npm)

Use when the MCP server runs on the user's machine (stdio or local HTTP).

### Recommended

- Publish as an npm package with a CLI entrypoint
- Support `npx` usage for zero-install onboarding
- Prefer stdio transport for local servers

### Checklist

- `bin` entry in `package.json`
- `--stdio` (default) or `--http` flag
- Clear env var config (API keys, Auth0 domain)
- Versioned releases and changelog

## B) Remote Dev (Cloudflare Tunnel)

Use during development when ChatGPT must reach localhost.

### Recommended

- Cloudflare Tunnel or ngrok
- Use HTTPS URL for connector setup
- Keep tunnel URL in `.env` for convenience

### Checklist

- Local server runs on a stable port
- Tunnel URL is exported to your MCP config
- CSP allows the tunnel domain if used in widget

## C) Remote Prod (Cloudflare Workers)

Use for production when you need a stable HTTPS endpoint.

### Recommended

- Streamable HTTP endpoint at `/mcp`
- Stateless handlers with durable storage if needed
- Validate auth on every request

### Checklist

- Requests routed to `/mcp`
- `MCP-Protocol-Version` handled
- Auth0 validation with cached JWKS
- Rate limiting and log correlation IDs

## D) Remote Prod (Container/VM)

Use when Workers are not suitable.

- Deploy on Fly/Vercel/AWS/etc.
- Streamable HTTP preferred
- Use managed TLS

## Notes

- SSE should be treated as backwards-compat only
- For local CLI servers, avoid logging to stdout when using stdio

## E) Cloudflare Workers Minimal Template

### wrangler.toml

```toml
name = "mcp-server"
main = "src/index.ts"
compatibility_date = "2025-12-31"

[vars]
AUTH0_DOMAIN = "your-tenant.us.auth0.com"
AUTH0_AUDIENCE = "https://api.your-service"
```

### src/index.ts (skeleton)

```ts
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    // Route only /mcp
    const url = new URL(request.url);
    if (url.pathname !== "/mcp") {
      return new Response("Not Found", { status: 404 });
    }

    // Validate MCP protocol header
    const proto = request.headers.get("MCP-Protocol-Version");
    if (!proto) {
      return new Response("Missing MCP-Protocol-Version", { status: 400 });
    }

    // TODO: Auth0 JWT validation (issuer, audience, exp, nbf, signature)
    // TODO: MCP JSON-RPC handling (tools/list, tools/call, resources/list)

    return new Response(JSON.stringify({ jsonrpc: "2.0", id: null, result: {} }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  },
};
```

### Deploy

```bash
npm install -g wrangler
wrangler login
wrangler deploy
```

## F) Cloudflare Workers Full Minimal MCP (JSON-RPC)

This is a self-contained MCP server for Workers with `tools/list`, `tools/call`, and `resources/list`.

### src/index.ts (working minimal)

```ts
export interface Env {
  AUTH0_DOMAIN: string;
  AUTH0_AUDIENCE: string;
}

type JsonRpcRequest = {
  jsonrpc: "2.0";
  id: string | number | null;
  method: string;
  params?: any;
};

type JsonRpcResponse = {
  jsonrpc: "2.0";
  id: string | number | null;
  result?: any;
  error?: { code: number; message: string; data?: any };
};

const TOOLS = [
  {
    name: "hello_world",
    title: "Hello World",
    description: "Use this when you want a simple connectivity test.",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string" },
      },
      required: ["name"],
      additionalProperties: false,
    },
    outputSchema: {
      type: "object",
      properties: {
        greeting: { type: "string" },
      },
      required: ["greeting"],
      additionalProperties: false,
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
    _meta: {
      // Example: set this if you have a widget template
      // "openai/outputTemplate": "ui://widget/hello.html"
    },
  },
] as const;

const RESOURCES = [
  // Example resource
  // {
  //   uri: "ui://widget/hello.html",
  //   name: "hello-widget",
  //   mimeType: "text/html+skybridge",
  // },
];

function jsonrpcResult(id: JsonRpcResponse["id"], result: any): JsonRpcResponse {
  return { jsonrpc: "2.0", id, result };
}

function jsonrpcError(id: JsonRpcResponse["id"], code: number, message: string, data?: any): JsonRpcResponse {
  return { jsonrpc: "2.0", id, error: { code, message, data } };
}

async function handleToolsList(req: JsonRpcRequest): Promise<JsonRpcResponse> {
  return jsonrpcResult(req.id, { tools: TOOLS });
}

async function handleResourcesList(req: JsonRpcRequest): Promise<JsonRpcResponse> {
  return jsonrpcResult(req.id, { resources: RESOURCES });
}

async function handleToolsCall(req: JsonRpcRequest): Promise<JsonRpcResponse> {
  const { params } = req;
  const toolName = params?.name;
  const tool = TOOLS.find((t) => t.name === toolName);
  if (!tool) {
    return jsonrpcError(req.id, -32602, `Unknown tool: ${toolName}`);
  }

  // Minimal example for hello_world
  if (tool.name === "hello_world") {
    const name = params?.arguments?.name;
    if (typeof name !== "string") {
      return jsonrpcError(req.id, -32602, "Invalid args: name must be string");
    }

    const structuredContent = { greeting: `Hello ${name}!` };
    return jsonrpcResult(req.id, {
      content: [{ type: "text", text: JSON.stringify(structuredContent) }],
      structuredContent,
      _meta: {},
    });
  }

  return jsonrpcError(req.id, -32601, "Tool not implemented");
}

async function handleJsonRpc(req: JsonRpcRequest): Promise<JsonRpcResponse> {
  switch (req.method) {
    case "tools/list":
      return handleToolsList(req);
    case "tools/call":
      return handleToolsCall(req);
    case "resources/list":
      return handleResourcesList(req);
    default:
      return jsonrpcError(req.id, -32601, "Method not found");
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname !== "/mcp") {
      return new Response("Not Found", { status: 404 });
    }
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    const proto = request.headers.get("MCP-Protocol-Version");
    if (!proto) {
      return new Response("Missing MCP-Protocol-Version", { status: 400 });
    }

    let body: JsonRpcRequest;
    try {
      body = (await request.json()) as JsonRpcRequest;
    } catch {
      const err = jsonrpcError(null, -32700, "Parse error");
      return new Response(JSON.stringify(err), { status: 400, headers: { "Content-Type": "application/json" } });
    }

    if (!body || body.jsonrpc !== "2.0" || !body.method) {
      const err = jsonrpcError(body?.id ?? null, -32600, "Invalid Request");
      return new Response(JSON.stringify(err), { status: 400, headers: { "Content-Type": "application/json" } });
    }

    const res = await handleJsonRpc(body);
    return new Response(JSON.stringify(res), { status: 200, headers: { "Content-Type": "application/json" } });
  },
};
```
