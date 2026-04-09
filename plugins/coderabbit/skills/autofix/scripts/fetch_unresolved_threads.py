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

GRAPHQL_QUERY = """
query($owner:String!, $repo:String!, $pr:Int!, $threadCursor:String, $commentCursor:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$pr) {
      reviewThreads(first:100, after:$threadCursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          isResolved
          path
          line
          startLine
          comments(first:10, after:$commentCursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
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


def _run_gh_graphql(owner: str, repo: str, pr: int, thread_cursor: str | None = None) -> dict[str, Any]:
    cmd = [
        "gh",
        "api",
        "graphql",
        "-F",
        f"owner={owner}",
        "-F",
        f"repo={repo}",
        "-F",
        f"pr={pr}",
        "-f",
        f"query={GRAPHQL_QUERY}",
    ]
    if thread_cursor is not None:
        cmd.extend(["-F", f"threadCursor={thread_cursor}"])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
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


def _extract_unresolved_threads(payload: dict[str, Any], thread_offset: int = 0) -> tuple[list[dict[str, Any]], bool, str | None]:
    root = (payload.get("data") or {}).get("repository", {}).get("pullRequest", {})
    if not isinstance(root, dict) or not root:
        raise RuntimeError("pull request not found in GitHub response")

    review_threads = (root.get("reviewThreads") or {})
    nodes = review_threads.get("nodes", [])
    page_info = review_threads.get("pageInfo", {})
    has_next = page_info.get("hasNextPage", False)
    end_cursor = page_info.get("endCursor")

    results: list[dict[str, Any]] = []

    for index, node in enumerate(nodes, start=thread_offset + 1):
        if node.get("isResolved") is True:
            continue

        comments = (node.get("comments") or {}).get("nodes", [])
        if not comments:
            continue

        matching_comment = None
        for comment in comments:
            author = (comment.get("author") or {}).get("login")
            if _is_coderabbit_author(author):
                matching_comment = comment
                break

        if matching_comment is None:
            continue

        results.append(
            {
                "thread_index": index,
                "comment_id": matching_comment.get("databaseId"),
                "author": (matching_comment.get("author") or {}).get("login"),
                "body": matching_comment.get("body", ""),
                "path": node.get("path"),
                "line": node.get("line"),
                "start_line": node.get("startLine"),
            }
        )
    return results, has_next, end_cursor


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, help="GitHub repository owner.")
    parser.add_argument("--repo", required=True, help="GitHub repository name.")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number.")
    args = parser.parse_args()

    try:
        all_unresolved: list[dict[str, Any]] = []
        thread_cursor: str | None = None
        thread_offset = 0

        while True:
            try:
                payload = _run_gh_graphql(args.owner, args.repo, args.pr, thread_cursor)
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(f"gh graphql request timed out after {exc.timeout}s") from exc

            unresolved, has_next, end_cursor = _extract_unresolved_threads(payload, thread_offset)
            all_unresolved.extend(unresolved)

            if not has_next or end_cursor is None:
                break

            thread_cursor = end_cursor
            thread_offset += 100

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