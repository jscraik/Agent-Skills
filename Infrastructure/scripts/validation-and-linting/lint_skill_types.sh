#!/usr/bin/env bash
set -euo pipefail

exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")/../lifecycle-and-sync" && pwd)/skill_scan.py" lint-skill-types "$@"
