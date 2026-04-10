#!/usr/bin/env python3
"""Fetch unresolved CodeRabbit-authored review threads for a GitHub PR."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

CODERABBIT_AUTHORS = {
    "coderabbitai",
    "coderabbit[bot]",
    "coderabbitai[bot]",
}

GH_TIMEOUT_SECONDS = 30

GRAPHQL_REVIEW_THREADS_QUERY = """
query($owner:String!, $repo:String!, $pr:Int!, $cursor:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$pr) {
      reviewThreads(first:100, after:$cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          path
          line
          startLine
          comments(first:1) {
            nodes {
              databaseId
              body
              author { login }
            }
          }
        }
      }
    }
  }
}
"""

def _run_gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    cmd = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={query}",
    ]
    for key, value in variables.items():
        if value is None:
            continue
        cmd.extend(["-F", f"{key}={value}"])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=GH_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"gh graphql request timed out after {GH_TIMEOUT_SECONDS}s") from exc

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "gh graphql request failed")

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"failed to parse gh output: {exc}") from exc

    errors = payload.get("errors")
    if isinstance(errors, list) and errors:
        message = "; ".join(
            str(item.get("message") or "unknown GraphQL error")
            for item in errors
            if isinstance(item, dict)
        )
        raise RuntimeError(f"gh graphql returned errors: {message or 'unknown GraphQL error'}")

    return payload


def _is_coderabbit_author(login: Any) -> bool:
    if not isinstance(login, str):
        return False
    return login.strip().lower() in CODERABBIT_AUTHORS


def _dict_nodes(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [node for node in value if isinstance(node, dict)]


def _collect_review_threads(owner: str, repo: str, pr: int) -> list[dict[str, Any]]:
    cursor: str | None = None
    threads: list[dict[str, Any]] = []

    while True:
        payload = _run_gh_graphql(
            GRAPHQL_REVIEW_THREADS_QUERY,
            {
                "owner": owner,
                "repo": repo,
                "pr": pr,
                "cursor": cursor,
            },
        )

        root = (payload.get("data") or {}).get("repository", {}).get("pullRequest", {})
        if not isinstance(root, dict) or not root:
            raise RuntimeError("pull request not found in GitHub response")

        review_threads = root.get("reviewThreads") or {}
        nodes = review_threads.get("nodes", [])
        if not isinstance(nodes, list):
            raise RuntimeError("invalid reviewThreads nodes payload")
        threads.extend(_dict_nodes(nodes))

        page_info = review_threads.get("pageInfo") or {}
        has_next_page = bool(page_info.get("hasNextPage"))
        cursor = page_info.get("endCursor")
        if not has_next_page:
            break
        if not isinstance(cursor, str) or not cursor:
            raise RuntimeError("missing reviewThreads endCursor during pagination")

    return threads


def _get_root_comment(thread: dict[str, Any]) -> dict[str, Any] | None:
    comments_conn = thread.get("comments") or {}
    nodes = _dict_nodes(comments_conn.get("nodes", []))
    if not nodes:
        return None
    return nodes[0]


def _extract_unresolved_threads(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(threads, list):
        raise RuntimeError("invalid review thread payload")

    results: list[dict[str, Any]] = []
    for index, thread in enumerate(threads, start=1):
        if thread.get("isResolved") is True:
            continue

        root_comment = _get_root_comment(thread)
        if root_comment is None:
            continue

        author = (root_comment.get("author") or {}).get("login")
        if not _is_coderabbit_author(author):
            continue

        results.append(
            {
                "thread_index": index,
                "comment_id": root_comment.get("databaseId"),
                "author": author,
                "body": root_comment.get("body", ""),
                "path": thread.get("path"),
                "line": thread.get("line"),
                "start_line": thread.get("startLine"),
            }
        )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, help="GitHub repository owner.")
    parser.add_argument("--repo", required=True, help="GitHub repository name.")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number.")
    args = parser.parse_args()

    try:
        threads = _collect_review_threads(args.owner, args.repo, args.pr)
        all_unresolved = _extract_unresolved_threads(threads)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "schema_version": 1,
                "owner": args.owner,
                "repo": args.repo,
                "pr": args.pr,
                "unresolved_count": len(all_unresolved),
                "unresolved_threads": all_unresolved,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())