#!/usr/bin/env bash
set -ex

cd /Users/jamiecraik/dev/Agent-Skills

# Restore skills-system root
mkdir -p skills-system
git mv Skills/skills-system/imagegen skills-system/ || true
git mv Skills/skills-system/openai-docs skills-system/ || true
rmdir Skills/skills-system || true

# Move Docs/product/security/*
git mv Docs/product/security/security-threat-model Skills/security-ops/ || true
git mv Docs/product/security/security-best-practices Skills/security-ops/ || true
git mv Docs/product/security/security-ownership-map Skills/security-ops/ || true

# Move Docs/product/specs/*
git mv Docs/product/specs/product-spec Skills/product-strategy/ || true

# Move Docs/product/content/*
git mv Docs/product/content/changelog Skills/content-publishing/ || true
git mv Docs/product/content/youtube-hooks-scripts Skills/content-publishing/ || true
git mv Docs/product/content/every-style-editor Skills/content-publishing/ || true
git mv Docs/product/content/feature-video Skills/content-publishing/ || true
git mv Docs/product/content/youtube-titles-thumbnails Skills/content-publishing/ || true
git mv Docs/product/content/video-transcript-downloader Skills/content-publishing/ || true

# Move Docs/product/docs/*
git mv Docs/product/docs/context7 Skills/agent-ops/ || true
git mv Docs/product/docs/agents-md Skills/agent-ops/ || true
git mv Docs/product/docs/llm-wiki Skills/content-publishing/ || true
git mv Docs/product/docs/docs-expert Skills/agent-ops/ || true

# Move Docs/product/review/*
git mv Docs/product/review/agent-native-audit Skills/agent-ops/ || true

# Move Docs/product/ops/*
git mv Docs/product/ops/fallback-release Skills/agent-ops/ || true
git mv Docs/product/ops/release Skills/agent-ops/ || true
git mv Docs/product/ops/triage Skills/agent-ops/ || true
git mv Docs/product/ops/resolve-todo-parallel Skills/agent-ops/ || true
git mv Docs/product/ops/production-deployment Skills/agent-ops/ || true
git mv Docs/product/ops/decide-build-primitive Skills/agent-ops/ || true

# Move Docs/product/domain/*
git mv Docs/product/domain/agent-native-architecture Skills/backend-platform/ || true
git mv Docs/product/domain/oak-api Skills/backend-platform/ || true
git mv Docs/product/domain/chatgpt-apps Skills/product-strategy/ || true

# Move Docs/product/strategy/*
git mv Docs/product/strategy/project-improver Skills/product-strategy/ || true
git mv Docs/product/strategy/product-design-critic Skills/product-strategy/ || true
git mv Docs/product/strategy/brainstorming Skills/product-strategy/ || true
