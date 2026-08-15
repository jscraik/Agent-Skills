#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null || { cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd; })"
cd "$repo_root"

runs_per_profile=2
window_days=7
out_root=".tmp/agent-skills-artifacts/skill-graphs/runs"
profiles_file="Docs/skill-graphs/schemas/examples/pilot-profiles.json"

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
Usage: Infrastructure/scripts/lifecycle-and-sync/run_recursive_skill_shadow_cycle.sh [options]

Options:
  --runs-per-profile N   Number of loop runs per pilot profile (default: 2)
  --window-days N        Window size for report aggregation (default: 7)
  --out-root PATH        Output root for run artifacts (default: .tmp/agent-skills-artifacts/skill-graphs/runs)
  --profiles-file PATH   JSON array of pilot profile ids or profile objects (default: Docs/skill-graphs/schemas/examples/pilot-profiles.json)
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
profile_files=()
profile_objectives=()
while IFS=$'\t' read -r profile profile_file profile_objective; do
  [[ -z "$profile" ]] && continue
  profiles+=("$profile")
  profile_files+=("$profile_file")
  profile_objectives+=("$profile_objective")
done < <(python3 - "$profiles_file" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
if not isinstance(data, list) or not data:
    raise SystemExit("profiles file must be a non-empty JSON array")


def sanitize(value: str) -> str:
    return value.replace("\t", " ").replace("\n", " ").strip()


def emit(profile_id: str, profile_file: str = "", objective: str = "") -> None:
    print("\t".join((sanitize(profile_id), sanitize(profile_file), sanitize(objective))))


for item in data:
    if isinstance(item, str):
        value = item.strip()
        if value:
            emit(value)
        continue
    if not isinstance(item, dict):
        raise SystemExit("profile entries must be strings or objects")

    profile_file = str(item.get("profile_file") or item.get("profile_path") or "").strip()
    objective = str(item.get("objective") or "").strip()
    profile_id = str(item.get("profile_id") or "").strip()

    if profile_file:
        resolved = Path(profile_file)
        if not resolved.is_absolute():
            manifest_relative = (path.parent / resolved).resolve()
            repo_relative = (Path.cwd() / resolved).resolve()
            if manifest_relative.is_file():
                resolved = manifest_relative
            else:
                resolved = repo_relative
        if not resolved.is_file():
            raise SystemExit(f"profile file does not exist: {profile_file}")
        profile_file = str(resolved)
        if not profile_id:
            profile_obj = json.loads(resolved.read_text(encoding="utf-8"))
            profile_id = str(profile_obj.get("profile_id") or "").strip()

    if not profile_id:
        raise SystemExit("profile object entries require profile_id or profile_file")

    emit(profile_id, profile_file, objective)
PY
)

if [[ ${#profiles[@]} -eq 0 ]]; then
  echo "[shadow-cycle] no profiles found in $profiles_file" >&2
  exit 2
fi

example_profile="Docs/skill-graphs/schemas/examples/ui-skills-profile.example.json"
loop_script="Plugins/skill-factory/scripts/skill-builder/recursive_skill_loop.py"
report_script="Plugins/skill-factory/scripts/skill-builder/build_recursive_skill_shadow_report.py"
shadow_md="Docs/skill-graphs/pilots/ui-skills-shadow-results.md"
readout_md="Docs/skill-graphs/pilots/ui-skills-pilot-readout.md"
dashboard_json=".harness/evidence/skill-graphs/pilot/shadow-dashboard.json"
baseline_snapshot_json=".harness/evidence/skill-graphs/pilot/shadow-baseline.json"
daily_health_md=".harness/evidence/skill-graphs/telemetry/daily-skill-health.md"
failure_patterns_jsonl=".harness/evidence/skill-graphs/telemetry/failure-pattern-candidates.jsonl"
promotion_queue_md=".harness/evidence/skill-graphs/telemetry/promotion-queue.md"

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

for idx in "${!profiles[@]}"; do
  profile="${profiles[$idx]}"
  source_profile_file="${profile_files[$idx]}"
  profile_objective="${profile_objectives[$idx]}"

  for n in $(seq 1 "$runs_per_profile"); do
    profile_file="$source_profile_file"
    if [[ -z "$profile_file" ]]; then
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
    else
      if [[ "$profile_file" != /* ]]; then
        profile_file="$repo_root/$profile_file"
      fi
      rendered_profile_file="$tmp_dir/${profile}-${n}.json"
      python3 - "$profile_file" "$rendered_profile_file" "$profile" <<'PY'
import json
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
profile = sys.argv[3]

obj = json.loads(src.read_text(encoding="utf-8"))
obj["profile_id"] = profile
out.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
PY
      profile_file="$rendered_profile_file"
    fi

    objective="$profile_objective"
    if [[ -z "$objective" ]]; then
      objective="Shadow evaluation run ${n} for ${profile}: improve instruction quality with safe, testable outputs."
    else
      objective="${objective//\{n\}/$n}"
      objective="${objective//\{profile_id\}/$profile}"
    fi

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
  --baseline-snapshot-json "$baseline_snapshot_json" \
  --refresh-baseline-snapshot \
  --daily-health-md "$daily_health_md" \
  --failure-patterns-jsonl "$failure_patterns_jsonl" \
  --promotion-queue-md "$promotion_queue_md"

for output in "$shadow_md" "$readout_md" "$dashboard_json" "$baseline_snapshot_json" "$daily_health_md" "$failure_patterns_jsonl" "$promotion_queue_md"; do
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
