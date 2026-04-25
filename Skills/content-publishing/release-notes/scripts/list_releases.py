#!/usr/bin/env python3
"""List GitHub releases for the release-notes skill."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_API_BASE = "https://api.github.com"
PR_RE = re.compile(r"(?:\[#(?P<bracket>\d+)\]|/pull/(?P<pull>\d+)|#(?P<hash>\d+))")
ALLOWED_API_BASES = {DEFAULT_API_BASE}


def emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def infer_repo_from_git() -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError:
        return None
    remote = result.stdout.strip()
    if not remote:
        return None
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def parse_repo(repo: str | None) -> tuple[str, str] | None:
    if not repo:
        return None
    cleaned = repo.strip().removesuffix(".git")
    if cleaned.startswith("https://github.com/"):
        cleaned = cleaned.removeprefix("https://github.com/")
    if cleaned.startswith("git@github.com:"):
        cleaned = cleaned.removeprefix("git@github.com:")
    parts = cleaned.split("/")
    if len(parts) != 2 or not all(parts):
        return None
    return parts[0], parts[1]


def linked_prs(text: str) -> list[int]:
    seen: set[int] = set()
    for match in PR_RE.finditer(text or ""):
        raw = match.group("bracket") or match.group("pull") or match.group("hash")
        if raw:
            seen.add(int(raw))
    return sorted(seen)


def normalize_release(release: dict[str, Any], tag_prefix: str) -> dict[str, Any] | None:
    tag = str(release.get("tag_name") or "")
    if not tag:
        return None
    if tag_prefix and not tag.startswith(tag_prefix):
        return None
    body = str(release.get("body") or "")
    version = tag[len(tag_prefix) :] if tag_prefix and tag.startswith(tag_prefix) else tag
    return {
        "tag": tag,
        "version": version,
        "name": release.get("name") or tag,
        "published_at": release.get("published_at"),
        "url": release.get("html_url"),
        "body": body,
        "prerelease": bool(release.get("prerelease")),
        "draft": bool(release.get("draft")),
        "linked_prs": linked_prs(body),
    }


def fetch_with_gh(owner: str, repo: str, limit: int) -> list[dict[str, Any]] | None:
    gh_bin = os.environ.get("RELEASE_NOTES_GH_BIN", "gh")
    path = f"/repos/{owner}/{repo}/releases?per_page={limit}"
    try:
        result = subprocess.run(
            [gh_bin, "api", path],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, list) else None


def fetch_anonymous(api_base: str, owner: str, repo: str, limit: int) -> tuple[list[dict[str, Any]] | None, dict[str, str] | None]:
    url = f"{api_base.rstrip('/')}/repos/{owner}/{repo}/releases?per_page={limit}"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "release-notes-skill"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        code = "rate_limit" if exc.code in {403, 429} else "http_error"
        return None, {
            "code": code,
            "message": f"GitHub API request failed with HTTP {exc.code}.",
            "user_hint": "Authenticate gh or retry with a smaller --limit.",
        }
    except (OSError, json.JSONDecodeError) as exc:
        return None, {
            "code": "network_outage",
            "message": f"Could not fetch GitHub releases: {exc}",
            "user_hint": "Check network access or use gh auth before retrying.",
        }
    return payload if isinstance(payload, list) else None, None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="List GitHub releases as JSON.")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or infer_repo_from_git(), help="GitHub repository as OWNER/REPO.")
    parser.add_argument("--tag-prefix", default="", help="Only include releases whose tag starts with this prefix.")
    parser.add_argument("--limit", type=int, default=40, help="Number of releases to fetch from GitHub.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="GitHub API base URL.")
    args = parser.parse_args(argv)

    api_base = args.api_base.rstrip("/")
    if api_base not in ALLOWED_API_BASES:
        return emit(
            {
                "ok": False,
                "error": {
                    "code": "disallowed_api_base",
                    "message": f"API base is not allowlisted: {api_base}",
                    "user_hint": "Use the default https://api.github.com endpoint.",
                },
            }
        )

    repo_parts = parse_repo(args.repo)
    if repo_parts is None:
        return emit(
            {
                "ok": False,
                "error": {
                    "code": "missing_repo",
                    "message": "A GitHub repository could not be inferred.",
                    "user_hint": "Pass --repo OWNER/REPO or run inside a GitHub-backed checkout.",
                },
            }
        )
    owner, repo = repo_parts
    limit = max(1, min(args.limit, 100))

    raw = fetch_with_gh(owner, repo, limit)
    source = "gh"
    if raw is None:
        raw, error = fetch_anonymous(api_base, owner, repo, limit)
        source = "anon"
        if raw is None:
            return emit({"ok": False, "error": error})

    releases = [item for release in raw if (item := normalize_release(release, args.tag_prefix))]
    return emit(
        {
            "ok": True,
            "source": source,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "repo": f"{owner}/{repo}",
            "tag_prefix": args.tag_prefix,
            "releases": releases,
        }
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
