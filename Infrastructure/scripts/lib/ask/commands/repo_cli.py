"""Auxiliary argument-parser construction for repository commands."""

from __future__ import annotations

import argparse


def _add_catalog(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "doctor-catalog",
        help="Diagnose canonical catalog parity drift",
        parents=[global_parser],
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict trend and stamp enforcement",
    )


def _add_attach(
    subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "attach-detached-head",
        help="Attach a detached checkout to a collision-safe Codex branch",
        parents=[global_parser],
    )
    parser.add_argument(
        "--branch-prefix",
        default="codex/feature",
        help="Branch namespace used when attaching a detached checkout",
    )


def add_repo_auxiliary_parsers(
    repo_subparsers: argparse._SubParsersAction,
    global_parser: argparse.ArgumentParser,
) -> None:
    """Register smaller repository diagnostics and attachment commands."""
    _add_catalog(repo_subparsers, global_parser)
    repo_subparsers.add_parser(
        "provider-audit",
        help="Audit active paths for legacy provider drift",
        parents=[global_parser],
    )
    _add_attach(repo_subparsers, global_parser)
    surface = repo_subparsers.add_parser(
        "surface",
        help="Inventory tracked repo surface ownership",
        parents=[global_parser],
    )
    surface.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when blocking surface findings exist",
    )


__all__ = ["add_repo_auxiliary_parsers"]
