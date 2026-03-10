#!/usr/bin/env python3
"""
Deterministic Agentation watch-mode readiness checker.

This helper stays offline and only evaluates local project evidence plus
explicitly supplied observed state. It does not call Agentation services.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT_CANDIDATES = [
    "app/layout.tsx",
    "app/layout.jsx",
    "app/layout.ts",
    "app/layout.js",
    "pages/_app.tsx",
    "pages/_app.jsx",
    "pages/_app.ts",
    "pages/_app.js",
    "src/App.tsx",
    "src/App.jsx",
    "src/App.ts",
    "src/App.js",
    "src/main.tsx",
    "src/main.jsx",
    "src/main.ts",
    "src/main.js",
]

FULL_WATCH_TOOLS = {
    "agentation_watch_annotations",
    "agentation_acknowledge",
    "agentation_resolve",
}

OPTIONAL_WATCH_TOOLS = {
    "agentation_reply",
    "agentation_get_pending",
    "agentation_get_all_pending",
    "agentation_get_session",
    "agentation_list_sessions",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Agentation watch-mode readiness")
    parser.add_argument("--project-root", required=True, help="Target app project root")
    parser.add_argument(
        "--mcp-tools",
        default="",
        help="Comma-separated MCP tools currently available in the client/runtime",
    )
    parser.add_argument(
        "--pending-state",
        choices=["unknown", "idle", "pending", "degraded"],
        default="unknown",
    )
    parser.add_argument(
        "--runner-state",
        choices=["manual", "critique", "autopilot", "watch_mode", "stopped"],
        default="manual",
    )
    parser.add_argument("--ui-mounted", action="store_true", help="Agentation widget confirmed mounted")
    parser.add_argument("--dev-gated", action="store_true", help="Widget mount confirmed dev-only")
    parser.add_argument(
        "--synthetic-webhook-verified",
        action="store_true",
        help="Synthetic webhook POST confirmed",
    )
    parser.add_argument(
        "--real-submit-verified",
        action="store_true",
        help="Real submit event confirmed end-to-end",
    )
    parser.add_argument("--webhook-url", help="Configured webhook URL, if known")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def detect_framework(project_root: Path) -> tuple[str, str | None]:
    for candidate in ROOT_CANDIDATES:
        full = project_root / candidate
        if full.exists():
            if candidate.startswith("app/layout"):
                return "next-app-router", candidate
            if candidate.startswith("pages/_app"):
                return "next-pages-router", candidate
            if candidate.startswith("src/App"):
                return "vite-react-or-tauri", candidate
            if candidate.startswith("src/main"):
                return "vite-react-or-tauri", candidate
    return "unknown", None


def load_package_json(project_root: Path) -> dict[str, Any]:
    package_json = project_root / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def dependency_presence(package_json: dict[str, Any], dependency: str) -> bool:
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        if dependency in package_json.get(section, {}):
            return True
    return False


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.project_root).expanduser().resolve()
    framework, root_file = detect_framework(project_root)
    package_json = load_package_json(project_root)

    declared_tools = {tool.strip() for tool in args.mcp_tools.split(",") if tool.strip()}
    full_watch_ready = FULL_WATCH_TOOLS.issubset(declared_tools)
    optional_hits = sorted(declared_tools & OPTIONAL_WATCH_TOOLS)

    if args.ui_mounted and args.dev_gated and root_file:
        ui_state = "ready"
    elif root_file:
        ui_state = "degraded"
    else:
        ui_state = "missing"

    if full_watch_ready:
        mcp_state = "connected"
    elif declared_tools:
        mcp_state = "degraded"
    else:
        mcp_state = "disconnected"

    if args.real_submit_verified:
        webhook_state = "real_submit_verified"
    elif args.synthetic_webhook_verified:
        webhook_state = "synthetic_only"
    elif args.webhook_url:
        webhook_state = "unverified"
    else:
        webhook_state = "unknown"

    findings: list[dict[str, str]] = []
    if not project_root.exists():
        findings.append({"severity": "critical", "message": "Project root does not exist"})
    if not root_file:
        findings.append({"severity": "critical", "message": "No supported root integration file detected"})
    if not dependency_presence(package_json, "agentation"):
        findings.append({"severity": "warn", "message": "package.json does not declare agentation"})
    if mcp_state != "connected":
        findings.append({"severity": "warn", "message": "Exact watch-mode MCP tool surface is incomplete"})
    if webhook_state in {"unknown", "unverified"}:
        findings.append({"severity": "warn", "message": "Webhook path is not yet end-to-end verified"})
    if ui_state != "ready":
        findings.append({"severity": "warn", "message": "UI mount is missing or not confirmed dev-only"})
    if args.pending_state == "unknown":
        findings.append({"severity": "info", "message": "Queue state is unknown"})

    blocked = any(item["severity"] == "critical" for item in findings)
    watch_mode_ready = (
        not blocked
        and ui_state == "ready"
        and mcp_state == "connected"
        and args.pending_state in {"idle", "pending"}
    )

    return {
        "schema_version": "1.0",
        "project_root": str(project_root),
        "framework": framework,
        "root_file": root_file,
        "states": {
            "ui_mount": ui_state,
            "mcp": mcp_state,
            "webhook": webhook_state,
            "queue": args.pending_state,
            "runner": args.runner_state,
        },
        "tooling": {
            "declared_watch_tools": sorted(declared_tools),
            "required_watch_tools": sorted(FULL_WATCH_TOOLS),
            "optional_watch_tools_detected": optional_hits,
        },
        "package_evidence": {
            "package_json_present": bool(package_json),
            "agentation_dependency": dependency_presence(package_json, "agentation"),
            "agentation_mcp_dependency": dependency_presence(package_json, "agentation-mcp"),
        },
        "summary": {
            "blocked": blocked,
            "watch_mode_ready": watch_mode_ready,
            "real_submit_verified": args.real_submit_verified,
        },
        "findings": findings,
    }


def emit_text(report: dict[str, Any]) -> str:
    lines = [
        "Agentation watch-mode readiness",
        f"project_root: {report['project_root']}",
        f"framework: {report['framework']}",
        f"root_file: {report['root_file'] or 'unknown'}",
        "",
        "states:",
    ]
    for key, value in report["states"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "summary:",
            f"- blocked: {str(report['summary']['blocked']).lower()}",
            f"- watch_mode_ready: {str(report['summary']['watch_mode_ready']).lower()}",
            f"- real_submit_verified: {str(report['summary']['real_submit_verified']).lower()}",
            "",
            "findings:",
        ]
    )
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- {finding['severity']}: {finding['message']}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(emit_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
