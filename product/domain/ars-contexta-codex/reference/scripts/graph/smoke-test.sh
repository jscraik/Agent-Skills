#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_DIR="$(mktemp -d)"
VAULT_DIR="$TMP_DIR/vault"
NOTES_DIR="$VAULT_DIR/notes"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$NOTES_DIR"

cat > "$NOTES_DIR/A.md" <<'MD'
---
type: note
description: A links into the dense core.
---
[[B]] [[C]]
MD

cat > "$NOTES_DIR/B.md" <<'MD'
---
type: note
description: B points deeper toward D.
---
[[C]] [[D]]
MD

cat > "$NOTES_DIR/C.md" <<'MD'
---
type: note
description: C reinforces the core.
---
[[A]] [[D]]
MD

cat > "$NOTES_DIR/D.md" <<'MD'
---
type: note
description: D bridges core and tail cluster.
---
[[E]]
MD

cat > "$NOTES_DIR/E.md" <<'MD'
---
type: note
description: E in the tail cluster.
---
[[F]]
MD

cat > "$NOTES_DIR/F.md" <<'MD'
---
type: note
description: F closes the tail triangle.
---
[[D]]
MD

cat > "$NOTES_DIR/G.md" <<'MD'
---
type: note
description: G is isolated.
---
MD

pushd "$VAULT_DIR" >/dev/null

PR_OUT="$TMP_DIR/pagerank.out"
BT_OUT="$TMP_DIR/betweenness.out"
LC_OUT="$TMP_DIR/leiden.out"
FB_OUT="$TMP_DIR/feedback.out"

"$SCRIPT_DIR/pagerank.sh" notes 5 > "$PR_OUT"
"$SCRIPT_DIR/betweenness.sh" notes 5 > "$BT_OUT"
"$SCRIPT_DIR/find-communities-leiden.sh" notes > "$LC_OUT"
"$SCRIPT_DIR/feedback-loop.sh" "$VAULT_DIR" notes 5 ops/metrics/graph > "$FB_OUT"

rg -q '^mode: pagerank$' "$PR_OUT"
rg -q '^notes: 7$' "$PR_OUT"
rg -q '\[\[D\]\]' "$PR_OUT"

rg -q '^mode: betweenness$' "$BT_OUT"
rg -q '^notes: 7$' "$BT_OUT"
rg -q '\[\[D\]\]' "$BT_OUT"

rg -q '^mode: ' "$LC_OUT"
rg -q '^notes: 7$' "$LC_OUT"
rg -q '^communities: ' "$LC_OUT"
rg -q '\[\[A\]\]' "$LC_OUT"
rg -q '\[\[G\]\]' "$LC_OUT"

rg -q '^feedback-loop: PASS$' "$FB_OUT"
rg -q 'snapshot:' "$FB_OUT"
rg -q 'report:' "$FB_OUT"
rg -q 'actions:' "$FB_OUT"
test -f "$VAULT_DIR/ops/metrics/graph/snapshots/latest.json"
test -f "$VAULT_DIR/ops/metrics/graph/reports/latest.md"
test -f "$VAULT_DIR/ops/metrics/graph/recommendations/latest.json"

popd >/dev/null

echo "smoke-test: PASS"
echo "pagerank sample:"
sed -n '1,12p' "$PR_OUT"
echo
echo "betweenness sample:"
sed -n '1,12p' "$BT_OUT"
echo
echo "communities sample:"
sed -n '1,16p' "$LC_OUT"
