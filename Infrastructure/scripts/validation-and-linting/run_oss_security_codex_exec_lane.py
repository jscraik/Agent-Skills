#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from classify_codex_exec_security_lane import classify
from extract_oss_security_review import validate_review


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TARGET = "Skills/agent-ops/improve-agent-native"
SECURITY_MODEL = "h4rithd/coder:14b"
DETERMINISTIC_LANE_TIMEOUT_SECONDS = 600
CODEX_EXEC_TIMEOUT_SECONDS = 1800


def _configs_root() -> Path:
    configured = os.environ.get("ASK_OSS_SECURITY_CONFIGS_ROOT")
    if configured:
        candidate = Path(configured).expanduser().resolve()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(
            "ASK_OSS_SECURITY_CONFIGS_ROOT points to a missing Codex config directory: "
            f"{candidate}"
        )
    sibling = REPO_ROOT.parent / "configs" / "codex"
    if sibling.exists():
        return sibling
    raise FileNotFoundError(
        "oss-security Codex config directory not found. Set ASK_OSS_SECURITY_CONFIGS_ROOT "
        f"or place configs at the sibling checkout path: {sibling}"
    )


def _copy_codex_home(codex_home: Path) -> None:
    codex_home.mkdir(parents=True, exist_ok=True)
    configs_root = _configs_root()
    for name in ("config.toml", "oss-security.config.toml"):
        source = configs_root / name
        if not source.exists():
            raise FileNotFoundError(
                f"required oss-security Codex config file is missing: {source}. "
                "Set ASK_OSS_SECURITY_CONFIGS_ROOT to a directory containing config.toml "
                "and oss-security.config.toml."
            )
        shutil.copy2(source, codex_home / name)


def _prompt(target: str) -> str:
    command = f"./bin/ask sdk security run-lane {shlex.quote(target)} --preview --profile oss-security --json --robot"
    js_source = (
        '// @exec: {"yield_time_ms": 30000, "max_output_tokens": 4000}\n'
        "const r = await tools.exec_command({\n"
        f"  cmd: {json.dumps(command)},\n"
        f"  workdir: {json.dumps(REPO_ROOT.as_posix())},\n"
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
    receipt = lane.get("receipt", {})
    return {
        "schema_version": "skills-sdk.oss-security-review-input.v0",
        "package": lane.get("package_id"),
        "lane_status": lane.get("status"),
        "security_lane_digest": lane.get("security_lane_digest"),
        "package_digest": lane.get("package_digest"),
        "package_security_signature_digest": lane.get("package_security_signature_digest"),
        "risk_mode_taxonomy_digest": lane.get("risk_mode_taxonomy_digest"),
        "indicator_summary": receipt.get("indicator_summary", {}),
        "primary_mode": receipt.get("primary_mode"),
        "detected_modes": receipt.get("detected_modes", []),
        "commands": receipt.get("commands", []),
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
        "a non-empty sentence. The reviewer_model_boundary value must explain that you "
        "reviewed only the supplied receipt and did not run tools or commands.\n\n"
        "Receipt summary JSON:\n"
        f"{json.dumps(review_input, sort_keys=True)}\n"
    )


def _run_deterministic_lane(target: str) -> tuple[int, dict[str, Any] | None, str]:
    try:
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
            timeout=DETERMINISTIC_LANE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, None, _timeout_output(exc)
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
    try:
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
            timeout=CODEX_EXEC_TIMEOUT_SECONDS,
        )
        output = process.stdout
        returncode = process.returncode
    except subprocess.TimeoutExpired as exc:
        output = _timeout_output(exc)
        returncode = 124
    jsonl_path.write_text(output, encoding="utf-8")
    return returncode, jsonl_path, last_message_path


def _codex_command(
    *,
    sandbox: str,
    last_message_path: Path,
    model: str | None,
    model_catalog_json: str | None,
) -> list[str]:
    model = _validate_model_override(model)
    model_catalog_json = _validate_model_catalog_json(model_catalog_json)
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
        command.extend(["-c", f"model={json.dumps(model)}"])
    if model_catalog_json:
        command.extend(["-c", f"model_catalog_json={json.dumps(model_catalog_json)}"])
    return command


def _validate_model_override(model: str | None) -> str | None:
    if model is None:
        return None
    if model != SECURITY_MODEL:
        raise ValueError(f"oss-security model override must be {SECURITY_MODEL!r}")
    return model


def _validate_model_catalog_json(model_catalog_json: str | None) -> str | None:
    if model_catalog_json is None:
        return None
    try:
        payload = json.loads(model_catalog_json)
    except json.JSONDecodeError as exc:
        raise ValueError("model_catalog_json must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("model_catalog_json must decode to a JSON object")
    model = payload.get("model")
    if model is not None and model != SECURITY_MODEL:
        raise ValueError(f"model_catalog_json.model must be {SECURITY_MODEL!r}")
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def _timeout_output(exc: subprocess.TimeoutExpired) -> str:
    output = exc.output if exc.output is not None else exc.stdout
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    output = output or ""
    return f"{output}\noss-security subprocess timed out after {exc.timeout} seconds.\n"


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
    try:
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
            timeout=CODEX_EXEC_TIMEOUT_SECONDS,
        )
        output = process.stdout
        returncode = process.returncode
    except subprocess.TimeoutExpired as exc:
        output = _timeout_output(exc)
        returncode = 124
    jsonl_path.write_text(output, encoding="utf-8")
    return returncode, jsonl_path, last_message_path


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
) -> tuple[str, list[str]]:
    deterministic_pass = _deterministic_pass(deterministic_exit_code, deterministic_payload)
    review_pass = _review_pass(review_exit_code, review_validation)
    blockers = _receipt_first_blockers(deterministic_pass, review_pass)
    return _receipt_status(deterministic_pass, review_pass), blockers


def _reviewed_summary(status: str, blockers: list[str]) -> str:
    if status == "pass":
        return "oss-security codex exec reviewed a deterministic security lane receipt."
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
) -> dict[str, Any]:
    return {
        "deterministic_exit_code": state["deterministic_exit_code"],
        "deterministic_output_path": state["deterministic_output_path"].as_posix(),
        "deterministic_lane_status": lane.get("status") if lane else None,
        "security_lane_digest": lane.get("security_lane_digest") if lane else None,
        "codex_exit_code": state["review_exit_code"],
        "model_override": state["model"],
        "model_catalog_json_override": state["model_catalog_json"],
        "review_validation": state["review_validation"],
        "blockers": blockers,
        "command": (
            "codex exec --profile oss-security -c skills.config=[] --sandbox read-only "
            "--ephemeral --json --output-last-message <last-message> < <receipt-review-prompt>"
        ),
        "agent_summary": _reviewed_summary(status, blockers),
    }


def _receipt_first_receipt(state: dict[str, Any]) -> dict[str, Any]:
    deterministic_exit_code = state["deterministic_exit_code"]
    deterministic_payload = state["deterministic_payload"]
    review_exit_code = state["review_exit_code"]
    review_validation = state["review_validation"]
    lane = _lane(deterministic_payload)
    status, blockers = _receipt_first_status(
        deterministic_exit_code,
        deterministic_payload,
        review_exit_code,
        review_validation,
    )
    receipt = _receipt_first_core(
        target=state["target"],
        codex_home=state["codex_home"],
        output_dir=state["output_dir"],
        status=status,
    )
    receipt.update(_receipt_first_details(state, lane=lane, blockers=blockers, status=status))
    receipt.update(
        _receipt_first_review_paths(
            review_input_path=state["review_input_path"],
            jsonl_path=state["jsonl_path"],
            last_message_path=state["last_message_path"],
        )
    )
    return receipt


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
    exit_code, payload, output = _run_deterministic_lane(target)
    output_path = _write_deterministic_output(output_dir, output)
    review_paths: tuple[Path | None, Path | None, Path | None] = (None, None, None)
    review_exit_code: int | None = None
    review_validation: dict[str, Any] | None = None
    lane = _lane(payload)
    if exit_code == 0 and lane is not None and lane.get("status") == "pass":
        review_input = _receipt_review_input(payload)
        review_paths, review_exit_code, review_validation = _review_receipt(
            codex_home=codex_home,
            output_dir=output_dir,
            review_input=review_input,
            model=model,
            model_catalog_json=model_catalog_json,
        )
    return _receipt_first_receipt(
        {
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
            "model": model,
            "model_catalog_json": model_catalog_json,
        }
    )


def _review_receipt(
    *,
    codex_home: Path,
    output_dir: Path,
    review_input: dict[str, Any],
    model: str | None,
    model_catalog_json: str | None,
) -> tuple[tuple[Path, Path, Path], int, dict[str, Any]]:
    review_input_path = output_dir / "oss-security-review-input.json"
    review_input_path.write_text(json.dumps(review_input, indent=2, sort_keys=True), encoding="utf-8")
    exit_code, jsonl_path, last_message_path = _run_receipt_review(
        codex_home=codex_home,
        review_input=review_input,
        output_dir=output_dir,
        model=model,
        model_catalog_json=model_catalog_json,
    )
    if last_message_path.exists():
        validation = validate_review(last_message_path, expected_digest=review_input["security_lane_digest"])
    else:
        validation = {
            "status": "blocked",
            "diagnostic": "oss-security review did not write an output-last-message file",
            "review_status": None,
            "evidence_digest_seen": None,
            "review_path": last_message_path.as_posix(),
        }
    return (review_input_path, jsonl_path, last_message_path), exit_code, validation


def _emit(receipt: dict[str, Any], *, as_json: bool) -> int:
    if as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(receipt["agent_summary"])
    return 0 if receipt["status"] == "pass" else 2


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
    auto_output_root = args.output_dir is None
    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="oss-security-codex-exec-"))
    try:
        codex_home = args.codex_home or output_dir / "codex-home"
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
        exit_code, jsonl_path, last_message_path = _run_codex(
            codex_home=codex_home,
            target=args.target,
            output_dir=output_dir,
            model=args.model,
            model_catalog_json=args.model_catalog_json,
        )
        classification = classify(jsonl_path)
        receipt = _receipt(
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
        return _emit(receipt, as_json=args.json)
    finally:
        if auto_output_root:
            shutil.rmtree(output_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
