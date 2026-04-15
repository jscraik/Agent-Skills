#!/usr/bin/env bash
set -euo pipefail

VAULT_ROOT="${1:-$(pwd)}"
RECOMMENDATION_ID="${2:-}"
DECISION="${3:-}"
OUTCOME="${4:-}"
CONFIDENCE="${5:-}"
NOTES="${6:-}"
METRICS_DIR_REL="${7:-Infrastructure/ops/metrics/graph}"

if [[ -z "$RECOMMENDATION_ID" || -z "$DECISION" || -z "$OUTCOME" || -z "$CONFIDENCE" ]]; then
  echo "Usage: $(basename "$0") [vault_root] <recommendation_id> <decision> <outcome> <confidence> [notes] [metrics_dir_rel]" >&2
  echo "decision: accepted|partial|rejected|deferred" >&2
  echo "outcome: good|neutral|bad|unknown" >&2
  echo "confidence: high|medium|low" >&2
  exit 1
fi

case "$DECISION" in
  accepted|partial|rejected|deferred) ;;
  *)
    echo "ERROR: invalid decision '$DECISION'" >&2
    exit 1
    ;;
esac

case "$OUTCOME" in
  good|neutral|bad|unknown) ;;
  *)
    echo "ERROR: invalid outcome '$OUTCOME'" >&2
    exit 1
    ;;
esac

case "$CONFIDENCE" in
  high|medium|low) ;;
  *)
    echo "ERROR: invalid confidence '$CONFIDENCE'" >&2
    exit 1
    ;;
esac

METRICS_DIR="$VAULT_ROOT/$METRICS_DIR_REL"
RECOMMEND_LATEST="$METRICS_DIR/recommendations/latest.json"
FEEDBACK_DIR="$METRICS_DIR/feedback"
FEEDBACK_LOG="$FEEDBACK_DIR/decision-feedback.jsonl"
mkdir -p "$FEEDBACK_DIR"

python3 - "$RECOMMEND_LATEST" "$FEEDBACK_LOG" "$RECOMMENDATION_ID" "$DECISION" "$OUTCOME" "$CONFIDENCE" "$NOTES" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

recommend_latest, feedback_log, rec_id, decision, outcome, confidence, notes = sys.argv[1:8]

action_key = "unknown"
action_text = ""
snapshot = None
report_timestamp = None

path = pathlib.Path(recommend_latest)
if path.exists():
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        snapshot = payload.get("snapshot")
        report_timestamp = payload.get("generated_at")
        for rec in payload.get("recommendations", []):
            if rec.get("id") == rec_id:
                action_key = rec.get("action_key", "unknown")
                action_text = rec.get("action", "")
                break
    except Exception:
        pass

event = {
    "schema_version": 1,
    "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    "recommendation_id": rec_id,
    "decision": decision,
    "outcome": outcome,
    "confidence": confidence,
    "notes": notes,
    "action_key": action_key,
    "action": action_text,
    "source_snapshot": snapshot,
    "source_generated_at": report_timestamp,
}

log_path = pathlib.Path(feedback_log)
with log_path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False) + "\n")

print("record-feedback: PASS")
print(f"log: {log_path}")
print(f"recommendation: {rec_id}")
print(f"action_key: {action_key}")
PY
