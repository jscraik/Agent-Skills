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


REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGS_ROOT = REPO_ROOT.parent / "configs" / "codex"
DEFAULT_TARGET = "Skills/agent-ops/improve-agent-native"


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
    command = [
        "codex",
        "exec",
        "--profile",
        "oss-security",
        "-c",
        "skills.config=[]",
        "--sandbox",
        "workspace-write",
        "--ephemeral",
        "--json",
        "--output-last-message",
        str(last_message_path),
    ]
    if model:
        command.extend(["-c", f'model="{model}"'])
    if model_catalog_json:
        command.extend(["-c", f'model_catalog_json="{model_catalog_json}"'])
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    process = subprocess.run(
        command,
        input=_prompt(target),
        cwd=REPO_ROOT,
        env=env,
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run and classify the oss-security Codex exec SDK security lane.")
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--model-catalog-json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="oss-security-codex-exec-"))
    codex_home = args.codex_home or output_dir / "codex-home"
    _copy_codex_home(codex_home)
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
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(receipt["agent_summary"])
    return 0 if receipt["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
