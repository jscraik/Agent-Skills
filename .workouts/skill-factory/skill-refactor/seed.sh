#!/usr/bin/env bash
set -euo pipefail

state_dir="${WORKOUT_STATE_DIR:?WORKOUT_STATE_DIR is required}"
mkdir -p "$state_dir"
cat > "$state_dir/verifier_state.env" <<STATE
scope=skill-health
recommendations=keep,improve,merge,retire
evidence=present
rollback=present
STATE
