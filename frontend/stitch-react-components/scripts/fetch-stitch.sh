#!/bin/bash
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  fetch-stitch.sh <url> <output_path>
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

URL="$1"
OUTPUT="$2"
echo "Initiating high-reliability fetch for Stitch HTML..."
if python3 - "$URL" "$OUTPUT" <<'PY'
import pathlib
import sys
import urllib.request

url, output = sys.argv[1], sys.argv[2]
pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "codex-skill-fetch/1.0",
        "Accept-Encoding": "gzip, deflate",
    },
)

with urllib.request.urlopen(req, timeout=20) as response:
    data = response.read()
pathlib.Path(output).write_bytes(data)
PY
then
  echo "✅ Successfully retrieved HTML at: $OUTPUT"
  exit 0
fi

echo "❌ Error: Failed to retrieve content. Check TLS/SNI or URL expiration."
exit 1
