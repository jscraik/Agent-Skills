---
name: beautiful-mermaid
description: Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when
  the user asks to render or convert Mermaid diagrams into images.
metadata:
  short-description: Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid.
---

# Beautiful Mermaid Diagram Rendering

Render Mermaid diagrams as SVG and PNG images using the Beautiful Mermaid library.

## Philosophy
- Favor deterministic, high-quality renders over quick hacks.
- Keep the workflow minimal and reproducible.
- Never auto-install dependencies without explicit approval.

## Scope and triggers
- The user provides Mermaid code and wants SVG/PNG outputs.
- The user describes a diagram and wants it rendered as Mermaid images.
- The user needs high-resolution diagram assets for docs or slides.

## Required inputs
- Mermaid code (string) or a path to a `.mmd` file.
- Output base name (without extension).
- Theme selection (optional; default `default`).
- Whether PNG capture is required (default: yes).

## Deliverables
- `<output>.svg` (vector output).
- `<output>.png` (high-resolution screenshot) when PNG capture is requested.
- Notes on theme and any constraints applied.

## Constraints / Safety
- Redact or avoid sensitive data in diagram content by default.
- Do not auto-install dependencies unless explicitly approved (`--allow-install`).
- Prefer installed runtimes/tools; avoid `npx` downloads without approval.
- Use local file paths for agent-browser; do not open remote URLs.
- Only remove intermediary files with explicit confirmation.

## Validation
- Verify SVG exists and is non-empty.
- If PNG capture is requested, confirm the PNG exists and is readable.
- Fail fast on missing inputs or unsupported themes.

## Anti-patterns
- Rendering diagrams that include secrets or tokens.
- Running install commands without approval.
- Capturing screenshots of remote pages or sensitive content.
- Deleting files without confirmation.

## Examples
- "Render this Mermaid sequence diagram to SVG and PNG."
- "Create a flowchart diagram image from this description."
- "Use the tokyo-night theme and output to onboarding-diagram."

## Dependencies

This skill requires the `agent-browser` skill for PNG rendering. Load it before proceeding with PNG capture.

Runtime notes:
- Prefer runtimes/tools that are already installed (bun, tsx, deno).
- Avoid auto-installing dependencies unless explicitly approved.

## Supported Diagram Types

- **Flowchart** - Process flows, decision trees, CI/CD pipelines
- **Sequence** - API calls, OAuth flows, database transactions
- **State** - State machines, connection lifecycles
- **Class** - UML class diagrams, design patterns
- **Entity-Relationship** - Database schemas, data models

## Available Themes

Default, Dracula, Solarized, Zinc Dark, Tokyo Night, Tokyo Night Storm, Tokyo Night Light, Catppuccin Latte, Nord, Nord Light, GitHub Dark, GitHub Light, One Dark.

If no theme is specified, use `default`.

## Common Syntax Patterns

### Flowchart Edge Labels

Use pipe syntax for edge labels:

```mermaid
A -->|label| B
A ---|label| B
```

Avoid space-dash syntax which can cause incomplete renders:

```mermaid
A -- label --> B   # May cause issues
```

### Node Labels with Special Characters

Wrap labels containing special characters in quotes:

```mermaid
A["Label with (parens)"]
B["Label with / slash"]
```

## Workflow

### Step 1: Generate or Validate Mermaid Code

If the user provides a description rather than code, generate valid Mermaid syntax. Consult `references/mermaid-syntax.md` for full syntax details.

### Step 2: Render SVG

Run the rendering script to produce an SVG file:

```bash
bun run scripts/render.ts --code "graph TD; A-->B" --output diagram --theme default
```

Or from a file:

```bash
bun run scripts/render.ts --input diagram.mmd --output diagram --theme tokyo-night
```

Alternative runtimes:
```bash
npx tsx scripts/render.ts --code "..." --output diagram
deno run --allow-read --allow-write --allow-net scripts/render.ts --code "..." --output diagram
```

If dependencies are missing, install them explicitly or re-run with `--allow-install`:
```bash
bun run scripts/render.ts --code "..." --output diagram --allow-install
```

This produces `<output>.svg` in the current working directory.

### Step 3: Create HTML Wrapper

Run the HTML wrapper script to prepare for screenshot:

```bash
bun run scripts/create-html.ts --svg diagram.svg --output diagram.html
```

This creates a minimal HTML file that displays the SVG with proper padding and background.

### Step 4: Capture High-Resolution PNG with agent-browser

Use the agent-browser CLI to capture a high-quality screenshot. Refer to the `agent-browser` skill for full CLI documentation.

```bash
# Set 4K viewport for high-resolution capture
agent-browser set viewport 3840 2160

# Open the HTML wrapper
agent-browser open "file://$(pwd)/diagram.html"

# Wait for render to complete
agent-browser wait 1000

# Capture full-page screenshot
agent-browser screenshot --full diagram.png

# Close browser
agent-browser close
```

For even higher resolution on complex diagrams, increase the viewport further or use the `--padding` option when creating the HTML wrapper to give the diagram more space.

### Step 5: Clean Up Intermediary Files

After rendering, remove all intermediary files. Only the final `.svg` and `.png` should remain.

Files to clean up:
- The HTML wrapper file (e.g., `diagram.html`)
- Any temporary `.mmd` files created to hold diagram code
- Any other files created during the rendering process

```bash
rm diagram.html
```

If a temporary `.mmd` file was created, remove it as well.

## Output files (details)

By default, both outputs are produced:
- **SVG**: Vector format, infinitely scalable, small file size.
- **PNG**: High-resolution raster captured at 4K (3840×2160) viewport with minimum 1200px diagram width.

Files are saved to the current working directory unless the user explicitly specifies a different path.

## Theme Selection Guide

| Theme | Background | Best For |
|-------|------------|----------|
| default | Light grey | General use |
| dracula | Dark purple | Dark mode preference |
| tokyo-night | Dark blue | Modern dark aesthetic |
| tokyo-night-storm | Darker blue | Higher contrast |
| nord | Dark arctic | Muted, calm visuals |
| nord-light | Light arctic | Light mode with soft tones |
| github-dark | GitHub dark | Matches GitHub UI |
| github-light | GitHub light | Matches GitHub UI |
| catppuccin-latte | Warm light | Soft pastel aesthetic |
| solarized | Tan/cream | Solarized colour scheme |
| one-dark | Atom dark | Atom editor aesthetic |
| zinc-dark | Neutral dark | Minimal, no colour bias |

## Troubleshooting

### Theme not applied

Check the render script output for the `bg` and `fg` values, or inspect the SVG's opening tag for `--bg` and `--fg` CSS custom properties.

### Diagram appears cut off or incomplete

- Check edge label syntax — use `-->|label|` pipe notation, not `-- label -->`
- Verify all node IDs are unique
- Check for unclosed brackets in node labels

### Render produces empty or malformed SVG

- Validate Mermaid syntax at https://mermaid.live before rendering
- Check for special characters that need escaping (wrap in quotes)
- Ensure flowchart direction is specified (`graph TD`, `graph LR`, etc.)

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
