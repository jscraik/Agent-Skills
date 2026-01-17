# MCP UI vs Apps SDK

Use this to decide between MCP UI and Apps SDK widgets.

## Apps SDK Widgets (ChatGPT)

- Intended for ChatGPT Apps
- Uses `text/html+skybridge` templates and `window.openai` runtime
- Requires HTTPS `/mcp` endpoint and CSP for submission
- Widget data split: `structuredContent` (model) vs `_meta` (widget-only)

## MCP UI (Standalone)

- Optional UI library for MCP servers outside Apps SDK
- Useful when you control the client UI or are not targeting ChatGPT Apps
- Does not require `text/html+skybridge` or `window.openai`
- Can still consume MCP tool outputs and resources

## Decision Quick Guide

- Building for ChatGPT Apps SDK: use Apps SDK widgets
- Building a custom MCP client UI: MCP UI can help
- Mixed use: keep Apps SDK metadata isolated from MCP UI concerns

## MCP UI Integration Patterns (Standalone)

- Treat MCP tool outputs as the single source of truth
- Normalize tool results into a UI state store
- Use resource links for files/documents rather than embedding blobs
- Keep tool outputs stable to prevent UI churn
- Add explicit loading and error states for tool calls

## React + Vite + Tailwind (Minimal Pattern)

Use this when building a standalone MCP UI client with React and Tailwind.

### App layout (example)

```tsx
import { useEffect, useState } from \"react\";

type ToolResult<T> = { data?: T; error?: string; loading: boolean };

export function App() {
  const [result, setResult] = useState<ToolResult<{ greeting: string }>>({
    loading: true,
  });

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch(\"/mcp\", {
          method: \"POST\",
          headers: {
            \"Content-Type\": \"application/json\",
            \"MCP-Protocol-Version\": \"2025-11-25\",
          },
          body: JSON.stringify({
            jsonrpc: \"2.0\",
            id: 1,
            method: \"tools/call\",
            params: { name: \"hello_world\", arguments: { name: \"Jamie\" } },
          }),
        });
        const json = await res.json();
        const data = json?.result?.structuredContent as { greeting: string };
        setResult({ data, loading: false });
      } catch (e: any) {
        setResult({ error: e?.message ?? \"Unknown error\", loading: false });
      }
    };
    run();
  }, []);

  return (
    <div className=\"min-h-screen bg-slate-950 text-slate-100 p-6\">
      <div className=\"max-w-xl mx-auto space-y-4\">
        <h1 className=\"text-2xl font-semibold\">MCP UI Demo</h1>
        {result.loading && <p className=\"text-slate-400\">Loading…</p>}
        {result.error && (
          <p className=\"text-red-400\">Error: {result.error}</p>
        )}
        {result.data && (
          <div className=\"rounded-lg bg-slate-900 p-4 border border-slate-800\">
            {result.data.greeting}
          </div>
        )}
      </div>
    </div>
  );
}
```

### Tailwind config (minimal)

```js
// tailwind.config.js
export default {
  content: [\"./index.html\", \"./src/**/*.{ts,tsx}\"],
  theme: { extend: {} },
  plugins: [],
};
```
