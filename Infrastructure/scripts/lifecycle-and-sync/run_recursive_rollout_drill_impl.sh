#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

out_root="${OUT_ROOT:-Infrastructure/artifacts/skill-graphs/drills/runs}"
controls_dir="${CONTROLS_DIR:-Infrastructure/artifacts/skill-graphs/drills/controls}"
report_json="${REPORT_JSON:-Infrastructure/artifacts/skill-graphs/pilot/rollback-drill-report.json}"
report_md="${REPORT_MD:-docs/skill-graphs/pilots/rollback-drill.md}"
profile_file="${PROFILE_FILE:-docs/skill-graphs/schemas/examples/ui-skills-profile.example.json}"
loop_script="Plugins/skill-factory/scripts/skill-builder/recursive_skill_loop.py"

mkdir -p "$out_root" "$controls_dir" "$(dirname "$report_json")" "$(dirname "$report_md")"

run_case() {
  local case_id="$1"
  local rollout_mode="$2"
  local kill_flag="$3"
  local rollback_flag="$4"

  rm -f "$controls_dir/kill-switch.txt" "$controls_dir/rollback-required.txt" "$controls_dir/rollout-mode.txt"
  printf '%s\n' "$rollout_mode" > "$controls_dir/rollout-mode.txt"
  if [[ "$kill_flag" == "1" ]]; then
    printf '1\n' > "$controls_dir/kill-switch.txt"
  fi
  if [[ "$rollback_flag" == "1" ]]; then
    printf '1\n' > "$controls_dir/rollback-required.txt"
  fi

  local objective="Rollback drill ${case_id}: rollout=${rollout_mode} kill=${kill_flag} rollback=${rollback_flag}"
  local output
  set +e
  output="$(
    python3 "$loop_script" \
      --profile-file "$profile_file" \
      --objective "$objective" \
      --out-root "$out_root" \
      --controls-dir "$controls_dir" \
      --kill-switch-file "$controls_dir/kill-switch.txt" \
      --rollback-required-file "$controls_dir/rollback-required.txt" \
      --uplift-gate-mode observe \
      --feedback-outcome partly \
      --feedback-note "rollback drill case ${case_id}" \
      2>&1
  )"
  local exit_code=$?
  set -e

  local run_dir
  run_dir="$(printf '%s\n' "$output" | python3 -c 'import re, sys; matches=[m.group(1) for line in sys.stdin for m in [re.search(r"\[recursive-loop\] out_dir=(.*)", line)] if m]; print(matches[-1] if matches else "")')"
  if [[ -z "$run_dir" ]]; then
    run_dir=""
  fi
  local run_json blocker_json blocker_code terminal_status stop_reason
  run_json="${run_dir:+${run_dir}/run.json}"
  blocker_json="${run_dir:+${run_dir}/run_blocker.json}"
  blocker_code="none"
  terminal_status="unknown"
  stop_reason="unknown"
  if [[ -f "$run_json" ]]; then
    terminal_status="$(python3 - <<'PY' "$run_json"
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
print(obj.get("terminal_status", "unknown"))
PY
)"
    stop_reason="$(python3 - <<'PY' "$run_json"
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
print(obj.get("stop_reason", "unknown"))
PY
)"
  fi
  if [[ -f "$blocker_json" ]]; then
    blocker_code="$(python3 - <<'PY' "$blocker_json"
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
print(obj.get("code", "none"))
PY
)"
  fi

  python3 - <<'PY' "$report_json" "$case_id" "$rollout_mode" "$kill_flag" "$rollback_flag" "$exit_code" "$run_dir" "$terminal_status" "$stop_reason" "$blocker_code"
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
row = {
    "case_id": sys.argv[2],
    "rollout_mode": sys.argv[3],
    "kill_switch": sys.argv[4] == "1",
    "rollback_required": sys.argv[5] == "1",
    "exit_code": int(sys.argv[6]),
    "run_dir": sys.argv[7],
    "terminal_status": sys.argv[8],
    "stop_reason": sys.argv[9],
    "blocker_code": sys.argv[10],
}

if path.exists():
    report = json.loads(path.read_text(encoding="utf-8"))
else:
    report = {"schema_version": "1.0", "generated_at": "", "cases": []}
report["cases"].append(row)
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
}

python3 - <<'PY' "$report_json"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(
    json.dumps(
        {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "cases": [],
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY

run_case "baseline_active" "active" "0" "0"
run_case "kill_switch" "active" "1" "0"
run_case "rollback_required" "active" "0" "1"
run_case "rollout_off" "off" "0" "0"

python3 - <<'PY' "$report_json" "$report_md"
import json, sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
lines = [
    "# Rollback Drill Report",
    "",
    f"- Generated at: `{report.get('generated_at', '')}`",
    "",
    "| Case | Rollout | Kill | Rollback | Exit | Status | Stop reason | Blocker |",
    "|---|---|:---:|:---:|---:|---|---|---|",
]
for row in report.get("cases", []):
    lines.append(
        f"| {row['case_id']} | {row['rollout_mode']} | "
        f"{'✅' if row['kill_switch'] else '❌'} | {'✅' if row['rollback_required'] else '❌'} | "
        f"{row['exit_code']} | {row['terminal_status']} | {row['stop_reason']} | {row['blocker_code']} |"
    )
lines.append("")
lines.append("Expected blockers:")
lines.append("- `kill_switch` -> `kill_switch_activated`")
lines.append("- `rollback_required` -> `run_rollback_required`")
lines.append("- `rollout_off` -> `run_rollforward_blocked`")
Path(sys.argv[2]).write_text("\n".join(lines) + "\n", encoding="utf-8")

# Validate observed blockers against expectations
expected_blockers = set()
observed_blockers = set()
for row in report.get("cases", []):
    case = row["case_id"]
    blocker = row["blocker_code"]
    if blocker != "none":
        observed_blockers.add((case, blocker))
    # Build expected set based on control inputs
    if row.get("kill_switch"):
        expected_blockers.add((case, "kill_switch_activated"))
    elif row.get("rollback_required"):
        expected_blockers.add((case, "run_rollback_required"))
    elif row.get("rollout_mode") == "off":
        expected_blockers.add((case, "run_rollforward_blocked"))

if observed_blockers != expected_blockers:
    print("Blocker mismatch detected:", file=sys.stderr)
    print(f"  Expected: {expected_blockers}", file=sys.stderr)
    print(f"  Observed: {observed_blockers}", file=sys.stderr)
    sys.exit(1)
PY

echo "[rollback-drill] report_json=$report_json"
echo "[rollback-drill] report_md=$report_md"
