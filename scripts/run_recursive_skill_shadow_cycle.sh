#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

runs_per_profile=2
window_days=7
out_root="artifacts/skill-graphs/runs"

while (($# > 0)); do
  case "$1" in
    --runs-per-profile)
      runs_per_profile="$2"
      shift 2
      ;;
    --window-days)
      window_days="$2"
      shift 2
      ;;
    --out-root)
      out_root="$2"
      shift 2
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: scripts/run_recursive_skill_shadow_cycle.sh [options]

Options:
  --runs-per-profile N   Number of loop runs per pilot profile (default: 2)
  --window-days N        Window size for report aggregation (default: 7)
  --out-root PATH        Output root for run artifacts (default: artifacts/skill-graphs/runs)
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

profiles=(
  "ui-ux-creative-coding"
  "interface-craft"
  "frontend-ui-design"
  "react-ui-patterns"
)

example_profile="docs/skill-graphs/schemas/examples/ui-skills-profile.example.json"
loop_script="utilities/skill-creator/scripts/recursive_skill_loop.py"
report_script="utilities/skill-creator/scripts/build_recursive_skill_shadow_report.py"

echo "[shadow-cycle] runs_per_profile=${runs_per_profile}"
echo "[shadow-cycle] window_days=${window_days}"

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
  --shadow-md "docs/skill-graphs/pilots/ui-skills-shadow-results.md" \
  --readout-md "docs/skill-graphs/pilots/ui-skills-pilot-readout.md" \
  --out-json "artifacts/skill-graphs/pilot/shadow-dashboard.json"

echo "[shadow-cycle] complete"
