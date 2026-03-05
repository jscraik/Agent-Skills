#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

CONTROL_DIR="$TMP_DIR/controls"
mkdir -p "$CONTROL_DIR"

run_check() {
  local expected_mode="$1"
  local expected_reason="$2"
  CONTROL_DIR="$CONTROL_DIR" EXPECTED_MODE="$expected_mode" EXPECTED_REASON="$expected_reason" \
  python3 - <<'PY'
import os
import sys
from pathlib import Path

repo = Path.cwd()
scripts_dir = repo / "utilities" / "skill-creator" / "scripts"
sys.path.insert(0, str(scripts_dir))

from router_controls import resolve_rollout_mode

controls = Path(os.environ["CONTROL_DIR"])
r = resolve_rollout_mode(controls, "autopilot")
assert r.effective_mode == os.environ["EXPECTED_MODE"], r
assert r.reason == os.environ["EXPECTED_REASON"], r
PY
}

echo "Running skill-router rollback drill..."

# 1) Active mode should allow requested policy mode.
echo "active" > "$CONTROL_DIR/rollout-mode.txt"
run_check "autopilot" "rollout_mode_active"

# 2) rollback-required must force observe_only.
echo "on" > "$CONTROL_DIR/rollback-required.txt"
run_check "observe_only" "rollback_required"
rm -f "$CONTROL_DIR/rollback-required.txt"

# 3) kill-switch must dominate everything.
echo "on" > "$CONTROL_DIR/kill-switch.txt"
run_check "observe_only" "kill_switch"

echo "Rollback drill passed."
