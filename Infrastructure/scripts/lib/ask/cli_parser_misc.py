"""Graph, memory, MCP, and wiki parser registration."""

from __future__ import annotations

import argparse


def _add_graph_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--topic-filter", dest="topic_filter", help="Filter by topic")
    parser.add_argument(
        "--tier", choices=["stable", "growing", "experimental"], help="Filter by tier"
    )


def add_graph_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    """Register skill-graph discovery commands."""
    graph = subparsers.add_parser(
        "graph", help="Skill graph navigation and discovery", parents=[global_parser]
    )
    actions = graph.add_subparsers(dest="action")
    related = actions.add_parser(
        "related", help="Find related skills", parents=[global_parser]
    )
    related.add_argument("skill", help="Skill name to find relations for")
    related.add_argument("--depth", type=int, default=1, help="BFS depth")
    related.add_argument(
        "--reverse", action="store_true", help="Follow in-links instead of out-links"
    )
    _add_graph_filters(related)
    find = actions.add_parser("find", help="Search for skills", parents=[global_parser])
    find.add_argument("query", help="Search query")
    _add_graph_filters(find)
    actions.add_parser(
        "info", help="Show skill details", parents=[global_parser]
    ).add_argument("skill", help="Skill name")
    _add_graph_tail(actions, global_parser)


def _add_graph_tail(actions, global_parser: argparse.ArgumentParser) -> None:
    chain = actions.add_parser(
        "chain", help="Find path between skills", parents=[global_parser]
    )
    chain.add_argument("from_skill", help="Starting skill")
    chain.add_argument("to_skill", help="Target skill")
    listing = actions.add_parser(
        "list", help="List all skills in graph", parents=[global_parser]
    )
    _add_graph_filters(listing)
    actions.add_parser(
        "topics", help="List all topic clusters", parents=[global_parser]
    )


def _add_mcp_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    parser = subparsers.add_parser(
        "mcp", help="MCP configuration management", parents=[global_parser]
    )
    actions = parser.add_subparsers(dest="action")
    sync = actions.add_parser(
        "sync",
        help="Sync MCP config from Codex to Codex JSON export",
        parents=[global_parser],
    )
    sync.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing"
    )


def _add_memory_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    parser = subparsers.add_parser(
        "memory", help="Read-only repo memory provider", parents=[global_parser]
    )
    actions = parser.add_subparsers(dest="action")
    listing = actions.add_parser(
        "list",
        help="List Project Brain and skill learning entries",
        parents=[global_parser],
    )
    listing.add_argument(
        "--source", dest="source_id", help="Filter by memory source id"
    )
    listing.add_argument("--limit", type=int, default=50, help="Max entries to return")
    read = actions.add_parser(
        "read", help="Read one memory entry by id or path", parents=[global_parser]
    )
    read.add_argument("identifier", help="Memory entry id or repo-relative path")
    search = actions.add_parser(
        "search",
        help="Search Project Brain and skill learning entries",
        parents=[global_parser],
    )
    search.add_argument("query", help="Search query")
    search.add_argument("--source", dest="source_id", help="Filter by memory source id")
    search.add_argument("--limit", type=int, default=10, help="Max results to return")


def add_mcp_and_memory_commands(
    subparsers, global_parser: argparse.ArgumentParser
) -> None:
    """Register MCP and read-only memory commands."""
    _add_mcp_commands(subparsers, global_parser)
    _add_memory_commands(subparsers, global_parser)


def _add_wiki_lint(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "lint", help="Lint wiki links and freshness", parents=[global_parser]
    )
    parser.add_argument("--wiki-root", default="Wiki/wiki", help="Wiki root path")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=60,
        help="Max last_reviewed age before warning",
    )


def _add_wiki_ingest(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "ingest", help="Ingest raw source notes into wiki logs", parents=[global_parser]
    )
    parser.add_argument("title", help="Ingest title")
    parser.add_argument(
        "--source", action="append", default=[], help="Source reference (repeatable)"
    )
    parser.add_argument("--summary", required=True, help="One-paragraph summary")
    parser.add_argument("--tag", action="append", default=[], help="Tag (repeatable)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview output without writing"
    )


def _add_wiki_add_core(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("title", nargs="?", help="Note title")
    parser.add_argument("--summary", help="Summary text")
    parser.add_argument("--source", help="Primary source reference")
    parser.add_argument(
        "--intent",
        choices=["finding", "playbook", "design-asset", "lesson-learned"],
        help="Triage intent",
    )
    parser.add_argument(
        "--status",
        choices=["needs-verification", "verified", "fix-now"],
        help="Current status",
    )


def _add_wiki_add_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--destination",
        choices=["failures", "playbooks", "assets/ui", "learnings"],
        help="Override destination folder under Wiki/wiki",
    )
    parser.add_argument("--tag", action="append", default=[], help="Tag (repeatable)")
    parser.add_argument(
        "--interactive", action="store_true", help="Prompt for missing triage fields"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview output without writing"
    )


def _add_wiki_add(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "add", help="Triage and add a structured wiki note", parents=[global_parser]
    )
    _add_wiki_add_core(parser)
    _add_wiki_add_options(parser)


def _add_wiki_query(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "query", help="Search wiki pages", parents=[global_parser]
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Max results to return")
    parser.add_argument("--wiki-root", default="Wiki/wiki", help="Wiki root path")


def _add_wiki_asset_core(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("asset_path", nargs="?", help="Path to local asset file")
    parser.add_argument("--title", help="Asset note title")
    parser.add_argument("--summary", help="Summary for why this asset matters")
    parser.add_argument(
        "--source", default="", help="Original source reference (optional)"
    )
    parser.add_argument(
        "--status",
        choices=["needs-verification", "verified", "fix-now"],
        help="Current status",
    )


def _add_wiki_asset_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--destination",
        choices=["assets/ui", "learnings"],
        help="Destination folder under wiki",
    )
    parser.add_argument("--tag", action="append", default=[], help="Tag (repeatable)")
    parser.add_argument(
        "--interactive", action="store_true", help="Prompt for missing asset fields"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview output without writing"
    )


def _add_wiki_asset(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "add-asset",
        help="Add screenshot/asset to wiki and create linked note",
        parents=[global_parser],
    )
    _add_wiki_asset_core(parser)
    _add_wiki_asset_options(parser)


def add_wiki_commands(subparsers, global_parser: argparse.ArgumentParser) -> None:
    """Register wiki operations."""
    wiki = subparsers.add_parser(
        "wiki", help="Skill Ops Wiki operations", parents=[global_parser]
    )
    actions = wiki.add_subparsers(dest="action")
    _add_wiki_lint(actions, global_parser)
    _add_wiki_ingest(actions, global_parser)
    _add_wiki_add(actions, global_parser)
    _add_wiki_query(actions, global_parser)
    _add_wiki_asset(actions, global_parser)
