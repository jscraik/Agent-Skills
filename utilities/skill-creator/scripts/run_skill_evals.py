#!/usr/bin/env python3
"""
run_skill_evals.py

Run evaluation cases for a Codex skill using Codex CLI non-interactive mode.

- Loads SKILL.md -> skill name
- Loads references/evals.yaml
- For each case, runs: codex exec (optionally with --output-schema)
- Captures final output via --output-last-message (-o)
- Applies acceptance assertions and exits non-zero on failures

Usage:
  python scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  all evals passed
  1  parsing/IO error
  2  one or more evals failed
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import yaml


_FM_DELIM = re.compile(r"^\s*---\s*$")


def _resolve_skill_md_path(path_like: str) -> Path:
    p = Path(path_like).expanduser().resolve()
    return (p / "SKILL.md") if p.is_dir() else p


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _parse_frontmatter(raw: str) -> Tuple[Dict[str, Any], str]:
    lines = raw.splitlines(keepends=True)
    if not lines:
        raise ValueError("SKILL.md is empty")

    start_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip():
            start_idx = i
            break
    if start_idx is None or not _FM_DELIM.match(lines[start_idx]):
        raise ValueError("Missing YAML frontmatter. Expected `---` as first non-empty line.")

    end_idx: Optional[int] = None
    for j in range(start_idx + 1, len(lines)):
        if _FM_DELIM.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        raise ValueError("Unterminated YAML frontmatter. Missing closing `---`.")

    yaml_text = "".join(lines[start_idx + 1 : end_idx])
    fm_obj = yaml.safe_load(yaml_text)
    if fm_obj is None:
        fm: Dict[str, Any] = {}
    elif isinstance(fm_obj, dict):
        fm = fm_obj
    else:
        raise ValueError("Frontmatter YAML must be a mapping/object.")

    body = "".join(lines[end_idx + 1 :]).lstrip("\n")
    return fm, body


def load_skill_name(skill_md_path: Path) -> str:
    raw = _read_text(skill_md_path)
    fm, _ = _parse_frontmatter(raw)
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("SKILL.md frontmatter missing valid `name`.")
    return name.strip()


Assertion = Union[str, Dict[str, Any]]


@dataclass(frozen=True)
class EvalCase:
    name: str
    prompt: str
    acceptance: List[Assertion]
    output_schema: Optional[str] = None


def load_evals(evals_path: Path) -> List[EvalCase]:
    obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or "cases" not in obj or not isinstance(obj["cases"], list):
        raise ValueError("evals.yaml must be a mapping with `cases: [...]`.")

    cases: List[EvalCase] = []
    for i, c in enumerate(obj["cases"], 1):
        if not isinstance(c, dict):
            raise ValueError(f"Case #{i} must be a mapping.")
        for k in ("name", "prompt", "acceptance"):
            if k not in c:
                raise ValueError(f"Case #{i} missing `{k}`.")
        if not isinstance(c["acceptance"], list):
            raise ValueError(f"Case #{i} `acceptance` must be a list.")

        cases.append(
            EvalCase(
                name=str(c["name"]),
                prompt=str(c["prompt"]),
                acceptance=list(c["acceptance"]),
                output_schema=str(c["output_schema"]) if "output_schema" in c and c["output_schema"] else None,
            )
        )
    return cases


def _json_get_path(obj: Any, path: str) -> Any:
    cur = obj
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\[\d+\]", path)
    for t in tokens:
        if t.startswith("["):
            idx = int(t[1:-1])
            if not isinstance(cur, list) or idx >= len(cur):
                raise KeyError(path)
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or t not in cur:
                raise KeyError(path)
            cur = cur[t]
    return cur


def _normalize_assert(a: Assertion) -> Dict[str, Any]:
    if isinstance(a, str):
        s = a.strip()
        for prefix, t in [
            ("regex:", "regex"),
            ("not_regex:", "not_regex"),
            ("not_contains:", "not_contains"),
            ("contains:", "contains"),
        ]:
            if s.lower().startswith(prefix):
                return {"type": t, "value": s[len(prefix) :].strip()}
        return {"type": "contains", "value": s}

    if isinstance(a, dict):
        if "type" not in a:
            raise ValueError("Assertion dict must include `type`.")
        return dict(a)

    raise ValueError("Assertion must be a string or mapping.")


def evaluate_assertions_text(text: str, assertions: List[Assertion]) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        a = _normalize_assert(raw)
        t = a["type"]
        v = a.get("value", "")

        if t == "contains":
            if v not in text:
                failures.append(f"contains failed: {v!r}")
        elif t == "not_contains":
            if v in text:
                failures.append(f"not_contains failed: {v!r}")
        elif t == "regex":
            if not re.search(v, text, flags=re.MULTILINE):
                failures.append(f"regex failed: /{v}/")
        elif t == "not_regex":
            if re.search(v, text, flags=re.MULTILINE):
                failures.append(f"not_regex failed: /{v}/")
        else:
            failures.append(f"unsupported assertion type for text output: {t!r}")
    return failures


def evaluate_assertions_json(obj: Any, assertions: List[Assertion]) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        a = _normalize_assert(raw)
        t = a["type"]

        if t in ("contains", "not_contains", "regex", "not_regex"):
            text = json.dumps(obj, ensure_ascii=False, indent=2)
            failures.extend(evaluate_assertions_text(text, [a]))
            continue

        if t == "jsonpath_equals":
            path = a.get("path")
            expected = a.get("value")
            if not isinstance(path, str) or path.strip() == "":
                failures.append("jsonpath_equals missing `path`")
                continue
            try:
                got = _json_get_path(obj, path)
            except KeyError:
                failures.append(f"jsonpath_equals missing path: {path}")
                continue
            if got != expected:
                failures.append(f"jsonpath_equals failed at {path}: got={got!r} expected={expected!r}")
        elif t == "jsonpath_exists":
            path = a.get("path")
            if not isinstance(path, str) or path.strip() == "":
                failures.append("jsonpath_exists missing `path`")
                continue
            try:
                _json_get_path(obj, path)
            except KeyError:
                failures.append(f"jsonpath_exists failed (missing): {path}")
        else:
            failures.append(f"unsupported assertion type for json output: {t!r}")
    return failures


def run_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    output_schema_path: Optional[Path],
    sandbox: str,
    ask_for_approval: str,
    model: Optional[str],
    profile: Optional[str],
    codex_home: Optional[Path],
    jsonl_path: Optional[Path],
    extra_codex_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    if extra_codex_args:
        cmd.extend(extra_codex_args)

    if profile:
        cmd.extend(["--profile", profile])
    if model:
        cmd.extend(["--model", model])
    if output_schema_path:
        cmd.extend(["--output-schema", str(output_schema_path)])

    if jsonl_path:
        cmd.append("--json")

    cmd.append("-")

    env = os.environ.copy()
    if codex_home:
        env["CODEX_HOME"] = str(codex_home)

    # Add a timeout to prevent hangs; default 60s, override with CODEX_EVAL_TIMEOUT_SEC
    timeout = float(os.environ.get("CODEX_EVAL_TIMEOUT_SEC", "60"))

    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
    except subprocess.TimeoutExpired:
        return 124, "", f"codex exec timed out after {timeout} seconds."

    if jsonl_path:
        jsonl_path.write_text(proc.stdout, encoding="utf-8")

    return proc.returncode, proc.stdout, proc.stderr


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="run_skill_evals.py", description="Run skill evals using Codex CLI (codex exec).")
    p.add_argument("path", help="Path to a skill directory or SKILL.md.")
    p.add_argument("--workspace", default=None, help="Workspace root to run codex exec in (defaults to repo root guess).")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument(
        "--ask-for-approval",
        default="never",
        choices=["untrusted", "on-failure", "on-request", "never"],
        help="Codex approval mode (use \"never\" for CI).",
    )
    p.add_argument("--model", default=None, help="Override model for codex exec.")
    p.add_argument("--profile", default=None, help="Codex config profile name.")
    p.add_argument("--codex-home", default=None, help="Set CODEX_HOME (useful for repo-scoped .codex).")
    p.add_argument("--capture-jsonl", action="store_true", help="Also capture Codex JSONL event stream (--json).")
    p.add_argument("--reports-dir", default="reports/skills", help="Base directory for eval reports.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra flag to pass to codex exec (repeatable), e.g. --codex-arg='--profile' --codex-arg=work",
    )
    return p


def _guess_repo_root(start: Path) -> Path:
    cur = start
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    skill_md = _resolve_skill_md_path(args.path)
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found at: {skill_md}", file=sys.stderr)
        return 1

    skill_dir = skill_md.parent
    skill_name = load_skill_name(skill_md)

    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        print(f"ERROR: Missing evals file: {evals_path}", file=sys.stderr)
        return 1

    cases = load_evals(evals_path)

    workspace_root = Path(args.workspace).expanduser().resolve() if args.workspace else _guess_repo_root(skill_dir)
    codex_home = Path(args.codex_home).expanduser().resolve() if args.codex_home else None

    run_id = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    reports_base = Path(args.reports_dir).expanduser().resolve() / skill_name / run_id
    reports_base.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, Any] = {
        "skill": skill_name,
        "skill_path": str(skill_dir),
        "workspace_root": str(workspace_root),
        "run_id": run_id,
        "cases": [],
        "passed": True,
    }

    any_failed = False

    for idx, c in enumerate(cases, 1):
        case_dir = reports_base / f"{idx:02d}-{re.sub(r'[^A-Za-z0-9_.-]+', '-', c.name).strip('-')}"
        case_dir.mkdir(parents=True, exist_ok=True)

        output_path = case_dir / "output_last_message.txt"
        jsonl_path = (case_dir / "codex_events.jsonl") if args.capture_jsonl else None

        schema_path: Optional[Path] = None
        if c.output_schema:
            schema_path = Path(c.output_schema)
            if not schema_path.is_absolute():
                schema_path = (skill_dir / schema_path).resolve()
            if not schema_path.exists():
                print(f"ERROR: Case {c.name}: output_schema not found: {schema_path}", file=sys.stderr)
                return 1

        composed_prompt = f"$" + skill_name + "\n\n" + c.prompt.strip() + "\n"

        (case_dir / "prompt.txt").write_text(composed_prompt, encoding="utf-8")

        rc, stdout, stderr = run_codex_exec(
            workspace_root=workspace_root,
            prompt=composed_prompt,
            output_last_message_path=output_path,
            output_schema_path=schema_path,
            sandbox=args.sandbox,
            ask_for_approval=args.ask_for_approval,
            model=args.model,
            profile=args.profile,
            codex_home=codex_home,
            jsonl_path=jsonl_path,
            extra_codex_args=args.codex_arg or None,
        )

        (case_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")
        (case_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")

        output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        (case_dir / "final.txt").write_text(output_text, encoding="utf-8")

        failures: List[str] = []
        if rc != 0:
            failures.append(f"codex exec returned non-zero exit code: {rc}")

        if schema_path:
            try:
                parsed = json.loads(output_text)
            except Exception as e:
                failures.append(f"expected JSON output (schema used), but parsing failed: {e}")
                parsed = None
            if parsed is not None:
                failures.extend(evaluate_assertions_json(parsed, c.acceptance))
        else:
            failures.extend(evaluate_assertions_text(output_text, c.acceptance))

        passed = len(failures) == 0
        any_failed = any_failed or (not passed)

        case_record = {
            "name": c.name,
            "passed": passed,
            "failures": failures,
            "dir": str(case_dir),
            "used_schema": bool(schema_path),
        }
        summary["cases"].append(case_record)

        (case_dir / "result.json").write_text(json.dumps(case_record, indent=2, ensure_ascii=False), encoding="utf-8")

    summary["passed"] = not any_failed
    (reports_base / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Skill evals: {skill_name}")
        print(f"Reports: {reports_base}")
        for c in summary["cases"]:
            status = "PASS" if c["passed"] else "FAIL"
            print(f"- {status}: {c['name']}")
            for f in c["failures"]:
                print(f"    - {f}")
        print(f"RESULT: {'PASS' if summary['passed'] else 'FAIL'}")

    return 0 if summary["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
