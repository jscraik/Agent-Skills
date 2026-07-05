#!/usr/bin/env bash
set -euo pipefail

state_dir="${WORKOUT_STATE_DIR:?WORKOUT_STATE_DIR is required}"
mkdir -p "$state_dir"
cat > "$state_dir/sdk_pipeline.env" <<STATE
skill=skill-builder
source=Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md
workout=skill-factory/skill-builder-sdk-pipeline
STATE
