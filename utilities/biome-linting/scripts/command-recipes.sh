#!/usr/bin/env bash
set -euo pipefail

# Biome command recipes referenced by SKILL.md
biome lint .
biome lint --write .
biome lint --write --unsafe .
npx @biomejs/biome ci
