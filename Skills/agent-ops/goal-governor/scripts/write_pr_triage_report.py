#!/usr/bin/env python3
"""Write a worktree-bound pull request triage report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[Sequence[str], Path], CommandResult]


def run_command(command: Sequence[str], cwd: Path) -> CommandResult:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        check=False,
        text=True,
        capture_output=True,
    )
    return CommandResult(
        command=tuple(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def command_text(command: Sequence[str]) -> str:
    return " ".join(command)


def indented(text: str) -> str:
    if not text:
        return "    (empty)"
    return "\n".join(f"    {line}" for line in text.rstrip().splitlines())


def parse_json_list(result: CommandResult) -> list[object] | None:
    if result.returncode != 0:
        return None
    try:
        parsed = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else None


def parse_json_object(result: CommandResult) -> dict[str, object] | None:
    if result.returncode != 0:
        return None
    try:
        parsed = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def review_comment_marked_addressed(comment: object) -> bool:
    if not isinstance(comment, dict):
        return False
    body = str(comment.get("body") or "")
    return "addressed in commit " in body.lower()


def review_comment_stale_for_head(comment: object, expected_head: str) -> bool:
    if not isinstance(comment, dict):
        return False
    comment_head = str(comment.get("commit_id") or "")
    return comment.get("line") is None and bool(comment_head) and comment_head != expected_head


def collect_results(worktree: Path, repo: str, pr_number: str, runner: Runner) -> dict[str, CommandResult]:
    return {
        "pwd": runner(("pwd",), worktree),
        "branch": runner(("git", "branch", "--show-current"), worktree),
        "local_head": runner(("git", "rev-parse", "HEAD"), worktree),
        "status": runner(("git", "status", "--short", "--branch"), worktree),
        "pr_view": runner(
            (
                "gh",
                "pr",
                "view",
                pr_number,
                "--repo",
                repo,
                "--json",
                "number,state,isDraft,mergeable,reviewDecision,headRefOid,headRefName,url,title,author",
            ),
            worktree,
        ),
        "checks": runner(("gh", "pr", "checks", pr_number, "--repo", repo, "--watch=false"), worktree),
        "reviews": runner(("gh", "api", f"repos/{repo}/pulls/{pr_number}/reviews"), worktree),
        "comments": runner(("gh", "api", f"repos/{repo}/pulls/{pr_number}/comments"), worktree),
    }


def classify(
    *,
    expected_worktree: Path,
    expected_head: str,
    results: dict[str, CommandResult],
) -> tuple[list[str], dict[str, str]]:
    blockers: list[str] = []
    facts: dict[str, str] = {}

    pwd = results["pwd"].stdout.strip()
    local_head = results["local_head"].stdout.strip()
    branch = results["branch"].stdout.strip()
    pr_view = parse_json_object(results["pr_view"])
    reviews = parse_json_list(results["reviews"])
    comments = parse_json_list(results["comments"])

    facts["pwd"] = pwd or "unknown"
    facts["branch"] = branch or "unknown"
    facts["local_head"] = local_head or "unknown"
    facts["expected_head"] = expected_head

    if pwd != str(expected_worktree):
        blockers.append(f"wrong_worktree: expected {expected_worktree}, got {pwd or 'unknown'}")

    if local_head != expected_head:
        blockers.append(f"local_head_mismatch: expected {expected_head}, got {local_head or 'unknown'}")

    if results["pr_view"].returncode != 0 or pr_view is None:
        blockers.append("pr_view_failed")
    else:
        pr_head = str(pr_view.get("headRefOid") or "")
        facts["pr_head"] = pr_head or "unknown"
        facts["pr_state"] = str(pr_view.get("state") or "unknown")
        facts["pr_draft"] = str(pr_view.get("isDraft"))
        facts["mergeable"] = str(pr_view.get("mergeable") or "unknown")
        facts["review_decision"] = str(pr_view.get("reviewDecision") or "")
        author = pr_view.get("author")
        author_login = ""
        if isinstance(author, dict):
            author_login = str(author.get("login") or "")
        facts["pr_author"] = author_login or "unknown"
        if not author_login:
            blockers.append("pr_author_unreadable")
        if pr_head != expected_head:
            blockers.append(f"pr_head_mismatch: expected {expected_head}, got {pr_head or 'unknown'}")

    if results["checks"].returncode != 0:
        blockers.append(f"checks_not_green: gh pr checks exited {results['checks'].returncode}")

    if reviews is None:
        blockers.append("reviews_unreadable")
        facts["submitted_reviews"] = "unknown"
        facts["independent_reviews"] = "unknown"
    else:
        facts["submitted_reviews"] = str(len(reviews))
        independent_reviews = [
            review
            for review in reviews
            if isinstance(review, dict)
            and isinstance(review.get("user"), dict)
            and str(review["user"].get("login") or "")
            and str(review["user"].get("login") or "") != facts.get("pr_author")
        ]
        facts["independent_reviews"] = str(len(independent_reviews))
        if len(independent_reviews) == 0:
            blockers.append(
                "independent_review_missing: no submitted GitHub review by someone other than the PR author"
            )

    if comments is None:
        facts["inline_comments"] = "unknown"
        facts["addressed_inline_comments"] = "unknown"
        facts["stale_inline_comments"] = "unknown"
        facts["active_inline_comments"] = "unknown"
        blockers.append("comments_unreadable")
    else:
        addressed_comments = [
            comment
            for comment in comments
            if review_comment_marked_addressed(comment)
        ]
        stale_comments = [
            comment
            for comment in comments
            if not review_comment_marked_addressed(comment)
            and review_comment_stale_for_head(comment, expected_head)
        ]
        active_comments = [
            comment
            for comment in comments
            if not review_comment_marked_addressed(comment)
            and not review_comment_stale_for_head(comment, expected_head)
        ]
        facts["inline_comments"] = str(len(comments))
        facts["addressed_inline_comments"] = str(len(addressed_comments))
        facts["stale_inline_comments"] = str(len(stale_comments))
        facts["active_inline_comments"] = str(len(active_comments))
        if active_comments:
            blockers.append(
                f"review_comments_present: {len(active_comments)} inline review comments require classification or remediation"
            )

    return blockers, facts


def render_report(
    *,
    repo: str,
    pr_number: str,
    expected_worktree: Path,
    expected_head: str,
    output_path: Path,
    results: dict[str, CommandResult],
    now: datetime,
) -> str:
    blockers, facts = classify(
        expected_worktree=expected_worktree,
        expected_head=expected_head,
        results=results,
    )
    status = "blocked" if blockers else "pass"
    can_progress = "no" if blockers else "yes"

    lines = [
        f"# PR #{pr_number} Governed Triage Report",
        "",
        "## Summary",
        "",
        f"- status: {status}",
        f"- repository: {repo}",
        f"- expected worktree: {expected_worktree}",
        f"- expected head: {expected_head}",
        f"- checked at: {now.isoformat().replace('+00:00', 'Z')}",
        f"- can progress under governed workflow: {can_progress}",
        "",
        "## Worktree Identity",
        "",
        f"- pwd: {facts.get('pwd', 'unknown')}",
        f"- branch: {facts.get('branch', 'unknown')}",
        f"- local head: {facts.get('local_head', 'unknown')}",
        "",
        "## PR State",
        "",
        f"- PR head: {facts.get('pr_head', 'unknown')}",
        f"- PR state: {facts.get('pr_state', 'unknown')}",
        f"- draft: {facts.get('pr_draft', 'unknown')}",
        f"- mergeable: {facts.get('mergeable', 'unknown')}",
        f"- review decision: {facts.get('review_decision', '')}",
        f"- PR author: {facts.get('pr_author', 'unknown')}",
        f"- submitted GitHub reviews: {facts.get('submitted_reviews', 'unknown')}",
        f"- independent GitHub reviews: {facts.get('independent_reviews', 'unknown')}",
        f"- inline review comments: {facts.get('inline_comments', 'unknown')}",
        f"- addressed inline review comments: {facts.get('addressed_inline_comments', 'unknown')}",
        f"- stale inline review comments: {facts.get('stale_inline_comments', 'unknown')}",
        f"- active inline review comments: {facts.get('active_inline_comments', 'unknown')}",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- none")

    lines.extend(["", "## Safe Next Action", ""])
    if blockers:
        lines.append(
            "Do not start the next implementation slice. Resolve the blockers above or record an explicit governance waiver that names the waived controls and residual risk."
        )
    else:
        lines.append(
            "The triage artifact is fresh for the requested worktree and head. The governor may continue only if the broader slice lifecycle also has no unresolved blockers."
        )

    lines.extend(["", "## Command Evidence", ""])
    for name, result in results.items():
        lines.extend(
            [
                f"### {name}",
                "",
                f"- command: {command_text(result.command)}",
                f"- exit: {result.returncode}",
                "",
                "stdout:",
                "",
                indented(result.stdout),
                "",
                "stderr:",
                "",
                indented(result.stderr),
                "",
            ]
        )

    lines.append(f"WROTE: {output_path.as_posix()}")
    return "\n".join(lines) + "\n"


def write_report(
    *,
    worktree: Path,
    repo: str,
    pr_number: str,
    expected_head: str,
    output_path: Path,
    runner: Runner = run_command,
    now: datetime | None = None,
) -> str:
    expected_worktree = worktree.resolve()
    if output_path.is_absolute():
        raise ValueError("--output must be relative to --worktree")
    destination = (expected_worktree / output_path).resolve()
    try:
        destination.relative_to(expected_worktree)
    except ValueError as exc:
        raise ValueError("--output must stay inside --worktree") from exc

    results = collect_results(expected_worktree, repo, pr_number, runner)
    report = render_report(
        repo=repo,
        pr_number=pr_number,
        expected_worktree=expected_worktree,
        expected_head=expected_head,
        output_path=output_path,
        results=results,
        now=now or datetime.now(UTC),
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    return report


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True, help="Absolute path to the checkout to inspect.")
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/name form.")
    parser.add_argument("--pr", required=True, help="Pull request number.")
    parser.add_argument("--head", required=True, help="Expected pull request head SHA.")
    parser.add_argument(
        "--output",
        required=True,
        help="Artifact path relative to --worktree. The report always ends with a WROTE line for this path.",
    )
    args = parser.parse_args(argv)
    if not Path(args.worktree).is_absolute():
        parser.error("--worktree must be an absolute path")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = write_report(
        worktree=Path(args.worktree),
        repo=args.repo,
        pr_number=args.pr,
        expected_head=args.head,
        output_path=Path(args.output),
    )
    print(report.splitlines()[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
