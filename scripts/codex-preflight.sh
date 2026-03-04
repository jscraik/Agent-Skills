#!/usr/bin/env bash
set -euo pipefail

preflight_repo() {
  local expected_repo="${1:-}"
  local bins_csv="${2:-git,bash,sed,rg}"
  local paths_csv="${3:-AGENTS.md,docs,docs/plans}"

  echo "== Codex Preflight =="
  echo "pwd: $(pwd)"

  if ! command -v git >/dev/null 2>&1; then
    echo "❌ missing binary: git" >&2
    return 2
  fi

  local root
  if ! root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    echo "❌ not inside a git repo (git rev-parse failed)" >&2
    return 2
  fi

  if [[ -z "${root}" ]]; then
    echo "❌ git rev-parse returned empty root" >&2
    return 2
  fi

  root="$(cd "${root}" && pwd -P)"
  local workspace_root
  workspace_root="$(cd "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
  echo "repo root: ${root}"

  if [[ "${root}" != "${workspace_root}" ]]; then
    echo "❌ script workspace mismatch: expected ${workspace_root}" >&2
    return 2
  fi

  if [[ -n "${expected_repo}" ]] && [[ "${root}" != *"${expected_repo}"* ]]; then
    echo "❌ repo mismatch: expected fragment '${expected_repo}' in '${root}'" >&2
    return 2
  fi

  cd "${root}"

  local -a bins=()
  local -a missing_bins=()
  IFS=',' read -r -a bins <<< "${bins_csv}"
  local b
  for b in "${bins[@]}"; do
    [[ -z "${b}" ]] && continue
    if ! command -v "${b}" >/dev/null 2>&1; then
      missing_bins+=("${b}")
    fi
  done

  if (( ${#missing_bins[@]} > 0 )); then
    echo "❌ missing binaries: ${missing_bins[*]}" >&2
    return 2
  fi
  echo "✅ binaries ok: ${bins_csv}"

  local -a paths=()
  IFS=',' read -r -a paths <<< "${paths_csv}"
  local p
  for p in "${paths[@]}"; do
    [[ -z "${p}" ]] && continue

    local -a matches=()
    shopt -s nullglob
    for match in ${p}; do
      matches+=("${match}")
    done
    shopt -u nullglob

    if (( ${#matches[@]} == 0 )); then
      matches+=("${p}")
    fi

    local found=0
    local match abs
    for match in "${matches[@]}"; do
      if [[ -e "${match}" ]]; then
        found=1
        if ! abs="$(python3 -c "import os, sys; print(os.path.realpath(sys.argv[1]))" "${match}")"; then
          echo "❌ failed to resolve path: ${match}" >&2
          return 2
        fi
        if [[ "${abs}" != "${root}" && "${abs}" != "${root}"/* ]]; then
          echo "❌ path escapes repo root: ${match} -> ${abs}" >&2
          return 2
        fi
      fi
    done

    if (( found == 0 )); then
      echo "❌ missing path: ${p}" >&2
      return 2
    fi
  done
  echo "✅ paths ok: ${paths_csv}"

  echo "git branch: $(git rev-parse --abbrev-ref HEAD)"
  echo "clean?: $(git status --porcelain | wc -l | tr -d ' ') changes"
  echo "✅ preflight passed"
}

preflight_js() {
  preflight_repo "${1:-}" "git,bash,sed,rg,node,npm" "${2:-AGENTS.md,package.json,docs,docs/plans}"
}

preflight_rust() {
  preflight_repo "${1:-}" "git,bash,sed,rg,python3,cargo" "${2:-AGENTS.md,Cargo.toml,docs,docs/plans}"
}

preflight_py() {
  preflight_repo "${1:-}" "git,bash,sed,rg,python3" "${2:-AGENTS.md,pyproject.toml,docs,docs/plans}"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  preflight_repo "$@"
fi
