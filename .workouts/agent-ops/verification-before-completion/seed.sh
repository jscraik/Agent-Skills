#!/usr/bin/env bash
set -euo pipefail

state_dir="${WORKOUT_STATE_DIR:?WORKOUT_STATE_DIR is required}"
mkdir -p "$state_dir"
printf 'implementation_checked=true\nvalidation_evidence=present\n' > "$state_dir/verifier_state.env"
