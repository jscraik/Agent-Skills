#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/dev"
TOP=12

while (($# > 0)); do
  case "$1" in
    --root)
      ROOT="${2:-}"
      shift 2
      ;;
    --top)
      TOP="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      echo "usage: $0 [--root <path>] [--top <n>]" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$ROOT" ]]; then
  echo "root path must not be empty" >&2
  exit 2
fi

if [[ ! -d "$ROOT" ]]; then
  echo "root path not found: $ROOT" >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

repo_file="$tmp_dir/repos.txt"
score_file="$tmp_dir/repo_scores.txt"
package_file="$tmp_dir/package_files.txt"

if command -v fd >/dev/null 2>&1; then
  fd -H -t d '^\.git$' "$ROOT" | sed -E 's#/\.git/?$##' | sort -u > "$repo_file"
else
  find "$ROOT" -type d -name .git -prune | sed -E 's#/\.git/?$##' | sort -u > "$repo_file"
fi

repo_count="$(wc -l < "$repo_file" | tr -d ' ')"

markers=(
  "AGENTS.md"
  "scripts/check-environment.sh"
  ".codex/environments/environment.toml"
  "scripts/codex-preflight.sh"
  "scripts/verify-work.sh"
  ".harness/ci-required-checks.json"
  "harness.contract.json"
  "docs/agents/tooling.md"
)

echo "style_scan.root=$ROOT"
echo "style_scan.repo_count=$repo_count"

for marker in "${markers[@]}"; do
  count=0
  while IFS= read -r repo; do
    if [[ -e "$repo/$marker" ]]; then
      count=$((count + 1))
    fi
  done < "$repo_file"
  echo "marker.$marker=$count"
done

while IFS= read -r repo; do
  score=0
  for marker in "${markers[@]}"; do
    if [[ -e "$repo/$marker" ]]; then
      score=$((score + 1))
    fi
  done
  printf '%s\t%s\n' "$score" "$repo" >> "$score_file"
done < "$repo_file"

echo "top_repos.begin"
sort -nr "$score_file" | head -n "$TOP" | while IFS=$'\t' read -r score repo; do
  echo "top_repo.score=$score path=$repo"
done
echo "top_repos.end"

if command -v fd >/dev/null 2>&1; then
  fd -a -t f 'package.json' "$ROOT" > "$package_file"
else
  find "$ROOT" -type f -name package.json > "$package_file"
fi

package_count="$(wc -l < "$package_file" | tr -d ' ')"
echo "node.package_json_count=$package_count"

npm_count=0
pnpm_count=0
yarn_count=0
other_count=0

if [[ "$package_count" -gt 0 ]] && command -v jq >/dev/null 2>&1; then
  while IFS= read -r package_path; do
    package_manager="$(jq -r '.packageManager // empty' "$package_path" 2>/dev/null || true)"
    case "$package_manager" in
      npm@*) npm_count=$((npm_count + 1)) ;;
      pnpm@*) pnpm_count=$((pnpm_count + 1)) ;;
      yarn@*) yarn_count=$((yarn_count + 1)) ;;
      "")
        ;;
      *) other_count=$((other_count + 1)) ;;
    esac
  done < "$package_file"
  echo "node.package_manager.npm=$npm_count"
  echo "node.package_manager.pnpm=$pnpm_count"
  echo "node.package_manager.yarn=$yarn_count"
  echo "node.package_manager.other=$other_count"
else
  echo "node.package_manager.parse_status=jq_unavailable_or_no_package_json"
fi

if command -v fd >/dev/null 2>&1; then
  npm_lock_count="$(fd -a -t f 'package-lock.json' "$ROOT" | wc -l | tr -d ' ')"
  pnpm_lock_count="$(fd -a -t f 'pnpm-lock.yaml' "$ROOT" | wc -l | tr -d ' ')"
  yarn_lock_count="$(fd -a -t f 'yarn.lock' "$ROOT" | wc -l | tr -d ' ')"
  pyproject_count="$(fd -a -t f 'pyproject.toml' "$ROOT" | wc -l | tr -d ' ')"
  uv_lock_count="$(fd -a -t f 'uv.lock' "$ROOT" | wc -l | tr -d ' ')"
else
  npm_lock_count="$(find "$ROOT" -type f -name package-lock.json | wc -l | tr -d ' ')"
  pnpm_lock_count="$(find "$ROOT" -type f -name pnpm-lock.yaml | wc -l | tr -d ' ')"
  yarn_lock_count="$(find "$ROOT" -type f -name yarn.lock | wc -l | tr -d ' ')"
  pyproject_count="$(find "$ROOT" -type f -name pyproject.toml | wc -l | tr -d ' ')"
  uv_lock_count="$(find "$ROOT" -type f -name uv.lock | wc -l | tr -d ' ')"
fi

echo "lockfiles.package-lock.json=$npm_lock_count"
echo "lockfiles.pnpm-lock.yaml=$pnpm_lock_count"
echo "lockfiles.yarn.lock=$yarn_lock_count"
echo "python.pyproject.toml=$pyproject_count"
echo "python.uv.lock=$uv_lock_count"
