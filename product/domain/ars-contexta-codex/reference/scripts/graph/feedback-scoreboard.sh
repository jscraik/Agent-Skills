#!/usr/bin/env bash
set -euo pipefail

VAULT_ROOT="${1:-$(pwd)}"
METRICS_DIR_REL="${2:-ops/metrics/graph}"
METRICS_DIR="$VAULT_ROOT/$METRICS_DIR_REL"
FEEDBACK_LOG="$METRICS_DIR/feedback/decision-feedback.jsonl"

if [[ ! -f "$FEEDBACK_LOG" ]]; then
  echo "feedback-scoreboard: no feedback log found at $FEEDBACK_LOG" >&2
  exit 1
fi

python3 - "$FEEDBACK_LOG" <<'PY'
import json
import pathlib
import sys
from collections import Counter, defaultdict

log_path = pathlib.Path(sys.argv[1])
rows = []
for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except Exception:
        continue

if not rows:
    print("feedback-scoreboard: no parseable events")
    sys.exit(0)

decision_counts = Counter(r.get("decision", "unknown") for r in rows)
outcome_counts = Counter(r.get("outcome", "unknown") for r in rows)
by_key = defaultdict(lambda: Counter())

for r in rows:
    key = r.get("action_key") or "unknown"
    outcome = r.get("outcome", "unknown")
    by_key[key][outcome] += 1
    by_key[key]["total"] += 1

print("feedback-scoreboard: PASS")
print(f"events: {len(rows)}")
print("\nDecision counts:")
for k in sorted(decision_counts):
    print(f"- {k}: {decision_counts[k]}")

print("\nOutcome counts:")
for k in sorted(outcome_counts):
    print(f"- {k}: {outcome_counts[k]}")

print("\nAction-key outcomes:")
print("action_key\ttotal\tgood\tneutral\tbad\tunknown\tgood_rate")
for key in sorted(by_key):
    c = by_key[key]
    total = c["total"]
    good = c["good"]
    neutral = c["neutral"]
    bad = c["bad"]
    unknown = c["unknown"]
    good_rate = (good / total) if total else 0.0
    print(f"{key}\t{total}\t{good}\t{neutral}\t{bad}\t{unknown}\t{good_rate:.2f}")
PY
