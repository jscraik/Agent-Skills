#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if repo_root="$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd "$script_dir/../../.." && pwd -P)"
fi
cd "$repo_root"

changed_only=0
base_sha=""
head_sha="HEAD"
strict_runs=0
report_json=".harness/evidence/skill-graphs/pilot/promotion-validation-report.json"
runs_root=".tmp/agent-skills-artifacts/skill-graphs/runs"
parity_manifest=".harness/evidence/skill-graphs/pilot/artifact-parity-manifest.json"
status=0
changed_run_count=0

changed_run_dirs=()

refresh_global_parity_manifest() {
  mkdir -p "$(dirname "$parity_manifest")"
  # Keep canonical manifest repo-wide even when strict checks are changed-only.
  if ! python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py \
    --manifest "$parity_manifest" \
    --runs-root "$runs_root" \
    > /dev/null; then
    :
  fi
}

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 2
  fi
}

usage() {
  cat <<'USAGE'
Usage: Infrastructure/scripts/lifecycle-and-sync/validate_recursive_promotions.sh [options]

Options:
  --changed-only         Validate only changed promotion_decision.json files in git diff
  --base-sha SHA         Base SHA for changed-only mode
  --head-sha SHA         Head SHA for changed-only mode (default: HEAD)
  --runs-root PATH       Runs root for strict run-dir parity checks (default: .tmp/agent-skills-artifacts/skill-graphs/runs)
  --report-json PATH     Output JSON report path
  --strict-runs          Enable strict run-parity checks for changed run directories
  --parity-manifest PATH Path for artifact-parity manifest output
USAGE
}

collect_changed_run_dirs() {
  local file
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ "$file" == "$runs_root"/* ]] || continue
  local rel="${file#"${runs_root}"/}"
    local run_dir_name="${rel%%/*}"
    [[ "$run_dir_name" == run_* ]] || continue
    changed_run_dirs+=("$runs_root/$run_dir_name")
    changed_run_count=$((changed_run_count + 1))
  done < <(git diff --name-only "$base_sha" "$head_sha")
}

collect_changed_decision_files() {
  local file
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ "$file" == "$runs_root"/run_*/promotion_decision.json ]] || continue
    if [[ -f "$file" ]]; then
      promotion_files+=("$file")
    fi
  done < <(git diff --name-only "$base_sha" "$head_sha")
}

while (($# > 0)); do
  case "$1" in
    --changed-only)
      changed_only=1
      shift
      ;;
    --base-sha)
      require_option_value "$1" "${2:-}"
      base_sha="$2"
      shift 2
      ;;
    --head-sha)
      require_option_value "$1" "${2:-}"
      head_sha="$2"
      shift 2
      ;;
    --report-json)
      require_option_value "$1" "${2:-}"
      report_json="$2"
      shift 2
      ;;
    --runs-root)
      require_option_value "$1" "${2:-}"
      runs_root="$2"
      shift 2
      ;;
    --strict-runs)
      strict_runs=1
      shift
      ;;
    --parity-manifest)
      require_option_value "$1" "${2:-}"
      parity_manifest="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

promotion_files=()

if [[ "$changed_only" -eq 1 ]]; then
  if [[ -z "$base_sha" ]]; then
    echo "--changed-only requires --base-sha" >&2
    exit 2
  fi

  collect_changed_run_dirs
  collect_changed_decision_files
else
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    promotion_files+=("$file")
  done < <(python3 - "$runs_root" <<'PY'
import sys
from pathlib import Path

runs_root = Path(sys.argv[1])
for p in sorted(runs_root.glob("run_*/promotion_decision.json")):
    print(p.as_posix())
PY
)
fi

if [[ ${#promotion_files[@]} -eq 0 ]]; then
  if [[ "$strict_runs" -ne 1 ]]; then
    echo "[promotion-ci] no promotion_decision.json files to validate"
    mkdir -p "$(dirname "$report_json")"
    python3 - <<'PY' "$report_json"
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
path.write_text(json.dumps({
    "status": "ok",
    "validated": 0,
    "failed": 0,
    "results": []
}, indent=2) + "\n", encoding="utf-8")
PY
  exit 0
  fi

  if [[ "$changed_only" -eq 1 ]]; then
    if [[ "$changed_run_count" -eq 0 ]]; then
      echo "[promotion-ci] strict run-parity validation skipped (no changed run directories)"
      mkdir -p "$(dirname "$report_json")"
      python3 - <<'PY' "$report_json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(
    json.dumps(
        {
            "status": "ok",
            "validated": 0,
            "failed": 0,
            "results": [],
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY
      mkdir -p "$(dirname "$parity_manifest")"
      refresh_global_parity_manifest
      exit 0
    fi
  fi

  mkdir -p "$(dirname "$parity_manifest")"
  strict_manifest="$parity_manifest"
  if [[ "$changed_only" -eq 1 && "$changed_run_count" -gt 0 ]]; then
    strict_manifest="${parity_manifest%.json}.changed-only.json"
    if [[ "$strict_manifest" == "$parity_manifest" ]]; then
      strict_manifest="${parity_manifest}.changed-only"
    fi
  fi
  strict_args=("--strict" "--run-state-check" "--manifest" "$strict_manifest" "--runs-root" "$runs_root")
  if [[ "$changed_only" -eq 1 && "$changed_run_count" -gt 0 ]]; then
    for run_dir in "${changed_run_dirs[@]}"; do
      strict_args+=("--run-dir" "$run_dir")
    done
  fi
  if ! python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py "${strict_args[@]}"; then
    echo "[promotion-ci] strict run-parity validation failed" >&2
    status=1
  fi
  refresh_global_parity_manifest
  if [[ "$status" -ne 0 ]]; then
    exit 2
  fi
  exit 0
fi
results_jsonl="$(mktemp)"
trap 'rm -f "$results_jsonl"' EXIT

# Resolve validator only when we actually have promotion files to validate
validator_candidates=(
  "Plugins/skill-factory/scripts/skill-builder/validate_recursive_promotion.py"
)
validator=""
for candidate in "${validator_candidates[@]}"; do
  if [[ -f "$candidate" ]]; then
    validator="$candidate"
    break
  fi
done
if [[ -z "$validator" ]]; then
  echo "Missing validator: tried ${validator_candidates[*]}" >&2
  exit 2
fi

for file in "${promotion_files[@]}"; do
  run_dir="$(dirname "$file")"
  echo "[promotion-ci] validate $file"
  if ! python3 "$validator" --run-dir "$run_dir" --decision-file "$file" | tee -a "$results_jsonl"; then
    status=1
  fi
done

mkdir -p "$(dirname "$report_json")"
python3 - <<'PY' "$results_jsonl" "$report_json"
import json
import sys
from pathlib import Path

in_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
rows = []
for line in in_path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except Exception:
        rows.append({"status": "error", "raw": line})

failed = [r for r in rows if r.get("status") != "ok"]
report = {
    "status": "ok" if not failed else "fail",
    "validated": len(rows),
    "failed": len(failed),
    "results": rows,
}
out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY

if [[ "$strict_runs" -eq 1 ]]; then
  mkdir -p "$(dirname "$parity_manifest")"
  strict_manifest="$parity_manifest"
  if [[ "$changed_only" -eq 1 && "$changed_run_count" -gt 0 ]]; then
    strict_manifest="${parity_manifest%.json}.changed-only.json"
    if [[ "$strict_manifest" == "$parity_manifest" ]]; then
      strict_manifest="${parity_manifest}.changed-only"
    fi
  fi
  strict_args=("--strict" "--run-state-check" "--manifest" "$strict_manifest" "--runs-root" "$runs_root")
  if [[ "$changed_only" -eq 1 && "$changed_run_count" -gt 0 ]]; then
    for run_dir in "${changed_run_dirs[@]}"; do
      strict_args+=("--run-dir" "$run_dir")
    done
  fi
  if ! python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py "${strict_args[@]}"; then
    echo "[promotion-ci] strict run-parity validation failed" >&2
    status=1
  fi
  refresh_global_parity_manifest
fi

python3 - <<'PY'
import json
from pathlib import Path

jsonl_path = Path(".harness/evidence/skill-graphs/lessons/canonical-lessons.jsonl")
index_path = Path(".harness/evidence/skill-graphs/lessons/canonical-lesson-index.json")
if jsonl_path.exists():
    for i, line in enumerate(jsonl_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "lesson_id" not in obj or "status" not in obj:
            raise SystemExit(f"invalid canonical-lessons.jsonl row at line {i}")
if index_path.exists():
    obj = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or "scopes" not in obj:
        raise SystemExit("invalid canonical-lesson-index.json structure")
PY

trap - EXIT
rm -f "$results_jsonl"

if [[ "$status" -ne 0 ]]; then
  echo "[promotion-ci] validation failed" >&2
  exit 2
fi

echo "[promotion-ci] validation passed (${#promotion_files[@]} file(s))"
