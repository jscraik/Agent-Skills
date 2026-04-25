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

if state.get("scope") != "skill-health":
    print("scope_mismatch", file=sys.stderr)
    raise SystemExit(1)
if state.get("evidence") != "present":
    print("evidence_missing", file=sys.stderr)
    raise SystemExit(1)
if state.get("rollback") != "present":
    print("rollback_missing", file=sys.stderr)
    raise SystemExit(1)

recommendations = {item.strip() for item in state.get("recommendations", "").split(",") if item.strip()}
if {"keep", "improve", "merge", "retire"} - recommendations:
    print("recommendation_classes_incomplete", file=sys.stderr)
    raise SystemExit(1)

print("skill_refactor_workout_pass")
