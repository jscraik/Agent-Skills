# Authority Replay Evaluation

Given a repository-owned cleanup receipt, the preview command should report a
receipt status of `preview`, preserve `mutation_performed: false` for cleanup,
and leave the fixture snapshot unchanged. This reference is an eval route, not
an instruction to execute a mutation or claim registry readiness.
