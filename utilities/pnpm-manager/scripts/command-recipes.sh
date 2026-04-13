#!/usr/bin/env bash
set -euo pipefail

# pnpm workspace command recipes referenced by SKILL.md
pnpm -r list --depth 0
pnpm --filter "${1:-<selector>}" run test
pnpm -r exec "${2:-echo}" "${3:-ok}"
