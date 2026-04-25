#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -P -- "$SCRIPT_DIR/../../.." && pwd -P)"
cd "$REPO_ROOT"

INDEX_PATH='Plugins/harness-engineering/references/deferred-context-index.md'
INVARIANT_MARKER='Do not remove important context for budget trimming'
LINK_MARKER='deferred-context-index.md'

resolve_base_ref() {
  local base_ref=""
  if git rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
    base_ref="$(git merge-base HEAD '@{upstream}')"
  else
    local candidate
    for candidate in origin/main origin/master main master; do
      if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
        base_ref="$(git merge-base HEAD "$candidate")"
        break
      fi
    done
  fi

  if [[ -z "$base_ref" ]]; then
    if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
      base_ref="HEAD^"
    else
      base_ref=""
    fi
  fi

  printf '%s' "$base_ref"
}

# collect_changed_he_skills prints changed Plugins/harness-engineering SKILL.md file paths (one per line), optionally including diffs relative to the provided base_ref; files under Plugins/harness-engineering/fixtures/preserved-context/ are ignored.
collect_changed_he_skills() {
  local base_ref="$1"
  local -a all_changed=()
  local path

  if [[ -n "$base_ref" ]]; then
    while IFS= read -r path; do
      [[ -n "$path" ]] && all_changed+=("$path")
    done < <(git diff --name-only --diff-filter=ACMR "$base_ref"...HEAD --)
  fi

  while IFS= read -r path; do
    [[ -n "$path" ]] && all_changed+=("$path")
  done < <(git diff --name-only --diff-filter=ACMR --)

  while IFS= read -r path; do
    [[ -n "$path" ]] && all_changed+=("$path")
  done < <(git diff --cached --name-only --diff-filter=ACMR --)

  if [[ ${#all_changed[@]} -eq 0 ]]; then
    return 0
  fi

  printf '%s\n' "${all_changed[@]}" \
    | awk '
        /^Plugins\/harness-engineering\/fixtures\/preserved-context\// { next }
        /^Plugins\/harness-engineering\/(skills\/.+\/SKILL\.md|fixtures\/.+\/skills\/.+\/SKILL(\.full)?\.md)$/ { print }
      ' \
    | sort -u
}

numstat_added_deleted() {
  local base_ref="$1"
  local target="$2"
  local added=0
  local deleted=0
  local a d p

  if [[ -n "$base_ref" ]]; then
    while IFS=$'\t' read -r a d p; do
      [[ "$a" =~ ^[0-9]+$ ]] && added=$((added + a))
      [[ "$d" =~ ^[0-9]+$ ]] && deleted=$((deleted + d))
    done < <(git diff --numstat "$base_ref"...HEAD -- "$target")
  fi

  while IFS=$'\t' read -r a d p; do
    [[ "$a" =~ ^[0-9]+$ ]] && added=$((added + a))
    [[ "$d" =~ ^[0-9]+$ ]] && deleted=$((deleted + d))
  done < <(git diff --numstat -- "$target")

  while IFS=$'\t' read -r a d p; do
    [[ "$a" =~ ^[0-9]+$ ]] && added=$((added + a))
    [[ "$d" =~ ^[0-9]+$ ]] && deleted=$((deleted + d))
  done < <(git diff --cached --numstat -- "$target")

  printf '%s %s\n' "$added" "$deleted"
}

# collect_unified_diff outputs unified diffs with zero context for the given target: the diff from `base_ref...HEAD` if `base_ref` is non-empty, then the working tree diff, and finally the staged (index) diff.
collect_unified_diff() {
  local base_ref="$1"
  local target="$2"
  if [[ -n "$base_ref" ]]; then
    git diff --unified=0 "$base_ref"...HEAD -- "$target"
  fi
  git diff --unified=0 -- "$target"
  git diff --cached --unified=0 -- "$target"
}

# append_candidate adds a candidate path to the referenced array and, if that candidate is a symlink whose target exists, also appends a normalized resolved path relative to REPO_ROOT.
append_candidate() {
  local -n candidate_list="$1"
  local candidate="$2"
  candidate_list+=("$candidate")

  if [[ ! -L "$candidate" ]]; then
    return 0
  fi

  local link_target resolved resolved_dir
  link_target="$(readlink "$candidate")" || return 0
  if [[ "$link_target" = /* ]]; then
    resolved="$link_target"
  else
    resolved="$(dirname -- "$candidate")/$link_target"
  fi

  if [[ ! -e "$resolved" ]]; then
    return 0
  fi

  resolved_dir="$(cd -P -- "$(dirname -- "$resolved")" && pwd -P)" || return 0
  candidate_list+=("${resolved_dir#$REPO_ROOT/}/$(basename -- "$resolved")")
}

# has_context_move_evidence determines whether any non-blank lines removed from a SKILL.md file reappear verbatim as added lines in the repository's reference candidates (the global INDEX_PATH plus files under the skill's references and Infrastructure/references), returning success (0) if at least one removed line is found and failure (1) otherwise.
has_context_move_evidence() {
  local base_ref="$1"
  local skill_path="$2"
  local skill_dir
  skill_dir="$(dirname "$skill_path")"
  local ref_dir="${skill_dir}/references"
  local infra_ref_dir="${skill_dir}/Infrastructure/references"
  local candidates=()
  local f

  append_candidate candidates "$INDEX_PATH"

  if [[ -d "$ref_dir" ]]; then
    while IFS= read -r -d '' f; do
      candidates+=("${f#$REPO_ROOT/}")
    done < <(find -L "$ref_dir" -type f -print0)
  fi
  if [[ -d "$infra_ref_dir" ]]; then
    while IFS= read -r -d '' f; do
      candidates+=("${f#$REPO_ROOT/}")
    done < <(find -L "$infra_ref_dir" -type f -print0)
  fi

  local target added deleted
  local moved_line added_blob
  local removed_lines=()
  while IFS= read -r moved_line; do
    [[ -n "$moved_line" ]] && removed_lines+=("$moved_line")
  done < <(
    collect_unified_diff "$base_ref" "$skill_path" \
      | awk '
          /^--- / || /^\+\+\+ / || /^@@/ {next}
          /^-/ {line=substr($0,2); if (line !~ /^[[:space:]]*$/) print line}
        ' \
      | sort -u
  )
  if [[ ${#removed_lines[@]} -eq 0 ]]; then
    return 0
  fi

  for target in "${candidates[@]}"; do
    read -r added deleted < <(numstat_added_deleted "$base_ref" "$target")
    if (( added <= 0 )); then
      continue
    fi
    added_blob="$(
      collect_unified_diff "$base_ref" "$target" \
        | awk '
            /^--- / || /^\+\+\+ / || /^@@/ {next}
            /^\+/ {line=substr($0,2); if (line !~ /^[[:space:]]*$/) print line}
          '
    )"
    for moved_line in "${removed_lines[@]}"; do
      if printf '%s\n' "$added_blob" | grep -Fqx -- "$moved_line"; then
        return 0
      fi
    done
  done

  return 1
}

base_ref="$(resolve_base_ref)"
changed_skills=()
while IFS= read -r skill_path; do
  [[ -n "$skill_path" ]] && changed_skills+=("$skill_path")
done < <(collect_changed_he_skills "$base_ref")

if [[ ${#changed_skills[@]} -eq 0 ]]; then
  echo "[he-progressive] pass: no changed harness-engineering SKILL.md files detected"
  exit 0
fi

echo "[he-progressive] validating ${#changed_skills[@]} changed harness-engineering SKILL.md files"

failures=0
for skill_file in "${changed_skills[@]}"; do
  if [[ ! -f "$skill_file" ]]; then
    continue
  fi

  if ! grep -Fq "$LINK_MARKER" "$skill_file"; then
    echo "[he-progressive] ERROR: $skill_file must link to deferred context index ($INDEX_PATH)"
    ((failures += 1))
  fi

  if ! grep -Fq "$INVARIANT_MARKER" "$skill_file"; then
    echo "[he-progressive] ERROR: $skill_file must include invariant marker: '$INVARIANT_MARKER'"
    ((failures += 1))
  fi

  read -r added deleted < <(numstat_added_deleted "$base_ref" "$skill_file")
  if (( deleted > 0 )); then
    if ! has_context_move_evidence "$base_ref" "$skill_file"; then
      echo "[he-progressive] ERROR: $skill_file removed ${deleted} line(s) but no added context was found in references or $INDEX_PATH"
      ((failures += 1))
    fi
  fi
done

if (( failures > 0 )); then
  echo "[he-progressive] FAIL: progressive-disclosure contract violations detected"
  exit 1
fi

echo "[he-progressive] pass: progressive-disclosure contract satisfied"
