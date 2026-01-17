#!/usr/bin/env bash
set -euo pipefail

if ! command -v mmdc >/dev/null 2>&1; then
  echo "error: mmdc (mermaid-cli) not found" >&2
  echo "install: npm i -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found (needed to extract Mermaid blocks from Markdown)" >&2
  exit 1
fi

OUT_DIR="${OUT_DIR:-docs/assets/diagrams}"
TMP_DIR="${TMP_DIR:-.tmp/mermaid-extracted}"
KEEP_TMP="${KEEP_TMP:-0}"
MMDC_EXTRA_ARGS="${MMDC_EXTRA_ARGS:-}"

mkdir -p "$OUT_DIR" "$TMP_DIR"

# Default to spec-output.md if no args provided
if [[ $# -gt 0 ]]; then
  MD_FILES=("$@")
else
  if [[ -f "spec-output.md" ]]; then
    MD_FILES=("spec-output.md")
  else
    echo "usage: $0 <markdown files...>" >&2
    echo "tip: run from a folder containing spec-output.md or pass explicit files" >&2
    exit 1
  fi
fi

# Split MMDC_EXTRA_ARGS into an array safely (space-delimited)
MMDC_ARGS=()
if [[ -n "$MMDC_EXTRA_ARGS" ]]; then
  # shellcheck disable=SC2206
  MMDC_ARGS=($MMDC_EXTRA_ARGS)
fi

# Extract mermaid code blocks into TMP_DIR and print list of extracted .mmd files
mapfile -t MMD_FILES < <(python3 - "$TMP_DIR" "${MD_FILES[@]}" <<'PY'
import re
import sys
from pathlib import Path

tmp_dir = Path(sys.argv[1])
md_files = [Path(p) for p in sys.argv[2:]]

tmp_dir.mkdir(parents=True, exist_ok=True)

# Match ```mermaid ... ``` blocks. Accept extra info after "mermaid" on the fence line.
pattern = re.compile(r"```mermaid[^\n]*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)

out_paths = []

for md in md_files:
    if not md.exists():
        continue
    text = md.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches, start=1):
        body = (m.group(1) or "").strip()
        if not body:
            continue

        safe_name = md.name.replace(" ", "_")
        out = tmp_dir / f"{safe_name}__mermaid_{i:03d}.mmd"
        out.write_text(body + "\n", encoding="utf-8")
        out_paths.append(str(out))

for p in out_paths:
    print(p)
PY
)

if [[ ${#MMD_FILES[@]} -eq 0 ]]; then
  echo "No Mermaid blocks found in: ${MD_FILES[*]}" >&2
  exit 0
fi

# Render each extracted .mmd file to PNG
rendered=0
for mmd in "${MMD_FILES[@]}"; do
  base="$(basename "$mmd")"
  out_png="$OUT_DIR/${base%.*}.png"
  mmdc -i "$mmd" -o "$out_png" "${MMDC_ARGS[@]}"
  echo "rendered: $out_png"
  rendered=$((rendered + 1))
done

echo "done: rendered $rendered diagram(s) into $OUT_DIR"

if [[ "$KEEP_TMP" != "1" ]]; then
  rm -rf "$TMP_DIR"
fi
