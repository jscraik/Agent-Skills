#!/usr/bin/env python3
import os
import sys
from pathlib import Path

state_dir_value = os.environ.get("WORKOUT_STATE_DIR")
if not state_dir_value:
    print("WORKOUT_STATE_DIR environment variable is required", file=sys.stderr)
    raise SystemExit(1)

state_file = Path(state_dir_value) / "verifier_state.env"
if not state_file.is_file():
    print("verifier_state_missing", file=sys.stderr)
    raise SystemExit(1)

state = {}
for raw_line in state_file.read_text(encoding="utf-8").splitlines():
    if "=" not in raw_line:
        continue
    key, value = raw_line.split("=", 1)
    state[key.strip()] = value.strip()

required = {
    "stage": "he-spec",
    "spec_direction": "standard-spec",
    "handoff": "he-plan",
}
for key, expected in required.items():
    if state.get(key) != expected:
        print(f"{key}_mismatch", file=sys.stderr)
        raise SystemExit(1)

inputs = {item.strip() for item in state.get("inputs", "").split(",") if item.strip()}
if {"feature_description", "constraints", "success_criteria"} - inputs:
    print("spec_inputs_incomplete", file=sys.stderr)
    raise SystemExit(1)

print("he_spec_workout_pass")
