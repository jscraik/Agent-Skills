#!/usr/bin/env python3
"""Shared GitHub helpers for skill install scripts."""

from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request

_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def github_request(url: str, user_agent: str, timeout: float = 10.0) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported URL scheme for github_request: '{parsed.scheme or '<empty>'}'")

    headers = {"User-Agent": user_agent}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def github_api_contents_url(repo: str, path: str, ref: str) -> str:
    cleaned_repo = repo.strip()
    if not _REPO_RE.fullmatch(cleaned_repo):
        raise ValueError("repo must be in owner/repo format")

    cleaned_path = path.strip()
    if not cleaned_path:
        raise ValueError("path must be a non-empty relative path")
    if cleaned_path.startswith("/"):
        raise ValueError("path must be relative and must not start with '/'")
    cleaned_path = cleaned_path.strip("/")
    if not cleaned_path:
        raise ValueError("path must be a non-empty relative path")
    if ".." in cleaned_path.split("/"):
        raise ValueError("path must not contain '..' segments")

    encoded_path = urllib.parse.quote(cleaned_path, safe="/._-")
    encoded_ref = urllib.parse.quote(ref, safe="")
    return f"https://api.github.com/repos/{cleaned_repo}/contents/{encoded_path}?ref={encoded_ref}"
