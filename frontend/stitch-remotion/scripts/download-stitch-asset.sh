#!/bin/bash

# Download Stitch screen asset with proper handling of Google Cloud Storage URLs
# Usage: ./download-stitch-asset.sh "https://storage.googleapis.com/..." "output-path.png"

set -e

if [ $# -ne 2 ]; then
  echo "Usage: $0 <download_url> <output_path>"
  echo "Example: $0 'https://storage.googleapis.com/stitch/screenshot.png' 'assets/screen.png'"
  exit 1
fi

DOWNLOAD_URL="$1"
OUTPUT_PATH="$2"

# Create directory if it doesn't exist
OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
mkdir -p "$OUTPUT_DIR"

echo "Downloading from: $DOWNLOAD_URL"
echo "Saving to: $OUTPUT_PATH"

python3 - "$DOWNLOAD_URL" "$OUTPUT_PATH" <<'PY'
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

if [ $? -ne 0 ]; then
  echo "✗ Download failed"
  exit 1
fi

echo "✓ Successfully downloaded to $OUTPUT_PATH"

# Display file size for verification
if command -v stat &> /dev/null; then
  FILE_SIZE=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || stat -c%s "$OUTPUT_PATH" 2>/dev/null)
  echo "  File size: $FILE_SIZE bytes"
fi
