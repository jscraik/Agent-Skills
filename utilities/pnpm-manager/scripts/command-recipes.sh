#!/usr/bin/env bash
set -euo pipefail

# pnpm workspace command recipes referenced by SKILL.md

list_pkgs() {
  pnpm -r list --depth 0
}

run_tests() {
  pnpm --filter "${1:-.}" run test
}

exec_cmd() {
  local cmd
  if [[ $# -lt 2 ]]; then
    cmd=(echo ok)
  else
    cmd=("${@:2}")
  fi
  pnpm -r exec "${cmd[@]}"
}

# Dispatch based on first argument
case "${1:-}" in
  list)
    list_pkgs
    ;;
  test)
    run_tests "${2:-.}"
    ;;
  exec)
    exec_cmd "$@"
    ;;
  *)
    echo "Usage: $0 {list|test [filter]|exec [cmd...]}" >&2
    exit 1
    ;;
esac