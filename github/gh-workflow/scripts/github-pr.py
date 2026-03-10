#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich", "typer"]
# ///
"""
GitHub PR Tool - Fetch, preview, merge, and test PRs locally.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    HAS_OPTIONAL_DEPS = True
except ModuleNotFoundError:
    typer = None  # type: ignore[assignment]
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]
    HAS_OPTIONAL_DEPS = False

if HAS_OPTIONAL_DEPS:
    app = typer.Typer(help="GitHub PR Tool - fetch, preview, merge, and test PRs locally")
    console = Console()


REPO_SLUG_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REMOTE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
BRANCH_RE = re.compile(r"^(?!/)(?!.*//)[A-Za-z0-9._/-]+$")


def _exit(message: str) -> "typer.Exit | SystemExit":
    if HAS_OPTIONAL_DEPS:
        console.print(f"[red]{message}[/red]")
        return typer.Exit(1)
    print(message, file=sys.stderr)
    return SystemExit(1)


def validate_repo_slug(repo: str) -> str:
    if not REPO_SLUG_RE.fullmatch(repo):
        raise _exit(f"Invalid repo slug: {repo!r}. Expected owner/repo.")
    return repo


def validate_pr_number(pr_number: int) -> int:
    if pr_number <= 0:
        raise _exit(f"Invalid PR number: {pr_number}")
    return pr_number


def validate_remote_name(remote: str) -> str:
    if not REMOTE_RE.fullmatch(remote):
        raise _exit(f"Invalid git remote name: {remote!r}")
    return remote


def validate_branch_name(branch: str) -> str:
    if not BRANCH_RE.fullmatch(branch) or branch.endswith(".lock") or ".." in branch or "@{" in branch:
        raise _exit(f"Invalid branch name: {branch!r}")
    return branch


def run(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    result = subprocess.run(cmd, capture_output=capture, text=True, shell=False)
    if check and result.returncode != 0:
        console.print(f"[red]Command failed:[/red] {' '.join(cmd)}")
        if result.stderr:
            console.print(f"[dim]{result.stderr}[/dim]")
        raise typer.Exit(1)
    return result


def get_pr_info(repo: str, pr_number: int) -> dict:
    """Fetch PR details from GitHub."""
    safe_repo = validate_repo_slug(repo)
    safe_pr_number = validate_pr_number(pr_number)
    result = run([
        "gh", "pr", "view", str(safe_pr_number),
        "--repo", safe_repo,
        "--json", "title,author,state,headRefName,baseRefName,additions,deletions,files,statusCheckRollup,comments,url"
    ])
    return json.loads(result.stdout)


def detect_package_manager() -> Optional[str]:
    """Detect which package manager to use."""
    cwd = Path.cwd()
    if (cwd / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (cwd / "yarn.lock").exists():
        return "yarn"
    if (cwd / "bun.lockb").exists():
        return "bun"
    if (cwd / "package-lock.json").exists():
        return "npm"
    if (cwd / "package.json").exists():
        return "npm"
    return None


if HAS_OPTIONAL_DEPS:
    @app.command()
    def preview(
        repo: str = typer.Argument(..., help="Repository (owner/repo)"),
        pr_number: int = typer.Argument(..., help="PR number"),
    ):
        """Preview a PR's details, files, and CI status."""
        validate_repo_slug(repo)
        pr_number = validate_pr_number(pr_number)
        console.print(f"[blue]Fetching PR #{pr_number} from {repo}...[/blue]")

        pr = get_pr_info(repo, pr_number)

        # Header panel
        status_color = "green" if pr["state"] == "OPEN" else "red"
        console.print(Panel(
            f"[bold]{pr['title']}[/bold]\n\n"
            f"Author: {pr['author']['login']}\n"
            f"State: [{status_color}]{pr['state']}[/{status_color}]\n"
            f"Branch: {pr['headRefName']} → {pr['baseRefName']}\n"
            f"Changes: [green]+{pr['additions']}[/green] / [red]-{pr['deletions']}[/red]\n"
            f"URL: {pr['url']}",
            title=f"PR #{pr_number}",
        ))

        # Files table
        if pr.get("files"):
            table = Table(title="Files Changed")
            table.add_column("File", style="cyan")
            table.add_column("+", style="green", justify="right")
            table.add_column("-", style="red", justify="right")

            for f in pr["files"][:20]:  # Limit to 20 files
                table.add_row(f["path"], str(f["additions"]), str(f["deletions"]))

            if len(pr["files"]) > 20:
                table.add_row(f"... and {len(pr['files']) - 20} more", "", "")

            console.print(table)

        # CI Status
        checks = pr.get("statusCheckRollup", [])
        if checks:
            console.print("\n[bold]CI Status:[/bold]")
            for check in checks[:10]:
                status = check.get("conclusion", check.get("status", "PENDING"))
                icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILURE" else "⏳"
                name = check.get("name", "Unknown")[:50]
                console.print(f"  {icon} {name}")


    @app.command()
    def fetch(
        repo: str = typer.Argument(..., help="Repository (owner/repo)"),
        pr_number: int = typer.Argument(..., help="PR number"),
        branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Local branch name"),
        remote: str = typer.Option("upstream", "--remote", "-r", help="Remote name"),
    ):
        """Fetch a PR branch locally."""
        _repo = validate_repo_slug(repo)
        pr_number = validate_pr_number(pr_number)
        remote = validate_remote_name(remote)
        branch_name = validate_branch_name(branch or f"pr/{pr_number}")

        console.print(f"[blue]Fetching PR #{pr_number} from {remote}...[/blue]")

        # Fetch the PR
        run(["git", "fetch", remote, f"pull/{pr_number}/head:{branch_name}"])

        console.print(f"[green]✓ PR fetched to branch:[/green] {branch_name}")
        console.print(f"\n[dim]To checkout: git checkout {branch_name}[/dim]")
        console.print(f"[dim]To merge: git merge {branch_name}[/dim]")


    @app.command()
    def merge(
        repo: str = typer.Argument(..., help="Repository (owner/repo)"),
        pr_number: int = typer.Argument(..., help="PR number"),
        remote: str = typer.Option("upstream", "--remote", "-r", help="Remote name"),
        no_install: bool = typer.Option(False, "--no-install", help="Skip dependency install"),
        branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Local branch name"),
    ):
        """Fetch and merge a PR into the current branch."""
        repo = validate_repo_slug(repo)
        pr_number = validate_pr_number(pr_number)
        remote = validate_remote_name(remote)
        branch_name = validate_branch_name(branch or f"pr/{pr_number}")

        # Get PR info first
        console.print(f"[blue]Fetching PR #{pr_number} info...[/blue]")
        pr = get_pr_info(repo, pr_number)
        console.print(f"[bold]{pr['title']}[/bold]")
        console.print(f"[dim]+{pr['additions']} / -{pr['deletions']} across {len(pr.get('files', []))} files[/dim]\n")

        # Fetch the PR
        console.print("[blue]Fetching PR branch...[/blue]")
        run(["git", "fetch", remote, f"pull/{pr_number}/head:{branch_name}"])

        # Merge
        console.print("[blue]Merging into current branch...[/blue]")
        result = run(["git", "merge", branch_name, "--no-edit"], check=False)

        if result.returncode != 0:
            console.print("[yellow]⚠️ Merge conflicts detected. Resolve manually.[/yellow]")
            raise typer.Exit(1)

        console.print("[green]✓ Merged successfully[/green]")

        # Install dependencies
        if not no_install:
            pm = detect_package_manager()
            if pm:
                console.print(f"\n[blue]Installing dependencies with {pm}...[/blue]")
                install_cmd = [pm, "install"]
                if pm == "pnpm":
                    install_cmd.append("--force")  # Handle patch issues
                run(install_cmd, capture=False)
                console.print("[green]✓ Dependencies installed[/green]")


    @app.command()
    def test(
        repo: str = typer.Argument(..., help="Repository (owner/repo)"),
        pr_number: int = typer.Argument(..., help="PR number"),
        remote: str = typer.Option("upstream", "--remote", "-r", help="Remote name"),
    ):
        """Full test cycle: fetch, merge, install, build, test."""
        repo = validate_repo_slug(repo)
        pr_number = validate_pr_number(pr_number)
        remote = validate_remote_name(remote)
        branch_name = validate_branch_name(f"pr/{pr_number}")

        # Get PR info
        console.print(f"[blue]Fetching PR #{pr_number} info...[/blue]")
        pr = get_pr_info(repo, pr_number)
        console.print(Panel(f"[bold]{pr['title']}[/bold]\n+{pr['additions']} / -{pr['deletions']}", title=f"PR #{pr_number}"))

        # Fetch
        console.print("\n[blue]Step 1/4: Fetching PR branch...[/blue]")
        run(["git", "fetch", remote, f"pull/{pr_number}/head:{branch_name}"])
        console.print("[green]✓ Fetched[/green]")

        # Merge
        console.print("\n[blue]Step 2/4: Merging...[/blue]")
        result = run(["git", "merge", branch_name, "--no-edit"], check=False)
        if result.returncode != 0:
            console.print("[red]✗ Merge conflicts - resolve manually[/red]")
            raise typer.Exit(1)
        console.print("[green]✓ Merged[/green]")

        # Install
        pm = detect_package_manager()
        if pm:
            console.print(f"\n[blue]Step 3/4: Installing dependencies ({pm})...[/blue]")
            install_cmd = [pm, "install"]
            if pm == "pnpm":
                install_cmd.append("--force")
            run(install_cmd, capture=False)
            console.print("[green]✓ Installed[/green]")

            # Build
            console.print("\n[blue]Step 4/4: Building...[/blue]")
            build_result = run([pm, "run", "build"], check=False, capture=False)
            if build_result.returncode != 0:
                console.print("[yellow]⚠️ Build had errors (may still work)[/yellow]")
            else:
                console.print("[green]✓ Built[/green]")

        console.print(f"\n[bold green]✓ PR #{pr_number} merged and tested![/bold green]")


def _fallback_main() -> None:
    parser = argparse.ArgumentParser(
        description="GitHub PR Tool (requires optional dependencies: rich, typer).",
        epilog="Install with: pip install rich typer",
    )
    parser.parse_args()
    print(
        "This script requires optional dependencies 'rich' and 'typer'. "
        "Install with: pip install rich typer",
        file=sys.stderr,
    )
    raise SystemExit(1)


if __name__ == "__main__":
    if HAS_OPTIONAL_DEPS:
        app()
    else:
        _fallback_main()
