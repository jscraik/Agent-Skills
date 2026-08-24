"""Route successful human-facing CLI output to focused renderers."""

from types import MappingProxyType

from ask.cli_human_success_misc import (
    render_evals_success,
    render_graph_success,
    render_mcp_success,
    render_memory_success,
    render_plugins_success,
    render_reviewer_success,
    render_runtime_success,
    render_wiki_success,
    render_workouts_success,
)
from ask.cli_human_success_repo import render_repo_success
from ask.cli_human_success_skills import render_skills_success


_TOPIC_RENDERERS = MappingProxyType(
    {
        "repo": render_repo_success,
        "skills": render_skills_success,
        "plugins": render_plugins_success,
        "evals": render_evals_success,
        "mcp": render_mcp_success,
        "memory": render_memory_success,
        "reviewers": render_reviewer_success,
        "runtime": render_runtime_success,
        "wiki": render_wiki_success,
        "workouts": render_workouts_success,
        "graph": render_graph_success,
    }
)


def render_success(_parser, args, result):
    renderer = _TOPIC_RENDERERS.get(args.topic)
    if renderer is not None:
        renderer(args, result)
