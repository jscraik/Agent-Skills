#!/usr/bin/env python3
"""List skills from a GitHub repo path."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from pathlib import Path

from github_utils import github_api_contents_url, github_request

DEFAULT_REPO = "openai/skills"
DEFAULT_PATH = "skills/.curated"
DEFAULT_REF = "main"


class ListError(Exception):
    pass


class Args(argparse.Namespace):
    repo: str
    path: str
    ref: str
    format: str


def _request(url: str) -> bytes:
    return github_request(url, "codex-skill-list")


def _skills_root() -> str:
    env_home = os.environ.get("AGENT_SKILLS_HOME")
    if env_home:
        return os.path.expanduser(env_home)
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return os.path.join(os.path.expanduser(codex_home), "skills")
    return os.path.expanduser("~/dev/agent-skills")


def _installed_skills() -> dict[str, list[str]]:
    root = Path(_skills_root())
    if not root.is_dir():
        return {}
    entries: dict[str, list[str]] = {}
    for skill_md in root.rglob("SKILL.md"):
        if ".git" in skill_md.parts:
            continue
        skill_name = skill_md.parent.name
        location = str(skill_md.parent.relative_to(root)).replace("\\", "/")
        entries.setdefault(skill_name, []).append(location)
    for locations in entries.values():
        locations.sort()
    return entries


def _list_skills(repo: str, path: str, ref: str) -> list[str]:
    api_url = github_api_contents_url(repo, path, ref)
    try:
        payload = _request(api_url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ListError(
                "Skills path not found: "
                f"https://github.com/{repo}/tree/{ref}/{path}"
            ) from exc
        raise ListError(f"Failed to fetch skills: HTTP {exc.code}") from exc
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, list):
        raise ListError("Unexpected skills listing response.")
    skills = [item["name"] for item in data if item.get("type") == "dir"]
    return sorted(skills)


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="List skills.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument(
        "--path",
        default=DEFAULT_PATH,
        help="Repo path to list (default: skills/.curated)",
    )
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        skills = _list_skills(args.repo, args.path, args.ref)
        installed = _installed_skills()
        if args.format == "json":
            payload = [
                {
                    "name": name,
                    "installed": name in installed,
                    "locations": installed.get(name, []),
                }
                for name in skills
            ]
            print(json.dumps(payload))
        else:
            for idx, name in enumerate(skills, start=1):
                locations = installed.get(name, [])
                if locations:
                    if len(locations) == 1:
                        suffix = f" (already installed: {locations[0]})"
                    else:
                        suffix = f" (already installed: {', '.join(locations)})"
                else:
                    suffix = ""
                print(f"{idx}. {name}{suffix}")
        return 0
    except ListError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
