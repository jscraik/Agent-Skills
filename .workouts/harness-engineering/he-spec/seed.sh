#!/usr/bin/env bash
set -euo pipefail

state_dir="${WORKOUT_STATE_DIR:?WORKOUT_STATE_DIR is required}"
mkdir -p "$state_dir"
cat > "$state_dir/verifier_state.env" <<STATE
stage=he-spec
spec_direction=standard-spec
handoff=he-plan
inputs=feature_description,constraints,success_criteria
STATE
