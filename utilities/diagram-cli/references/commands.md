# Command Reference

## analyze

Analyze file structure and dependencies without rendering a diagram.

```bash
diagram analyze [path] [options]
```

**Options:**
- `-p, --patterns <list>` - File patterns (default: `**/*.ts,**/*.tsx,**/*.js,**/*.jsx,**/*.py,**/*.go,**/*.rs`)
- `-e, --exclude <list>` - Exclude patterns
- `-m, --max-files <n>` - Max files to analyze (default: 100)
- `-j, --json` - JSON output

**Examples:**
```bash
diagram analyze ./my-project
diagram analyze . --json
diagram analyze . --patterns "**/*.py,**/*.go"
diagram analyze . --max-files 200
```

---

## generate

Generate one Mermaid diagram and print a preview URL.

```bash
diagram generate [path] [options]
```

**Options:**
- `-t, --type <type>` - Diagram type (default: architecture)
  - Types: architecture, sequence, dependency, class, flow, database, user, events, auth, security
- `-f, --focus <module>` - Focus on one module or directory
- `-o, --output <file>` - Write `.mmd`, `.svg`, or `.png`
- `-m, --max-files <n>` - Max files to analyze
- `--theme <theme>` - Theme: default, dark, forest, neutral
- `--open` - Open generated preview URL

**Examples:**
```bash
diagram generate .
diagram generate . --type sequence
diagram generate . --focus src/api
diagram generate . --theme dark
diagram generate . --output diagram.mmd
diagram generate . --output diagram.svg
```

---

## all

Generate all diagram types in one run.

```bash
diagram all [path] [options]
```

**Options:**
- `-o, --output-dir <dir>` - Output directory (default: ./diagrams)

**Examples:**
```bash
diagram all .
diagram all . --output-dir ./docs/diagrams
```

---

## test

Validate architecture constraints against declarative YAML rules.

```bash
diagram test [path] [options]
```

**Options:**
- `-c, --config <file>` - Config file path (default: .architecture.yml)
- `-f, --format <format>` - Output: console, json, junit (default: console)
- `-o, --output <file>` - Write output to file
- `-p, --patterns <list>` - Analyzed file patterns
- `-e, --exclude <list>` - Excluded paths
- `-m, --max-files <n>` - Max files to analyze (default: 100)
- `--dry-run` - Preview file matching only
- `--verbose` - Verbose output
- `--init` - Generate starter config
- `--force` - Overwrite existing config when used with --init

**Examples:**
```bash
# Generate starter configuration
diagram test --init

# Validate rules
diagram test

# Preview matching files only
diagram test --dry-run --verbose

# CI-friendly output (JUnit)
diagram test --format junit --output architecture-results.xml
```

---

## manifest

Summarize the generated `.diagram/manifest.json` artifact.

```bash
diagram manifest [path] [options]
```

**Options:**
- `-d, --manifest-dir <dir>` - Directory containing manifest.json (default: .diagram)
- `-o, --output <file>` - Write summary JSON to file
- `--require-types <list>` - Require specific diagram types, comma-separated
- `--fail-on-placeholder` - Fail if any diagram entry is a placeholder

**Examples:**
```bash
diagram manifest .
diagram manifest . --manifest-dir .diagram --output .diagram/manifest-summary.json
diagram manifest . --require-types architecture,security --fail-on-placeholder
```

---

## video

Generate an animated video from a Mermaid diagram.

```bash
diagram video [path] [options]
```

**Options:**
- `-t, --type <type>` - Diagram type (default: architecture)
- `-o, --output <file>` - Output file (default: diagram.mp4)
- `-d, --duration <sec>` - Video duration in seconds (default: 5)
- `-f, --fps <n>` - Frames per second (default: 30)
- `--width <n>` - Output width in pixels (default: 1280)
- `--height <n>` - Output height in pixels (default: 720)
- `--theme <theme>` - Theme (default: dark)
- `-m, --max-files <n>` - Max files to analyze (default: 100)

**Prerequisites:**
```bash
npm install
npx playwright install chromium
brew install ffmpeg
```

**Examples:**
```bash
diagram video .
diagram video . --type dependency --output architecture.mp4
diagram video . --duration 8 --fps 60 --width 1920 --height 1080
```

---

## animate

Generate an animated SVG with CSS animations.

```bash
diagram animate [path] [options]
```

**Options:**
- `-t, --type <type>` - Diagram type (default: architecture)
- `-o, --output <file>` - Output file (default: diagram-animated.svg)
- `--theme <theme>` - Theme (default: dark)
- `-m, --max-files <n>` - Max files to analyze (default: 100)

**Prerequisites:**
```bash
npm install
npx playwright install chromium
```

**Examples:**
```bash
diagram animate .
diagram animate . --type sequence --output sequence-animated.svg
diagram animate . --theme forest
```

---

## workflow pr

Analyze the architecture impact of PR changes including blast radius and risk scoring.

```bash
diagram workflow pr [path] [options]
```

**Options:**
- `--base <ref>` - Base git ref (SHA, branch, tag). Required unless auto-detected.
- `--head <ref>` - Head git ref (SHA, branch, tag). Defaults to HEAD.
- `-o, --output-dir <dir>` - Output directory (default: .diagram/pr-impact)
- `--max-depth <n>` - Maximum blast radius traversal depth (default: 2)
- `--max-nodes <n>` - Maximum components in blast radius (default: 50)
- `--risk-threshold <level>` - Risk threshold for gating: none, low, medium, high (default: none)
- `--fail-on-risk` - Exit with code 1 if risk meets or exceeds threshold
- `--risk-override-reason <string>` - Override risk gate with documented reason
- `-j, --json` - Output as JSON only (skip HTML generation)
- `--verbose` - Show detailed output

**Output Artifacts:**
- `pr-impact.json` - Full JSON report with delta, blast radius, and risk
- `pr-impact.html` - Human-readable HTML explainer

**Exit Codes:**
- 0: Success, below risk threshold
- 1: Risk threshold exceeded (with --fail-on-risk)
- 2: Configuration or git error

**Examples:**
```bash
# Basic usage
diagram workflow pr . --base origin/main --head HEAD

# With risk threshold
diagram workflow pr . --base origin/main --head HEAD \
  --risk-threshold high --fail-on-risk

# JSON output only
diagram workflow pr . --json

# Override risk gate with documentation
diagram workflow pr . --base origin/main --head HEAD \
  --risk-threshold high --fail-on-risk \
  --risk-override-reason "Approved by security team per ticket SEC-123"
```
