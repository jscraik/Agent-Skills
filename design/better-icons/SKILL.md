---
name: better-icons
description: "Use this skill to search and extract SVG icons via the better-icons CLI or MCP. Use this when you need icons from Iconify collections for UI/UX work, product mocks, or codebases."
metadata:
  short-description: Search Iconify libraries and fetch SVGs via CLI/MCP.
---

# Better Icons

Search and retrieve icons from 200+ libraries via Iconify.

## Philosophy

- Prefer clarity over decoration; icons should reinforce meaning.
- Keep visual consistency by staying within one family per surface.
- Optimize for accessibility: icons should not be the only cue.

## When to Use

- You need SVG icons quickly from Iconify libraries.
- You want consistent icon families across UI or docs.
- You need batch fetch or sync into a project file.
- You want to use the MCP tools from an agent.

## Inputs

- Search query (string) and optional collection prefix.
- Icon ID (`prefix:name`).
- Optional size and color (use design tokens when available).
- Output target path (if writing a file).
- Framework target for `sync_icon` (e.g., React, Vue, Svelte).

## Outputs

- SVG output to stdout or a file.
- Search results (JSON list of icon IDs).
- Updated project icon file (when syncing).
- Collections list (when listing libraries).

## Constraints / Safety

- Redact sensitive file paths, project names, or proprietary terms from logs by default.
- Do not overwrite existing files without explicit confirmation.
- If icons are used for interactive controls, ensure a minimum 44x44 hit-area and align spacing/breakpoints to design tokens where applicable.

## Anti-Patterns

- Mixing icon styles (stroke vs solid) within the same UI surface.
- Using icons without text labels for critical actions.
- Hardcoding colors that ignore the design system.
- Fetching excessive icons without narrowing by prefix or use case.

## Procedure

1. Confirm the use case and icon style constraints.
2. Search by query (optionally with a prefix).
3. Select icon IDs that match the family and style.
4. Fetch SVGs with token-aligned size/color.
5. Sync into the project if needed.
6. Validate output and usage context.

## CLI

```bash
# Search icons
better-icons search <query> [--prefix <prefix>] [--limit <n>] [--json]

# Get icon SVG (outputs to stdout)
better-icons get <icon-id> [--color <color>] [--size <px>] [--json]

# Setup MCP server for AI agents
better-icons setup [-a cursor,claude-code] [-s global|project]
```

## Examples

```bash
better-icons search arrow --limit 10
better-icons search home --json | jq '.icons[0]'
better-icons get lucide:home > icon.svg
better-icons get mdi:home --color '#333' --json
```

## Icon ID Format

`prefix:name` - e.g., `lucide:home`, `mdi:arrow-right`, `heroicons:check`

## Popular Collections

`lucide`, `mdi`, `heroicons`, `tabler`, `ph`, `ri`, `solar`, `iconamoon`

---

## MCP Tools (for AI agents)

| Tool | Description |
|------|-------------|
| `search_icons` | Search across all libraries |
| `get_icon` | Get single icon SVG |
| `get_icons` | Batch retrieve multiple icons |
| `list_collections` | Browse available icon sets |
| `recommend_icons` | Smart recommendations for use cases |
| `find_similar_icons` | Find variations across collections |
| `sync_icon` | Add icon to project file |
| `scan_project_icons` | List icons in project |

## TypeScript Interfaces

```typescript
interface SearchIcons {
  query: string
  limit?: number        // 1-999, default 32
  prefix?: string       // e.g., 'mdi', 'lucide'
  category?: string     // e.g., 'General', 'Emoji'
}

interface GetIcon {
  icon_id: string       // 'prefix:name' format
  color?: string        // e.g., '#ff0000', 'currentColor'
  size?: number         // pixels
}

interface GetIcons {
  icon_ids: string[]    // max 20
  color?: string
  size?: number
}

interface RecommendIcons {
  use_case: string      // e.g., 'navigation menu'
  style?: 'solid' | 'outline' | 'any'
  limit?: number        // default 10
}

interface SyncIcon {
  icons_file: string    // absolute path
  framework: 'react' | 'vue' | 'svelte' | 'solid' | 'svg'
  icon_id: string
  component_name?: string
}
```

## API

All icons from `https://api.iconify.design`

## Validation

- `better-icons search home --limit 5` returns a list of icon IDs.
- `better-icons get lucide:home` outputs valid SVG markup.
- If syncing, verify the target file updates and renders correctly.
- See `references/contract.yaml` (schema_version: 1) and `references/evals.yaml` for the formal contract and eval cases.
- Fail fast: stop at the first failed check and fix before continuing.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
