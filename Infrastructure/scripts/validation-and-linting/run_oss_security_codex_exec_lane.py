#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from classify_codex_exec_security_lane import classify
from extract_oss_security_review import validate_review


REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGS_ROOT = REPO_ROOT.parent / "configs" / "codex"
DEFAULT_TARGET = "Skills/agent-ops/improve-agent-native"
SECURITY_MODEL = "h4rithd/coder:14b"
REVIEW_PROMPT_CONTRACT_VERSION = "skills-sdk.oss-security-review-prompt.v1"
REVIEW_INPUT_COMPACT_LIMIT_BYTES = 24 * 1024


def _copy_codex_home(codex_home: Path) -> None:
    codex_home.mkdir(parents=True, exist_ok=True)
    for name in ("config.toml", "oss-security.config.toml"):
        shutil.copy2(CONFIGS_ROOT / name, codex_home / name)


def _prompt(target: str) -> str:
    js_source = (
        '// @exec: {"yield_time_ms": 30000, "max_output_tokens": 4000}\n'
        "const r = await tools.exec_command({\n"
        f'  cmd: "./bin/ask sdk security run-lane {target} --preview --profile oss-security --json --robot",\n'
        f'  workdir: "{REPO_ROOT.as_posix()}",\n'
        "  yield_time_ms: 30000,\n"
        "  max_output_tokens: 4000\n"
        "});\n"
        'text("exit=" + r.exit_code + "\\n" + r.output);'
    )
    return (
        "Call the exec tool exactly once. The exec tool input must be raw JavaScript source, "
        "not JSON and not a shell command. Do not call request_permissions. Submit this exact "
        "raw exec input:\n\n"
        f"{js_source}\n\n"
        "After the tool returns, answer with the observed exit code and whether "
        "skills_sdk_security_lane.status is pass."
    )


def _receipt_review_input(lane_receipt: dict[str, Any]) -> dict[str, Any]:
    lane = lane_receipt["data"]["skills_sdk_security_lane"]
    return {
        "schema_version": "skills-sdk.oss-security-review-input.v0",
        "package": lane.get("package_id"),
        "lane_status": lane.get("status"),
        "security_lane_digest": lane.get("security_lane_digest"),
        "package_digest": lane.get("package_digest"),
        "package_security_signature_digest": lane.get("package_security_signature_digest"),
        "risk_mode_taxonomy_digest": lane.get("risk_mode_taxonomy_digest"),
        "indicator_summary": lane.get("indicator_summary", {}),
        "primary_mode": lane.get("primary_mode"),
        "detected_modes": lane.get("detected_modes", []),
        "commands": lane.get("commands", []),
        "profile_review": lane.get("profile_review", {}),
    }


def _review_prompt(review_input: dict[str, Any]) -> str:
    return (
        "You are reviewing a deterministic Skills SDK security-lane receipt summary. "
        "Do not call tools. Do not claim you ran commands. Return JSON only with keys: "
        "schema_version, review_status, risk_summary, required_followups, "
        "evidence_digest_seen, reviewer_model_boundary. The evidence_digest_seen value "
        "must be the security_lane_digest from the receipt. The review_status value must "
        "be exactly one of: pass, warn, fail, blocked. The risk_summary value must be "
        "a non-empty sentence under 320 characters. The required_followups value must "
        "contain at most 5 compact strings. The reviewer_model_boundary value must explain "
        "that you reviewed only the supplied receipt and did not run tools or commands. "
        f"Prompt contract: {REVIEW_PROMPT_CONTRACT_VERSION}.\n\n"
        "Receipt summary JSON:\n"
        f"{json.dumps(review_input, sort_keys=True)}\n"
    )


def _model_blocker(model: str | None) -> str | None:
    if model is None or model == SECURITY_MODEL:
        return None
    return f"oss-security receipt review only allows {SECURITY_MODEL}; got {model}"


def _run_deterministic_lane(target: str) -> tuple[int, dict[str, Any] | None, str]:
    process = subprocess.run(
        [
            "./bin/ask",
            "sdk",
            "security",
            "run-lane",
            target,
            "--preview",
            "--profile",
            "oss-security",
            "--json",
            "--robot",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError:
        payload = None
    return process.returncode, payload, process.stdout


def _run_codex(
    *,
    codex_home: Path,
    target: str,
    output_dir: Path,
    model: str | None,
    model_catalog_json: str | None,
) -> tuple[int, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "oss-security-codex-exec-security-lane.jsonl"
    last_message_path = output_dir / "oss-security-codex-exec-security-lane-last.txt"
    process = subprocess.run(
        _codex_command(
            sandbox="workspace-write",
            last_message_path=last_message_path,
            model=model,
            model_catalog_json=model_catalog_json,
        ),
        input=_prompt(target),
        cwd=REPO_ROOT,
        env=_codex_env(codex_home),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    jsonl_path.write_text(process.stdout, encoding="utf-8")
    return process.returncode, jsonl_path, last_message_path


def _codex_command(
    *,
    sandbox: str,
    last_message_path: Path,
    model: str | None,
    model_catalog_json: str | None,
) -> list[str]:
    blocker = _model_blocker(model)
    if blocker:
        raise ValueError(blocker)
    command = [
        "codex",
        "exec",
        "--profile",
        "oss-security",
        "-c",
        "skills.config=[]",
        "--sandbox",
        sandbox,
        "--ephemeral",
        "--json",
        "--output-last-message",
        str(last_message_path),
    ]
    if model:
        command.extend(["-c", f'model="{model}"'])
    if model_catalog_json:
        command.extend(["-c", f'model_catalog_json="{model_catalog_json}"'])
    return command


def _codex_env(codex_home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    env["MISE_TRUSTED_CONFIG_PATHS"] = str(REPO_ROOT / ".mise.toml")
    return env


def _run_receipt_review(
    *,
    codex_home: Path,
    review_input: dict[str, Any],
    output_dir: Path,
    model: str | None,
    model_catalog_json: str | None,
) -> tuple[int, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "oss-security-codex-exec-receipt-review.jsonl"
    last_message_path = output_dir / "oss-security-codex-exec-receipt-review-last.txt"
    process = subprocess.run(
        _codex_command(
            sandbox="read-only",
            last_message_path=last_message_path,
            model=model,
            model_catalog_json=model_catalog_json,
        ),
        input=_review_prompt(review_input),
        cwd=REPO_ROOT,
        env=_codex_env(codex_home),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    jsonl_path.write_text(process.stdout, encoding="utf-8")
    return process.returncode, jsonl_path, last_message_path


def _receipt(
    *,
    target: str,
    codex_home: Path,
    output_dir: Path,
    exit_code: int,
    jsonl_path: Path,
    last_message_path: Path,
    classification: dict[str, Any],
    model: str | None,
    model_catalog_json: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.oss-security-codex-exec-lane.v0",
        "status": "pass" if exit_code == 0 and classification["status"] == "pass" else "blocked",
        "target": target,
        "codex_profile": "oss-security",
        "sandbox": "workspace-write",
        "codex_home": codex_home.as_posix(),
        "output_dir": output_dir.as_posix(),
        "jsonl_path": jsonl_path.as_posix(),
        "last_message_path": last_message_path.as_posix(),
        "codex_exit_code": exit_code,
        "model_override": model,
        "model_catalog_json_override": model_catalog_json,
        "classification": classification,
        "command": (
            "codex exec --profile oss-security -c skills.config=[] --sandbox workspace-write "
            "--ephemeral --json --output-last-message <last-message>"
        ),
        "agent_summary": (
            "oss-security codex exec produced a security lane receipt."
            if classification["status"] == "pass"
            else f"oss-security codex exec is blocked: {classification['diagnostic']}"
        ),
    }


def _model_policy_receipt(
    *,
    target: str,
    codex_home: Path,
    output_dir: Path,
    model: str | None,
    model_catalog_json: str | None,
    blocker: str,
) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.oss-security-codex-exec-lane.v0",
        "status": "blocked",
        "process_status": "blocked",
        "security_decision": "blocked",
        "security_decision_source": "security_model_policy_violation",
        "target": target,
        "codex_profile": "oss-security",
        "security_model": SECURITY_MODEL,
        "model_override": model,
        "model_catalog_json_override": model_catalog_json,
        "codex_home": codex_home.as_posix(),
        "output_dir": output_dir.as_posix(),
        "blockers": [blocker],
        "agent_summary": f"oss-security receipt-first lane is blocked: {blocker}",
    }


def _lane(deterministic_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if deterministic_payload is None:
        return None
    lane = deterministic_payload.get("data", {}).get("skills_sdk_security_lane")
    return lane if isinstance(lane, dict) else None


def _deterministic_pass(exit_code: int, payload: dict[str, Any] | None) -> bool:
    lane = _lane(payload)
    return (
        exit_code == 0
        and payload is not None
        and payload.get("status") == "success"
        and lane is not None
        and lane.get("status") == "pass"
    )


def _review_pass(exit_code: int | None, validation: dict[str, Any] | None) -> bool:
    return exit_code == 0 and validation is not None and validation.get("status") == "pass"


def _model_review_status(review_validation: dict[str, Any] | None) -> str | None:
    if not review_validation or review_validation.get("status") != "pass":
        return None
    review = review_validation.get("review")
    if not isinstance(review, dict):
        return None
    value = str(review.get("review_status", "")).strip().lower()
    return value.split(":", 1)[0] if value else None


def _security_decision(model_review_status: str | None, process_status: str) -> tuple[str, str]:
    if process_status != "pass":
        return "blocked", "process_blocked_requires_valid_deterministic_and_review_receipts"
    if model_review_status == "pass":
        return "accepted_with_receipt", "model_review_pass"
    if model_review_status == "warn":
        return "needs_triage", "model_review_warn_requires_triage"
    if model_review_status == "fail":
        return "blocked", "model_review_fail_requires_triage"
    if model_review_status == "blocked":
        return "blocked", "model_review_blocked_requires_evidence"
    return "blocked", "model_review_status_missing_or_unknown"


def _receipt_first_blockers(deterministic_pass: bool, review_pass: bool) -> list[str]:
    blockers: list[str] = []
    if not deterministic_pass:
        blockers.append("deterministic security lane did not produce a passing receipt")
    if not review_pass:
        blockers.append("oss-security profile did not produce a valid digest-matching review receipt")
    return blockers


def _receipt_status(deterministic_pass: bool, review_pass: bool) -> str:
    return "pass" if deterministic_pass and review_pass else "blocked"


def _receipt_first_status(
    deterministic_exit_code: int,
    deterministic_payload: dict[str, Any] | None,
    review_exit_code: int | None,
    review_validation: dict[str, Any] | None,
) -> tuple[str, str, str, str | None, str, str, list[str]]:
    deterministic_pass = _deterministic_pass(deterministic_exit_code, deterministic_payload)
    review_pass = _review_pass(review_exit_code, review_validation)
    process_status = _receipt_status(deterministic_pass, review_pass)
    review_extraction_status = "pass" if review_pass else "blocked"
    model_review_status = _model_review_status(review_validation)
    security_decision, security_decision_source = _security_decision(model_review_status, process_status)
    status = "pass" if security_decision == "accepted_with_receipt" else "blocked"
    blockers = _receipt_first_blockers(deterministic_pass, review_pass)
    if process_status == "pass" and security_decision == "needs_triage":
        blockers.append("oss-security model review produced warnings that require triage")
    elif process_status == "pass" and security_decision == "blocked":
        blockers.append("oss-security model review blocks security readiness until triaged")
    return (
        status,
        process_status,
        review_extraction_status,
        model_review_status,
        security_decision,
        security_decision_source,
        blockers,
    )


def _reviewed_summary(status: str, blockers: list[str]) -> str:
    if status == "pass":
        return "oss-security codex exec accepted a deterministic security lane receipt."
    return f"oss-security receipt-first lane is blocked: {'; '.join(blockers)}"


def _optional_path(path: Path | None) -> str | None:
    return path.as_posix() if path else None


def _receipt_first_core(
    *,
    target: str,
    codex_home: Path,
    output_dir: Path,
    status: str,
) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.oss-security-codex-exec-lane.v0",
        "mode": "receipt_first",
        "status": status,
        "target": target,
        "codex_profile": "oss-security",
        "sandbox": "read-only",
        "codex_home": codex_home.as_posix(),
        "output_dir": output_dir.as_posix(),
    }


def _receipt_first_review_paths(
    *,
    review_input_path: Path | None,
    jsonl_path: Path | None,
    last_message_path: Path | None,
) -> dict[str, str | None]:
    return {
        "review_input_path": _optional_path(review_input_path),
        "jsonl_path": _optional_path(jsonl_path),
        "last_message_path": _optional_path(last_message_path),
    }


def _receipt_first_details(
    state: dict[str, Any],
    *,
    lane: dict[str, Any] | None,
    blockers: list[str],
    status: str,
    process_status: str,
    review_extraction_status: str,
    model_review_status: str | None,
    security_decision: str,
    security_decision_source: str,
) -> dict[str, Any]:
    compact = (
        state["review_input_bytes"] is not None
        and state["review_input_bytes"] <= REVIEW_INPUT_COMPACT_LIMIT_BYTES
    )
    details = {
        "process_status": process_status,
        "deterministic_exit_code": state["deterministic_exit_code"],
        "deterministic_output_path": state["deterministic_output_path"].as_posix(),
        "deterministic_lane_status": lane.get("status") if lane else None,
        "review_extraction_status": review_extraction_status,
        "model_review_status": model_review_status,
        "security_decision": security_decision,
        "security_decision_source": security_decision_source,
        "security_model": SECURITY_MODEL,
        "review_prompt_contract_version": REVIEW_PROMPT_CONTRACT_VERSION,
        "review_input_bytes": state["review_input_bytes"],
        "review_input_compact_limit_bytes": REVIEW_INPUT_COMPACT_LIMIT_BYTES,
        "review_input_compact": compact,
        "security_lane_digest": lane.get("security_lane_digest") if lane else None,
        "codex_exit_code": state["review_exit_code"],
        "model_override": state["model"],
        "model_catalog_json_override": state["model_catalog_json"],
        "review_validation": state["review_validation"],
        "blockers": blockers,
        "agent_summary": _reviewed_summary(status, blockers),
    }
    details["command"] = _receipt_first_command_summary()
    return details


def _receipt_first_command_summary() -> str:
    return (
        "codex exec --profile oss-security -c skills.config=[] --sandbox read-only "
        "--ephemeral --json --output-last-message <last-message> < <receipt-review-prompt>"
    )


def _receipt_status_bundle(state: dict[str, Any]) -> tuple[dict[str, Any] | None, tuple[Any, ...]]:
    lane = _lane(state["deterministic_payload"])
    bundle = _receipt_first_status(
        state["deterministic_exit_code"],
        state["deterministic_payload"],
        state["review_exit_code"],
        state["review_validation"],
    )
    return lane, bundle


def _receipt_first_receipt(state: dict[str, Any]) -> dict[str, Any]:
    lane, status_bundle = _receipt_status_bundle(state)
    (
        status,
        process_status,
        review_extraction_status,
        model_review_status,
        security_decision,
        security_decision_source,
        blockers,
    ) = status_bundle
    receipt = _receipt_first_core(
        target=state["target"],
        codex_home=state["codex_home"],
        output_dir=state["output_dir"],
        status=status,
    )
    receipt.update(
        _receipt_first_details(
            state,
            lane=lane,
            blockers=blockers,
            status=status,
            process_status=process_status,
            review_extraction_status=review_extraction_status,
            model_review_status=model_review_status,
            security_decision=security_decision,
            security_decision_source=security_decision_source,
        )
    )
    receipt.update(
        _receipt_first_review_paths(
            review_input_path=state["review_input_path"],
            jsonl_path=state["jsonl_path"],
            last_message_path=state["last_message_path"],
        )
    )
    return receipt


def _receipt_first_state(
    *,
    target: str,
    codex_home: Path,
    output_dir: Path,
    model: str | None,
    model_catalog_json: str | None,
) -> dict[str, Any]:
    exit_code, payload, output = _run_deterministic_lane(target)
    output_path = _write_deterministic_output(output_dir, output)
    review_paths: tuple[Path | None, Path | None, Path | None] = (None, None, None)
    review_exit_code: int | None = None
    review_validation: dict[str, Any] | None = None
    review_input_bytes: int | None = None
    lane = _lane(payload)
    if exit_code == 0 and lane is not None and lane.get("status") == "pass":
        review_input = _receipt_review_input(payload)
        review_paths, review_exit_code, review_validation, review_input_bytes = _review_receipt(
            codex_home=codex_home,
            output_dir=output_dir,
            review_input=review_input,
            model=model,
            model_catalog_json=model_catalog_json,
        )
    return _receipt_first_state_payload(
        target=target,
        codex_home=codex_home,
        output_dir=output_dir,
        model=model,
        model_catalog_json=model_catalog_json,
        deterministic=(exit_code, payload, output_path),
        review=(review_paths, review_exit_code, review_validation, review_input_bytes),
    )


def _receipt_first_state_payload(
    *,
    target: str,
    codex_home: Path,
    output_dir: Path,
    model: str | None,
    model_catalog_json: str | None,
    deterministic: tuple[int, dict[str, Any] | None, Path],
    review: tuple[tuple[Path | None, Path | None, Path | None], int | None, dict[str, Any] | None, int | None],
) -> dict[str, Any]:
    exit_code, payload, output_path = deterministic
    review_paths, review_exit_code, review_validation, review_input_bytes = review
    return {
        "target": target,
        "codex_home": codex_home,
        "output_dir": output_dir,
        "deterministic_exit_code": exit_code,
        "deterministic_output_path": output_path,
        "deterministic_payload": payload,
        "review_input_path": review_paths[0],
        "review_exit_code": review_exit_code,
        "jsonl_path": review_paths[1],
        "last_message_path": review_paths[2],
        "review_validation": review_validation,
        "review_input_bytes": review_input_bytes,
        "model": model,
        "model_catalog_json": model_catalog_json,
    }


def _write_deterministic_output(output_dir: Path, output: str) -> Path:
    deterministic_output_path = output_dir / "deterministic-security-lane.json"
    deterministic_output_path.write_text(output, encoding="utf-8")
    return deterministic_output_path


def _run_receipt_first_mode(
    *,
    target: str,
    codex_home: Path,
    output_dir: Path,
    model: str | None,
    model_catalog_json: str | None,
) -> dict[str, Any]:
    state = _receipt_first_state(
        target=target,
        codex_home=codex_home,
        output_dir=output_dir,
        model=model,
        model_catalog_json=model_catalog_json,
    )
    return _receipt_first_receipt(state)


def _review_receipt(
    *,
    codex_home: Path,
    output_dir: Path,
    review_input: dict[str, Any],
    model: str | None,
    model_catalog_json: str | None,
) -> tuple[tuple[Path, Path, Path], int, dict[str, Any], int]:
    review_input_path = output_dir / "oss-security-review-input.json"
    review_input_body = json.dumps(review_input, indent=2, sort_keys=True)
    review_input_path.write_text(review_input_body, encoding="utf-8")
    exit_code, jsonl_path, last_message_path = _run_receipt_review(
        codex_home=codex_home,
        review_input=review_input,
        output_dir=output_dir,
        model=model,
        model_catalog_json=model_catalog_json,
    )
    validation = validate_review(last_message_path, expected_digest=review_input["security_lane_digest"])
    return (review_input_path, jsonl_path, last_message_path), exit_code, validation, len(review_input_body.encode("utf-8"))


def _emit(receipt: dict[str, Any], *, as_json: bool) -> int:
    if as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(receipt["agent_summary"])
    if receipt["status"] == "pass":
        return 0
    if "process_status" not in receipt:
        return 2
    if receipt.get("process_status") == "pass":
        return 2
    return 3


def _blocked_model_policy_receipt(
    args: argparse.Namespace,
    *,
    codex_home: Path,
    output_dir: Path,
    blocker: str,
) -> dict[str, Any]:
    return _model_policy_receipt(
        target=args.target,
        codex_home=codex_home,
        output_dir=output_dir,
        model=args.model,
        model_catalog_json=args.model_catalog_json,
        blocker=blocker,
    )


def _run_tool_mode(args: argparse.Namespace, *, codex_home: Path, output_dir: Path) -> dict[str, Any]:
    exit_code, jsonl_path, last_message_path = _run_codex(
        codex_home=codex_home,
        target=args.target,
        output_dir=output_dir,
        model=args.model,
        model_catalog_json=args.model_catalog_json,
    )
    classification = classify(jsonl_path)
    return _receipt(
        target=args.target,
        codex_home=codex_home,
        output_dir=output_dir,
        exit_code=exit_code,
        jsonl_path=jsonl_path,
        last_message_path=last_message_path,
        classification=classification,
        model=args.model,
        model_catalog_json=args.model_catalog_json,
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and classify the oss-security Codex exec SDK security lane.")
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--model-catalog-json")
    parser.add_argument(
        "--mode",
        choices=("tool", "receipt-first"),
        default="tool",
        help="tool asks the model to call exec; receipt-first runs the deterministic lane first and asks the profile to review the receipt.",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="oss-security-codex-exec-"))
    codex_home = args.codex_home or output_dir / "codex-home"
    model_blocker = _model_blocker(args.model)
    if model_blocker:
        receipt = _blocked_model_policy_receipt(
            args,
            codex_home=codex_home,
            output_dir=output_dir,
            blocker=model_blocker,
        )
        return _emit(receipt, as_json=args.json)
    _copy_codex_home(codex_home)
    if args.mode == "receipt-first":
        receipt = _run_receipt_first_mode(
            target=args.target,
            codex_home=codex_home,
            output_dir=output_dir,
            model=args.model,
            model_catalog_json=args.model_catalog_json,
        )
        return _emit(receipt, as_json=args.json)
    receipt = _run_tool_mode(args, codex_home=codex_home, output_dir=output_dir)
    return _emit(receipt, as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
