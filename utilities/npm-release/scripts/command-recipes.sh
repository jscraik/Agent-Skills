#!/usr/bin/env bash
set -euo pipefail

# npm release command recipes referenced by SKILL.md
npm version patch
npm publish --provenance --access public
npm dist-tag ls "${1:-<package-name>}"
