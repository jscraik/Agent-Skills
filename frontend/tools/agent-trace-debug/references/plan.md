# Plan for Agent Trace Debug

This skill is intentionally instruction-only and small.

Plan used:
1. Scaffold a new Codex skill folder under `.agents/skills/agent-trace-debug`.
2. Rewrite `SKILL.md` to match the requested “exact sequence” debugging workflow.
3. Add eval prompts (`references/evals.yaml`) to lock down triggers and required outputs.
4. Run `quick_validate.py`, `skill_gate.py`, and `run_skill_evals.py` and fix any failures.
