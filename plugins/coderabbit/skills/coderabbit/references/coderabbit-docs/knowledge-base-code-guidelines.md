---
source: https://docs.coderabbit.ai/knowledge-base/code-guidelines
---

# Code Guidelines

CodeRabbit scans your repository for well-known AI coding assistant configuration files and uses their content as review criteria. If your team already writes instructions for tools like Cursor, Claude, or Windsurf, CodeRabbit picks those up automatically and enforces the same standards during code review.

## Supported files

The following file patterns are detected by default:

| File pattern | Associated tool |
| --- | --- |
| `**/AGENTS.md` | AI agent instructions |
| `**/.cursorrules` | Cursor |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.github/instructions/*.instructions.md` | GitHub Copilot (scoped instructions) |
| `**/CLAUDE.md` | Claude Code |
| `**/GEMINI.md` | Gemini CLI |
| `**/.cursor/rules/*` | Cursor (rules directory) |
| `**/.windsurfrules` | Windsurf |
| `**/.clinerules/*` | Cline |
| `**/.rules/*` | Generic team rules |
| `**/AGENT.md` | AI agent instructions |

## How scoping works

A guideline file applies to the directory it lives in and all of its subdirectories. CodeRabbit does not apply guidelines from one part of your repository tree to unrelated paths.

**Examples:**

- `CLAUDE.md` at the repository root → applies to all files
- `src/frontend/CLAUDE.md` → applies only to files under `src/frontend/`
- `src/backend/.cursorrules` → applies only to files under `src/backend/`

This directory-scoped behaviour means you can maintain separate, purpose-fit guidelines for different areas of a monorepo without them interfering with each other.

## Adding custom file patterns

If your team stores coding standards in files that are not in the default list, you can extend the detected patterns by setting `knowledge_base.code_guidelines.filePatterns` in your `.coderabbit.yaml`.

Custom patterns are **added on top of** the defaults — they do not replace them.

```
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
knowledge_base:
  code_guidelines:
    filePatterns:
      - "**/CODING_STANDARDS.md"
      - "**/docs/style-guide.md"
      - "**/.teamrules"
```

Glob patterns follow the same syntax used elsewhere in CodeRabbit configuration. The `**` wildcard matches any number of path segments.

## Configuration reference

```
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
knowledge_base:
  code_guidelines:
    enabled: true
    filePatterns:
      - "**/CODING_STANDARDS.md"
```

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `enabled` | boolean | `true` | Apply coding guideline files as review criteria. Set to `false` to disable auto-detection entirely. |
| `filePatterns` | array of strings | `[]` | Additional glob patterns for guideline files. Supplements the built-in defaults; does not replace them. File names are case-sensitive. |
