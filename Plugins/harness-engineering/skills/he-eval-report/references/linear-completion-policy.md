# Linear Completion Policy

Every Linear parent issue, milestone, or approved execution slice produced by
the Harness Engineering workflow needs a matching eval artifact before closure:

```text
.harness/evals/<repo-name>-<linear-parent-issue-or-milestone>-eval.md
```

The eval artifact is the Harness Engineering Definition of Done. Do not
recommend closure unless the report confirms:

- the implementation satisfies the approved execution slice
- required validation gates passed or have justified exceptions
- architectural invariants were preserved
- routing determinism was preserved
- context load did not regress without justification
- agent discoverability did not regress
- governance did not become heavier without clear value
- moat-critical behavior was preserved or improved
- proof artifacts are present or linked
- follow-up work is classified as `Now`, `Next`, `Later`, or `Do Not Create`

If the eval artifact is missing, incomplete, or materially failing, the Linear
completion recommendation must be one of:

```text
Blocked
Needs rework
Unsafe to close
```

Do not recommend closing Linear work when critical evals failed, drift
regression is unresolved, rollback conditions triggered, architecture invariants
were violated, proof artifacts are missing for high-risk work, the eval artifact
is missing or incomplete, or implementation deviates from approved scope without
documented approval.

The report must include:

```text
Linear Project:
Linear Milestone:
Linear Parent Issue:
Linear Sub-Issues:
Linear Status Recommendation:
Proof Artifact Links:
```

If a Linear identifier is missing, state whether the traceability gap blocks
completion and how to repair it.
