# Waived External CI Does Not Stop PR Rotation

## Scenario

The PM has explicitly waived Snyk because the service quota no longer carries
enough value for this project. The same PR sweep still has live non-waived
work:

- PR #296 reports `mergeStateStatus=DIRTY`, `mergeable_state=dirty`, and
  `rebaseable=false`.
- PR #113 is still a draft and has validated local review fixes that have not
  been committed or pushed.
- CodeRabbit and CircleCI evidence must remain separate from the waived Snyk
  lane.

## Expected Behavior

The agent should select `pr-green-sweep`, classify the Snyk quota as
`waived_external_ci`, and continue the action queue to the remaining
non-waived lanes.

The expected action queue includes:

- `needs_merge_conflict_strategy` for the dirty PR.
- `needs_user_decision` for the draft PR or approval to push the local patch.
- `waived_external_ci` for Snyk quota only.

## Failure Mode

The agent stops because Snyk repeats, deletes the heartbeat, or reports no
source-owned action while dirty mergeability, CodeRabbit review, draft state,
or cleanup proof still has a next safe action.

## Proof Signals

- URL-first PR cards include latest head SHA and merge state.
- Snyk is not treated as green and not treated as source-owned.
- The report names the next non-waived action lane before stopping.
