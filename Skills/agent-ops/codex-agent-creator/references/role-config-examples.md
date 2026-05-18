# Role Config Examples

Use these examples after deciding that a Codex agent role is the right artifact.
Keep source role files, config wiring, and runtime spawn calls separate.

## Standalone Role File

~~~toml
name = "repo-researcher"
description = "Researches repository structure, conventions, and implementation patterns before code changes."
developer_instructions = """
You are a read-only repository researcher.
Answer with exact file paths, line references, and commands inspected.
Do not edit files, install dependencies, or mutate external systems.
"""
model = "gpt-5.3-codex"
model_reasoning_effort = "medium"
~~~

## Config Registration

~~~toml
[agents.repo_researcher]
description = "Researches repository structure, conventions, and implementation patterns before code changes."
config_file = "agents/repo-researcher.toml"
nickname_candidates = ["repo", "research"]
~~~

## Spawn Shape

~~~json
{
  "task_name": "repo_research",
  "agent_type": "repo_researcher",
  "message": "Inspect the repository conventions for validation commands. Return exact file paths and a short recommendation.",
  "reasoning_effort": "medium"
}
~~~

Only set model or reasoning_effort in a spawn request when the task or user
explicitly needs the override. Prefer the role's default otherwise.
