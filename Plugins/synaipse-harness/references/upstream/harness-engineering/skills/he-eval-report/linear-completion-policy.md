# Linear Completion Policy

Every HE parent issue, milestone, or approved execution slice needs a matching
artifact before closure:

```text
.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<linear-parent-issue-or-milestone>-eval.md

When no Linear issue is known, use the dated repo fallback:

```text
.harness/evals/YYYY-MM-DD-<repo-name>-<linear-parent-issue-or-milestone>-eval.md
```
```

Do not recommend closure unless the eval confirms scope satisfaction, passed or
justified validation gates, preserved architecture/routing/context/agent-native
invariants, simple governance, preserved moat behavior, linked proof artifacts,
and follow-up work classified as `Now`, `Next`, `Later`, or `Do Not Create`.

If the artifact is missing, incomplete, untraceable, or materially failing, the
recommendation must be `Blocked`, `Needs rework`, or `Unsafe to close`.

Required backlink fields: `Linear Project`, `Linear Milestone`, `Linear Parent
Issue`, `Linear Sub-Issues`, `Linear Status Recommendation`, and `Proof Artifact
Links`. Missing identifiers must include repair guidance and closure impact.
