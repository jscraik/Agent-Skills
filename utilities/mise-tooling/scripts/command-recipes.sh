#!/usr/bin/env bash
set -euo pipefail

# Mise command recipes referenced by SKILL.md
mise use node@24
mise exec -- node --version
mise trust --show
