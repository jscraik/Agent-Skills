#!/usr/bin/env python3
"""Shared runtime projection-mode parsing and sync-plan metadata."""

from __future__ import annotations

import argparse
import json
import os
import shlex
from dataclasses import asdict, dataclass
from collections.abc import Mapping

from selection_policy import (
    DEFAULT_PROJECTION_MODE,
    DEFERRED_PROJECTION_MODES,
    PROJECTION_MODE_ALIASES,
    SUPPORTED_PROJECTION_MODES,
    policy_identity,
)

ENV_PROJECTION_MODE = "SYNC_SKILLS_PROJECTION_MODE"
ENGINE_NAME = "projection_engine.py"


class ProjectionModeError(ValueError):
    """Raised when a requested projection mode cannot be used."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        requested_mode: str,
        resolved_mode: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.requested_mode = requested_mode
        self.resolved_mode = resolved_mode


@dataclass(frozen=True)
class ProjectionModeDecision:
    """Normalized projection-mode decision for reporting and sync dispatch."""

    projection_mode: str
    requested_mode: str
    mode_source: str
    default_projection_mode: str
    policy_identity: str
    engine: str = ENGINE_NAME
    alias_of: str | None = None
    mutation_available: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _clean_mode(raw_mode: str) -> str:
    return raw_mode.strip().lower().replace("_", "-")


def normalize_projection_mode(
    requested_mode: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> ProjectionModeDecision:
    """
    Normalize the requested projection mode.

    Precedence is explicit CLI/request value, then SYNC_SKILLS_PROJECTION_MODE,
    then the rooted default.
    """
    env_values = env if env is not None else os.environ
    raw_requested = (requested_mode or "").strip()
    if raw_requested:
        raw_mode = raw_requested
        mode_source = "cli"
    else:
        env_mode = (env_values.get(ENV_PROJECTION_MODE) or "").strip()
        if env_mode:
            raw_mode = env_mode
            mode_source = "env"
        else:
            raw_mode = DEFAULT_PROJECTION_MODE
            mode_source = "default"

    cleaned = _clean_mode(raw_mode)
    canonical = PROJECTION_MODE_ALIASES.get(cleaned, cleaned)
    alias_of = canonical if canonical != cleaned else None

    if cleaned in DEFERRED_PROJECTION_MODES:
        raise ProjectionModeError(
            "ERR_DEFERRED_PROJECTION_MODE",
            f"Projection mode '{raw_mode}' is deferred and cannot be used for sync yet.",
            requested_mode=raw_mode,
        )
    if canonical not in SUPPORTED_PROJECTION_MODES:
        choices = ", ".join((*SUPPORTED_PROJECTION_MODES, *PROJECTION_MODE_ALIASES, *DEFERRED_PROJECTION_MODES))
        raise ProjectionModeError(
            "ERR_INVALID_PROJECTION_MODE",
            f"Unsupported projection mode '{raw_mode}'. Expected one of: {choices}.",
            requested_mode=raw_mode,
        )

    return ProjectionModeDecision(
        projection_mode=canonical,
        requested_mode=raw_mode,
        mode_source=mode_source,
        default_projection_mode=DEFAULT_PROJECTION_MODE,
        alias_of=alias_of,
        mutation_available=canonical in {"flat", "rooted"},
        policy_identity=policy_identity(),
    )


def ensure_mutation_supported(decision: ProjectionModeDecision, *, dry_run: bool) -> None:
    """Fail before mutation when a parsed mode is not implemented for writes."""
    if dry_run or decision.mutation_available:
        return
    raise ProjectionModeError(
        "ERR_PROJECTION_MUTATION_UNAVAILABLE",
        (
            f"Projection mode '{decision.projection_mode}' is parsed but mutation is not "
            "implemented in this phase; use --dry-run or --projection flat."
        ),
        requested_mode=decision.requested_mode,
        resolved_mode=decision.projection_mode,
    )


def build_projection_plan_metadata(
    decision: ProjectionModeDecision,
    *,
    scope: str,
    dry_run: bool,
    warnings: list[str] | None = None,
) -> dict[str, object]:
    """Return common metadata embedded in sync dry-run and mutation results."""
    return {
        **decision.to_dict(),
        "scope": scope,
        "dry_run": dry_run,
        "warnings": list(warnings or []),
    }


def _format_shell(decision: ProjectionModeDecision) -> str:
    values = {
        "SYNC_SKILLS_RESOLVED_PROJECTION_MODE": decision.projection_mode,
        "SYNC_SKILLS_REQUESTED_PROJECTION_MODE": decision.requested_mode,
        "SYNC_SKILLS_PROJECTION_MODE_SOURCE": decision.mode_source,
        "SYNC_SKILLS_PROJECTION_ENGINE": decision.engine,
        "SYNC_SKILLS_PROJECTION_MUTATION_AVAILABLE": "1" if decision.mutation_available else "0",
    }
    return "\n".join(f"{name}={shlex.quote(value)}" for name, value in values.items())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default=None, help="Requested projection mode")
    parser.add_argument("--format", choices=("json", "shell"), default="json")
    args = parser.parse_args()

    try:
        decision = normalize_projection_mode(args.mode)
    except ProjectionModeError as exc:
        payload = {
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "requested_mode": exc.requested_mode,
            "resolved_mode": exc.resolved_mode,
        }
        if args.format == "shell":
            print(f"SYNC_SKILLS_PROJECTION_ERROR={shlex.quote(exc.code)}")
            print(f"SYNC_SKILLS_PROJECTION_ERROR_MESSAGE={shlex.quote(exc.message)}")
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    if args.format == "shell":
        print(_format_shell(decision))
    else:
        print(json.dumps({"status": "success", **decision.to_dict()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
