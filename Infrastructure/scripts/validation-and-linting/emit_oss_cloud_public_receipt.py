#!/usr/bin/env python3
"""Emit the bounded, value-blind oss-cloud receipt from allowlisted fields."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json


EXPECTED_MODEL = "deepseek-v4-flash:cloud"
EXPECTED_PROVIDER = "ollama-cloud"
DEFAULT_MARKER = "CODEX_OSS_CLOUD_OK"
_FINDING_MESSAGES = (
    ("oss_cloud_profile_missing", "oss-cloud profile source must be a regular file."),
    ("oss_cloud_model_mismatch", "The reviewed oss-cloud model did not match."),
    ("oss_cloud_provider_mismatch", "The reviewed oss-cloud provider did not match."),
    ("oss_cloud_marker_not_allowlisted", "The bounded cloud smoke requires its fixed marker."),
    ("oss_cloud_auth_stream_missing", "Desktop-owned OLLAMA_API_KEY FIFO is required."),
    ("oss_cloud_auth_wrapper_missing", "Configs auth wrapper is required for oss-cloud."),
    ("oss_cloud_exec_wrapper_missing", "Configs Codex wrapper is required for oss-cloud."),
    ("oss_cloud_auth_wrapper_identity_mismatch", "The supplied auth wrapper must be canonical."),
    ("oss_cloud_exec_wrapper_identity_mismatch", "The supplied Codex wrapper must be canonical."),
    ("codex_runtime_metadata_fallback", "Codex reported fallback metadata."),
    ("codex_runtime_visible_thinking", "Model output exposed a thinking trace."),
    ("codex_runtime_token_budget_exceeded", "The smoke transcript exceeded its token budget."),
    ("oss_cloud_secret_output_observed", "Captured smoke output matched a secret-shaped marker."),
    ("oss_cloud_secret_output_scan_unavailable", "Captured smoke output could not be safely scanned."),
    ("oss_cloud_smoke_exit_nonzero", "Codex exited with a non-zero status."),
    ("oss_cloud_smoke_marker_mismatch", "Cloud smoke marker did not match."),
    ("unclassified_smoke_finding", "An unclassified smoke finding was observed."),
)
_REDACTED_COMMAND = (
    "bash", "<configs-auth-wrapper>", "--env-file", "<operator-approved-opaque-env-stream>",
    "--require-env", "OLLAMA_API_KEY", "--", "env", "-u", "CODEX_CONFIG_HOME",
    "CODEX_HOME=<isolated-codex-home>", "bash", "<configs-codex-exec-wrapper>",
    "--profile", "oss-cloud", "--strict-config", "-c", 'approval_policy="on-request"',
    "--skip-git-repo-check", "--sandbox", "read-only", "--ephemeral", "--model",
    EXPECTED_MODEL, f"Reply exactly {DEFAULT_MARKER}",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit a value-blind oss-cloud smoke receipt.")
    parser.add_argument("--status", choices=("pass", "blocked"), required=True)
    parser.add_argument("--auth-source", choices=("1password_desktop_fifo", "missing_or_invalid"), required=True)
    parser.add_argument("--provider-invoked", choices=("true", "false"), required=True)
    parser.add_argument("--command-present", choices=("true", "false"), required=True)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--duration-seconds", type=float, required=True)
    parser.add_argument("--findings", default="")
    parser.add_argument("--warnings", default="")
    parser.add_argument("--secret-status", choices=("clear", "blocked", "unavailable"), required=True)
    parser.add_argument("--json", action="store_true")
    return parser


def _projected_findings(raw_codes: str) -> list[dict[str, str]]:
    """Project only immutable, reviewed receipt strings from requested code names."""
    requested_codes = frozenset(raw_codes.split(","))
    return [
        {"code": code, "message": message}
        for code, message in _FINDING_MESSAGES
        if code in requested_codes
    ]


def _receipt(args: argparse.Namespace) -> dict[str, object]:
    secret_status = args.secret_status
    return {
        "schema_version": "skills-sdk.oss-cloud-smoke-run.v0",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": args.status,
        "lane": "oss-cloud",
        "codex_profile": "oss-cloud",
        "model": EXPECTED_MODEL,
        "model_provider": EXPECTED_PROVIDER,
        "auth_source": args.auth_source,
        "provider_invoked": args.provider_invoked == "true",
        "command": list(_REDACTED_COMMAND) if args.command_present == "true" else None,
        "execution_argv": list(_REDACTED_COMMAND) if args.command_present == "true" else None,
        "duration_seconds": args.duration_seconds,
        "exit_code": args.exit_code,
        "marker": DEFAULT_MARKER,
        "stdout_path": "<captured-stdout>",
        "stderr_path": "<captured-stderr>",
        "last_message_path": "<captured-last-message>",
        "warnings": _projected_findings(args.warnings),
        "findings": _projected_findings(args.findings),
        "secret_observation": {
            "status": secret_status,
            "source": "captured_output_scan",
            "redacted": True,
        },
        "secret_value_observed": secret_status == "blocked",
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    receipt = _receipt(args)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")) if args.json else receipt["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
