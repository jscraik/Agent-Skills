#!/usr/bin/env bash
set -ex

cd /Users/jamiecraik/dev/Agent-Skills/Skills

# Move root skills-system
mkdir -p skills-system
git mv ../skills-system/imagegen skills-system/ || true
git mv ../skills-system/openai-docs skills-system/ || true
rm -d ../skills-system || true

# From agent-ops
git mv agent-ops/frontend-design frontend-ui/ || true
git mv agent-ops/test-browser frontend-ui/ || true
git mv agent-ops/elixir-pro backend-platform/ || true
git mv agent-ops/go backend-platform/ || true
git mv agent-ops/rust-pro backend-platform/ || true
git mv agent-ops/sql-pro backend-platform/ || true
git mv agent-ops/uv-python-project-setup backend-platform/ || true
git mv agent-ops/swift-development mobile-native/ || true

# From mobile-native
git mv mobile-native/process-watch agent-ops/ || true
git mv mobile-native/test-driven-development agent-ops/ || true

# From frontend-ui
git mv frontend-ui/beautiful-mermaid content-publishing/ || true
git mv frontend-ui/slides content-publishing/ || true
git mv frontend-ui/sora content-publishing/ || true
git mv frontend-ui/visual-explainer content-publishing/ || true

# From backend-platform
git mv backend-platform/bootstrap agent-ops/ || true
git mv backend-platform/cli-spec product-strategy/ || true
git mv backend-platform/fix-mise agent-ops/ || true
git mv backend-platform/gh-workflow agent-ops/ || true
git mv backend-platform/simplify agent-ops/ || true
git mv backend-platform/using-git-worktrees agent-ops/ || true

# Javascript could be either. Moving to backend-platform
git mv agent-ops/javascript-pro backend-platform/ || true
