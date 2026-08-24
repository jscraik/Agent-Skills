"""Skill identity and package parser registration."""

from __future__ import annotations

import argparse


def _add_handles(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "handles",
        help="Inspect SDK-visible skill target registry",
        parents=[global_parser],
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when SDK skill target validation finds drift",
    )
    parser.add_argument(
        "--no-handles",
        action="store_true",
        help="Omit the full target list from JSON output",
    )
    parser.add_argument(
        "--write-projection",
        action="store_true",
        help="Removed flag; use skills sync --projection flat",
    )
    parser.add_argument(
        "--check-projection",
        action="store_true",
        help="Removed flag; use skills sync --projection flat, then skills list",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Accepted only with removed projection flags",
    )


def _add_resolve_and_parse(actions, global_parser: argparse.ArgumentParser) -> None:
    resolve = actions.add_parser(
        "resolve",
        help="Resolve an SDK-visible skill target or source path",
        parents=[global_parser],
    )
    resolve.add_argument(
        "handle", help="Skill target or repo-relative source path to resolve"
    )
    parse = actions.add_parser(
        "parse",
        help="Parse and resolve SDK skill mentions and @ reviewer roles from a prompt",
        parents=[global_parser],
    )
    parse.add_argument(
        "request",
        nargs="+",
        help="Prompt text containing SDK skill mentions and @ reviewer roles",
    )


def _add_proof_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    proof = actions.add_parser(
        "proof",
        help="Prove an SDK skill target reaches workspace and user runtime surfaces",
        parents=[global_parser],
    )
    proof.add_argument("handle", help="Skill target or source path to prove")
    proof.add_argument(
        "--runtime-target",
        default="any",
        help="Runtime that must satisfy proof: any, codex, or agents",
    )
    actions.add_parser(
        "prove", help="Show a skill proof scorecard", parents=[global_parser]
    ).add_argument(
        "handle", nargs="+", help="Skill target, source path, or goal to prove"
    )
    actions.add_parser(
        "explain",
        help="Explain when and how to use a skill target or source path",
        parents=[global_parser],
    ).add_argument("handle", help="Skill target or source path to explain")


def _add_doctor(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "doctor",
        help="Diagnose readiness for one skill target or source path",
        parents=[global_parser],
    )
    parser.add_argument(
        "target", help="Skill target or repo-relative skill source path"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Run strict audit instead of the default compat audit",
    )
    parser.add_argument(
        "--codex-parity",
        action="store_true",
        help="Require Codex-targeted runtime proof before reporting SDK conformance",
    )


def _add_package_core(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "target", help="Skill target, repo-relative skill source path, or 'verify'"
    )
    parser.add_argument(
        "verify_target",
        nargs="?",
        help="Skill target, source path, or package archive to verify when target is 'verify'",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when package readiness metadata is incomplete",
    )
    parser.add_argument(
        "--checkout-test",
        action="store_true",
        help="Run read-only local checkout evidence for the install gate",
    )


def _add_package_proof(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--expected-sha256", help="Expected package archive digest for verify mode"
    )
    parser.add_argument(
        "--trusted-provenance",
        help="Comma-separated trusted provenance sources for verify mode",
    )
    parser.add_argument(
        "--rollback-journal", help="Rollback journal JSONL evidence for verify mode"
    )


def _add_package(actions, global_parser: argparse.ArgumentParser) -> None:
    parser = actions.add_parser(
        "package",
        help="Report or verify package readiness for one skill",
        parents=[global_parser],
    )
    _add_package_core(parser)
    _add_package_proof(parser)


def add_identity_commands(actions, global_parser: argparse.ArgumentParser) -> None:
    """Register skill identity and package commands."""
    _add_handles(actions, global_parser)
    _add_resolve_and_parse(actions, global_parser)
    _add_proof_commands(actions, global_parser)
    _add_doctor(actions, global_parser)
    _add_package(actions, global_parser)
