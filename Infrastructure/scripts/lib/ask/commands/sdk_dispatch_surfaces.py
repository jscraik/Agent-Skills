from __future__ import annotations

import argparse
from pathlib import Path

import ask.commands.skills as skills_commands
from ask.cli_errors import build_unknown_action_result
from ask.envelope import CallResult, ErrorObject
from ask.skills_sdk.lenses import (
    LensCatalogError,
    explain_lens,
    list_lenses,
    select_lenses,
    validate_lens_catalog,
)
from ask.skills_sdk.local_score import (
    build_local_score_receipt_from_lane_payloads,
    write_local_score_receipts,
)
from ask.skills_sdk.review_execute import build_review_execution
from ask.skills_sdk.review_handoff import build_review_handoff
from ask.skills_sdk.review_plan import build_review_plan
from ask.skills_sdk.review_verify import build_review_verification


def _validation_error(command: str, message: str, fix_suggestion: str) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = command
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result


def _score_target(repo_root: Path, query: str) -> tuple[object, Path | None]:
    target_info, _audit_target = skills_commands._resolve_doctor_target(repo_root, query)
    value = target_info.get("source_path") if isinstance(target_info, dict) else None
    path = Path(str(value)) if value else None
    if path and not path.is_absolute():
        path = repo_root / path
    return value, path


def _blocked_score(query: str, gate: str, source_path_value: object, write_current: bool) -> CallResult:
    result = CallResult(status="error")
    result.metadata["command"] = "sdk score local"
    result.data["skills_sdk_local_score"] = {
        "schema_version": "skills-sdk-local-score-preview.v0",
        "status": "blocked",
        "query": query,
        "gate": gate,
        "canonical_source_path": source_path_value,
        "receipt": None,
        "receipt_paths": None,
        "write_current": write_current,
        "validation_commands": [f"ask sdk score local {query} --gate {gate} --json --robot"],
        "agent_summary": f"Local score is blocked for {query}: canonical source is missing.",
    }
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=f"Skills SDK local score is missing a canonical SKILL.md source for '{query}'.", fix_suggestion="Use a valid skill handle or repo-relative skill source path."))
    return result


def _score_receipt(repo_root: Path, query: str, source_path: Path, args: argparse.Namespace) -> dict[str, object]:
    return build_local_score_receipt_from_lane_payloads(
        repo_root,
        source_path=source_path,
        query=query,
        gate=args.gate,
        quality_result=skills_commands.skills_package_verify(repo_root, target=query),
        impact_result=skills_commands.skills_sdk_eval_scenario_quality(repo_root, target=query),
        security_result=skills_commands.skills_sdk_security_risk_modes_preview(repo_root, target=query),
        ttl_seconds=args.ttl_seconds,
    )


def _score_result(repo_root: Path, query: str, source_path: Path, args: argparse.Namespace, receipt: dict[str, object]) -> CallResult:
    paths = write_local_score_receipts(repo_root, receipt) if args.write_current else None
    result = CallResult(status="success")
    result.metadata["command"] = "sdk score local"
    result.data["skills_sdk_local_score"] = {
        "schema_version": "skills-sdk-local-score-preview.v0",
        "status": receipt["score"]["status"],
        "query": query,
        "gate": args.gate,
        "score": receipt["score"],
        "lanes": receipt["lanes"],
        "receipt": receipt,
        "receipt_paths": paths,
        "write_current": bool(args.write_current),
        "validation_commands": [f"ask sdk score local {query} --gate {args.gate} --json --robot"],
        "agent_summary": f"Local score for {receipt['skill_name']} is {receipt['score']['value']} ({receipt['score']['status']}).",
    }
    return result


def _dispatch_sdk_score(repo_root: Path, args: argparse.Namespace) -> CallResult:
    if args.score_action != "local":
        return build_unknown_action_result("sdk score", args.score_action)
    query = args.target.strip()
    source_path_value, source_path = _score_target(repo_root, query)
    if source_path is None:
        return _blocked_score(query, args.gate, source_path_value, bool(args.write_current))
    return _score_result(repo_root, query, source_path, args, _score_receipt(repo_root, query, source_path, args))


def _dispatch_sdk_observability(repo_root: Path, args: argparse.Namespace) -> CallResult:
    action = args.observability_action
    if action in {"feedback", "promote"} and not args.preview:
        return _validation_error(
            f"sdk observability {action}",
            f"Skills SDK observability {action} is preview-only in PU-026.",
            "ask sdk observability feedback --skill <target> --events <events.jsonl> --preview --json --robot",
        )
    if action == "feedback":
        return skills_commands.skills_sdk_observability_feedback(repo_root, target=args.skill, events=args.events)
    if action == "promote":
        return skills_commands.skills_sdk_observability_promote(
            repo_root,
            feedback_receipt=args.feedback_receipt,
            package_receipt=args.package_receipt,
            eval_run_receipt=args.eval_run_receipt,
        )
    if action == "phoenix-status":
        return skills_commands.skills_sdk_observability_phoenix_status(repo_root, base_url=args.base_url, timeout_seconds=args.timeout_seconds)
    if action == "phoenix-smoke":
        return _dispatch_phoenix_smoke(repo_root, args)
    if action == "phoenix-mirror":
        if args.preview == args.write:
            return _validation_error(
                "sdk observability phoenix-mirror",
                "Phoenix mirror requires exactly one of --preview or --write.",
                "ask sdk observability phoenix-mirror --receipt <receipt.json> --preview --json --robot",
            )
        return skills_commands.skills_sdk_observability_phoenix_mirror(
            repo_root, receipt_path=args.receipt, out_path=args.out, write=args.write
        )
    return build_unknown_action_result("sdk observability", action)


def _dispatch_phoenix_smoke(repo_root: Path, args: argparse.Namespace) -> CallResult:
    return skills_commands.skills_sdk_observability_phoenix_smoke(
        repo_root,
        base_url=args.base_url,
        profile=args.profile,
        timeout_seconds=args.timeout_seconds,
        otel_python_path=args.otel_python,
        model_name=args.model,
        provider=args.provider,
        prompt_tokens=args.prompt_tokens,
        completion_tokens=args.completion_tokens,
    )


def _lens_payload(repo_root: Path, args: argparse.Namespace) -> tuple[str, str, object]:
    action = args.lenses_action
    if action == "list":
        return "lens_catalog", "pass", list_lenses(repo_root, registry_path=args.registry)
    if action == "explain":
        return "lens", "pass", explain_lens(repo_root, args.lens_id, registry_path=args.registry)
    if action == "validate":
        return "lens_catalog_validation", "validate", validate_lens_catalog(repo_root, registry_path=args.registry)
    if action == "select":
        return "lens_selection", "select", select_lenses(
            repo_root,
            prompt=args.prompt,
            task_intent=args.task_intent,
            repo_files=args.repo_file,
            max_lenses=args.max_lenses,
            skill=args.skill,
            registry_path=args.registry,
        )
    raise LensCatalogError(f"Unknown lens action: {action}")


def _dispatch_sdk_lenses(repo_root: Path, args: argparse.Namespace) -> CallResult:
    result = CallResult(status="success")
    action = args.lenses_action
    result.metadata["command"] = f"sdk lenses {action}"
    try:
        key, kind, payload = _lens_payload(repo_root, args)
    except LensCatalogError as exc:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(exc), fix_suggestion="Run ask sdk lenses validate --json --robot to inspect the shared lens catalog."))
        return result
    result.data[key] = payload
    if kind in {"validate", "select"} and payload["status"] != "pass":
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Shared SDK lens catalog validation failed." if kind == "validate" else "Shared SDK lens selection could not run because catalog validation failed.", fix_suggestion="Run ask sdk lenses validate --json --robot and fix the reported findings."))
    return result


def _review_payload(repo_root: Path, args: argparse.Namespace) -> tuple[str, object, str]:
    action = args.review_action
    if action == "plan":
        return "review_plan", build_review_plan(repo_root, target=args.target, task_intent=args.task_intent, prompt=args.prompt, repo_files=args.repo_file, max_lenses=args.max_lenses, receipt_out=args.receipt_out), "Skills SDK review plan could not be built."
    if action == "handoff":
        return "review_handoff", build_review_handoff(repo_root, plan_path=args.plan, target=args.target, task_intent=args.task_intent, receipt_out=args.receipt_out), "Skills SDK review handoff could not be built."
    if action == "execute":
        return "review_execution", build_review_execution(repo_root, handoff_path=args.handoff, receipt_out=args.receipt_out), "Skills SDK review execution could not materialize every required artifact."
    if action == "verify":
        return "review_verification", build_review_verification(repo_root, handoff_path=args.handoff, receipt_out=args.receipt_out), "Skills SDK review artifacts are missing or invalid."
    raise ValueError(f"Unknown review action: {action}")


def _dispatch_sdk_review(repo_root: Path, args: argparse.Namespace) -> CallResult:
    result = CallResult(status="success")
    action = args.review_action
    result.metadata["command"] = f"sdk review {action}"
    try:
        key, payload, failure_message = _review_payload(repo_root, args)
    except (LensCatalogError, ValueError) as exc:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(exc), fix_suggestion="Repair the review receipt inputs and retry the requested SDK review action."))
        return result
    result.data[key] = payload
    if payload["status"] != "pass":
        fixes = {
            "plan": "Run ask sdk lenses validate --json --robot and fix catalog findings.",
            "handoff": "Repair the source review plan and retry the handoff action.",
            "execute": "Repair every path in data.review_execution.failed_artifacts.",
            "verify": "Create or repair every path in data.review_verification.missing_or_invalid_artifacts.",
        }
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=failure_message, fix_suggestion=fixes[action]))
    return result
