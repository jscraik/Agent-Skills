#!/usr/bin/env python3
import os
import sys
from pathlib import Path


state_dir = Path(os.environ.get("WORKOUT_STATE_DIR", ""))
state_file = state_dir / "verifier_state.env"
if not state_file.is_file():
    print("verifier_state_missing", file=sys.stderr)
    raise SystemExit(1)

state = {}
for raw_line in state_file.read_text(encoding="utf-8").splitlines():
    if "=" not in raw_line:
        continue
    key, value = raw_line.split("=", 1)
    state[key.strip()] = value.strip()

if state.get("implementation_checked") != "true":
    print("implementation_check_missing", file=sys.stderr)
    raise SystemExit(1)
if state.get("validation_evidence") != "present":
    print("validation_evidence_missing", file=sys.stderr)
    raise SystemExit(1)

print("verification_state_pass")
