#!/usr/bin/env bash
set -euo pipefail

# Biome command recipes referenced by SKILL.md
biome lint .
biome lint --write .
if [ "${ALLOW_UNSAFE_FIXES:-0}" = "1" ]; then
  biome lint --write --unsafe .
fi
npx @biomejs/biome ci
