#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/preflight.sh --repo-root <path> --mode <dry-run|manual|silent-on-open|ci-only>

Checks repository readiness for diagram context refresh operations.
No files are modified.
USAGE
}

repo_root=""
mode=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      repo_root="${2:-}"
      shift 2
      ;;
    --mode)
      mode="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$repo_root" ]]; then
  echo "[FAIL] Missing required --repo-root" >&2
  usage >&2
  exit 2
fi

if [[ -z "$mode" ]]; then
  echo "[FAIL] Missing required --mode" >&2
  usage >&2
  exit 2
fi

case "$mode" in
  dry-run|manual|silent-on-open|ci-only) ;;
  *)
    echo "[FAIL] Unsupported mode: $mode" >&2
    usage >&2
    exit 2
    ;;
esac

repo_root="$(cd "$repo_root" && pwd)"
failures=0

ok() {
  echo "[OK] $1"
}

warn() {
  echo "[WARN] $1"
}

fail() {
  echo "[FAIL] $1" >&2
  failures=$((failures + 1))
}

require_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "Command available: $cmd"
  else
    fail "Required command missing: $cmd"
  fi
}

require_canonical_repo_root() {
  local canonical
  if git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    canonical="$(git -C "$repo_root" rev-parse --show-toplevel)"
    if [[ "$repo_root" != "$canonical" ]]; then
      fail "Repo root is not the canonical project root. Use: $canonical"
    else
      ok "Repo root is canonical: $canonical"
    fi
  else
    fail "Not a git repository at $repo_root; canonical-root mode requires git repo"
  fi
}

require_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    ok "File exists: $path"
  else
    fail "Required file missing: $path"
  fi
}

echo "== Diagram context refresh preflight =="
echo "Repo root: $repo_root"
echo "Mode: $mode"

if [[ -d "$repo_root" ]]; then
  ok "Repo root exists"
else
  fail "Repo root does not exist: $repo_root"
fi

if [[ -w "$repo_root" ]]; then
  ok "Repo root is writable"
else
  fail "Repo root is not writable: $repo_root"
fi

require_canonical_repo_root

require_cmd rg
require_cmd jq

if [[ -f "$repo_root/src/diagram.js" ]]; then
  ok "Repo-local diagram entrypoint found: $repo_root/src/diagram.js"
elif command -v diagram >/dev/null 2>&1; then
  ok "Global diagram CLI available: $(command -v diagram)"
else
  fail "Neither repo-local src/diagram.js nor global diagram CLI was found"
fi

if command -v diagram >/dev/null 2>&1; then
  if diagram --version >/dev/null 2>&1; then
    ok "Global diagram CLI version check passed"
  else
    fail "Global diagram CLI exists but --version failed"
  fi
fi

if command -v mise >/dev/null 2>&1; then
  if mise current | rg "@brainwav/diagram" >/dev/null 2>&1; then
    ok "mise reports @brainwav/diagram"
  else
    warn "mise is installed but @brainwav/diagram is not reported"
  fi
fi

has_refresh_entrypoint=false

if [[ -f "$repo_root/scripts/refresh-diagram-context.sh" ]]; then
  ok "Repo-local refresh script found: $repo_root/scripts/refresh-diagram-context.sh"
  has_refresh_entrypoint=true
fi

if [[ -f "$repo_root/package.json" ]]; then
  if jq -e '.scripts["refresh-diagram-context"]' "$repo_root/package.json" >/dev/null 2>&1; then
    ok "package.json defines npm script: refresh-diagram-context"
    has_refresh_entrypoint=true
    require_cmd npm
  else
    warn "package.json exists but does not define refresh-diagram-context script"
  fi
else
  warn "package.json not found; skipping npm-script refresh checks"
fi

if [[ "$has_refresh_entrypoint" == "false" ]]; then
  fail "No refresh entrypoint found. Expected either scripts/refresh-diagram-context.sh or package.json script 'refresh-diagram-context'"
fi

if [[ "$mode" == "silent-on-open" ]]; then
  require_file "$repo_root/scripts/install-repo-open-hook.sh"
fi

if [[ "$mode" == "ci-only" ]]; then
  require_file "$repo_root/.github/workflows/refresh-diagram-context.yml"
fi

if [[ $failures -gt 0 ]]; then
  echo "Preflight result: FAIL ($failures check(s) failed)" >&2
  exit 1
fi

echo "Preflight result: PASS"
