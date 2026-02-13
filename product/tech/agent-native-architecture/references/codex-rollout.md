# Codex Rollout and Rollback

## Rollout steps

1. Ensure canonical skill path exists in repo.
2. Sync skill symlinks/index:
   - `/Users/jamiecraik/dev/agent-skills/scripts/sync_skills.sh`
3. Confirm skill appears in flat skills view:
   - `/Users/jamiecraik/dev/agent-skills/skills/agent-native-architecture`
4. Verify explicit invocation in Codex:
   - `$agent-native-architecture ...`
5. Run evals and validation gates before broad adoption.

## Collision handling

If duplicate skill names exist across active scopes:

1. Rename this skill to `agent-native-architecture-codex`.
2. Re-run sync and validators.
3. Re-run trigger evals and ensure precision targets remain met.

## Kill switch / rollback

Disable without deleting files using `~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/Users/jamiecraik/dev/agent-skills/product/tech/agent-native-architecture/SKILL.md"
enabled = false
```

Then restart Codex and verify the skill no longer appears/activates.

If full rollback is required:

1. Remove/rename canonical folder.
2. Re-run `scripts/sync_skills.sh`.
3. Confirm symlink and index removal.
