#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

run_id=""
run_dir=""
lesson_id=""
reviewers=""
expected_version=""
lesson_file=""
decision="approved"
note="Human gate review completed."
skip_lesson_scan=0

usage() {
  cat <<'USAGE'
Usage: scripts/human_promote_recursive_run.sh [options]

Required:
  --run-id ID                 Run id under artifacts/skill-graphs/runs (or use --run-dir)
  --lesson-id ID              Canonical lesson id
  --reviewer ID[,ID2...]      Reviewer id(s)
  --expected-version VERSION  Optimistic version token for promotion write (required for approved)

Optional:
  --run-dir PATH              Explicit run directory (overrides --run-id)
  --lesson-file PATH          Lesson content file for secret/PII scan (required for approved decisions)
  --decision STATE            approved|rejected|candidate (default: approved)
  --note TEXT                 Gate note/comment
  --skip-lesson-scan          Skip lesson content scan (only allowed for non-approved decisions)
USAGE
}

while (($# > 0)); do
  case "$1" in
    --run-id)
      run_id="$2"
      shift 2
      ;;
    --run-dir)
      run_dir="$2"
      shift 2
      ;;
    --lesson-id)
      lesson_id="$2"
      shift 2
      ;;
    --reviewer)
      reviewers="$2"
      shift 2
      ;;
    --expected-version)
      expected_version="$2"
      shift 2
      ;;
    --lesson-file)
      lesson_file="$2"
      shift 2
      ;;
    --decision)
      decision="$2"
      shift 2
      ;;
    --note)
      note="$2"
      shift 2
      ;;
    --skip-lesson-scan)
      skip_lesson_scan=1
      shift
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

if [[ -z "$run_dir" ]]; then
  if [[ -z "$run_id" ]]; then
    echo "Either --run-id or --run-dir is required" >&2
    exit 2
  fi
  run_dir="artifacts/skill-graphs/runs/${run_id}"
fi

if [[ -z "$lesson_id" ]]; then
  echo "--lesson-id is required" >&2
  exit 2
fi
if [[ -z "$reviewers" ]]; then
  echo "--reviewer is required" >&2
  exit 2
fi
if [[ -z "$expected_version" && "$decision" == "approved" ]]; then
  echo "--expected-version is required for approved decisions" >&2
  exit 2
fi
if [[ "$decision" == "approved" && "$skip_lesson_scan" -eq 1 ]]; then
  echo "--skip-lesson-scan is not allowed for approved decisions" >&2
  exit 2
fi
if [[ "$decision" == "approved" && -z "$lesson_file" ]]; then
  echo "--lesson-file is required for approved decisions" >&2
  exit 2
fi

run_dir="$(cd "$run_dir" 2>/dev/null && pwd || true)"
if [[ -z "$run_dir" ]]; then
  echo "Run directory not found" >&2
  exit 2
fi

decision_path="$run_dir/promotion_decision.json"
run_json_path="$run_dir/run.json"
template_path="$run_dir/promotion_decision.template.json"
seed_path="$decision_path"
if [[ ! -f "$seed_path" ]]; then
  seed_path="$template_path"
fi

if [[ ! -f "$seed_path" ]]; then
  echo "Missing seed decision file: $decision_path (or template $template_path)" >&2
  exit 2
fi
if [[ ! -f "$run_json_path" ]]; then
  echo "Missing run.json: $run_json_path" >&2
  exit 2
fi

python3 - "$repo_root" "$seed_path" "$decision_path" "$lesson_id" "$reviewers" "$expected_version" "$decision" "$note" "$lesson_file" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
seed_file = Path(sys.argv[2])
out = Path(sys.argv[3])
lesson_id = sys.argv[4]
reviewers = [r.strip() for r in sys.argv[5].split(',') if r.strip()]
expected_version = sys.argv[6]
decision = sys.argv[7].strip().lower()
note = sys.argv[8]
lesson_file_raw = sys.argv[9].strip()

obj = json.loads(seed_file.read_text(encoding='utf-8'))
obj['decision'] = decision
obj['lesson_id'] = lesson_id
obj['reviewer_ids'] = reviewers
obj['expected_version'] = expected_version
obj['updated_at'] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
obj['review_note'] = note

if lesson_file_raw:
    lesson_path = Path(lesson_file_raw).expanduser().resolve()
    if lesson_path.exists():
        try:
            rel = lesson_path.relative_to(repo_root)
            obj['lesson_source_path'] = rel.as_posix()
        except Exception:
            obj['lesson_source_path'] = str(lesson_path)

        digest = hashlib.sha256(lesson_path.read_bytes()).hexdigest()
        obj['lesson_content_sha256'] = digest


gate = obj.setdefault('gate_decision', {})
if decision == 'approved':
    gate['runtime_gates_passed'] = True
    gate['provenance_complete'] = True
    gate['security_checklist_passed'] = True
else:
    gate.setdefault('runtime_gates_passed', False)
    gate.setdefault('provenance_complete', False)
    gate.setdefault('security_checklist_passed', False)

gate['notes'] = note

out.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY

validator="utilities/skill-creator/scripts/validate_recursive_promotion.py"
validator_cmd=(python3 "$validator" --run-dir "$run_dir" --decision-file "$decision_path")

if [[ -n "$lesson_file" ]]; then
  validator_cmd+=(--lesson-file "$lesson_file")
elif [[ "$skip_lesson_scan" -eq 1 ]]; then
  validator_cmd+=(--skip-lesson-content-scan)
fi

"${validator_cmd[@]}"

if [[ "$decision" == "approved" ]]; then
  python3 - "$run_json_path" "$run_dir/debug/events.jsonl" "$reviewers" "$lesson_id" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run_path = Path(sys.argv[1])
events_path = Path(sys.argv[2])
reviewers = [r.strip() for r in sys.argv[3].split(',') if r.strip()]
lesson_id = sys.argv[4].strip()
actor = reviewers[0] if reviewers else 'human-reviewer'

run = json.loads(run_path.read_text(encoding='utf-8'))
events_path.parent.mkdir(parents=True, exist_ok=True)

existing = []
if events_path.exists():
    for line in events_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            existing.append(json.loads(line))
        except Exception:
            continue

for event in existing:
    if (
        event.get("event_type") == "promotion_approved"
        and event.get("run_id") == run.get("run_id")
        and event.get("lesson_id") == lesson_id
    ):
        print("[promotion-gate] promotion_approved already present; skipping duplicate append")
        raise SystemExit(0)

ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
seed = f"{run.get('run_id')}::promotion_approved::{actor}::{lesson_id}".encode('utf-8')
event_id = hashlib.sha256(seed).hexdigest()[:16]

event = {
    'schema_version': '1.0',
    'event_id': event_id,
    'ts': ts,
    'run_id': run.get('run_id'),
    'lesson_id': lesson_id,
    'skill_name': run.get('scope_skill'),
    'task_profile': run.get('profile_id'),
    'event_type': 'promotion_approved',
    'severity': 'info',
    'terminal_status': run.get('terminal_status'),
    'stop_reason': run.get('stop_reason'),
    'actor_id': actor,
    'evaluator_version': run.get('versions', {}).get('evaluator_version'),
    'rubric_version': run.get('versions', {}).get('rubric_version'),
    'prompt_hash': run.get('prompt_hash'),
}

with events_path.open('a', encoding='utf-8') as f:
    f.write(json.dumps(event, sort_keys=True))
    f.write('\n')
PY
fi

echo "[promotion-gate] decision written: $decision_path"
if [[ "$decision" == "approved" ]]; then
  echo "[promotion-gate] promotion event log path: $run_dir/debug/events.jsonl"
fi

echo "[promotion-gate] validation passed"
