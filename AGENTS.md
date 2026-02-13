# agent-skills Agent Guide


<!-- AGENT-FIRST-SCAFFOLD:START -->
## Agent-First Scaffold Contract (managed by ~/.codex)

This repository participates in Jamie's global agent-first scaffold program.

Required global references:
- `/Users/jamiecraik/.codex/instructions/openai-agent-workflow-playbook.md`
- `/Users/jamiecraik/.codex/instructions/README.checklist.md`
- `/Users/jamiecraik/.codex/instructions/validator-contracts.md`
- `/Users/jamiecraik/.codex/instructions/strict-toggle-governance.md`
- `/Users/jamiecraik/.codex/instructions/agent-first-scaffold-spec.md`

Repo-level requirements:
- Maintain `.agent/PLANS.md` using `tasks / id / depends_on` contract.
- Validate plan files with:
  `python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py <plan-file>`
- Run canonical verification:
  `/Users/jamiecraik/.codex/scripts/verify-work.sh`

State model: `S0 -> S1 -> S2 -> S3 -> S4 -> S5` with rollback to `Sx` on critical governance events.
<!-- AGENT-FIRST-SCAFFOLD:END -->
