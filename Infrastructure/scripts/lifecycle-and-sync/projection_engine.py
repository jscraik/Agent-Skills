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
        """
        Initialize the ProjectionModeError with an error code, human-readable message, and the projection mode context.
        
        Parameters:
            code (str): Machine-readable error code identifying the failure reason.
            message (str): Human-readable explanation of the error.
            requested_mode (str): The original mode value provided by the caller or environment.
            resolved_mode (str | None): The canonical resolved mode when available, or None if resolution failed.
        """
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
        """
        Convert the ProjectionModeDecision into a plain dictionary.
        
        Returns:
            A dictionary representation of the dataclass suitable for serialization (keys are the dataclass fields).
        """
        return asdict(self)


def _clean_mode(raw_mode: str) -> str:
    """
    Normalize a projection mode token.
    
    Parameters:
        raw_mode (str): Input mode string that may include surrounding whitespace, uppercase letters, or underscores.
    
    Returns:
        cleaned_mode (str): The mode string trimmed of surrounding whitespace, lowercased, with underscores replaced by hyphens.
    """
    return raw_mode.strip().lower().replace("_", "-")


def normalize_projection_mode(
    requested_mode: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> ProjectionModeDecision:
    """
    Resolve and validate the projection mode chosen by the caller and return a canonical decision.
    
    When `requested_mode` is provided and non-empty it takes precedence, otherwise the function reads
    the `SYNC_SKILLS_PROJECTION_MODE` value from `env` (or the process environment if `env` is None),
    and falls back to the module `DEFAULT_PROJECTION_MODE` if neither is set. The selected value is
    cleaned, alias-resolved, validated, and returned as a frozen ProjectionModeDecision.
    
    Parameters:
        requested_mode (str | None): Optional raw mode value supplied by the caller (e.g., CLI).
        env (Mapping[str, str] | None): Optional mapping to read environment values from; if None,
            the process environment is used.
    
    Returns:
        ProjectionModeDecision: Immutable decision containing the resolved canonical `projection_mode`,
        the original `requested_mode` (raw string), `mode_source` (`"cli"`, `"env"`, or `"default"`),
        `default_projection_mode`, `policy_identity`, `engine`, optional `alias_of` if an alias was used,
        and `mutation_available` which is true only for canonical modes `"flat"` and `"rooted"`.
    
    Raises:
        ProjectionModeError: If the cleaned mode is in a deferred set (code `ERR_DEFERRED_PROJECTION_MODE`)
            or if the resolved canonical mode is not supported (code `ERR_INVALID_PROJECTION_MODE`).
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
    """
    Abort operation if the resolved projection mode does not permit mutations.
    
    Parameters:
        decision (ProjectionModeDecision): Normalized projection mode decision.
        dry_run (bool): When True, allow the operation even if mutations are unavailable.
    
    Raises:
        ProjectionModeError: If mutations are unavailable for the resolved mode and `dry_run` is False. The error includes `requested_mode` and `resolved_mode`.
    """
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
    """
    Compose shared metadata for a projection plan result.
    
    Parameters:
        decision (ProjectionModeDecision): Normalized projection mode decision to include.
        scope (str): Identifier for the scope the plan covers (for example, a project, workspace, or path).
        dry_run (bool): Whether the plan was produced as a dry run.
        warnings (list[str] | None): Optional list of warning messages; treated as an empty list when omitted.
    
    Returns:
        dict[str, object]: A dictionary containing the fields from `decision.to_dict()`, plus `scope`, `dry_run`, and `warnings` (always a list).
    """
    return {
        **decision.to_dict(),
        "scope": scope,
        "dry_run": dry_run,
        "warnings": list(warnings or []),
    }


def _format_shell(decision: ProjectionModeDecision) -> str:
    """
    Format a ProjectionModeDecision as newline-separated shell-style KEY=VALUE assignments.
    
    Parameters:
        decision (ProjectionModeDecision): Normalized projection decision whose fields are emitted.
    
    Returns:
        str: Newline-separated lines like `KEY=VALUE` suitable for shell consumption. Values are shell-quoted; `SYNC_SKILLS_PROJECTION_MUTATION_AVAILABLE` is `"1"` when mutation is available and `"0"` otherwise.
    """
    values = {
        "SYNC_SKILLS_RESOLVED_PROJECTION_MODE": decision.projection_mode,
        "SYNC_SKILLS_REQUESTED_PROJECTION_MODE": decision.requested_mode,
        "SYNC_SKILLS_PROJECTION_MODE_SOURCE": decision.mode_source,
        "SYNC_SKILLS_PROJECTION_ENGINE": decision.engine,
        "SYNC_SKILLS_PROJECTION_MUTATION_AVAILABLE": "1" if decision.mutation_available else "0",
    }
    return "\n".join(f"{name}={shlex.quote(value)}" for name, value in values.items())


def main() -> int:
    """
    CLI entrypoint that parses arguments, normalizes the requested projection mode, and emits a result payload.
    
    Parses `--mode` and `--format` (json|shell). On successful normalization prints a success payload (JSON or shell-style KEY=VALUE lines). If normalization fails, prints an error payload formatted for the selected output and returns a non-zero exit status.
    
    Returns:
        int: Exit code: `0` on success, `2` if projection mode normalization fails.
    """
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
