#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_ROOT="${1:-$(pwd)}"
NOTES_DIR_REL="${2:-notes}"
TOP_N="${3:-20}"
METRICS_DIR_REL="${4:-Infrastructure/ops/metrics/graph}"

if ! [[ "$TOP_N" =~ ^[0-9]+$ ]] || [[ "$TOP_N" -lt 1 ]]; then
  echo "ERROR: top_n must be a positive integer (got: $TOP_N)" >&2
  echo "Usage: $(basename "$0") [vault_root] [notes_dir_rel] [top_n] [metrics_dir_rel]" >&2
  exit 1
fi

NOTES_DIR="$VAULT_ROOT/$NOTES_DIR_REL"
METRICS_DIR="$VAULT_ROOT/$METRICS_DIR_REL"
SNAPSHOT_DIR="$METRICS_DIR/snapshots"
REPORT_DIR="$METRICS_DIR/reports"
RAW_ROOT="$METRICS_DIR/raw"
RECOMMEND_DIR="$METRICS_DIR/recommendations"
FEEDBACK_DIR="$METRICS_DIR/feedback"
FEEDBACK_LOG="$FEEDBACK_DIR/decision-feedback.jsonl"

if [[ ! -d "$NOTES_DIR" ]]; then
  echo "ERROR: notes directory not found: $NOTES_DIR" >&2
  exit 1
fi

mkdir -p "$SNAPSHOT_DIR" "$REPORT_DIR" "$RAW_ROOT" "$RECOMMEND_DIR" "$FEEDBACK_DIR"

STAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
STAMP_HUMAN="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
RAW_DIR="$RAW_ROOT/$STAMP"
mkdir -p "$RAW_DIR"

PAGERANK_OUT="$RAW_DIR/pagerank.tsv"
BETWEENNESS_OUT="$RAW_DIR/betweenness.tsv"
COMMUNITIES_OUT="$RAW_DIR/communities.tsv"

"$SCRIPT_DIR/pagerank.sh" "$NOTES_DIR" "$TOP_N" > "$PAGERANK_OUT"
"$SCRIPT_DIR/betweenness.sh" "$NOTES_DIR" "$TOP_N" > "$BETWEENNESS_OUT"
"$SCRIPT_DIR/find-communities-leiden.sh" "$NOTES_DIR" > "$COMMUNITIES_OUT"

# ── Compute session co-invocation weights ────────────────────────────────────
WEIGHTS_SCRIPT="$VAULT_ROOT/Infrastructure/scripts/skill-graph/compute-edge-weights.py"
if [[ -f "$WEIGHTS_SCRIPT" ]]; then
  python3 "$WEIGHTS_SCRIPT" "$VAULT_ROOT" || true
fi

# ── Extract real skill-graph edges from See Also sections ────────────────────
EDGES_OUT="$METRICS_DIR/skill-edges.json"
python3 "$SCRIPT_DIR/extract-skill-edges.py" "$VAULT_ROOT" "$EDGES_OUT" || true


SNAPSHOT_PATH="$SNAPSHOT_DIR/$STAMP.json"
REPORT_PATH="$REPORT_DIR/$STAMP.md"
RECOMMEND_PATH="$RECOMMEND_DIR/$STAMP.json"

python3 - "$SNAPSHOT_DIR" "$PAGERANK_OUT" "$BETWEENNESS_OUT" "$COMMUNITIES_OUT" "$SNAPSHOT_PATH" "$REPORT_PATH" "$RECOMMEND_PATH" "$STAMP_HUMAN" "$NOTES_DIR_REL" "$TOP_N" "$FEEDBACK_LOG" <<'PY'
import json
import pathlib
import re
import sys

(
    snapshot_dir,
    pagerank_path,
    betweenness_path,
    communities_path,
    snapshot_out,
    report_out,
    recommend_out,
    generated_at,
    notes_dir_rel,
    top_n,
    feedback_log,
) = sys.argv[1:12]

snapshot_dir = pathlib.Path(snapshot_dir)
pagerank_path = pathlib.Path(pagerank_path)
betweenness_path = pathlib.Path(betweenness_path)
communities_path = pathlib.Path(communities_path)
snapshot_out = pathlib.Path(snapshot_out)
report_out = pathlib.Path(report_out)
recommend_out = pathlib.Path(recommend_out)
top_n_int = int(top_n)

wikilink_re = re.compile(r"\[\[([^\]]+)\]\]")


def parse_kv_and_rows(path: pathlib.Path):
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    header = {}
    rows = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            break
        if ":" in line:
            k, v = line.split(":", 1)
            header[k.strip()] = v.strip()
        i += 1

    if i < len(lines):
        if lines[i].strip().startswith("rank") or lines[i].strip().startswith("community"):
            col_names = [c.strip() for c in lines[i].split("\t")]
            i += 1
            while i < len(lines):
                row = lines[i].strip()
                if not row:
                    i += 1
                    continue
                parts = [p.strip() for p in lines[i].split("\t")]
                if len(parts) < len(col_names):
                    parts = parts + [""] * (len(col_names) - len(parts))
                rows.append(dict(zip(col_names, parts)))
                i += 1
    return header, rows


pr_meta, pr_rows = parse_kv_and_rows(pagerank_path)
bt_meta, bt_rows = parse_kv_and_rows(betweenness_path)
cm_meta, cm_rows = parse_kv_and_rows(communities_path)


def note_name(value: str):
    m = wikilink_re.search(value or "")
    return m.group(1) if m else value


pr_top = [note_name(r.get("note", "")) for r in pr_rows[:5] if r.get("note")]
bt_top = [note_name(r.get("note", "")) for r in bt_rows[:5] if r.get("note")]

isolated_communities = []
for row in cm_rows:
    try:
        size = int(row.get("size", "0"))
    except ValueError:
        size = 0
    if size == 1:
        members = [m.strip() for m in row.get("members", "").split(",") if m.strip()]
        isolated_communities.extend([note_name(m) for m in members])


def to_int(meta, key, default=0):
    try:
        return int(meta.get(key, default))
    except Exception:
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


snapshot = {
    "schema_version": 1,
    "generated_at": generated_at,
    "notes_dir": notes_dir_rel,
    "top_n": top_n_int,
    "pagerank": {"meta": pr_meta, "rows": pr_rows},
    "betweenness": {"meta": bt_meta, "rows": bt_rows},
    "communities": {"meta": cm_meta, "rows": cm_rows},
    "signals": {
        "notes": to_int(pr_meta, "notes"),
        "edges_directed": to_int(pr_meta, "edges"),
        "edges_undirected": to_int(bt_meta, "edges"),
        "community_count": to_int(cm_meta, "communities"),
        "community_quality_score": to_float(cm_meta.get("quality_score", "0")),
        "top_pagerank": pr_top,
        "top_bridges": bt_top,
        "isolated_notes": isolated_communities,
    },
}
snapshot_out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")

previous_path = None
all_snapshots = sorted(p for p in snapshot_dir.glob("*.json") if p.name != snapshot_out.name and p.name != "latest.json")
if all_snapshots:
    previous_path = all_snapshots[-1]

prev = None
if previous_path:
    try:
        prev = json.loads(previous_path.read_text(encoding="utf-8"))
    except Exception:
        prev = None

recommendations = []
insights = []
curr_signals = snapshot["signals"]


def add_recommendation(priority: str, action: str, reason: str, action_key: str):
    rec_id = f"rec-{len(recommendations)+1:03d}"
    recommendations.append(
        {
            "id": rec_id,
            "priority": priority,
            "action_key": action_key,
            "action": action,
            "reason": reason,
        }
    )

if prev:
    prev_signals = prev.get("signals", {})
    notes_delta = curr_signals["notes"] - int(prev_signals.get("notes", 0))
    communities_delta = curr_signals["community_count"] - int(prev_signals.get("community_count", 0))

    prev_pr = set(prev_signals.get("top_pagerank", [])[:5])
    curr_pr = set(curr_signals["top_pagerank"][:5])
    pr_overlap = (len(prev_pr & curr_pr) / len(prev_pr | curr_pr)) if (prev_pr or curr_pr) else 1.0

    prev_bt = set(prev_signals.get("top_bridges", [])[:5])
    curr_bt = set(curr_signals["top_bridges"][:5])
    bt_overlap = (len(prev_bt & curr_bt) / len(prev_bt | curr_bt)) if (prev_bt or curr_bt) else 1.0

    insights.append(f"Notes delta vs previous snapshot: {notes_delta:+d}")
    insights.append(f"Community count delta: {communities_delta:+d}")
    insights.append(f"Top-5 PageRank overlap: {pr_overlap:.2f}")
    insights.append(f"Top-5 bridge overlap: {bt_overlap:.2f}")

    if pr_overlap < 0.4:
        add_recommendation(
            "high",
            "Run /graph forward on the newest top PageRank note and /reflect to stabilize new linkage patterns.",
            "Top influence set shifted materially (overlap < 0.40).",
            "influence_shift",
        )
    if bt_overlap < 0.4:
        add_recommendation(
            "high",
            "Run /graph bridges and /reweave on emerging bridge notes to reduce single-point-of-failure risk.",
            "Bridge structure shifted materially (overlap < 0.40).",
            "bridge_shift",
        )
    if communities_delta > 1:
        add_recommendation(
            "medium",
            "Run /graph clusters and add 1-2 cross-community links where conceptually justified.",
            "Community count increased; graph may be fragmenting.",
            "community_fragmentation",
        )
else:
    insights.append("No previous snapshot found; this is your baseline run.")

if curr_signals["isolated_notes"]:
    add_recommendation(
        "high",
        "Run /graph health and /reflect on isolated notes to attach them to active MOCs.",
        f"Detected isolated singleton communities: {', '.join(curr_signals['isolated_notes'][:5])}",
        "isolated_notes",
    )

if curr_signals["top_pagerank"] and curr_signals["top_bridges"]:
    top_influence = curr_signals["top_pagerank"][0]
    top_bridge = curr_signals["top_bridges"][0]
    if top_influence == top_bridge:
        add_recommendation(
            "medium",
            f"Review [[{top_influence}]] for potential split/summary-note extraction.",
            "Same note is top influence and top bridge; may become a bottleneck.",
            "single_point_bottleneck",
        )

if not recommendations:
    add_recommendation(
        "low",
        "No urgent graph drift detected. Continue normal /reflect and /reweave cadence.",
        "Current metrics are stable.",
        "stable_state",
    )

recommend_payload = {
    "schema_version": 1,
    "generated_at": generated_at,
    "snapshot": snapshot_out.name,
    "previous_snapshot": previous_path.name if previous_path else None,
    "feedback_log": feedback_log,
    "feedback_schema": {
        "decision": ["accepted", "partial", "rejected", "deferred"],
        "outcome": ["good", "neutral", "bad", "unknown"],
        "confidence": ["high", "medium", "low"],
    },
    "insights": insights,
    "recommendations": recommendations,
}
recommend_out.write_text(json.dumps(recommend_payload, indent=2) + "\n", encoding="utf-8")

report_lines = [
    "# Graph Feedback Loop Report",
    "",
    f"Generated: {generated_at}",
    f"Snapshot: `{snapshot_out.name}`",
    f"Previous snapshot: `{previous_path.name}`" if previous_path else "Previous snapshot: _none (baseline)_",
    "",
    "## Key Signals",
    f"- Notes: **{curr_signals['notes']}**",
    f"- Directed edges: **{curr_signals['edges_directed']}**",
    f"- Communities: **{curr_signals['community_count']}**",
    f"- Community quality score: **{curr_signals['community_quality_score']:.4f}**",
    f"- Top PageRank notes: {', '.join(f'[[{n}]]' for n in curr_signals['top_pagerank']) or '_none_'}",
    f"- Top bridge notes: {', '.join(f'[[{n}]]' for n in curr_signals['top_bridges']) or '_none_'}",
    "",
    "## Drift Insights",
]
for item in insights:
    report_lines.append(f"- {item}")

report_lines.extend(["", "## Recommended Actions"])
for rec in recommendations:
    report_lines.append(f"- **{rec['priority'].upper()}** `{rec['id']}` ({rec['action_key']}) — {rec['action']}  ")
    report_lines.append(f"  Reason: {rec['reason']}")

report_lines.extend([
    "",
    "## Decision Feedback (AskQuestion / request_user_input)",
    "- Capture user feedback for each HIGH/MEDIUM recommendation after it is attempted.",
    "- Record outcomes with `Infrastructure/ops/Infrastructure/scripts/graph/record-feedback.sh` so the loop can learn what worked.",
    f"- Feedback log path: `{feedback_log}`",
    "",
    "## Next Run",
    "- Re-run this script after meaningful note growth or on a weekly schedule.",
    "- Track trend by comparing reports in `Infrastructure/ops/metrics/graph/Infrastructure/reports/`.",
])
report_out.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
PY

cp "$SNAPSHOT_PATH" "$SNAPSHOT_DIR/latest.json"
cp "$REPORT_PATH" "$REPORT_DIR/latest.md"
cp "$RECOMMEND_PATH" "$RECOMMEND_DIR/latest.json"

# ── Regenerate visual HTML graph if generator script is present ──────────────
GRAPH_GEN="$VAULT_ROOT/Infrastructure/scripts/skill-graph/gen-skill-graph.py"
GRAPH_HTML="${HOME}/.agents/diagrams/skill-graph.html"
if [[ -f "$GRAPH_GEN" ]] && [[ -f "$EDGES_OUT" ]]; then
  python3 "$GRAPH_GEN" "$VAULT_ROOT" "$EDGES_OUT" "$GRAPH_HTML" || true
  echo "graph:    $GRAPH_HTML"
fi

echo "feedback-loop: PASS"
echo "snapshot: $SNAPSHOT_PATH"
echo "report:   $REPORT_PATH"
echo "actions:  $RECOMMEND_PATH"
echo "edges:    ${EDGES_OUT}"
echo "feedback: $FEEDBACK_LOG"
