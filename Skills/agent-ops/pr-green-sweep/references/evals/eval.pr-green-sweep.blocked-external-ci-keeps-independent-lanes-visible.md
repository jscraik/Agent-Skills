# Blocked External CI Keeps Independent PR Lanes Visible

## Scenario

Snyk reports an unauthenticated external-service failure. The same PR sweep
still has separate work:

- PR #296 reports `mergeStateStatus=DIRTY`, `mergeable_state=dirty`, and
  `rebaseable=false`.
- PR #113 is a draft with validated local review fixes that have not been
  committed or pushed.
- CodeRabbit and CircleCI evidence remain separate from the Snyk failure.

## Expected Behavior

Select `pr-green-sweep`, classify Snyk as `blocked_external_ci`, and keep the
remaining independent lanes visible. The failure blocks the affected PR's
merge; it is neither green nor a source-owned defect.

The action queue includes:

- `needs_merge_conflict_strategy` for the dirty PR.
- `needs_user_decision` for the draft PR or approval to push its local patch.
- `blocked_external_ci` for Snyk only.

## Failure Mode

The agent relabels Snyk as green or source-owned, or stops with no next action
while dirty mergeability, CodeRabbit review, draft state, or cleanup proof has
a safe next action.

## Proof Signals

- URL-first PR cards include latest head SHA and merge state.
- Snyk is explicitly external and blocks only the affected merge.
- The report names the next independent action lane before stopping.
