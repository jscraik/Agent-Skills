#!/usr/bin/env python3
"""Install a skill from GitHub into canonical repository skill categories."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import zipfile
from pathlib import Path

from github_utils import github_request
DEFAULT_REF = "main"


@dataclass
class Args:
    url: str | None = None
    repo: str | None = None
    path: list[str] | None = None
    ref: str = DEFAULT_REF
    dest: str | None = None
    name: str | None = None
    method: str = "auto"


@dataclass
class Source:
    owner: str
    repo: str
    ref: str
    paths: list[str]
    repo_url: str | None = None


class InstallError(Exception):
    pass


def _tmp_root() -> str:
    """
    Provide the base temporary directory used by the installer, ensuring it exists.
    
    Ensures a directory named `codex` under the system temporary directory exists.
    
    Returns:
        The absolute path to the base temporary directory.
    """
    base = os.path.join(tempfile.gettempdir(), "codex")
    os.makedirs(base, exist_ok=True)
    return base


def _request(url: str) -> bytes:
    return github_request(url, "codex-skill-install")


def _parse_github_url(url: str, default_ref: str) -> tuple[str, str, str, str | None]:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != "github.com":
        raise InstallError("Only GitHub URLs are supported for download mode.")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise InstallError("Invalid GitHub URL.")
    owner, repo = parts[0], parts[1]
    ref = default_ref
    subpath = ""
    if len(parts) > 2:
        if parts[2] in ("tree", "blob"):
            if len(parts) < 4:
                raise InstallError("GitHub URL missing ref or path.")
            ref = parts[3]
            subpath = "/".join(parts[4:])
        else:
            subpath = "/".join(parts[2:])
    return owner, repo, ref, subpath or None


def _download_repo_zip(owner: str, repo: str, ref: str, dest_dir: str) -> str:
    zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/{ref}"
    zip_path = os.path.join(dest_dir, "repo.zip")
    try:
        payload = _request(zip_url)
    except urllib.error.HTTPError as exc:
        raise InstallError(f"Download failed: HTTP {exc.code}") from exc
    with open(zip_path, "wb") as file_handle:
        file_handle.write(payload)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        _safe_extract_zip(zip_file, dest_dir)
        top_levels = {name.split("/")[0] for name in zip_file.namelist() if name}
    if not top_levels:
        raise InstallError("Downloaded archive was empty.")
    if len(top_levels) != 1:
        raise InstallError("Unexpected archive layout.")
    return os.path.join(dest_dir, next(iter(top_levels)))


def _run_git(args: list[str]) -> None:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise InstallError(result.stderr.strip() or "Git command failed.")


def _safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: str) -> None:
    dest_root = os.path.realpath(dest_dir)
    for info in zip_file.infolist():
        extracted_path = os.path.realpath(os.path.join(dest_dir, info.filename))
        if extracted_path == dest_root or extracted_path.startswith(dest_root + os.sep):
            continue
        raise InstallError("Archive contains files outside the destination.")
    zip_file.extractall(dest_dir)


def _validate_relative_path(path: str) -> None:
    if os.path.isabs(path) or os.path.normpath(path).startswith(".."):
        raise InstallError("Skill path must be a relative path inside the repo.")


def _validate_skill_name(name: str) -> None:
    altsep = os.path.altsep
    if not name or os.path.sep in name or (altsep and altsep in name):
        raise InstallError("Skill name must be a single path segment.")
    if name in (".", ".."):
        raise InstallError("Invalid skill name.")


def _git_sparse_checkout(repo_url: str, ref: str, paths: list[str], dest_dir: str) -> str:
    repo_dir = os.path.join(dest_dir, "repo")
    clone_cmd = [
        "git",
        "clone",
        "--filter=blob:none",
        "--depth",
        "1",
        "--sparse",
        "--single-branch",
        "--branch",
        ref,
        repo_url,
        repo_dir,
    ]
    try:
        _run_git(clone_cmd)
    except InstallError:
        _run_git(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--depth",
                "1",
                "--sparse",
                "--single-branch",
                repo_url,
                repo_dir,
            ]
        )
    _run_git(["git", "-C", repo_dir, "sparse-checkout", "set", *paths])
    _run_git(["git", "-C", repo_dir, "checkout", ref])
    return repo_dir


def _validate_skill(path: str) -> None:
    if not os.path.isdir(path):
        raise InstallError(f"Skill path not found: {path}")
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise InstallError("SKILL.md not found in selected skill directory.")


def _copy_skill(src: str, dest_dir: str) -> None:
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    if os.path.exists(dest_dir):
        raise InstallError(f"Destination already exists: {dest_dir}")
    shutil.copytree(src, dest_dir)


def _build_repo_url(owner: str, repo: str) -> str:
    return f"https://github.com/{owner}/{repo}.git"


def _build_repo_ssh(owner: str, repo: str) -> str:
    return f"git@github.com:{owner}/{repo}.git"


def _prepare_repo(source: Source, method: str, tmp_dir: str) -> str:
    if method in ("download", "auto"):
        try:
            return _download_repo_zip(source.owner, source.repo, source.ref, tmp_dir)
        except InstallError as exc:
            if method == "download":
                raise
            err_msg = str(exc)
            if "HTTP 401" in err_msg or "HTTP 403" in err_msg or "HTTP 404" in err_msg:
                pass
            else:
                raise
    if method in ("git", "auto"):
        repo_url = source.repo_url or _build_repo_url(source.owner, source.repo)
        try:
            return _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir)
        except InstallError:
            repo_url = _build_repo_ssh(source.owner, source.repo)
            return _git_sparse_checkout(repo_url, source.ref, source.paths, tmp_dir)
    raise InstallError("Unsupported method.")


def _resolve_source(args: Args) -> Source:
    """
    Resolve CLI arguments into a Source describing the GitHub repository, ref and repository-relative paths to install.
    
    When `args.url` is provided the URL is parsed to determine owner, repo and ref; installation paths are taken from `args.path` if present or from the URL subpath, and at least one path is required. When `args.repo` contains "://", it is treated as a URL and resolved the same way. When `args.repo` is given in `owner/repo` form, `args.path` must be provided and is used as the list of repository-relative paths.
    
    Parameters:
        args (Args): Parsed command-line arguments containing `url`, `repo`, `path`, and `ref`.
    
    Returns:
        Source: Resolved source with `owner`, `repo`, `ref`, and `paths` populated.
    
    Raises:
        InstallError: If neither `--repo` nor `--url` is provided; if `--repo` is not in `owner/repo` format; or if no installation paths are available for the given input.
    """
    if args.url:
        owner, repo, ref, url_path = _parse_github_url(args.url, args.ref)
        if args.path is not None:
            paths = list(args.path)
        elif url_path:
            paths = [url_path]
        else:
            paths = []
        if not paths:
            raise InstallError("Missing --path for GitHub URL.")
        return Source(owner=owner, repo=repo, ref=ref, paths=paths)

    if not args.repo:
        raise InstallError("Provide --repo or --url.")
    if "://" in args.repo:
        return _resolve_source(
            Args(url=args.repo, repo=None, path=args.path, ref=args.ref)
        )

    repo_parts = [p for p in args.repo.split("/") if p]
    if len(repo_parts) != 2:
        raise InstallError("--repo must be in owner/repo format.")
    if not args.path:
        raise InstallError("Missing --path for --repo.")
    paths = list(args.path)
    return Source(
        owner=repo_parts[0],
        repo=repo_parts[1],
        ref=args.ref,
        paths=paths,
    )


def _canonical_repo_dest() -> str | None:
    """
    Locate the canonical skills destination directory for the local repository or an environment override.
    
    If the environment variable `ASK_SKILLS_CANONICAL_DEST` is set and non-empty that value is returned. Otherwise the filesystem is scanned upwards from this script for a repository root that contains a `.git` directory, an `AGENTS.md` file, a `scripts/sync_skills.sh` file and a `plugins` directory; when found, the function returns the path to the `github` directory inside that repository. If no override is set and no repository root is detected, `None` is returned.
    
    Returns:
        str | None: Path to the canonical `github` directory, or `None` if not detected.
    """
    override = os.environ.get("ASK_SKILLS_CANONICAL_DEST", "").strip()
    if override:
        return override

    script_path = Path(__file__).resolve()
    for parent in [script_path.parent, *script_path.parents]:
        if not (parent / ".git").exists():
            continue
        if (parent / "AGENTS.md").is_file() and (parent / "scripts" / "sync_skills.sh").is_file() and (parent / "plugins").is_dir():
            return str(parent / "github")
    return None


def _resolve_dest_root(dest: str | None) -> str:
    """
    Resolve the final absolute destination directory within the canonical agent-skills repository.
    
    Parameters:
        dest (str | None): If None, use the detected canonical `<repo>/github` destination.
            If provided and absolute, it must be inside the canonical repository root.
            If provided and relative, it is interpreted as a path relative to the canonical repository root
            and must target a category directory (not the repository root itself).
    
    Returns:
        str: Absolute path to the resolved destination directory.
    
    Raises:
        InstallError: If the canonical destination cannot be detected, if the resolved path lies outside
            the canonical repository root, or if the resolved path targets the repository root instead of
            a category directory.
    """
    canonical = _canonical_repo_dest()
    if not canonical:
        raise InstallError(
            "Canonical skill destination was not detected. "
            "Set ASK_SKILLS_CANONICAL_DEST or run inside the canonical agent-skills repository."
        )

    canonical_dest = Path(canonical).resolve()
    repo_root = canonical_dest.parent

    if not dest:
        return str(canonical_dest)

    requested = Path(dest)
    resolved = requested.resolve() if requested.is_absolute() else (repo_root / requested).resolve()
    try:
        rel = resolved.relative_to(repo_root)
    except ValueError as exc:
        raise InstallError(
            f"Destination must stay inside canonical repository root: {repo_root}"
        ) from exc

    if len(rel.parts) != 1:
        raise InstallError(
            "Destination must target a single top-level category under canonical repository root."
        )
    return str(resolved)


def _parse_args(argv: list[str]) -> Args:
    """
    Parse command-line arguments and populate an Args dataclass.
    
    Parameters:
        argv (list[str]): Command-line arguments (excluding program name).
    
    Returns:
        Args: Parsed arguments with fields: repo, url, path, ref, dest, name, and method.
    """
    parser = argparse.ArgumentParser(description="Install a skill from GitHub.")
    parser.add_argument("--repo", help="owner/repo")
    parser.add_argument("--url", help="https://github.com/owner/repo[/tree/ref/path]")
    parser.add_argument(
        "--path",
        nargs="+",
        help="Path(s) to skill(s) inside repo",
    )
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument("--dest", help="Canonical destination category (repo-relative or absolute within canonical repo)")
    parser.add_argument(
        "--name", help="Destination skill name (defaults to basename of path)"
    )
    parser.add_argument(
        "--method",
        choices=["auto", "download", "git"],
        default="auto",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    """
    Install one or more skills from a GitHub repository into the canonical repository skill category directories.
    
    Parses command-line arguments from `argv`, resolves the GitHub source and destination category, acquires the repository content (by download or git), validates each skill path and name, copies each valid skill into the resolved destination, and cleans up temporary work files. Prints a line "Installed <skill_name> to <dest_dir>" for each successful install; on failure prints an error message to stderr.
    
    Parameters:
        argv (list[str]): Command-line arguments (excluding the program name).
    
    Returns:
        int: Exit status code: `0` on success, `1` on failure.
    """
    args = _parse_args(argv)
    try:
        source = _resolve_source(args)
        source.ref = source.ref or args.ref
        if not source.paths:
            raise InstallError("No skill paths provided.")
        for path in source.paths:
            _validate_relative_path(path)
        dest_root = _resolve_dest_root(args.dest)
        tmp_dir = tempfile.mkdtemp(prefix="skill-install-", dir=_tmp_root())
        try:
            repo_root = _prepare_repo(source, args.method, tmp_dir)
            installed = []
            for path in source.paths:
                skill_name = args.name if len(source.paths) == 1 else None
                skill_name = skill_name or os.path.basename(path.rstrip("/"))
                _validate_skill_name(skill_name)
                if not skill_name:
                    raise InstallError("Unable to derive skill name.")
                dest_dir = os.path.join(dest_root, skill_name)
                if os.path.exists(dest_dir):
                    raise InstallError(f"Destination already exists: {dest_dir}")
                skill_src = os.path.join(repo_root, path)
                _validate_skill(skill_src)
                _copy_skill(skill_src, dest_dir)
                installed.append((skill_name, dest_dir))
        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
        for skill_name, dest_dir in installed:
            print(f"Installed {skill_name} to {dest_dir}")
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
