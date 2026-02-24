#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

changed_only=0
base_sha=""
head_sha="HEAD"
report_json="artifacts/skill-graphs/pilot/promotion-validation-report.json"

usage() {
  cat <<'USAGE'
Usage: scripts/validate_recursive_promotions.sh [options]

Options:
  --changed-only         Validate only changed promotion_decision.json files in git diff
  --base-sha SHA         Base SHA for changed-only mode
  --head-sha SHA         Head SHA for changed-only mode (default: HEAD)
  --report-json PATH     Output JSON report path
USAGE
}

while (($# > 0)); do
  case "$1" in
    --changed-only)
      changed_only=1
      shift
      ;;
    --base-sha)
      base_sha="$2"
      shift 2
      ;;
    --head-sha)
      head_sha="$2"
      shift 2
      ;;
    --report-json)
      report_json="$2"
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

validator="utilities/skill-creator/scripts/validate_recursive_promotion.py"
if [[ ! -f "$validator" ]]; then
  echo "Missing validator: $validator" >&2
  exit 2
fi

promotion_files=()

if [[ "$changed_only" -eq 1 ]]; then
  if [[ -z "$base_sha" ]]; then
    echo "--changed-only requires --base-sha" >&2
    exit 2
  fi

  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ "$file" == *"/promotion_decision.json" ]] || continue
    if [[ -f "$file" ]]; then
      promotion_files+=("$file")
    fi
  done < <(git diff --name-only "$base_sha" "$head_sha")
else
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    promotion_files+=("$file")
  done < <(python3 - <<'PY'
from pathlib import Path
for p in sorted(Path("artifacts/skill-graphs/runs").glob("run_*/promotion_decision.json")):
    print(p.as_posix())
PY
)
fi

if [[ ${#promotion_files[@]} -eq 0 ]]; then
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

status=0
results_jsonl="$(mktemp)"
trap 'rm -f "$results_jsonl"' EXIT

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

python3 - <<'PY'
import json
from pathlib import Path

jsonl_path = Path("artifacts/skill-graphs/lessons/canonical-lessons.jsonl")
index_path = Path("artifacts/skill-graphs/lessons/canonical-lesson-index.json")
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
