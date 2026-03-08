#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

runs_per_profile=2
window_days=7
out_root="artifacts/skill-graphs/runs"
profiles_file="docs/skill-graphs/schemas/examples/pilot-profiles.json"

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    exit 2
  fi
}

while (($# > 0)); do
  case "$1" in
    --runs-per-profile)
      require_option_value "$1" "${2:-}"
      runs_per_profile="$2"
      shift 2
      ;;
    --window-days)
      require_option_value "$1" "${2:-}"
      window_days="$2"
      shift 2
      ;;
    --out-root)
      require_option_value "$1" "${2:-}"
      out_root="$2"
      shift 2
      ;;
    --profiles-file)
      require_option_value "$1" "${2:-}"
      profiles_file="$2"
      shift 2
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: scripts/run_recursive_skill_shadow_cycle.sh [options]

Options:
  --runs-per-profile N   Number of loop runs per pilot profile (default: 2)
  --window-days N        Window size for report aggregation (default: 7)
  --out-root PATH        Output root for run artifacts (default: artifacts/skill-graphs/runs)
  --profiles-file PATH   JSON array of pilot profile ids (default: docs/skill-graphs/schemas/examples/pilot-profiles.json)
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "$profiles_file" ]]; then
  echo "[shadow-cycle] missing profiles file: $profiles_file" >&2
  exit 2
fi

profiles=()
while IFS= read -r profile; do
  [[ -z "$profile" ]] && continue
  profiles+=("$profile")
done < <(python3 - "$profiles_file" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
if not isinstance(data, list) or not data:
    raise SystemExit("profiles file must be a non-empty JSON array")
for item in data:
    value = str(item).strip()
    if value:
        print(value)
PY
)

if [[ ${#profiles[@]} -eq 0 ]]; then
  echo "[shadow-cycle] no profiles found in $profiles_file" >&2
  exit 2
fi

example_profile="docs/skill-graphs/schemas/examples/ui-skills-profile.example.json"
loop_script="utilities/skill-builder/scripts/recursive_skill_loop.py"
report_script="utilities/skill-builder/scripts/build_recursive_skill_shadow_report.py"
shadow_md="docs/skill-graphs/pilots/ui-skills-shadow-results.md"
readout_md="docs/skill-graphs/pilots/ui-skills-pilot-readout.md"
dashboard_json="artifacts/skill-graphs/pilot/shadow-dashboard.json"
daily_health_md="docs/skill-graphs/telemetry/daily-skill-health.md"
failure_patterns_jsonl="artifacts/skill-graphs/telemetry/failure-pattern-candidates.jsonl"
promotion_queue_md="artifacts/skill-graphs/telemetry/promotion-queue.md"

echo "[shadow-cycle] runs_per_profile=${runs_per_profile}"
echo "[shadow-cycle] window_days=${window_days}"
echo "[shadow-cycle] profiles_file=${profiles_file}"

require_file_nonempty() {
  local path="$1"
  local label="$2"
  if [[ ! -s "$path" ]]; then
    echo "[shadow-cycle] required telemetry output missing or empty: ${label} (${path})" >&2
    return 1
  fi
  return 0
}

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

for profile in "${profiles[@]}"; do
  for n in $(seq 1 "$runs_per_profile"); do
    profile_file="$tmp_dir/${profile}-${n}.json"
    python3 - "$example_profile" "$profile_file" "$profile" <<'PY'
import json
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
profile = sys.argv[3]

obj = json.loads(src.read_text(encoding="utf-8"))
obj["profile_id"] = profile
obj["scope_skill"] = profile
obj["scope_profile"] = "ui"
out.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
PY

    objective="Shadow evaluation run ${n} for ${profile}: improve instruction quality with safe, testable outputs."

    echo "[shadow-cycle] run profile=${profile} n=${n}"
    if ! python3 "$loop_script" \
      --profile-file "$profile_file" \
      --objective "$objective" \
      --out-root "$out_root" \
      --run-owner "shadow-cycle"; then
      echo "[shadow-cycle] warning: loop exited non-zero (expected in bounded shadow scenarios)" >&2
    fi
  done
done

python3 "$report_script" \
  --runs-root "$out_root" \
  --window-days "$window_days" \
  --pilot-profiles-file "$profiles_file" \
  --shadow-md "$shadow_md" \
  --readout-md "$readout_md" \
  --out-json "$dashboard_json" \
  --daily-health-md "$daily_health_md" \
  --failure-patterns-jsonl "$failure_patterns_jsonl" \
  --promotion-queue-md "$promotion_queue_md"

for output in "$shadow_md" "$readout_md" "$dashboard_json" "$daily_health_md" "$failure_patterns_jsonl" "$promotion_queue_md"; do
  require_file_nonempty "$output" "$(basename "$output")"
done

if ! python3 - "$failure_patterns_jsonl" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    line = line.strip()
    if not line:
        continue
    try:
        json.loads(line)
    except Exception as exc:
        raise SystemExit(f"failure-pattern row {line_no} invalid JSON: {exc}")
PY
then
  echo "[shadow-cycle] failure-pattern output is not valid jsonl" >&2
  exit 2
fi

if ! python3 - "$dashboard_json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
obj = json.loads(path.read_text(encoding="utf-8"))
if not isinstance(obj, dict):
    raise SystemExit("dashboard JSON is not an object")
for key in ("artifact_outputs", "current", "decision"):
    if key not in obj:
        raise SystemExit(f"dashboard JSON missing key: {key}")
PY
then
  echo "[shadow-cycle] dashboard output is invalid JSON" >&2
  exit 2
fi

echo "[shadow-cycle] complete"
