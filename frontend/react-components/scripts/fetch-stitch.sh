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

URL=$1
OUTPUT=$2
if [ -z "$URL" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: $0 <url> <output_path>"
  exit 1
fi
echo "Initiating high-reliability fetch for Stitch HTML..."
python3 - "$URL" "$OUTPUT" <<'PY'
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

if [ $? -eq 0 ]; then
  echo "✅ Successfully retrieved HTML at: $OUTPUT"
  exit 0
fi

echo "❌ Error: Failed to retrieve content. Check TLS/SNI or URL expiration."
exit 1
