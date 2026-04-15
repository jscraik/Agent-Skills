# Tooling Inventory

Repo-local tooling inventory generated from `Docs/agents/tooling.contract.json`.

## Table of Contents

- [Pinned Tools (`.mise.toml`)](#pinned-tools-misetoml)
- [Required Binaries](#required-binaries)
- [Required Codex Actions (`.codex/environments/environment.toml`)](#required-codex-actions-codexenvironmentsenvironmenttoml)
- [Regeneration](#regeneration)

## Pinned Tools (`.mise.toml`)

| Tool |
| --- |
| `node` |
| `pnpm` |
| `python` |
| `uv` |
| `cargo:prek` |
| `npm:@brainwav/diagram` |
| `npm:@argos-ci/cli` |
| `cosign` |
| `cloudflared` |
| `npm:vitest` |
| `ruff` |
| `npm:eslint` |
| `npm:agent-browser` |
| `npm:agentation` |
| `npm:agentation-mcp` |
| `npm:@mermaid-js/mermaid-cli` |
| `npm:@brainwav/rsearch` |
| `npm:@brainwav/wsearch-cli` |
| `npm:beautiful-mermaid` |
| `npm:markdownlint-cli2` |
| `npm:semver` |
| `npm:wrangler` |
| `semgrep` |
| `trivy` |
| `vale` |

## Required Binaries

| Binary |
| --- |
| `pnpm` |
| `node` |
| `jq` |
| `make` |
| `rg` |
| `fd` |
| `prek` |
| `diagram` |
| `mise` |
| `vale` |
| `argos` |
| `cosign` |
| `cloudflared` |
| `vitest` |
| `ruff` |
| `eslint` |
| `agent-browser` |
| `agentation-mcp` |
| `mmdc` |
| `markdownlint-cli2` |
| `wrangler` |
| `beautiful-mermaid` |
| `semgrep` |
| `semver` |
| `trivy` |
| `rsearch` |
| `wsearch` |

## Required Codex Actions (`.codex/environments/environment.toml`)

| Action | Icon |
| --- | --- |
| `Tools` | `tool` |
| `Run` | `run` |
| `Debug` | `debug` |
| `Test` | `test` |
| `Prek` | `test` |
| `Diagram` | `tool` |
| `Ralph` | `debug` |
| `Mise` | `tool` |
| `Vale` | `debug` |
| `Argos` | `test` |
| `Cosign` | `debug` |
| `Cloudflared` | `run` |
| `Vitest` | `test` |
| `Ruff` | `debug` |
| `ESLint` | `debug` |
| `Agent Browser` | `tool` |
| `Agentation` | `tool` |
| `Mermaid CLI` | `tool` |
| `MarkdownLint` | `debug` |
| `Wrangler` | `run` |
| `1Password` | `tool` |
| `Beautiful Mermaid` | `tool` |
| `Auth0` | `tool` |
| `Semgrep` | `debug` |
| `Semver` | `tool` |
| `Trivy` | `debug` |
| `Gitleaks` | `debug` |
| `Research` | `tool` |
| `WSearch` | `tool` |

## Regeneration

```bash
bash Infrastructure/scripts/generate-tooling-doc.sh
```
