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

# Installs 'act' (https://github.com/nektos/act) for running GitHub Actions locally.
# Downloads the latest release tarball + checksum manifest from GitHub Releases,
# verifies SHA256, then installs the extracted binary.
# Usage: ./install-act.sh

set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  install-act.sh

Installs the latest nektos/act binary system-wide when sudo is available,
or to ~/.local/bin otherwise.
TXT
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "ERROR: unknown option: $1"
  usage
  exit 2
fi

INSTALL_DIR="${HOME}/.local/bin"

echo "🔧 Installing act..."

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
  linux|darwin) ;;
  *)
    echo "❌ Unsupported operating system: $OS"
    exit 1
    ;;
esac

case "$ARCH" in
  x86_64)  ARCH="x86_64" ;;
  aarch64) ARCH="arm64" ;;
  arm64)   ARCH="arm64" ;;
  *)
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

case "$OS" in
  linux) ASSET_OS="Linux" ;;
  darwin) ASSET_OS="Darwin" ;;
  *)
    echo "❌ Unsupported operating system for act release assets: $OS"
    exit 1
    ;;
esac

echo "  Detected platform: ${OS}/${ARCH} (asset=${ASSET_OS}/${ARCH})"

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

if ! command -v python3 &> /dev/null; then
  echo "❌ python3 is required to download and verify act artifacts."
  exit 1
fi

if ! command -v tar &> /dev/null; then
  echo "❌ tar is required to extract act release assets."
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
CHECKSUMS_TXT="${TMP_DIR}/checksums.txt"
EXTRACT_DIR="${TMP_DIR}/extract"

read -r ACT_TAG ASSET_URL CHECKSUMS_URL <<EOF
$(python3 - "$ASSET_OS" "$ARCH" <<'PY'
import json
import sys
import urllib.request

asset_os = sys.argv[1]
asset_arch = sys.argv[2]
target_name = f"act_{asset_os}_{asset_arch}.tar.gz"

url = "https://api.github.com/repos/nektos/act/releases/latest"
request = urllib.request.Request(url, headers={"User-Agent": "agent-skills-install-act"})
with urllib.request.urlopen(request) as response:
    release = json.loads(response.read().decode("utf-8"))

tag = str(release.get("tag_name", "")).strip()
assets = release.get("assets", [])
asset_url = ""
checksums_url = ""
for asset in assets:
    name = str(asset.get("name", ""))
    download_url = str(asset.get("browser_download_url", ""))
    if name == target_name:
        asset_url = download_url
    if (
        not checksums_url
        and "checksum" in name.lower()
        and name.lower().endswith((".txt", ".sha256", ".sha256sum", ".sha256sums"))
    ):
        checksums_url = download_url

if not tag or not asset_url or not checksums_url:
    raise SystemExit(1)

print(f"{tag} {asset_url} {checksums_url}")
PY
EOF

if [[ -z "${ACT_TAG:-}" || -z "${ASSET_URL:-}" || -z "${CHECKSUMS_URL:-}" ]]; then
  echo "❌ Failed to resolve act release asset/checksum URLs from GitHub Releases."
  exit 1
fi

ASSET_FILENAME="$(basename "${ASSET_URL%%\?*}")"
ASSET_TAR="${TMP_DIR}/${ASSET_FILENAME}"

python3 - "$ASSET_URL" "$ASSET_TAR" "$CHECKSUMS_URL" "$CHECKSUMS_TXT" <<'PY'
import shutil
import sys
import urllib.request

asset_url, asset_dest, checksums_url, checksums_dest = sys.argv[1:5]
asset_request = urllib.request.Request(asset_url, headers={"User-Agent": "agent-skills-install-act"})
with urllib.request.urlopen(asset_request) as response, open(asset_dest, "wb") as fh:
    shutil.copyfileobj(response, fh)
checksums_request = urllib.request.Request(checksums_url, headers={"User-Agent": "agent-skills-install-act"})
with urllib.request.urlopen(checksums_request) as response, open(checksums_dest, "wb") as fh:
    shutil.copyfileobj(response, fh)
PY

python3 - "$ASSET_TAR" "$CHECKSUMS_TXT" <<'PY'
import hashlib
import os
import sys

asset_path, checksums_path = sys.argv[1:3]
asset_name = os.path.basename(asset_path)
expected = None
with open(checksums_path, "r", encoding="utf-8", errors="ignore") as fh:
    for raw in fh:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.replace("  ", " ").split()
        if len(parts) < 2:
            continue
        digest = parts[0].strip().lower()
        filename = parts[-1].lstrip("*").strip()
        if filename == asset_name or filename.endswith("/" + asset_name):
            expected = digest
            break

if not expected:
    raise SystemExit("checksum entry not found for asset")

h = hashlib.sha256()
with open(asset_path, "rb") as fh:
    for chunk in iter(lambda: fh.read(65536), b""):
        h.update(chunk)
actual = h.hexdigest().lower()
if actual != expected:
    raise SystemExit(f"checksum mismatch: expected={expected} actual={actual}")
PY

mkdir -p "$EXTRACT_DIR"
tar -xzf "$ASSET_TAR" -C "$EXTRACT_DIR"

ACT_BIN="$(find "$EXTRACT_DIR" -type f -name act -perm -u+x | head -n 1)"
if [[ -z "${ACT_BIN:-}" ]]; then
  echo "❌ Unable to locate act binary in extracted release archive."
  exit 1
fi

# Try system-wide install first, fall back to user-local
if command -v sudo &> /dev/null && sudo -n true 2>/dev/null; then
  echo "  Installing to /usr/local/bin (system-wide)..."
  sudo install -m 0755 "$ACT_BIN" /usr/local/bin/act
else
  echo "  No sudo access. Installing to ${INSTALL_DIR} (user-local)..."
  install -m 0755 "$ACT_BIN" "${INSTALL_DIR}/act"

  # Ensure install dir is on PATH
  if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo "  ⚠️  ${INSTALL_DIR} is not on your PATH."
    echo "  Add this to your shell profile: export PATH=\"${INSTALL_DIR}:\$PATH\""
    export PATH="${INSTALL_DIR}:$PATH"
  fi
fi

# Verify installation
if command -v act &> /dev/null; then
  echo "✅ act installed successfully: $(act --version)"
  echo "  Installed release: ${ACT_TAG}"
else
  echo "❌ Installation failed. act not found on PATH."
  exit 1
fi
