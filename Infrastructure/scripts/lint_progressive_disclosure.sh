#!/usr/bin/env bash
set -euo pipefail

exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skill_scan.py" lint-progressive-disclosure "$@"
