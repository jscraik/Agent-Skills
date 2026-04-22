#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
fi
CONTRACT_PATH="${1:-$REPO_ROOT/Docs/agents/tooling.contract.json}"
OUTPUT_PATH="${2:-$REPO_ROOT/Docs/agents/tooling.md}"

if ! command -v jq >/dev/null 2>&1; then
	echo "Error: jq is required to generate tooling.md"
	exit 1
fi

if [[ ! -f "$CONTRACT_PATH" ]]; then
	echo "Error: missing contract file at $CONTRACT_PATH"
	exit 1
fi

if ! jq -e '
	(.required_mise_tools | type == "array") and
	(.required_bins | type == "array") and
	(.required_codex_actions | type == "array")
' "$CONTRACT_PATH" >/dev/null; then
	echo "Error: invalid contract schema at $CONTRACT_PATH"
	exit 1
fi

{
	cat <<'EOF'
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
EOF

	jq -r '.required_mise_tools[] | "| `\(.)` |"' "$CONTRACT_PATH"

	cat <<'EOF'

## Required Binaries

| Binary |
| --- |
EOF

	jq -r '.required_bins[] | "| `\(.)` |"' "$CONTRACT_PATH"

	cat <<'EOF'

## Required Codex Actions (`.codex/environments/environment.toml`)

| Action | Icon |
| --- | --- |
EOF

	jq -r '.required_codex_actions[] | "| `\(.name)` | `\(.icon)` |"' "$CONTRACT_PATH"

	cat <<'EOF'

## Regeneration

```bash
bash Infrastructure/scripts/lifecycle-and-sync/generate-tooling-doc.sh
```
EOF
} > "$OUTPUT_PATH"

echo "Generated $OUTPUT_PATH from $CONTRACT_PATH"
