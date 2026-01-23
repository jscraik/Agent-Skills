#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-audit}"
mkdir -p "$OUT_DIR"

OUT_FILE="$OUT_DIR/context.md"

echo "# Project Context Pack" > "$OUT_FILE"
echo "" >> "$OUT_FILE"
echo "**Generated:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$OUT_FILE"
echo "" >> "$OUT_FILE"

if command -v git >/dev/null 2>&1 && [[ -d .git ]]; then
  {
    echo "## Git"
    echo ""
    echo "**Remote:**"
    git remote -v || true
    echo ""
    echo "**Branch:**"
    git branch --show-current || true
    echo ""
    echo "**Recent commits:**"
    git --no-pager log -n 20 --oneline || true
    echo ""
    echo "**Status:**"
    git status --porcelain || true
    echo ""
  } >> "$OUT_FILE"
fi

{
  echo "## Repo structure (top-level)"
  echo ""
  ls -la
  echo ""
} >> "$OUT_FILE"

{
  echo "## Key docs found"
  echo ""
  for f in README.md spec-output.md tech-spec-output.md docs/*.md docs/**/*.md; do
    [[ -f "$f" ]] && echo "- $f"
  done
  echo ""
} >> "$OUT_FILE"

{
  echo "## Dependency manifests"
  echo ""
  for f in package.json pnpm-lock.yaml yarn.lock requirements.txt pyproject.toml poetry.lock Pipfile go.mod Cargo.toml; do
    [[ -f "$f" ]] && echo "- $f"
  done
  echo ""
} >> "$OUT_FILE"

if command -v rg >/dev/null 2>&1; then
  {
    echo "## TODO/FIXME hotspots (top 50)"
    echo ""
    rg -n --hidden --no-ignore-vcs "TODO|FIXME|HACK|XXX" . | head -n 50 || true
    echo ""
  } >> "$OUT_FILE"
fi

echo "Wrote: $OUT_FILE"
