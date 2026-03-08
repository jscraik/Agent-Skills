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
policy_file="docs/skill-graphs/governance/recursive-loop-approvers.yaml"
policy_sig_file="docs/skill-graphs/governance/recursive-loop-approvers.sig"
canonical_policy_file="docs/skill-graphs/governance/recursive-loop-approvers.yaml"
canonical_policy_sig_file="docs/skill-graphs/governance/recursive-loop-approvers.sig"

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 2
  fi
}

# M-01: run_id must be a safe identifier — no path separators, dotdot, or
# shell-special characters that could target unexpected artifact locations.
validate_run_id() {
  local id="$1"
  if [[ ! "$id" =~ ^[A-Za-z0-9_][A-Za-z0-9_.\-]*$ ]]; then
    echo "[promotion-gate] invalid --run-id '${id}': must match [A-Za-z0-9_][A-Za-z0-9_.\-]* (no path separators or special characters)" >&2
    exit 2
  fi
  if [[ "$id" == *".."* || "$id" == *"/"* || "$id" == *"\\"* ]]; then
    echo "[promotion-gate] invalid --run-id '${id}': path traversal sequences are not permitted" >&2
    exit 2
  fi
}

# H-02: resolved run directory must stay within the canonical runs subtree.
# Prevents symlink attacks and user-controlled --run-dir values from escaping.
confine_run_dir() {
  local resolved_dir="$1"
  local canonical_runs_dir
  canonical_runs_dir="$(cd "${repo_root}/artifacts/skill-graphs/runs" 2>/dev/null && pwd || true)"
  if [[ -z "$canonical_runs_dir" ]]; then
    # Runs directory doesn't exist yet — verify at least repo_root is the prefix.
    canonical_runs_dir="${repo_root}/artifacts/skill-graphs/runs"
  fi
  if [[ "$resolved_dir" != "${canonical_runs_dir}"/* && "$resolved_dir" != "$canonical_runs_dir" ]]; then
    echo "[promotion-gate] run directory '${resolved_dir}' is outside the canonical runs subtree '${canonical_runs_dir}'" >&2
    echo "[promotion-gate] set RECURSIVE_PROMOTION_ALLOW_RUN_DIR_OVERRIDE=1 only in tests" >&2
    exit 2
  fi
}

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
  --policy-file PATH          Reviewer policy file (default: docs/skill-graphs/governance/recursive-loop-approvers.yaml)
  --policy-sig-file PATH      Policy signature file containing sha256(policy_file) (default: docs/skill-graphs/governance/recursive-loop-approvers.sig)
USAGE
}

while (($# > 0)); do
  case "$1" in
    --run-id)
      require_option_value "$1" "${2:-}"
      run_id="$2"
      shift 2
      ;;
    --run-dir)
      require_option_value "$1" "${2:-}"
      run_dir="$2"
      shift 2
      ;;
    --lesson-id)
      require_option_value "$1" "${2:-}"
      lesson_id="$2"
      shift 2
      ;;
    --reviewer)
      require_option_value "$1" "${2:-}"
      reviewers="$2"
      shift 2
      ;;
    --expected-version)
      require_option_value "$1" "${2:-}"
      expected_version="$2"
      shift 2
      ;;
    --lesson-file)
      require_option_value "$1" "${2:-}"
      lesson_file="$2"
      shift 2
      ;;
    --decision)
      require_option_value "$1" "${2:-}"
      decision="$2"
      shift 2
      ;;
    --note)
      require_option_value "$1" "${2:-}"
      note="$2"
      shift 2
      ;;
    --skip-lesson-scan)
      skip_lesson_scan=1
      shift
      ;;
    --policy-file)
      require_option_value "$1" "${2:-}"
      policy_file="$2"
      shift 2
      ;;
    --policy-sig-file)
      require_option_value "$1" "${2:-}"
      policy_sig_file="$2"
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

if [[ -z "$run_dir" ]]; then
  if [[ -z "$run_id" ]]; then
    echo "Either --run-id or --run-dir is required" >&2
    exit 2
  fi
  # M-01: validate run_id format before constructing any path from it.
  validate_run_id "$run_id"
  run_dir="artifacts/skill-graphs/runs/${run_id}"
fi

write_blocker_and_exit() {
  local code="$1"
  local message="$2"
  local now
  now="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local blocker_path="$run_dir/run_blocker.json"
  local events_path="$run_dir/events.jsonl"

  # M-03: run_blocker.json is write-once per run — the first blocking event is the
  # forensic truth. If one already exists, log the conflict and exit without overwriting.
  if [[ -f "$blocker_path" ]]; then
    echo "[promotion-gate] run_blocker.json already exists (write-once protection); new code='${code}' message='${message}'" >&2
    echo "[promotion-gate] existing blocker preserved at: $blocker_path" >&2
    exit 3
  fi

  python3 - "$run_json_path" "$blocker_path" "$events_path" "$code" "$message" "$reviewers" "$now" <<'PY'
import fcntl
import hashlib
import json
import sys
from pathlib import Path

run_path = Path(sys.argv[1])
blocker_path = Path(sys.argv[2])
events_path = Path(sys.argv[3])
code = sys.argv[4]
message = sys.argv[5]
reviewers = [r.strip() for r in sys.argv[6].split(",") if r.strip()]
ts = sys.argv[7]

run = json.loads(run_path.read_text(encoding="utf-8"))
actor = reviewers[0] if reviewers else "promotion-gate"
blocker = {
    "schema_version": "1.0",
    "run_id": run.get("run_id"),
    "code": code,
    "message": message,
    "remediation_owner": actor,
    "created_at": ts,
}
blocker_path.write_text(json.dumps(blocker, indent=2, sort_keys=True) + "\n", encoding="utf-8")
events_path.parent.mkdir(parents=True, exist_ok=True)
seed = f"{run.get('run_id')}::{code}::{ts}".encode("utf-8")
event = {
    "schema_version": "1.0",
    "event_id": hashlib.sha256(seed).hexdigest()[:16],
    "ts": ts,
    "run_id": run.get("run_id"),
    "skill_name": run.get("scope_skill"),
    "task_profile": run.get("profile_id"),
    "event_type": "run_blocked",
    "severity": "warn",
    "terminal_status": "failed",
    "stop_reason": "policy_failed",
    "blocker_code": code,
    "actor_id": actor,
    "evaluator_version": run.get("versions", {}).get("evaluator_version"),
    "rubric_version": run.get("versions", {}).get("rubric_version"),
    "prompt_hash": run.get("prompt_hash"),
}
with events_path.open("a+", encoding="utf-8") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    f.seek(0, 2)
    f.write(json.dumps(event, sort_keys=True) + "\n")
    f.flush()
    try:
        import os
        os.fsync(f.fileno())
    except Exception:
        pass
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
PY
  echo "[promotion-gate] blocked: $message" >&2
  exit 3
}

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
if [[ -n "$lesson_file" && ! -f "$lesson_file" ]]; then
  echo "--lesson-file does not exist: $lesson_file" >&2
  exit 2
fi

run_dir="$(cd "$run_dir" 2>/dev/null && pwd || true)"
if [[ -z "$run_dir" ]]; then
  echo "Run directory not found" >&2
  exit 2
fi

# H-02: confine resolved run directory to the canonical subtree, unless the
# test-only override env var is explicitly set.
allow_run_dir_override="${RECURSIVE_PROMOTION_ALLOW_RUN_DIR_OVERRIDE:-0}"
if [[ "$allow_run_dir_override" != "1" && "$allow_run_dir_override" != "true" && "$allow_run_dir_override" != "TRUE" ]]; then
  confine_run_dir "$run_dir"
fi

decision_path="$run_dir/promotion_decision.json"
decision_tmp="$(mktemp "${run_dir}/promotion_decision.XXXXXX.tmp")"
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

resolve_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
}

if [[ "$decision" == "approved" || "$decision" == "candidate" ]]; then
  allow_policy_override="${RECURSIVE_PROMOTION_ALLOW_POLICY_OVERRIDE:-0}"
  policy_file_resolved="$(resolve_path "$policy_file")"
  policy_sig_file_resolved="$(resolve_path "$policy_sig_file")"
  canonical_policy_file_resolved="$(resolve_path "$canonical_policy_file")"
  canonical_policy_sig_file_resolved="$(resolve_path "$canonical_policy_sig_file")"
  if [[ "$allow_policy_override" != "1" && "$allow_policy_override" != "true" && "$allow_policy_override" != "TRUE" ]]; then
    if [[ "$policy_file_resolved" != "$canonical_policy_file_resolved" ]]; then
      write_blocker_and_exit "run_rollforward_blocked" "non-canonical policy-file rejected (set RECURSIVE_PROMOTION_ALLOW_POLICY_OVERRIDE=1 to override)"
    fi
    if [[ "$policy_sig_file_resolved" != "$canonical_policy_sig_file_resolved" ]]; then
      write_blocker_and_exit "run_rollforward_blocked" "non-canonical policy-sig-file rejected (set RECURSIVE_PROMOTION_ALLOW_POLICY_OVERRIDE=1 to override)"
    fi
  fi
  if [[ ! -f "$policy_file" ]]; then
    write_blocker_and_exit "run_rollforward_blocked" "missing reviewer policy file: $policy_file"
  fi
  if [[ ! -f "$policy_sig_file" ]]; then
    write_blocker_and_exit "run_rollforward_blocked" "missing reviewer policy signature file: $policy_sig_file"
  fi
  if ! python3 - "$policy_file" "$policy_sig_file" "$reviewers" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

policy_path = Path(sys.argv[1])
sig_path = Path(sys.argv[2])
reviewers = [r.strip() for r in sys.argv[3].split(",") if r.strip()]
policy_raw = policy_path.read_text(encoding="utf-8")
actual_sig = hashlib.sha256(policy_raw.encode("utf-8")).hexdigest()
recorded_sig = sig_path.read_text(encoding="utf-8").strip().split()[0]
if actual_sig != recorded_sig:
    raise SystemExit("signature mismatch for reviewer policy")
obj = json.loads(policy_raw)
allowed = {}
for row in obj.get("reviewers", []):
    rid = str(row.get("id", "")).strip()
    if not rid:
        continue
    allowed[rid] = {
        "role": str(row.get("role", "")).strip().lower(),
        "source_type": str(row.get("source_type", "")).strip().lower(),
    }
required_roles = set(str(r).strip().lower() for r in obj.get("min_roles_for_approve", ["approver"]))
if not required_roles:
    required_roles = {"approver"}
if not reviewers:
    raise SystemExit("empty reviewer list")
for reviewer in reviewers:
    row = allowed.get(reviewer)
    if row is None:
        raise SystemExit(f"reviewer not allowlisted: {reviewer}")
    if row["role"] not in required_roles:
        raise SystemExit(f"reviewer role not permitted: {reviewer}:{row['role']}")
print("ok")
PY
  then
    write_blocker_and_exit "run_rollforward_blocked" "reviewer policy validation failed (allowlist/role/signature)"
  fi
fi

trap 'rm -f "$decision_tmp"' EXIT

python3 - "$repo_root" "$seed_path" "$decision_tmp" "$lesson_id" "$reviewers" "$expected_version" "$decision" "$note" "$lesson_file" <<'PY'
import fcntl
import hashlib
import json
import os
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

# ---------------------------------------------------------------------------
# C-01 (option 1): HMAC-SHA256 decision signing
# Sign the canonical JSON of the decision tmp file using PROMOTION_SIGNING_KEY.
# The sig is written to <decision_tmp>.sig and verified by the validator before
# any canonical lesson write occurs.
#
# If PROMOTION_SIGNING_KEY is unset:
#   - PROMOTION_SIG_REQUIRED=1 (CI): hard-fail.
#   - Otherwise (local/interactive): warn and skip signing.
#
# Migration path to option 2 (Ed25519) is documented in
# docs/skill-graphs/governance/promotion-signing.md.
# ---------------------------------------------------------------------------
decision_sig_file="${decision_tmp}.sig"
promotion_key="${PROMOTION_SIGNING_KEY:-}"
sig_required="${PROMOTION_SIG_REQUIRED:-0}"

if [[ -n "$promotion_key" ]]; then
  python3 - "$decision_tmp" "$decision_sig_file" "$promotion_key" <<'PY'
import hmac
import json
import sys
from hashlib import sha256
from pathlib import Path

decision_path = Path(sys.argv[1])
sig_path = Path(sys.argv[2])
key = sys.argv[3].encode("utf-8")

# Canonical form: sorted keys, no trailing whitespace variation
obj = json.loads(decision_path.read_text(encoding="utf-8"))
canonical = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
mac = hmac.new(key, canonical, sha256).hexdigest()
sig_path.write_text(f"hmac-sha256:{mac}\n", encoding="utf-8")
print(f"[promotion-gate] decision signed → {sig_path}")
PY
  echo "[promotion-gate] HMAC-SHA256 signature written: $decision_sig_file"
elif [[ "$sig_required" == "1" || "$sig_required" == "true" || "$sig_required" == "TRUE" ]]; then
  echo "[promotion-gate] ERROR: PROMOTION_SIGNING_KEY is not set but PROMOTION_SIG_REQUIRED=1 — cannot sign decision" >&2
  echo "[promotion-gate] Set PROMOTION_SIGNING_KEY from the GitHub secret 'PROMOTION_SIGNING_KEY' in CI." >&2
  exit 2
else
  echo "[promotion-gate] WARNING: PROMOTION_SIGNING_KEY not set; decision will not be signed." >&2
  echo "[promotion-gate] Set PROMOTION_SIG_REQUIRED=1 in CI to hard-fail on unsigned decisions." >&2
fi

validator="utilities/skill-builder/scripts/validate_recursive_promotion.py"
validator_cmd=(python3 "$validator" --run-dir "$run_dir" --decision-file "$decision_tmp")

if [[ -f "$decision_sig_file" ]]; then
  validator_cmd+=(--decision-sig-file "$decision_sig_file")
fi

if [[ -n "$lesson_file" ]]; then
  validator_cmd+=(--lesson-file "$lesson_file")
elif [[ "$skip_lesson_scan" -eq 1 ]]; then
  validator_cmd+=(--skip-lesson-content-scan)
fi

"${validator_cmd[@]}"

if [[ "$decision" == "approved" ]]; then
  if ! python3 - "$run_json_path" "$decision_tmp" "$lesson_id" "$expected_version" "$reviewers" <<'PY'
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

run_path = Path(sys.argv[1])
decision_path = Path(sys.argv[2])
lesson_id = sys.argv[3].strip()
expected_version = sys.argv[4].strip()
reviewers = [r.strip() for r in sys.argv[5].split(",") if r.strip()]

repo_root = Path.cwd()
lessons_dir = repo_root / "artifacts/skill-graphs/lessons"
jsonl_path = lessons_dir / "canonical-lessons.jsonl"
index_path = lessons_dir / "canonical-lesson-index.json"
lessons_dir.mkdir(parents=True, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_jsonl_rows(path: Path):
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
    return rows


def write_text_atomic(path: Path, payload: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def write_jsonl_atomic(path: Path, rows):
    write_text_atomic(path, "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def write_json_atomic(path: Path, obj):
    write_text_atomic(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


run = json.loads(run_path.read_text(encoding="utf-8"))
decision = json.loads(decision_path.read_text(encoding="utf-8"))
scope_skill = str(run.get("scope_skill", "")).strip()
scope_profile = str(run.get("scope_profile", "")).strip()
if not scope_skill or not scope_profile:
    raise SystemExit("run missing scope_skill/scope_profile")

lock_path = lessons_dir / ".canonical-lessons.lock"
with lock_path.open("a+", encoding="utf-8") as lock_file:
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

    entries = load_jsonl_rows(jsonl_path)
    index = {"schema_version": "1.0", "scopes": {}}
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if "scopes" not in index or not isinstance(index["scopes"], dict):
            index["scopes"] = {}

    scope_key = f"{scope_skill}::{scope_profile}"
    scope_state = index["scopes"].get(scope_key, {"current_version": 0, "active_lesson_id": ""})
    current_version = int(scope_state.get("current_version", 0))
    expected_token = f"v{current_version}"
    if expected_version != expected_token:
        raise SystemExit(f"expected-version mismatch: got {expected_version} expected {expected_token}")

    for e in entries:
        provenance = e.get("provenance")
        if not isinstance(provenance, dict):
            provenance = {}
        if (
            str(e.get("lesson_id", "")) == lesson_id
            and str(e.get("status", "")) == "active"
            and str(provenance.get("run_id", "")) == str(run.get("run_id", ""))
        ):
            decision["lesson_status"] = "active"
            decision["lesson_effective_to"] = None
            decision["canonical_version"] = f"v{current_version}"
            decision_path.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print("idempotent")
            raise SystemExit(0)

    ts = now_iso()
    new_version = current_version + 1
    for e in entries:
        if (
            str(e.get("scope_skill", "")) == scope_skill
            and str(e.get("scope_profile", "")) == scope_profile
            and str(e.get("status", "")) == "active"
            and not e.get("effective_to")
        ):
            e["status"] = "superseded"
            e["effective_to"] = ts
            e["superseded_by_lesson_id"] = lesson_id

    new_entry = {
        "schema_version": "1.0",
        "lesson_id": lesson_id,
        "scope_skill": scope_skill,
        "scope_profile": scope_profile,
        "status": "active",
        "effective_from": ts,
        "effective_to": None,
        "supersedes_lesson_id": scope_state.get("active_lesson_id") or None,
        "superseded_by_lesson_id": None,
        "confidence": 0.75,
        "version": f"v{new_version}",
        "provenance": {
            "run_id": run.get("run_id"),
            "iteration_ids": (
                decision.get("provenance", {}).get("iteration_ids", [])
                if isinstance(decision.get("provenance"), dict)
                else []
            ),
            "prompt_hash": run.get("prompt_hash"),
            "rubric_version": run.get("versions", {}).get("rubric_version"),
            "evaluator_version": run.get("versions", {}).get("evaluator_version"),
        },
        "review": {
            "reviewer_ids": reviewers,
            "decision": "approved",
            "security_checklist_passed": True,
        },
    }
    entries.append(new_entry)

    write_jsonl_atomic(jsonl_path, entries)
    scope_state["current_version"] = new_version
    scope_state["active_lesson_id"] = lesson_id
    scope_state["updated_at"] = ts
    index["scopes"][scope_key] = scope_state
    write_json_atomic(index_path, index)

    decision["lesson_status"] = "active"
    decision["lesson_effective_to"] = None
    decision["canonical_version"] = f"v{new_version}"
    decision_path.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("updated")
PY
  then
    write_blocker_and_exit "run_rollforward_blocked" "canonical lesson persistence failed (CAS/policy/index conflict)"
  fi
fi

mv -f "$decision_tmp" "$decision_path"
trap - EXIT

if [[ "$decision" == "approved" ]]; then
  python3 - "$run_json_path" "$run_dir/events.jsonl" "$reviewers" "$lesson_id" <<'PY'
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

with events_path.open('a+', encoding='utf-8') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    f.seek(0)
    for line in f.read().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if (
            row.get("event_type") == "promotion_approved"
            and row.get("run_id") == run.get("run_id")
            and row.get("lesson_id") == lesson_id
        ):
            print("[promotion-gate] promotion_approved already present; skipping duplicate append")
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
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
    f.seek(0, 2)
    f.write(json.dumps(event, sort_keys=True) + '\n')
    f.flush()
    os.fsync(f.fileno())
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
PY
fi

echo "[promotion-gate] decision written: $decision_path"
if [[ "$decision" == "approved" ]]; then
  echo "[promotion-gate] promotion event log path: $run_dir/events.jsonl"
fi

echo "[promotion-gate] validation passed"
