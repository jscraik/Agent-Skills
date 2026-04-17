#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

missing=0
move_or_track() {
  local src="$1"
  local dst="$2"
  if [[ -e "$src" ]]; then
    git mv "$src" "$dst"
  else
    echo "Missing expected path: $src" >&2
    missing=$((missing + 1))
  fi
}

# Restore skills-system root
mkdir -p skills-system
move_or_track Skills/skills-system/imagegen skills-system/
move_or_track Skills/skills-system/openai-docs skills-system/
if [[ -d Skills/skills-system ]]; then
  rmdir Skills/skills-system || true
fi

# Move Docs/product/security/*
move_or_track Docs/product/security/security-threat-model Skills/security-ops/
move_or_track Docs/product/security/security-best-practices Skills/security-ops/
move_or_track Docs/product/security/security-ownership-map Skills/security-ops/

# Move Docs/product/specs/*
move_or_track Docs/product/specs/product-spec Skills/product-strategy/

# Move Docs/product/content/*
move_or_track Docs/product/content/changelog Skills/content-publishing/
move_or_track Docs/product/content/youtube-hooks-scripts Skills/content-publishing/
move_or_track Docs/product/content/every-style-editor Skills/content-publishing/
move_or_track Docs/product/content/feature-video Skills/content-publishing/
move_or_track Docs/product/content/youtube-titles-thumbnails Skills/content-publishing/
move_or_track Docs/product/content/video-transcript-downloader Skills/content-publishing/

# Move Docs/product/docs/*
move_or_track Docs/product/docs/context7 Skills/agent-ops/
move_or_track Docs/product/docs/agents-md Skills/agent-ops/
move_or_track Docs/product/docs/llm-wiki Skills/content-publishing/
move_or_track Docs/product/docs/docs-expert Skills/agent-ops/

# Move Docs/product/review/*
move_or_track Docs/product/review/agent-native-audit Skills/agent-ops/

# Move Docs/product/ops/*
move_or_track Docs/product/ops/fallback-release Skills/agent-ops/
move_or_track Docs/product/ops/release Skills/agent-ops/
move_or_track Docs/product/ops/triage Skills/agent-ops/
move_or_track Docs/product/ops/resolve-todo-parallel Skills/agent-ops/
move_or_track Docs/product/ops/production-deployment Skills/agent-ops/
move_or_track Docs/product/ops/decide-build-primitive Skills/agent-ops/

# Move Docs/product/domain/*
move_or_track Docs/product/domain/agent-native-architecture Skills/backend-platform/
move_or_track Docs/product/domain/oak-api Skills/backend-platform/
move_or_track Docs/product/domain/chatgpt-apps Skills/product-strategy/

# Move Docs/product/strategy/*
move_or_track Docs/product/strategy/project-improver Skills/product-strategy/
move_or_track Docs/product/strategy/product-design-critic Skills/product-strategy/
move_or_track Docs/product/strategy/brainstorming Skills/product-strategy/

if (( missing > 0 )); then
  echo "Aborting: $missing expected moves were skipped." >&2
  exit 1
fi
