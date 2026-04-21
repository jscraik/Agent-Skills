#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -P "$script_dir/../../.." && pwd -P)"
cd "$repo_root"

marker="Do not remove important context for budget trimming"

skills=(
  "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md"
  "Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md"
  "Plugins/skill-factory/skills/infrastructure_ops/skill-installer/SKILL.md"
  "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md"
)

missing=0

echo "[authoring-context] validating authoring context-preservation contract"
for skill in "${skills[@]}"; do
  if [[ ! -f "$skill" ]]; then
    echo "[authoring-context] ERROR: missing skill file: $skill"
    missing=1
    continue
  fi

  if ! rg -Fq "$marker" "$skill"; then
    echo "[authoring-context] ERROR: marker missing in $skill"
    missing=1
  fi

  if ! rg -q 'references/' "$skill"; then
    echo "[authoring-context] ERROR: references signpost missing in $skill"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "[authoring-context] FAIL: context-preservation contract violations detected"
  exit 1
fi

echo "[authoring-context] pass: context-preservation contract satisfied"
