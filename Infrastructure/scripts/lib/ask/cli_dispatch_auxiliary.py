"""Small auxiliary topic dispatchers for the ask CLI."""

import ask.commands.skills as skills_commands

from ask.cli_errors import build_unknown_action_result
from ask.commands.graph import (
    graph_chain,
    graph_find,
    graph_info,
    graph_list,
    graph_related,
    graph_topics,
)
from ask.commands.mcp import sync_mcp
from ask.commands.memory import memory_list, memory_read, memory_search


def dispatch_reviewers(repo_root, args):
    """Run reviewer handle resolution."""
    if args.action == "resolve":
        return skills_commands.reviewers_resolve(repo_root, handle=args.handle)
    return build_unknown_action_result("reviewers", args.action)


def dispatch_graph(repo_root, args):
    """Run the selected graph query."""
    handlers = {
        "related": lambda: graph_related(
            repo_root,
            skill=args.skill,
            depth=args.depth,
            reverse=args.reverse,
            topic=args.topic_filter,
            tier=args.tier,
        ),
        "find": lambda: graph_find(
            repo_root, query=args.query, topic=args.topic_filter, tier=args.tier
        ),
        "info": lambda: graph_info(repo_root, skill=args.skill),
        "chain": lambda: graph_chain(
            repo_root, from_skill=args.from_skill, to_skill=args.to_skill
        ),
        "list": lambda: graph_list(repo_root, topic=args.topic_filter, tier=args.tier),
        "topics": lambda: graph_topics(repo_root),
    }
    handler = handlers.get(args.action)
    return handler() if handler else build_unknown_action_result("graph", args.action)


def dispatch_mcp(repo_root, args):
    """Run the selected MCP command."""
    if args.action == "sync":
        return sync_mcp(repo_root, dry_run=args.dry_run)
    return build_unknown_action_result("mcp", args.action)


def dispatch_memory(repo_root, args):
    """Run the selected memory command."""
    handlers = {
        "list": lambda: memory_list(
            repo_root, source_id=args.source_id, limit=args.limit
        ),
        "read": lambda: memory_read(repo_root, identifier=args.identifier),
        "search": lambda: memory_search(
            repo_root,
            query=args.query,
            source_id=args.source_id,
            limit=args.limit,
        ),
    }
    handler = handlers.get(args.action)
    return handler() if handler else build_unknown_action_result("memory", args.action)
