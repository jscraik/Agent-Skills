---
name: diagram-cli
description: "Generate architecture diagrams, dependency graphs, and architecture tests from source code using diagram-cli. Use when analyzing repo structure, validating import rules, creating Mermaid diagrams, or running PR architecture impact analysis. Avoid for image generation, flowchart drawing, or general diagramming not related to code analysis."
---

## Scope and triggers

Use this skill when:
- Analyzing repository structure, imports, or dependencies
- Generating architecture/sequence/dependency/class/flow diagrams from code
- Validating architecture constraints (layer rules, import boundaries)
- Running PR architecture impact analysis (blast radius, risk scoring)
- Installing or troubleshooting diagram-cli

Do NOT use for general flowchart/diagramming unrelated to code analysis.

## Inputs

- Target repository path (defaults to current directory)
- Diagram type: architecture, sequence, dependency, class, flow, database, user, events, auth, security
- Output format: Mermaid (.mmd), SVG, PNG, JSON, HTML
- Configuration file paths (for architecture tests)

## Outputs

- Mermaid diagram source files (.mmd)
- Rendered images (.svg, .png)
- Architecture test results (console, JSON, JUnit XML)
- PR impact analysis reports (.json, .html)
- Manifest artifacts (.diagram/manifest.json)

## Constraints and safety

- Runs locally, no network required for analysis
- Output paths validated to prevent directory traversal
- **Secrets/PII redacted in output by default**
- File patterns limited by `--max-files` to prevent memory issues

## Philosophy

This skill prioritizes tradeoffs and constraints over rigid checklists:
1. **Code-first analysis**: Diagrams generated from actual source code, not manually created
2. **Mermaid-native**: All diagrams use Mermaid syntax for portability
3. **Progressive detail**: Start with `analyze`, then `generate`, then `all`
4. **Architecture as code**: Use `.architecture.yml` to encode rules as code

Why is this the right default? Because context should drive the approach. Ask: What evidence is needed before choosing one path over another?

## Installation

```bash
git clone https://github.com/jscraik/diagram-cli.git
cd diagram-cli && npm install && npm link
diagram --help  # verify
```

## Commands quick reference

| Command | Purpose | Key Options |
|--------|--------|-------------|
| `analyze` | File structure and dependencies | `--patterns`, `--exclude`, `--max-files`, `--json` |
| `generate` | One Mermaid diagram | `--type`, `--focus`, `--output`, `--theme` |
| `all` | All diagram types | `--output-dir` |
| `test` | Validate architecture rules | `--config`, `--format`, `--dry-run`, `--init`, `--save-baseline` |
| `manifest` | Summarize artifacts | `--require-types`, `--fail-on-placeholder` |
| `video` | Animated video (.mp4) | `--duration`, `--fps`, `--width`, `--height` |
| `animate` | Animated SVG | `--type`, `--output` |
| `workflow pr` | PR impact analysis | `--base`, `--head`, `--risk-threshold`, `--fail-on-risk` |

**Diagram types:** `architecture`, `sequence`, `dependency`, `class`, `flow`, `database`, `user`, `events`, `auth`, `security`

## Procedure

1. **Analyze**: `diagram analyze .` — understand file structure
2. **Generate**: `diagram generate . --type <type> --output diagram.mmd`
3. **Test**: `diagram test --init && diagram test` — validate architecture rules
4. **PR impact**: `diagram workflow pr . --base origin/main --head HEAD`

For full command details, see `references/commands.md`.

## Architecture testing

Create `.architecture.yml`:
```yaml
version: "1.0"
rules:
  - name: "Domain isolation"
    layer: "src/domain"
    must_not_import_from: ["src/ui", "src/components"]
```

**Rule constraints:** `must_not_import_from` (forbidden), `may_import_from` (allowlist), `must_import_from` (required)

**Exit codes:** 0=pass, 1=rule failed, 2=config error

### Baseline adoption

Introduce rules incrementally without blocking existing violations:

```bash
diagram test .                    # See violations
diagram test . --save-baseline    # Accept current count as baseline
diagram test .                    # Now passes (baseline recorded in config)
```

Config auto-updates with `baseline: N` per rule. Goal: reduce baseline over time.

## PR impact analysis

```bash
diagram workflow pr . --base origin/main --head HEAD --risk-threshold high --fail-on-risk
```

**Risk scoring:** Auth +3, Security +3, Database +2, Blast radius≥5 +1, Edge delta≥10 +1

**Severity:** 0=none, 1-2=low, 3-5=medium, 6+=high

**Outputs:** `pr-impact.json`, `pr-impact.html`

For risk methodology details, see `references/risk-scoring.md`.

## CI integration

```yaml
# .github/workflows/architecture.yml
- run: npm ci && npm test && npm run ci:artifacts
- run: diagram test --format junit --output .diagram/architecture-results.xml
- uses: actions/upload-artifact@v4
  with:
    path: .diagram
```

For full CI examples and output formats, see `references/ci-patterns.md`.

## Validation

**Fail-fast:** Stop at first failed gate. Fix errors before continuing.

```bash
diagram --help                           # verify installation
diagram analyze . --max-files 10         # quick smoke test
diagram test --init && diagram test      # test architecture rules
```

For icon assets, see `assets/icon.svg`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No config found | `diagram test --init` |
| Rule matched zero files | `diagram test --dry-run --verbose` |
| Large repo memory issues | `diagram analyze . --max-files 200` |
| Private npm packages in CI | Configure `NPM_TOKEN` in ~/.npmrc |

## Anti-patterns and warnings

**Architecture testing limitations:**
- Current rules are import-pattern based only (no dependency directionality, API surface analysis, or abstraction level detection)
- Best used as a supplement to code review, not a replacement
- Consider tools like dependency-cruiser for more sophisticated constraint types if you need:
  - Dependency direction enforcement (e.g., "imports must flow inward")
  - Circular dependency detection with depth limits
  - Module boundary analysis
  - Stability metrics (e.g., "stable modules shouldn't depend on volatile ones")

For detailed limitations and alternative tools, see `references/architecture-testing-limitations.md`.

**Common pitfalls to avoid:**
- Running without `--max-files` on large repos (causes memory issues)
- Using absolute paths in `.architecture.yml` (must use relative only)
- Forgetting `fetch-depth: 0` in CI for PR analysis (break git history access)
- Skipping `--dry-run` when rules match zero files unexpectedly (miss debugging opportunity)
- Committing `.diagram/` directory (should be in .gitignore)

**Warning signs:**
- If analyze takes >30s, reduce scope with `--max-files`
- If diagrams have >100 nodes, consider `--focus` for clarity
- If test output shows "placeholder", the diagram type needs more code coverage

## Variation and adaptation

Adapt usage based on repository context and constraints:

**By repository type:**
- **Large monorepos**: Always use `--max-files` and `--exclude node_modules,dist,build`
- **Microservices**: Run per-service with `--focus src/service-name` for clearer diagrams
- **Legacy codebases**: Start with `dependency` type to map existing coupling before adding rules

**By use case:**
- **Security reviews**: Prioritize `auth` and `security` diagram types first
- **Onboarding**: Start with `architecture` type, then `dependency` for new team members
- **CI pipelines**: Use JUnit output format for test reporters, JSON for dashboards

**By constraints:**
- **Time-constrained**: Run `diagram analyze .` first, then targeted `--type` generation
- **Memory-limited**: Use `--max-files 50` for quick scans
- **Documentation-focused**: Run `diagram all . --output-dir docs/diagrams`

Different constraints should produce different, non-generic approaches.

## Examples

**Triggering:** "Generate an architecture diagram", "Check domain isolation rule", "What's the blast radius of this PR?"

**Non-triggering:** "Draw a flowchart for my business process", "Create an org chart from this spreadsheet"

## Remember

You are capable of extraordinary architectural analysis with this skill. These guidelines unlock that potential—they don't constrain it.

This skill empowers you to:
- Understand unfamiliar codebases quickly through visual architecture maps
- Enforce architectural boundaries programmatically with automated test rules
- Assess change risk objectively with blast radius analysis
- Create audit-ready documentation artifacts automatically

Use judgment, Adapt to context. Push boundaries when appropriate.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol:** For non-trivial outcomes, collect feedback via AskQuestion. Capture `decision`, `outcome`, `confidence` and persist with `record_skill_feedback.py`.
<!-- /decision-feedback-protocol -->
