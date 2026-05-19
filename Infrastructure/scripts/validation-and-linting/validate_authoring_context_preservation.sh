#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -P "$script_dir/../../.." && pwd -P)"
cd "$repo_root"

marker="Apply the context-disposition policy"

skills=(
  "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md"
  "skills-system/skill-creator/references/skill-factory/foundations.md"
  "skills-system/skill-installer/references/skill-factory/install-flows.md"
  "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md"
)

missing=0

has_fixed_text() {
  local needle="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -Fq "$needle" "$file"
  else
    grep -Fq "$needle" "$file"
  fi
}

has_regex_text() {
  local pattern="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -q "$pattern" "$file"
  else
    grep -Eq "$pattern" "$file"
  fi
}

echo "[authoring-context] validating authoring context-preservation contract"
for skill in "${skills[@]}"; do
  # Require a regular file so directory/symlink drift fails explicitly.
  if [[ ! -f "$skill" ]]; then
    echo "[authoring-context] ERROR: missing skill file: $skill"
    missing=1
    continue
  fi

  if ! has_fixed_text "$marker" "$skill"; then
    echo "[authoring-context] ERROR: marker missing in $skill"
    missing=1
  fi

  if ! has_regex_text 'references/' "$skill"; then
    echo "[authoring-context] ERROR: references signpost missing in $skill"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "[authoring-context] FAIL: context-preservation contract violations detected"
  exit 1
fi

echo "[authoring-context] pass: context-preservation contract satisfied"
