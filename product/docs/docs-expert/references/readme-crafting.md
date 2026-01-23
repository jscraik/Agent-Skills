# Crafting README Files

> Core insight: A README is a sales pitch, onboarding guide, and reference manual compressed into one document. Lead with value, prove with examples, document with precision.

## Why This Matters

Most READMEs fail because they:
- Bury the value proposition under installation steps
- Explain what the tool is instead of what problem it solves
- Lack concrete examples (abstract descriptions do not sell)
- Miss a fast, safe escape hatch for impatient users (package manager or verified download)
- Do not show how it compares to alternatives

Great READMEs convert scanners into users in under 60 seconds.

---

## The Exact Prompt - README Revision

```text
Read the current README.md and dramatically revise it following this structure:

1. Hero section: illustration + badges + one-liner description + quick install (package manager or verified download)
2. TL;DR: "The Problem" + "The Solution" + "Why Use X?" feature table
3. Quick example showing the tool in action (5-10 commands)
4. Design philosophy (3-5 principles with explanations)
5. Comparison table vs alternatives
6. Installation (package managers, verified download, from source)
7. Quick start (numbered steps, copy-paste ready)
8. Command reference (every command with examples)
9. Configuration (full config file example with comments)
10. Architecture diagram (ASCII art showing data flow)
11. Troubleshooting (common errors with fixes)
12. Limitations (honest about what it does not do)
13. FAQ (anticipate user questions)

Make it comprehensive but scannable. Use tables for comparisons.
Show, do not tell. Every claim should have a concrete example.
Use ultrathink.
```

---

## Golden Structure

```text
1. HERO SECTION (above the fold)
   - Illustration/logo (centered)
   - Badges (CI, license, version)
   - One-liner description
   - Quick install (package manager or verified download)

2. TL;DR (sell the value)
   - The Problem (pain point)
   - The Solution (what this does)
   - Why Use X? (feature table)

3. QUICK EXAMPLE (prove it works)
   - 5-10 commands showing core workflow

4. REFERENCE SECTIONS
   - Design Philosophy
   - Comparison vs Alternatives
   - Installation (multiple paths)
   - Quick Start
   - Commands
   - Configuration
   - Architecture

5. SUPPORT SECTIONS
   - Troubleshooting
   - Limitations
   - FAQ
   - Contributing
   - License
```

---

## Section Templates

### Hero Section

````markdown
# tool-name

<div align="center">
  <img src="illustration.webp" alt="tool-name - One-line description">
</div>

<div align="center">

[![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)](https://github.com/user/repo/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

One-sentence description of what this tool does and its key differentiator.

<div align="center">
<h3>Quick Install</h3>

```bash
# Preferred: package manager
brew install user/tap/tool
```

**Or install from a verified release:**

```bash
curl -fsSL https://example.com/tool-v1.2.3.tar.gz -o /tmp/tool.tar.gz
curl -fsSL https://example.com/tool-v1.2.3.tar.gz.sha256 -o /tmp/tool.tar.gz.sha256
shasum -a 256 -c /tmp/tool.tar.gz.sha256
tar -xzf /tmp/tool.tar.gz -C /tmp
install /tmp/tool ~/.local/bin/tool
```

**Or build from source:**

```bash
cargo install --git https://github.com/user/repo.git
```

</div>
````

### TL;DR Section

````markdown
## TL;DR

**The Problem**: [Specific pain point in 1-2 sentences. Be concrete.]

**The Solution**: [What this tool does to solve it. Action-oriented.]

### Why Use tool-name?

| Feature | What It Does |
|---------|--------------|
| **Feature 1** | Concrete benefit, not abstract capability |
| **Feature 2** | Another specific value proposition |
| **Feature 3** | Quantify when possible (e.g., "<10ms search") |
````

### Quick Example

````markdown
### Quick Example

```bash
# Initialize (one-time setup)
tool init

# Core operation
tool do-thing --flag value

# See results
tool show results

# The killer feature
tool magic --auto
```
````

### Comparison Table

````markdown
## How tool-name Compares

| Feature | tool-name | Alternative A | Alternative B | Manual |
|---------|-----------|---------------|---------------|--------|
| Feature 1 | Yes | Partial | No | No |
| Feature 2 | Yes (<10ms) | Slow (~500ms) | Yes (fast) | NA |
| Setup time | Yes (~10 seconds) | No (hours) | Partial (minutes) | No |

**When to use tool-name:**
- Bullet point of ideal use case
- Another use case

**When tool-name might not be ideal:**
- Honest limitation
- Another case where alternatives win
````

### Installation Section

````markdown
## Installation

### Preferred Install (Recommended)

```bash
# Homebrew
brew install user/tap/tool
```

**Scripted install (optional, inspect first):**

```bash
# Download the installer, review, then run
curl -fsSL https://example.com/install.sh -o /tmp/install.sh
sed -n '1,200p' /tmp/install.sh
bash /tmp/install.sh --easy-mode

# Specific version
bash /tmp/install.sh --version v1.0.0

# System-wide (requires sudo)
sudo bash /tmp/install.sh --system
```

### Package Managers

```bash
# Homebrew
brew install user/tap/tool

# Windows (Scoop)
scoop bucket add user https://github.com/user/scoop-bucket
scoop install tool
```

### From Source

```bash
git clone https://github.com/user/repo.git
cd repo
cargo build --release
cp target/release/tool ~/.local/bin/
```
````

### Command Reference Pattern

````markdown
## Commands

Global flags available on all commands:

```bash
--verbose       # Increase logging
--quiet         # Suppress non-error output
--format json   # Machine-readable output
```

### `tool command`

Brief description of what this command does.

```bash
tool command                    # Basic usage
tool command --flag value       # With options
tool command --help             # See all options
```
````

### Architecture Diagram

````markdown
## Architecture

```
+-----------------------------------------------------------------+
|                         Input Layer                             |
|   (files, API calls, user commands)                             |
+-----------------------------------------------------------------+
                            |
                            v
+-----------------------------------------------------------------+
|                      Processing Layer                           |
|   Component A -> Component B -> Component C                      |
+-----------------------------------------------------------------+
                            |
        +-------------------+-------------------+
        v                   v                   v
+------------------+ +------------------+ +------------------+
| Storage A        | | Storage B        | | Output           |
| - Detail 1       | | - Detail 1       | | - Format 1       |
| - Detail 2       | | - Detail 2       | | - Format 2       |
+------------------+ +------------------+ +------------------+
```
````

### Troubleshooting Pattern

````markdown
## Troubleshooting

### "Error message here"

```bash
# Solution
command to fix it
```

### "Another common error"

Explanation of why this happens and how to fix it.

```bash
# Check the state
diagnostic command

# Fix it
fix command
```
````

### Limitations Section

````markdown
## Limitations

### What tool-name Does Not Do (Yet)

- **Limitation 1**: Brief explanation, workaround if any
- **Limitation 2**: Why this is out of scope

### Known Limitations

| Capability | Current State | Planned |
|------------|---------------|---------|
| Feature X | Not supported | v2.0 |
| Feature Y | Partial | Improving |
````

### FAQ Pattern

````markdown
## FAQ

### Why "tool-name"?

Brief etymology or meaning.

### Is my data safe?

Yes/No with explanation. Privacy guarantees.

### Does it work with X?

Compatibility information.

### How do I [common task]?

```bash
# Command to accomplish it
tool do-thing
```
````

---

## Critical Rules

1. Lead with value, not installation - TL;DR before Quick Start.
2. Curl one-liner above the fold - impatient users need an escape hatch.
3. Every feature claim needs an example - show, do not tell.
4. Comparison tables beat prose - scannable beats readable.
5. Be honest about limitations - builds trust, saves support time.
6. Multiple installation paths - curl, package manager, source.
7. Architecture diagrams for complex tools - ASCII art is fine.
8. Troubleshooting section is mandatory - top 5 errors with fixes.

---

## Anti-Patterns (Avoid)

| Anti-Pattern | Why Bad | Fix |
|--------------|---------|-----|
| Installation-first README | Buries value proposition | Lead with TL;DR |
| "This is a tool that..." | Passive, abstract | "Solves X by doing Y" |
| Screenshot-heavy | Breaks, does not copy-paste | ASCII + code blocks |
| No examples | Abstract claims do not sell | Every feature -> example |
| Hiding limitations | Users discover painfully | Honest Limitations section |
| Single install method | Alienates users | curl + pkg manager + source |
| No troubleshooting | Support burden | Top 5 errors with fixes |
| Outdated badges | Looks abandoned | Remove or keep current |

---

## AGENTS.md Blurb Template

For CLI tools, include a condensed reference block:

````markdown
## tool - Brief Description

One-line description of what it does and key differentiator.

### Core Workflow

```bash
# 1. Initialize
tool init

# 2. Main operation
tool do-thing

# 3. View results
tool show
```

### Key Flags

```text
--flag1    # Description
--flag2    # Description
```

### Storage

```text
- Location 1: path/to/thing
- Location 2: path/to/other
```

### Notes

```text
- Important caveat 1
- Important caveat 2
```
````

This provides AI agents with scannable reference without loading the full README.

---

## Checklist

Before publishing:

```
[] Hero section with illustration + badges + one-liner + quick install
[] TL;DR with Problem/Solution/Feature table
[] Quick example (5-10 commands)
[] At least 3 installation methods documented
[] Every command has usage examples
[] Architecture diagram for complex tools
[] Comparison table vs at least 2 alternatives
[] Troubleshooting section (top 5 errors)
[] Honest Limitations section
[] FAQ with 5+ questions
[] All code blocks are copy-paste ready
[] No broken links or badges
[] Consistent terminology throughout
[] Grammar/spelling checked
```

---

## Badge Reference

Common badges for GitHub READMEs:

````markdown
# CI Status
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)

# License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Version/Release
[![GitHub release](https://img.shields.io/github/v/release/USER/REPO)](https://github.com/USER/REPO/releases)

# Downloads
[![Downloads](https://img.shields.io/github/downloads/USER/REPO/total)](https://github.com/USER/REPO/releases)

# Crates.io (Rust)
[![Crates.io](https://img.shields.io/crates/v/CRATE.svg)](https://crates.io/crates/CRATE)

# npm (JavaScript)
[![npm](https://img.shields.io/npm/v/PACKAGE.svg)](https://www.npmjs.com/package/PACKAGE)

# PyPI (Python)
[![PyPI](https://img.shields.io/pypi/v/PACKAGE.svg)](https://pypi.org/project/PACKAGE/)
````

---

## Real-World Examples

Study these READMEs for patterns:

| Project | Notable Pattern |
|---------|-----------------|
| https://github.com/Dicklesworthstone/xf | Comprehensive CLI docs, search deep-dives |
| https://github.com/BurntSushi/ripgrep | Benchmarks, comparison tables |
| https://github.com/sharkdp/bat | GIF demos, feature highlights |
| https://github.com/ogham/exa | Screenshot galleries, color themes |
| https://github.com/starship/starship | Preset configurations, installation matrix |
| https://github.com/jqlang/jq | Tutorial progression, manual links |

---

## Advanced: Progressive Disclosure for Long READMEs

For READMEs exceeding 1000 lines, use collapsible sections:

````markdown
<details>
<summary><strong>Advanced Configuration</strong></summary>

Content that most users do not need on first read...

</details>
````

Or link to separate docs:

````markdown
## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Contributing Guide](CONTRIBUTING.md)
````

Keep the README itself focused on the 80% use case.
