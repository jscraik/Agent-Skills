# Report Format Specification

The HTML report structure and content sections.

## File Location

```
file://$HOME/dev/configs/codex/usage-data/report.html
```

Also saved with timestamp: `~/.codex/usage-data/report-{YYYY-MM-DD}.html`

## Visual Design

- Single-file HTML with embedded CSS
- Responsive layout (mobile-friendly)
- CSS bar charts (no external dependencies)
- Color coding:
  - Green: Working well, wins
  - Red: Friction, issues
  - Blue: Patterns, suggestions
  - Gray: Neutral sections

## Report Sections

### 1. Header

```
Codex Insights Report
Generated: {date}
Period: Last {N} days
Sessions: {count} | Success Rate: {percent} | Avg Duration: {minutes}m
```

### 2. At a Glance (4-box grid)

| Box | Content |
|-----|---------|
| **What's working** | 3-4 bullets of effective patterns |
| **What's hindering** | 3-4 friction points |
| **Quick wins** | Immediate improvements to try |
| **On the horizon** | Future AI capabilities to prepare for |

### 3. Charts

- **Tool Usage**: Horizontal bar chart (top 10 tools)
- **Response Time**: Histogram buckets (fast/medium/slow)

### 4. What You Work On

Project area breakdown:
```
Backend/API development — 12 sessions
Frontend/UX — 8 sessions
DevOps/Infrastructure — 3 sessions
```

### 5. How You Use Codex

Narrative paragraph describing interaction style:
> "You tend to start with broad exploratory requests, then narrow down...
> You validate changes carefully before accepting them..."

### 6. Impressive Things

Bulleted list of wins:
- Completed complex refactor across 15 files
- Effective use of parallel tool calls
- Quick recovery from errors

### 7. Where Things Go Wrong

Friction categories with session examples:

| Category | Count | Example |
|----------|-------|---------|
| Misunderstood request | 3 | "Session #abc123: asked for refactoring, got new feature" |
| Wrong tool suggested | 2 | "Session #def456: grep would have been faster" |

### 8. Suggestions for AGENTS.md

Patterns to codify:
- "You often ask for tests — add testing requirement to AGENTS.md"
- "You prefer compact edits — add style preference"

### 9. Features to Try

| Feature | Why | How |
|---------|-----|-----|
| MCP servers | You do a lot of API work | `codex mcp add` |
| Skills | Repeated workflows | Create a skill |

### 10. On the Horizon

Upcoming AI capabilities to prepare for:
- **Agent teams**: Start structuring work for delegation
- **Long context**: You could use deeper codebase understanding

## Output Example

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
    .section { margin: 20px 0; padding: 15px; border-radius: 8px; }
    .working { background: #f0fdf4; border-left: 4px solid #22c55e; }
    .friction { background: #fef2f2; border-left: 4px solid #ef4444; }
    /* ... */
  </style>
</head>
<body>
  <h1>Codex Insights Report</h1>
  <!-- sections -->
</body>
</html>
```
