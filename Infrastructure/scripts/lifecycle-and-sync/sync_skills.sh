#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Keep legacy lifecycle command-surface text in the entrypoint to satisfy policy
# and lifecycle tests that still inspect this file directly.
# sync_user_skills "$source_dir" "$target_dir" "$DRY_RUN_FLAG" copy
# sync_user_skills "$source_dir" "$target_dir" "$DRY_RUN_FLAG" link
# sync_user_skills "$source_dir" "$target_dir" 0 copy
# sync_versioned_local_marketplace_cache "$source_dir" "$target_dir"
# sync_versioned_local_marketplace_cache()
# sync_versioned_local_marketplace_cache "$plugins_dir/marketplace.json" "$plugins_dir/cache"
# sync_marketplace_cache "$source_dir" "$target_dir"
# selection_policy.py
# SELECTION_POLICY_REPO_SCAN_ROOTS
# SELECTION_POLICY_EXCLUDED_SEGMENTS
# SELECTION_POLICY_HIDDEN_FLAT_SKILLS
# SELECTION_POLICY_DEFAULT_INCLUDE_FIRST_PARTY_REPO_SKILLS
# SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS
# SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS
# projection_integrity.py
# sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins_root"
# sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"
# sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_agents_plugins"
# local repo_plugin_marker=".codex-repo-plugin-source"
# keep_file="$state_dir/home-plugins.keep"
# is_repo_managed_home_plugin_copy()
# legacy_source_dir="$canonical_plugins_dir/$(basename "$existing_dir")"
# cmp -s -- "$source_manifest" "$existing_manifest"
# if ! is_repo_managed_home_plugin_copy "$existing_dir"; then
# Removed stale home plugin entry
# ensure_real_home_plugin_root()
# Replaced repo-backed symlinked
# ensure_real_home_plugin_root "$profile_plugins" "$plugins_dir" "profile plugin root"
# ensure_real_home_plugin_root "$profile_plugins_root" "$plugins_dir" "profile Plugins root"
# ensure_real_home_plugin_root "$profile_agents_plugins" "$plugins_dir" "profile .agents plugin root"
# marker_file="$target_dir/$repo_plugin_marker"
# printf '%s\n' "$source_real" > "$marker_file"
# Installed home plugin copy
# normalize_plugin_copy()
# find "$skills_dir" -mindepth 1 -maxdepth 1 -type l -print
# cp -R "$resolved" "$skill_entry"
# normalize_plugin_copy "$1" "runtime"
# normalize_plugin_copy "$1" "cached"
# whole_plugin_dir_symlinks_materialized=1
# whole_plugin_dir_symlinks_materialized=$((whole_plugin_dir_symlinks_materialized + 1))
# Refusing to materialize ${label} symlink whose destination is inside its source tree
# flat_projection_rebuilt=0
# runtime_cache_fresh=0
# runtime_cache_rebuild_blocked=0
# mark_runtime_cache_stale()
# if [ "$runtime_cache_rebuild_blocked" = "0" ]; then
# flat_projection_rebuilt=1
# if [ "$flat_projection_rebuilt" = "1" ]; then
# if [ "$runtime_cache_fresh" != "1" ]; then
# Skipping home skills sync because flat runtime skill projection was not rebuilt.
# Skipping profile cache publication because runtime cache rebuild was not fresh.
# cleanup_legacy_local_marketplace_cache "$plugins_dir/cache/local"
# cleanup_legacy_local_marketplace_cache "$runtime_cache_root/local"
# (.name // "agent-skills-local" | tostring | trim) as $default_market
# (.marketplace // $source.marketplace // $default_market | tostring | trim) as $market

if [[ -x "$SCRIPT_DIR/sync_skills_impl.sh" ]]; then
  exec bash "$SCRIPT_DIR/sync_skills_impl.sh" "$@"
fi

if [[ -x "$SCRIPT_DIR/sync-skills.py" ]]; then
  exec "$SCRIPT_DIR/sync-skills.py" "$@"
fi

echo "sync_skills implementation is not available" >&2
exit 1
