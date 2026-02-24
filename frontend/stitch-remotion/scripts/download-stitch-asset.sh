#!/bin/bash

# Download Stitch screen asset with proper handling of Google Cloud Storage URLs
# Usage: ./download-stitch-asset.sh "https://storage.googleapis.com/..." "output-path.png"

set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  download-stitch-asset.sh <download_url> <output_path>
Example:
  download-stitch-asset.sh 'https://storage.googleapis.com/stitch/screenshot.png' 'assets/screen.png'
TXT
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 2 ]]; then
  usage
  exit 2
fi

DOWNLOAD_URL="$1"
OUTPUT_PATH="$2"

# Create directory if it doesn't exist
OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
mkdir -p "$OUTPUT_DIR"

echo "Downloading from: $DOWNLOAD_URL"
echo "Saving to: $OUTPUT_PATH"

if python3 - "$DOWNLOAD_URL" "$OUTPUT_PATH" <<'PY'
import pathlib
import sys
import urllib.request

url, output = sys.argv[1], sys.argv[2]
path = pathlib.Path(output)
path.parent.mkdir(parents=True, exist_ok=True)

req = urllib.request.Request(url, headers={"User-Agent": "codex-stitch-remotion/1.0"})
with urllib.request.urlopen(req, timeout=30) as response:
    path.write_bytes(response.read())
PY
then
  echo "✓ Successfully downloaded to $OUTPUT_PATH"
else
  echo "✗ Download failed"
  exit 1
fi

# Display file size for verification
if command -v stat &> /dev/null; then
  FILE_SIZE=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || stat -c%s "$OUTPUT_PATH" 2>/dev/null)
  echo "  File size: $FILE_SIZE bytes"
fi
