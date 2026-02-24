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
# Always installs the latest release.
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
ACT_INSTALLER_URL="https://raw.githubusercontent.com/nektos/act/master/install.sh"

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

echo "  Detected platform: ${OS}/${ARCH}"

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

if ! command -v python3 &> /dev/null; then
  echo "❌ python3 is required to download the act installer."
  exit 1
fi

TMP_INSTALL_SCRIPT="$(mktemp)"
trap 'rm -f "$TMP_INSTALL_SCRIPT"' EXIT
python3 - "$ACT_INSTALLER_URL" "$TMP_INSTALL_SCRIPT" <<'PY'
import sys
import urllib.request

url, dest = sys.argv[1], sys.argv[2]
with urllib.request.urlopen(url) as response, open(dest, "wb") as fh:
    fh.write(response.read())
PY
chmod +x "$TMP_INSTALL_SCRIPT"

# Try system-wide install first, fall back to user-local
if command -v sudo &> /dev/null && sudo -n true 2>/dev/null; then
  echo "  Installing to /usr/local/bin (system-wide)..."
  sudo bash "$TMP_INSTALL_SCRIPT" -b /usr/local/bin
else
  echo "  No sudo access. Installing to ${INSTALL_DIR} (user-local)..."
  bash "$TMP_INSTALL_SCRIPT" -b "$INSTALL_DIR"

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
else
  echo "❌ Installation failed. act not found on PATH."
  exit 1
fi
