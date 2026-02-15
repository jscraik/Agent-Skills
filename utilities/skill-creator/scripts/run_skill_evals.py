#!/usr/bin/env python3
"""
run_skill_evals.py

Run evaluation cases for a Codex skill using Codex CLI and/or Claude Code CLI.

Capabilities:
- Loads SKILL.md -> skill name
- Loads references/evals.yaml (v1 compatible; v2 fields optional)
- Per case, runs one runner (`--runner`) or both (`--dual-run`)
- Captures final output and optional Codex JSONL traces
- Applies acceptance assertions (text and JSON)
- Applies deterministic Codex trace checks (tier 1 hard / tier 2 budgets)
- Produces merged scorecards and exits non-zero on configured gate failures

Usage:
  ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  all required gates passed
  1  parsing/IO/configuration error
  2  one or more required eval gates failed
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

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_CREATOR_PYYAML_REEXEC") == "1"
    if preferred.exists() and not already_reexec:
        env = dict(os.environ)
        env["SKILL_CREATOR_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)

    print(
        "ERROR: PyYAML is required to run run_skill_evals.py.\n\n"
        "Fix:\n"
        "  ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>\n",
        file=sys.stderr,
    )
    raise SystemExit(1)

# Local deterministic checker (same directory as this script)
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from deterministic_trace_checks import evaluate_trace, load_jsonl_events  # noqa: E402

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
    id: str
    name: str
    prompt: str
    acceptance: List[Assertion]
    output_schema: Optional[str] = None
    should_trigger: Optional[bool] = None
    category: Optional[str] = None
    deterministic_checks: Optional[Dict[str, Any]] = None
    budgets: Optional[Dict[str, Any]] = None
    prepend_skill: bool = True


_VALID_CATEGORIES = {"happy", "edge", "negative", "pressure"}


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

        case_id_raw = c.get("id", f"case-{i:02d}")
        case_id = str(case_id_raw).strip() or f"case-{i:02d}"

        category = c.get("category")
        if category is not None:
            category = str(category).strip().lower()
            if category and category not in _VALID_CATEGORIES:
                raise ValueError(
                    f"Case #{i} category must be one of {sorted(_VALID_CATEGORIES)}; got {category!r}."
                )

        should_trigger = c.get("should_trigger")
        if should_trigger is not None and not isinstance(should_trigger, bool):
            raise ValueError(f"Case #{i} `should_trigger` must be boolean when provided.")

        deterministic_checks = c.get("deterministic_checks")
        if deterministic_checks is not None and not isinstance(deterministic_checks, dict):
            raise ValueError(f"Case #{i} `deterministic_checks` must be a mapping when provided.")

        budgets = c.get("budgets")
        if budgets is not None and not isinstance(budgets, dict):
            raise ValueError(f"Case #{i} `budgets` must be a mapping when provided.")

        prepend_skill = c.get("prepend_skill", True)
        if not isinstance(prepend_skill, bool):
            raise ValueError(f"Case #{i} `prepend_skill` must be boolean when provided.")

        cases.append(
            EvalCase(
                id=case_id,
                name=str(c["name"]),
                prompt=str(c["prompt"]),
                acceptance=list(c["acceptance"]),
                output_schema=str(c["output_schema"]) if c.get("output_schema") else None,
                should_trigger=should_trigger,
                category=category if category else None,
                deterministic_checks=deterministic_checks,
                budgets=budgets,
                prepend_skill=prepend_skill,
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
        if "type" in a:
            return dict(a)

        # Back-compat single-key shorthand, e.g. {contains: "x"}
        if len(a) == 1:
            key, value = next(iter(a.items()))
            t = str(key)
            if t in {"contains", "not_contains", "regex", "not_regex"}:
                return {"type": t, "value": value}
            if t == "jsonpath_exists":
                if isinstance(value, dict):
                    return {"type": t, "path": value.get("path")}
                return {"type": t, "path": value}
            if t == "jsonpath_equals":
                if isinstance(value, dict):
                    return {"type": t, "path": value.get("path"), "value": value.get("value")}
                raise ValueError("jsonpath_equals shorthand must be mapping with {path, value}.")
            if t in {"skill_selected", "skill_not_selected"}:
                if isinstance(value, dict):
                    payload = {"type": t}
                    payload.update(value)
                    return payload
                return {"type": t, "expected_skill": value}

    raise ValueError("Assertion must be a string, typed mapping, or supported shorthand mapping.")


def _to_text_blob(data: Any) -> str:
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False, indent=2)


def _evaluate_skill_selection_assertion(
    assertion: Dict[str, Any],
    *,
    skill_name: str,
    selected: Optional[bool],
) -> Optional[str]:
    t = assertion.get("type")
    expected_skill = assertion.get("expected_skill") or assertion.get("value") or skill_name
    expected_skill = str(expected_skill)

    if expected_skill and expected_skill != skill_name:
        # This eval runner validates the active skill; if another skill is expected, flag explicitly.
        return f"{t} expected_skill mismatch: expected {expected_skill!r}, active skill is {skill_name!r}"

    if selected is None:
        return f"{t} check unavailable: skill selection signal not found"

    if t == "skill_selected" and not selected:
        return f"skill_selected failed: expected {skill_name!r} to be selected"

    if t == "skill_not_selected" and selected:
        return f"skill_not_selected failed: expected {skill_name!r} to NOT be selected"

    return None


def evaluate_assertions_text(
    text: str,
    assertions: List[Assertion],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        a = _normalize_assert(raw)
        t = a["type"]
        v = a.get("value", "")

        if t == "contains":
            needle = _to_text_blob(v)
            if needle not in text:
                failures.append(f"contains failed: {needle!r}")
        elif t == "not_contains":
            needle = _to_text_blob(v)
            if needle in text:
                failures.append(f"not_contains failed: {needle!r}")
        elif t == "regex":
            pattern = _to_text_blob(v)
            if not re.search(pattern, text, flags=re.MULTILINE):
                failures.append(f"regex failed: /{pattern}/")
        elif t == "not_regex":
            pattern = _to_text_blob(v)
            if re.search(pattern, text, flags=re.MULTILINE):
                failures.append(f"not_regex failed: /{pattern}/")
        elif t in {"skill_selected", "skill_not_selected"}:
            msg = _evaluate_skill_selection_assertion(
                a,
                skill_name=skill_name,
                selected=selected_skill,
            )
            if msg:
                failures.append(msg)
        else:
            failures.append(f"unsupported assertion type for text output: {t!r}")
    return failures


def evaluate_assertions_json(
    obj: Any,
    assertions: List[Assertion],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        a = _normalize_assert(raw)
        t = a["type"]

        if t in {"contains", "not_contains", "regex", "not_regex", "skill_selected", "skill_not_selected"}:
            text = json.dumps(obj, ensure_ascii=False, indent=2)
            failures.extend(
                evaluate_assertions_text(
                    text,
                    [a],
                    skill_name=skill_name,
                    selected_skill=selected_skill,
                )
            )
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


def detect_skill_selected(
    *,
    skill_name: str,
    output_text: str,
    stdout_text: str,
    stderr_text: str,
    events: Optional[List[Dict[str, Any]]],
) -> Optional[bool]:
    """
    Best-effort skill-selection detection from runner artifacts.

    Returns True/False when signals are present, or None when unknown.
    """

    skill_l = skill_name.lower().strip()
    if not skill_l:
        return None

    blobs = [output_text or "", stdout_text or "", stderr_text or ""]
    if events:
        blobs.append(json.dumps(events, ensure_ascii=False))
    blob = "\n".join(blobs)
    low = blob.lower()

    positive_patterns = [
        rf"\${re.escape(skill_l)}\b",
        rf"\b(?:using|used|invoke(?:d)?|select(?:ed)?|trigger(?:ed)?|route(?:d)?)\b[^\n]{{0,64}}\$?{re.escape(skill_l)}\b",
        rf"\bskill(?:_name| name)?\b[^\n]{{0,40}}{re.escape(skill_l)}\b",
        rf"\b{re.escape(skill_l)}\b[^\n]{{0,30}}\bskill\b",
    ]

    negative_patterns = [
        rf"\b(?:did not|didn't|not|failed to|unable to)\b[^\n]{{0,50}}\b(?:trigger|select|invoke)\b[^\n]{{0,64}}\$?{re.escape(skill_l)}\b",
        rf"\b(?:not selected|not triggered)\b[^\n]{{0,40}}\$?{re.escape(skill_l)}\b",
    ]

    pos = any(re.search(p, low, flags=re.IGNORECASE) for p in positive_patterns)
    neg = any(re.search(p, low, flags=re.IGNORECASE) for p in negative_patterns)

    if pos and not neg:
        return True
    if neg and not pos:
        return False
    if pos and neg:
        # conflicting signal; unknown
        return None

    return None


def extract_rubric_metrics(parsed_json: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(parsed_json, dict):
        return None

    has_any = any(k in parsed_json for k in ("overall_pass", "score", "checks"))
    if not has_any:
        return None

    metrics: Dict[str, Any] = {}
    if isinstance(parsed_json.get("overall_pass"), bool):
        metrics["overall_pass"] = parsed_json["overall_pass"]
    if isinstance(parsed_json.get("score"), (int, float)):
        metrics["score"] = float(parsed_json["score"])
    checks = parsed_json.get("checks")
    if isinstance(checks, list):
        metrics["checks_count"] = len(checks)
        passed = 0
        failed = 0
        for item in checks:
            if isinstance(item, dict) and isinstance(item.get("pass"), bool):
                if item["pass"]:
                    passed += 1
                else:
                    failed += 1
        metrics["checks_passed"] = passed
        metrics["checks_failed"] = failed

    return metrics or None


def run_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    output_schema_path: Optional[Path],
    sandbox: str,
    ask_for_approval: Optional[str],
    model: Optional[str],
    profile: Optional[str],
    codex_home: Optional[Path],
    jsonl_path: Optional[Path],
    codex_bin: Optional[Path],
    extra_codex_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    if codex_bin:
        node_bin = codex_bin.parent / "node"
        if node_bin.exists():
            cmd = [
                str(node_bin),
                str(codex_bin),
                "exec",
            ]
        else:
            cmd = [
                str(codex_bin),
                "exec",
            ]
    else:
        cmd = [
            "codex",
            "exec",
        ]

    cmd.extend(["--sandbox", sandbox])

    if ask_for_approval:
        cmd.extend(["--ask-for-approval", ask_for_approval])

    cmd.extend([
        "--output-last-message",
        str(output_last_message_path),
    ])

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
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    timeout = float(os.environ.get("CODEX_EVAL_TIMEOUT_SEC", "60"))

    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            env=env,
            cwd=workspace_root,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
    except subprocess.TimeoutExpired:
        return 124, "", f"codex exec timed out after {timeout} seconds."

    if jsonl_path:
        jsonl_path.write_text(proc.stdout, encoding="utf-8")

    return proc.returncode, proc.stdout, proc.stderr


def run_claude_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    claude_bin: Optional[Path],
    output_format: str,
    extra_claude_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    if claude_bin:
        cmd = [str(claude_bin), "-p"]
    else:
        cmd = ["claude", "-p"]

    cmd.extend(["--output-format", output_format])
    if extra_claude_args:
        cmd.extend(extra_claude_args)

    timeout = float(os.environ.get("CODEX_EVAL_TIMEOUT_SEC", "60"))

    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "claude CLI not found on PATH. Install Claude Code CLI and ensure it is on PATH."
    except subprocess.TimeoutExpired:
        return 124, "", f"claude headless timed out after {timeout} seconds."

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr = proc.stderr or ""
    stdout = proc.stdout or ""

    if proc.returncode != 0 and ("not logged in" in stdout.lower() or "/login" in stdout.lower()):
        hint = (
            "Claude CLI appears to be unauthenticated.\n"
            "Fix:\n"
            "  1) Run `claude` interactively and execute `/login`, then re-run evals.\n"
            "  2) Or run `claude setup-token` if you use token-based auth.\n"
            "Note: if you maintain multiple Claude setups/profiles, ensure the intended one is active.\n"
        )
        stderr = (hint + "\n" + stderr).strip() + "\n"

    return proc.returncode, stdout, stderr


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_skill_evals.py",
        description="Run skill evals using Codex CLI and/or Claude Code CLI.",
    )
    p.add_argument("path", help="Path to a skill directory or SKILL.md.")

    p.add_argument("--runner", choices=["codex", "claude"], default="claude", help="Single-run mode runner.")
    p.add_argument("--dual-run", action="store_true", help="Run both Codex and Claude for every eval case.")

    p.add_argument("--workspace", default=None, help="Workspace root to run commands in (defaults to repo root guess).")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument(
        "--ask-for-approval",
        default=None,
        choices=["untrusted", "on-failure", "on-request", "never"],
        help="Codex approval mode (optional; older codex versions may not support this flag).",
    )
    p.add_argument("--model", default=None, help="Override model for codex exec.")
    p.add_argument("--profile", default=None, help="Codex config profile name.")
    p.add_argument("--codex-home", default=None, help="Set CODEX_HOME (useful for repo-scoped .codex).")
    p.add_argument("--codex-bin", default=None, help="Override codex CLI path.")
    p.add_argument("--claude-bin", default=None, help="Override claude CLI path.")
    p.add_argument(
        "--claude-output-format",
        choices=["text", "json"],
        default="text",
        help="Claude output format (default: text).",
    )
    p.add_argument(
        "--claude-arg",
        action="append",
        default=[],
        help="Extra flag to pass to claude CLI (repeatable).",
    )
    p.add_argument(
        "--capture-jsonl",
        action="store_true",
        help="Capture Codex JSONL event stream (--json). Required for --dual-run.",
    )
    p.add_argument("--reports-dir", default="artifacts/reports/skills", help="Base directory for eval reports.")
    p.add_argument("--scorecard-out", default=None, help="Optional explicit path for merged scorecard JSON.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--tier2-mode",
        choices=["warn", "fail", "off"],
        default="warn",
        help="How to treat tier-2 findings (rubric/efficiency budgets).",
    )
    p.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra flag to pass to codex exec (repeatable).",
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


def _extract_min_rubric_score(budgets: Optional[Dict[str, Any]]) -> Optional[float]:
    if not budgets:
        return None
    v = budgets.get("min_rubric_score")
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def _extract_require_overall_pass(budgets: Optional[Dict[str, Any]]) -> Optional[bool]:
    if not budgets:
        return None
    v = budgets.get("require_overall_pass")
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        text = v.strip().lower()
        if text in {"true", "yes", "1"}:
            return True
        if text in {"false", "no", "0"}:
            return False
    return None


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    if args.dual_run and not args.capture_jsonl:
        print("ERROR: --dual-run requires --capture-jsonl for deterministic Codex checks.", file=sys.stderr)
        return 1

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
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and not codex_bin.exists():
        print(f"ERROR: --codex-bin not found: {codex_bin}", file=sys.stderr)
        return 1
    claude_bin = Path(args.claude_bin).expanduser() if args.claude_bin else None
    if claude_bin and not claude_bin.exists():
        print(f"ERROR: --claude-bin not found: {claude_bin}", file=sys.stderr)
        return 1

    run_id = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    reports_base = Path(args.reports_dir).expanduser().resolve() / skill_name / run_id
    reports_base.mkdir(parents=True, exist_ok=True)

    selected_runners = ["codex", "claude"] if args.dual_run else [args.runner]

    summary: Dict[str, Any] = {
        "schema_version": "2.0",
        "skill": skill_name,
        "skill_path": str(skill_dir),
        "workspace_root": str(workspace_root),
        "runner_mode": "dual" if args.dual_run else args.runner,
        "tier2_mode": args.tier2_mode,
        "run_id": run_id,
        "cases": [],
        "passed": True,
        "tier1_failures": 0,
        "tier2_findings": 0,
    }

    any_tier1_failed = False
    any_tier2_failed = False

    for idx, c in enumerate(cases, 1):
        case_slug = _safe_slug(c.id or c.name)
        case_dir = reports_base / f"{idx:02d}-{case_slug}"
        case_dir.mkdir(parents=True, exist_ok=True)

        schema_path: Optional[Path] = None
        if c.output_schema:
            schema_path = Path(c.output_schema)
            if not schema_path.is_absolute():
                schema_path = (skill_dir / schema_path).resolve()
            if not schema_path.exists():
                print(f"ERROR: Case {c.name}: output_schema not found: {schema_path}", file=sys.stderr)
                return 1

        prompt_body = c.prompt.strip() + "\n"
        composed_prompt = f"${skill_name}\n\n{prompt_body}" if c.prepend_skill else prompt_body
        (case_dir / "prompt.txt").write_text(composed_prompt, encoding="utf-8")

        case_tier1_failures: List[str] = []
        case_tier2_findings: List[str] = []
        case_warnings: List[str] = []
        runner_records: Dict[str, Any] = {}

        for runner_name in selected_runners:
            runner_dir = case_dir / runner_name
            runner_dir.mkdir(parents=True, exist_ok=True)

            output_path = runner_dir / "output_last_message.txt"
            jsonl_path = (runner_dir / "codex_events.jsonl") if (runner_name == "codex" and args.capture_jsonl) else None

            if runner_name == "claude":
                rc, stdout, stderr = run_claude_exec(
                    workspace_root=workspace_root,
                    prompt=composed_prompt,
                    output_last_message_path=output_path,
                    claude_bin=claude_bin,
                    output_format=args.claude_output_format,
                    extra_claude_args=args.claude_arg or None,
                )
            else:
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
                    codex_bin=codex_bin,
                    extra_codex_args=args.codex_arg or None,
                )

            (runner_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")
            (runner_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")

            output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            (runner_dir / "final.txt").write_text(output_text, encoding="utf-8")

            runner_tier1_failures: List[str] = []
            runner_tier2_findings: List[str] = []
            runner_warnings: List[str] = []
            runner_metrics: Dict[str, Any] = {}
            events: Optional[List[Dict[str, Any]]] = None

            if rc != 0:
                runner_tier1_failures.append(f"{runner_name} returned non-zero exit code: {rc}")

            if runner_name == "codex" and jsonl_path is not None:
                events, parse_warnings = load_jsonl_events(jsonl_path)
                runner_warnings.extend(parse_warnings)

                if c.deterministic_checks or c.budgets:
                    trace_result = evaluate_trace(
                        events,
                        deterministic_checks=c.deterministic_checks,
                        budgets=c.budgets,
                    )
                    runner_metrics["trace"] = trace_result.to_dict()["metrics"]
                    runner_tier1_failures.extend(trace_result.hard_failures)
                    if args.tier2_mode != "off":
                        runner_tier2_findings.extend(trace_result.soft_failures)
                    runner_warnings.extend(trace_result.warnings)
                else:
                    # still emit basic trace metrics when JSONL is available
                    trace_result = evaluate_trace(events, deterministic_checks=None, budgets=None)
                    runner_metrics["trace"] = trace_result.to_dict()["metrics"]

            if runner_name == "codex" and (c.deterministic_checks or c.budgets) and jsonl_path is None:
                runner_tier1_failures.append(
                    "deterministic_checks/budgets requested but Codex JSONL was not captured (enable --capture-jsonl)."
                )

            selected_skill = detect_skill_selected(
                skill_name=skill_name,
                output_text=output_text,
                stdout_text=stdout,
                stderr_text=stderr,
                events=events,
            )
            runner_metrics["selected_skill"] = selected_skill

            if c.should_trigger is not None and selected_skill is not None and selected_skill != c.should_trigger:
                runner_tier1_failures.append(
                    f"should_trigger failed: expected {c.should_trigger}, detected {selected_skill}"
                )
            if c.should_trigger is not None and selected_skill is None:
                runner_warnings.append("should_trigger set, but skill selection signal was unavailable for this run.")

            # Assertions + rubric parsing
            parsed_json: Optional[Any] = None
            used_json_assertions = False

            if schema_path and runner_name == "codex":
                try:
                    parsed_json = json.loads(output_text)
                except Exception as e:  # noqa: BLE001
                    runner_tier1_failures.append(f"expected JSON output (schema used), but parsing failed: {e}")
                else:
                    used_json_assertions = True
            elif runner_name == "claude" and args.claude_output_format == "json":
                try:
                    parsed_json = json.loads(output_text)
                except Exception as e:  # noqa: BLE001
                    runner_tier1_failures.append(f"expected JSON output (Claude json format), but parsing failed: {e}")
                else:
                    used_json_assertions = True

            if used_json_assertions and parsed_json is not None:
                runner_tier1_failures.extend(
                    evaluate_assertions_json(
                        parsed_json,
                        c.acceptance,
                        skill_name=skill_name,
                        selected_skill=selected_skill,
                    )
                )
            else:
                runner_tier1_failures.extend(
                    evaluate_assertions_text(
                        output_text,
                        c.acceptance,
                        skill_name=skill_name,
                        selected_skill=selected_skill,
                    )
                )

            rubric = extract_rubric_metrics(parsed_json) if parsed_json is not None else None
            if rubric:
                runner_metrics["rubric"] = rubric
                min_score = _extract_min_rubric_score(c.budgets)
                if (
                    args.tier2_mode != "off"
                    and min_score is not None
                    and isinstance(rubric.get("score"), (int, float))
                    and float(rubric["score"]) < min_score
                ):
                    runner_tier2_findings.append(
                        f"rubric score below budget: got {rubric['score']} < min_rubric_score {min_score}"
                    )

                require_overall_pass = _extract_require_overall_pass(c.budgets)
                if args.tier2_mode != "off" and require_overall_pass is True and rubric.get("overall_pass") is False:
                    runner_tier2_findings.append("rubric overall_pass is false but require_overall_pass budget is true")

            runner_record = {
                "runner": runner_name,
                "exit_code": rc,
                "passed": len(runner_tier1_failures) == 0,
                "tier1_failures": runner_tier1_failures,
                "tier2_findings": runner_tier2_findings,
                "warnings": runner_warnings,
                "artifacts": {
                    "dir": str(runner_dir),
                    "final": str(runner_dir / "final.txt"),
                    "stdout": str(runner_dir / "stdout.txt"),
                    "stderr": str(runner_dir / "stderr.txt"),
                    "jsonl": str(jsonl_path) if jsonl_path else None,
                },
                "metrics": runner_metrics,
                "used_schema": bool(schema_path and runner_name == "codex"),
            }
            (runner_dir / "result.json").write_text(json.dumps(runner_record, indent=2, ensure_ascii=False), encoding="utf-8")

            runner_records[runner_name] = runner_record
            case_tier1_failures.extend([f"[{runner_name}] {x}" for x in runner_tier1_failures])
            case_tier2_findings.extend([f"[{runner_name}] {x}" for x in runner_tier2_findings])
            case_warnings.extend([f"[{runner_name}] {x}" for x in runner_warnings])

        case_tier1_failed = len(case_tier1_failures) > 0
        case_tier2_failed = len(case_tier2_findings) > 0

        case_pass = (not case_tier1_failed) and (
            args.tier2_mode != "fail" or (not case_tier2_failed)
        )

        case_record = {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "should_trigger": c.should_trigger,
            "prepend_skill": c.prepend_skill,
            "dir": str(case_dir),
            "runners": runner_records,
            "passed": case_pass,
            "tier1_failed": case_tier1_failed,
            "tier2_failed": case_tier2_failed,
            "tier1_failures": case_tier1_failures,
            "tier2_findings": case_tier2_findings,
            "warnings": case_warnings,
        }

        (case_dir / "result.json").write_text(json.dumps(case_record, indent=2, ensure_ascii=False), encoding="utf-8")

        summary["cases"].append(case_record)

        if case_tier1_failed:
            any_tier1_failed = True
            summary["tier1_failures"] += 1
        if case_tier2_failed:
            any_tier2_failed = True
            summary["tier2_findings"] += 1

    summary["passed"] = (not any_tier1_failed) and (
        args.tier2_mode != "fail" or (not any_tier2_failed)
    )

    summary_path = reports_base / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    scorecard_path = Path(args.scorecard_out).expanduser().resolve() if args.scorecard_out else (reports_base / "scorecard.json")
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Skill evals: {skill_name}")
        print(f"Reports: {reports_base}")
        print(f"Scorecard: {scorecard_path}")
        print(f"Runner mode: {summary['runner_mode']}")
        print(f"Tier-2 mode: {args.tier2_mode}")
        for c in summary["cases"]:
            status = "PASS" if c["passed"] else "FAIL"
            print(f"- {status}: {c['id']} ({c['name']})")
            for f in c["tier1_failures"]:
                print(f"    - TIER1: {f}")
            for f in c["tier2_findings"]:
                print(f"    - TIER2: {f}")
        if any_tier2_failed and args.tier2_mode == "warn":
            print("RESULT: PASS (tier-2 findings present; warn mode)")
        else:
            print(f"RESULT: {'PASS' if summary['passed'] else 'FAIL'}")

    return 0 if summary["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
