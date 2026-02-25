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

# Setup script for the automate-github-issues skill
set -e

usage() {
  cat <<'TXT'
Usage:
  setup.sh

Bootstraps Node/npm dependencies and .env scaffolding for automate-github-issues.
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

echo "🔧 Setting up automate-github-issues skill..."
echo ""

# Check for Node.js + npm
if command -v node &> /dev/null; then
  echo "✅ Node.js found: $(node --version)"
else
  echo "❌ Node.js is required but was not found on PATH."
  echo ""
  echo "Install Node.js (LTS) using a trusted package source, then re-run setup:"
  echo "  - macOS (Homebrew): brew install node"
  echo "  - Ubuntu/Debian: sudo apt install nodejs npm"
  echo "  - Official docs: https://nodejs.org/"
  exit 1
fi

if command -v npm &> /dev/null; then
  echo "✅ npm found: $(npm --version)"
else
  echo "❌ npm is required but was not found on PATH."
  exit 1
fi

echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install
echo "✅ Dependencies installed."

echo ""

# Scaffold .env if it doesn't exist
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$SKILL_DIR/.env"
ENV_EXAMPLE="$SKILL_DIR/assets/.env.example"

if [ ! -f "$ENV_FILE" ]; then
  if [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "📝 Created .env from template. Edit it with your API keys."
  else
    echo "⚠️  No .env.example found. Create .env manually with JULES_API_KEY and GITHUB_TOKEN."
  fi
else
  echo "✅ .env already exists."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next steps (manual):"
echo ""
echo "  1. Edit .env with your API keys:"
echo "     JULES_API_KEY=your-key-here"
echo "     GITHUB_TOKEN=your-token-here"
echo ""
echo "  2. Add GitHub Actions workflows:"
echo "     cp assets/fleet-dispatch.yml .github/workflows/"
echo "     cp assets/fleet-merge.yml .github/workflows/"
echo ""
echo "  3. Add secrets to your GitHub repo:"
echo "     Settings → Secrets → Actions → New repository secret"
echo "     - JULES_API_KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
