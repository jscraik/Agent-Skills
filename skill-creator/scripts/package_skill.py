#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python scripts/package_skill.py skills/public/my-skill
    python scripts/package_skill.py skills/public/my-skill ./dist
"""

import argparse
import fnmatch
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

from quick_validate import validate_skill

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}
DEFAULT_IGNORE_FILES = {".DS_Store", "Thumbs.db"}
DEFAULT_IGNORE_GLOBS = {"*.pyc", "*.pyo"}


def load_skillignore_patterns(skill_path):
    """Load ignore patterns from .skillignore if present."""
    ignore_file = skill_path / ".skillignore"
    if not ignore_file.exists():
        return [], False
    patterns = []
    for line in ignore_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns, True


def should_ignore(file_path, skill_path, extra_patterns, *, use_default_ignores):
    """Return True if file_path should be excluded from the package."""
    rel_path = file_path.relative_to(skill_path)
    if use_default_ignores:
        if any(part in DEFAULT_IGNORE_DIRS for part in rel_path.parts):
            return True
        if rel_path.name in DEFAULT_IGNORE_FILES:
            return True

    rel_posix = rel_path.as_posix()
    if use_default_ignores:
        for pattern in DEFAULT_IGNORE_GLOBS:
            if fnmatch.fnmatch(rel_path.name, pattern) or fnmatch.fnmatch(rel_posix, pattern):
                return True

    for pattern in extra_patterns:
        if fnmatch.fnmatch(rel_path.name, pattern) or fnmatch.fnmatch(rel_posix, pattern):
            return True

    return False


def _run_git(args, *, cwd):
    try:
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _normalize_repo_url(url: str) -> str:
    cleaned = url.strip()
    if cleaned.startswith("git@") and ":" in cleaned:
        host, path = cleaned.split(":", 1)
        host = host.replace("git@", "")
        cleaned = f"https://{host}/{path}"
    if cleaned.startswith("ssh://git@"):
        cleaned = cleaned.replace("ssh://git@", "https://", 1)
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    return cleaned


def _get_git_metadata(skill_path: Path, *, source_repo: str | None, source_rev: str | None, allow_dirty: bool):
    if (source_repo is None) != (source_rev is None):
        raise ValueError("Provide both --source-repo and --source-rev, or neither.")

    if source_repo and source_rev:
        repo_url = source_repo
        rev = source_rev
        dirty_paths: list[str] = []
        return repo_url, rev, False, dirty_paths

    inside = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=skill_path)
    if inside != "true":
        raise ValueError("Not a git repo. Provide --source-repo and --source-rev to override.")

    repo_url = _run_git(["remote", "get-url", "origin"], cwd=skill_path)
    if not repo_url:
        raise ValueError("Unable to read git remote URL (origin). Provide --source-repo to override.")
    repo_url = _normalize_repo_url(repo_url)

    rev = _run_git(["rev-parse", "HEAD"], cwd=skill_path)
    if not rev:
        raise ValueError("Unable to read git HEAD. Provide --source-rev to override.")

    status = _run_git(["status", "--porcelain"], cwd=skill_path)
    dirty_paths = []
    if status:
        dirty_paths = [line.strip().split(" ", 1)[-1] for line in status.splitlines() if line.strip()]
        if not allow_dirty:
            raise ValueError("Working tree is dirty. Commit changes or pass --allow-dirty.")
        rev = f"{rev}-dirty"
    return repo_url, rev, bool(status), dirty_paths


def _inject_metadata(skill_md_text: str, *, source_repo: str, source_rev: str, dirty: bool, dirty_paths: list[str]):
    match = re.match(r"^---\n(.*?)\n---", skill_md_text, re.DOTALL)
    if not match:
        raise ValueError("Invalid frontmatter format in SKILL.md")

    frontmatter_text = match.group(1)
    frontmatter = yaml.safe_load(frontmatter_text)
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a YAML mapping/object.")

    metadata = frontmatter.get("metadata")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("Frontmatter metadata must be a mapping/object.")

    metadata["source_repo"] = str(source_repo)
    metadata["source_rev"] = str(source_rev)
    if dirty:
        metadata["source_dirty"] = "true"
        if dirty_paths:
            metadata["source_dirty_paths"] = ", ".join(dirty_paths)

    frontmatter["metadata"] = metadata
    new_frontmatter = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    body = skill_md_text[match.end() :].lstrip("\n")
    return f"---\n{new_frontmatter}\n---\n\n{body}"


def package_skill(
    skill_path,
    output_dir=None,
    *,
    target="portable",
    source_repo=None,
    source_rev=None,
    allow_dirty=False,
    skip_provenance=False,
):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"[ERROR] Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"[ERROR] Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("Validating skill...")
    valid, message, warnings = validate_skill(skill_path, target=target)
    if not valid:
        print(f"[ERROR] Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    for warning in warnings:
        print(f"[WARN] {warning}")
    print(f"[OK] {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format)
    try:
        ignore_patterns, has_skillignore = load_skillignore_patterns(skill_path)
        use_default_ignores = not has_skillignore
        if skip_provenance:
            source_repo_value = None
            source_rev_value = None
            dirty = False
            dirty_paths = []
        else:
            source_repo_value, source_rev_value, dirty, dirty_paths = _get_git_metadata(
                skill_path,
                source_repo=source_repo,
                source_rev=source_rev,
                allow_dirty=allow_dirty,
            )
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            for file_path in skill_path.rglob("*"):
                if file_path.is_file():
                    if should_ignore(file_path, skill_path, ignore_patterns, use_default_ignores=use_default_ignores):
                        continue
                    # Calculate the relative path within the zip
                    arcname = file_path.relative_to(skill_path.parent)
                    if file_path.name == "SKILL.md" and not skip_provenance:
                        skill_md_text = file_path.read_text(encoding="utf-8")
                        updated_skill_md = _inject_metadata(
                            skill_md_text,
                            source_repo=source_repo_value,
                            source_rev=source_rev_value,
                            dirty=dirty,
                            dirty_paths=dirty_paths,
                        )
                        zipf.writestr(str(arcname), updated_skill_md)
                        print(f"  Added: {arcname} (metadata injected)")
                    else:
                        zipf.write(file_path, arcname)
                        print(f"  Added: {arcname}")

        print(f"\n[OK] Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"[ERROR] Error creating .skill file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Package a skill folder into a .skill file.")
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument("output_dir", nargs="?", default=None, help="Optional output directory")
    parser.add_argument(
        "--target",
        choices=("portable", "codex", "claude"),
        default="portable",
        help="Validation target for SKILL.md",
    )
    parser.add_argument("--source-repo", default=None, help="Override source repo URL for metadata")
    parser.add_argument("--source-rev", default=None, help="Override source revision for metadata")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow dirty working tree; source_rev will be suffixed with -dirty",
    )
    parser.add_argument(
        "--skip-provenance",
        action="store_true",
        help="Skip injecting metadata.source_repo/source_rev into SKILL.md",
    )
    args = parser.parse_args()

    print(f"Packaging skill: {args.skill_path}")
    if args.output_dir:
        print(f"   Output directory: {args.output_dir}")
    print()

    result = package_skill(
        args.skill_path,
        args.output_dir,
        target=args.target,
        source_repo=args.source_repo,
        source_rev=args.source_rev,
        allow_dirty=args.allow_dirty,
        skip_provenance=args.skip_provenance,
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
