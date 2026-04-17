#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  collect-project-context.sh [--out-dir DIR]

Environment:
  OUT_DIR   Output directory for context.md (default: audit)
TXT
}

OUT_DIR="${OUT_DIR:-audit}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir)
      if [[ -z "${2:-}" || "${2:-}" == --* ]]; then
        echo "ERROR: missing value for $1" >&2
        usage >&2
        exit 2
      fi
      OUT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$OUT_DIR"

OUT_FILE="$OUT_DIR/context.md"

{
  echo "# Project Context Pack"
  echo ""
  echo "**Generated:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""
} > "$OUT_FILE"

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

# shellcheck disable=SC2012,SC2129
{
  echo "## Repo structure (top-level)"
  echo ""
  ls -la
  echo ""
} >> "$OUT_FILE"

{
  echo "## Key docs found"
  echo ""
  for f in README.md spec-output.md tech-spec-output.md; do
    [[ -f "$f" ]] && echo "- $f"
  done
  if command -v fd >/dev/null 2>&1; then
    fd -t f -e md . docs 2>/dev/null | sed 's|^\./||' | sed 's/^/- /'
  elif command -v rg >/dev/null 2>&1; then
    rg --files docs 2>/dev/null | rg '\.md$' | sed 's/^/- /'
  fi
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
