#!/usr/bin/env python3
"""
run_skill_evals.py

Run evaluation cases for a Codex skill using Codex CLI, Codex (Kimi/Zai), and/or OpenAI CLI.

Capabilities:
- Loads SKILL.md -> skill name
- Loads Infrastructure/references/evals.yaml (v1 compatible; v2 fields optional)
- Per case, runs one runner (`--runner`), dual legacy mode (`--dual-run`), or explicit multi-runner list (`--runners`)
- Captures final output and optional Codex JSONL traces
- Applies acceptance assertions (text and JSON)
- Applies deterministic Codex trace checks (tier 1 hard / tier 2 budgets)
- Produces merged scorecards and exits non-zero on configured gate failures

Usage:
  ~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  all required gates passed
  1  parsing/IO/configuration error
  2  one or more required eval gates failed
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shlex
import subprocess as sp
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
for path_entry in (str(REPO_ROOT), str(SCRIPT_DIR)):
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_CREATOR_PYYAML_REEXEC") == "1"
    preferred_site_packages: Optional[Path] = None
    if preferred.exists():
        lib_root = preferred.parent.parent / "lib"
        for candidate in sorted(lib_root.glob("python*/site-packages")):
            if candidate.exists():
                preferred_site_packages = candidate
                break

    # Import-safe fallback: when this module is imported by tests from a Python
    # interpreter without PyYAML, pull PyYAML from the dedicated helper venv
    # instead of re-executing the CLI entrypoint.
    if preferred_site_packages is not None and str(preferred_site_packages) not in sys.path:
        sys.path.insert(0, str(preferred_site_packages))
        import yaml  # type: ignore
    elif preferred.exists() and not already_reexec and __name__ == "__main__":
        env = dict(os.environ)
        env["SKILL_CREATOR_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)
    else:
        sys.stderr.write(
            "ERROR: PyYAML is required to run run_skill_evals.py.\n\n"
            "Fix:\n"
            "  ~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>\n"
        )
        raise SystemExit(1)

from deterministic_trace_checks import evaluate_trace, load_jsonl_events  # noqa: E402

_FM_DELIM = re.compile(r"^\s*---\s*$")
_CODEX_HELP_CACHE: Dict[str, Optional[str]] = {}
_RUNNER_CHOICES = ["codex", "codex-kimi", "codex-zai", "openai", "discovery-smoke"]
_TIMEOUT_PROFILE_CHOICES = ["default", "codex-heavy", "discovery-heavy"]
_EVAL_MODE_CHOICES = ["standard", "smoke", "release"]
_CODEX_AUTH_ENV_VARS = ("OPENAI_API_KEY", "OPENAI_API_TOKEN", "OPENAI_ACCESS_TOKEN")
_BASELINE_TYPE_CHOICES = {"no_skill", "prior_skill_snapshot", "neutral_repo_baseline"}
_ROUND_STATE_CHOICES = {
    "prepared",
    "running",
    "evidence_captured",
    "reviewed",
    "decision_recorded",
    "blocked",
}
_READINESS_STATE_CHOICES = {
    "starter_valid",
    "comparison_incomplete",
    "comparison_blocked",
    "downstream_ready",
}
_METRIC_AVAILABILITY_CHOICES = {"available", "unavailable"}

# Script-level options (used to disambiguate `--codex-arg --foo` intent).
_SCRIPT_OPTIONS: Set[str] = {
    "--list-cases",
    "--runner",
    "--runners",
    "--dual-run",
    "--smoke",
    "--case",
    "--eval-mode",
    "--category",
    "--workspace",
    "--sandbox",
    "--ask-for-approval",
    "--timeout-sec",
    "--timeout-profile",
    "--model",
    "--profile",
    "--codex-fallback-profile",
    "--codex-home",
    "--codex-bin",
    "--codex-bin",
    "--openai-bin",
    "--codex-output-format",
    "--openai-output-format",
    "--codex-settings",
    "--codex-kimi-settings",
    "--codex-zai-settings",
    "--codex-kimi-command",
    "--codex-zai-command",
    "--codex-arg",
    "--openai-arg",
    "--capture-jsonl",
    "--reports-dir",
    "--scorecard-out",
    "--format",
    "--tier2-mode",
    "--codex-arg",
    "-h",
    "--help",
}


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


def load_skill_frontmatter(skill_md_path: Path) -> Dict[str, Any]:
    raw = _read_text(skill_md_path)
    fm, _ = _parse_frontmatter(raw)
    return fm


def _git_metadata(path: Path) -> Dict[str, Optional[str]]:
    repo_hint = str(path)
    metadata: Dict[str, Optional[str]] = {"commit": None, "branch": None}
    for key, args in {
        "commit": ["rev-parse", "HEAD"],
        "branch": ["rev-parse", "--abbrev-ref", "HEAD"],
    }.items():
        try:
            proc = sp.run(
                ["git", "-C", repo_hint, *args],
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception:
            metadata[key] = None
            continue
        if proc.returncode == 0:
            metadata[key] = proc.stdout.strip() or None
    return metadata


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
    timeout_sec: Optional[float] = None
    timeout_profile: Optional[str] = None
    smoke_mode: Optional[str] = None
    eval_modes: Optional[Tuple[str, ...]] = None
    baseline_type: Optional[str] = None
    comparison_inputs: Optional[Dict[str, Any]] = None
    iteration_round_state: Optional[str] = None
    metric_availability: Optional[str] = None
    readiness_state: Optional[str] = None
    comparison_review_artifact: Optional[str] = None
    neutral_baseline_approval_id: Optional[str] = None


_VALID_CATEGORIES = {"happy", "edge", "negative", "pressure"}


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_optional_case_artifact_path(case_dir: Path, artifact: Optional[str], workspace_root: Optional[Path] = None) -> Optional[str]:
    if artifact is None:
        return None
    candidate = Path(artifact)
    if candidate.is_absolute():
        result = candidate
    else:
        result = (case_dir / candidate).resolve()
    if workspace_root:
        try:
            return str(result.relative_to(workspace_root))
        except ValueError:
            pass
    return str(result)


def _normalize_eval_modes(raw: Any, *, case_number: int) -> Optional[Tuple[str, ...]]:
    if raw is None:
        return None
    if not isinstance(raw, list) or not raw:
        raise ValueError(
            f"Case #{case_number} `eval_modes` must be a non-empty list when provided; "
            f"allowed: {', '.join(_EVAL_MODE_CHOICES[1:])}."
        )
    normalized: List[str] = []
    for mode in raw:
        mode_text = str(mode).strip().lower()
        if mode_text not in {"smoke", "release"}:
            raise ValueError(
                f"Case #{case_number} `eval_modes` entries must be one of smoke, release; got {mode!r}."
            )
        if mode_text not in normalized:
            normalized.append(mode_text)
    return tuple(normalized)


def _load_evals_document(evals_path: Path) -> Dict[str, Any]:
    obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or "cases" not in obj or not isinstance(obj["cases"], list):
        raise ValueError("evals.yaml must be a mapping with `cases: [...]`.")
    return obj


def load_neutral_baseline_approvals(evals_path: Path) -> Dict[str, Dict[str, Any]]:
    obj = _load_evals_document(evals_path)
    raw = obj.get("neutral_baseline_approvals")
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise ValueError("`neutral_baseline_approvals` must be a list when provided.")

    approvals: Dict[str, Dict[str, Any]] = {}
    for i, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError(f"neutral_baseline_approvals entry #{i} must be a mapping.")
        approval_id = str(item.get("id") or "").strip()
        if not approval_id:
            raise ValueError(f"neutral_baseline_approvals entry #{i} missing non-empty `id`.")
        approvals[approval_id] = dict(item)
    return approvals


def load_evals(evals_path: Path) -> List[EvalCase]:
    obj = _load_evals_document(evals_path)

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

        timeout_sec = c.get("timeout_sec")
        if timeout_sec is not None:
            try:
                timeout_sec = float(timeout_sec)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Case #{i} `timeout_sec` must be numeric when provided.") from exc
            if timeout_sec <= 0:
                raise ValueError(f"Case #{i} `timeout_sec` must be > 0 when provided.")

        timeout_profile = c.get("timeout_profile")
        if timeout_profile is not None:
            timeout_profile = str(timeout_profile).strip().lower()
            if timeout_profile and timeout_profile not in _TIMEOUT_PROFILE_CHOICES:
                raise ValueError(
                    f"Case #{i} `timeout_profile` must be one of {_TIMEOUT_PROFILE_CHOICES}; "
                    f"got {timeout_profile!r}."
                )

        smoke_mode = c.get("smoke_mode")
        if smoke_mode is not None:
            smoke_mode = str(smoke_mode).strip()
            if not smoke_mode:
                smoke_mode = None
        eval_modes = _normalize_eval_modes(c.get("eval_modes"), case_number=i)

        baseline_type = c.get("baseline_type")
        if baseline_type is not None:
            baseline_type = str(baseline_type).strip().lower()
            if baseline_type and baseline_type not in _BASELINE_TYPE_CHOICES:
                raise ValueError(
                    f"Case #{i} `baseline_type` must be one of {sorted(_BASELINE_TYPE_CHOICES)}; "
                    f"got {baseline_type!r}."
                )

        comparison_inputs = c.get("comparison_inputs")
        if comparison_inputs is not None and not isinstance(comparison_inputs, dict):
            raise ValueError(f"Case #{i} `comparison_inputs` must be a mapping when provided.")

        iteration_round_state = c.get("iteration_round_state")
        if iteration_round_state is not None:
            iteration_round_state = str(iteration_round_state).strip().lower()
            if iteration_round_state and iteration_round_state not in _ROUND_STATE_CHOICES:
                raise ValueError(
                    f"Case #{i} `iteration_round_state` must be one of {sorted(_ROUND_STATE_CHOICES)}; "
                    f"got {iteration_round_state!r}."
                )

        metric_availability = c.get("metric_availability")
        if metric_availability is not None:
            metric_availability = str(metric_availability).strip().lower()
            if metric_availability and metric_availability not in _METRIC_AVAILABILITY_CHOICES:
                raise ValueError(
                    f"Case #{i} `metric_availability` must be one of {sorted(_METRIC_AVAILABILITY_CHOICES)}; "
                    f"got {metric_availability!r}."
                )

        readiness_state = c.get("readiness_state")
        if readiness_state is not None:
            readiness_state = str(readiness_state).strip().lower()
            if readiness_state and readiness_state not in _READINESS_STATE_CHOICES:
                raise ValueError(
                    f"Case #{i} `readiness_state` must be one of {sorted(_READINESS_STATE_CHOICES)}; "
                    f"got {readiness_state!r}."
                )

        comparison_review_artifact = c.get("comparison_review_artifact")
        if comparison_review_artifact is not None:
            comparison_review_artifact = str(comparison_review_artifact).strip()
            if not comparison_review_artifact:
                comparison_review_artifact = None

        neutral_baseline_approval_id = c.get("neutral_baseline_approval_id")
        if neutral_baseline_approval_id is not None:
            neutral_baseline_approval_id = str(neutral_baseline_approval_id).strip()
            if not neutral_baseline_approval_id:
                neutral_baseline_approval_id = None

        if baseline_type == "neutral_repo_baseline" and not neutral_baseline_approval_id:
            raise ValueError(
                f"Case #{i} uses baseline_type=neutral_repo_baseline but is missing `neutral_baseline_approval_id`."
            )

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
                timeout_sec=timeout_sec,
                timeout_profile=timeout_profile if timeout_profile else None,
                smoke_mode=smoke_mode,
                eval_modes=eval_modes,
                baseline_type=baseline_type if baseline_type else None,
                comparison_inputs=dict(comparison_inputs) if isinstance(comparison_inputs, dict) else None,
                iteration_round_state=iteration_round_state if iteration_round_state else None,
                metric_availability=metric_availability if metric_availability else None,
                readiness_state=readiness_state if readiness_state else None,
                comparison_review_artifact=comparison_review_artifact,
                neutral_baseline_approval_id=neutral_baseline_approval_id,
            )
        )
    return cases


def _case_matches_eval_mode(case: EvalCase, *, eval_mode: str) -> bool:
    if eval_mode == "standard":
        return True
    if case.eval_modes:
        return eval_mode in case.eval_modes
    if eval_mode == "release":
        return True
    if case.category in {"negative", "pressure"}:
        return False
    if case.deterministic_checks or case.budgets:
        return False
    return True


def _filter_cases_for_eval_mode(cases: Sequence[EvalCase], *, eval_mode: str) -> List[EvalCase]:
    return [case for case in cases if _case_matches_eval_mode(case, eval_mode=eval_mode)]


def _is_smoke_only_case(case: EvalCase) -> bool:
    if not case.smoke_mode:
        return False
    if case.eval_modes is None:
        return True
    return case.eval_modes == ("smoke",)


def _write_junit_report(summary: Dict[str, Any], destination: Path) -> None:
    tier2_fail_mode = str(summary.get("tier2_mode") or "warn") == "fail"
    junit_failures = sum(
        1
        for case in summary.get("cases", [])
        if case.get("tier1_failed") or (tier2_fail_mode and case.get("tier2_failed"))
    )
    suite_attrs = {
        "name": str(summary.get("skill") or "skill-evals"),
        "tests": str(len(summary.get("cases", []))),
        "failures": str(junit_failures),
        "errors": "0",
    }
    if summary.get("generated_at"):
        suite_attrs["timestamp"] = str(summary["generated_at"])
    if summary.get("run_id"):
        suite_attrs["id"] = str(summary["run_id"])

    lines: List[str] = ['<?xml version="1.0" encoding="utf-8"?>']
    suite_open = " ".join(f'{k}="{html.escape(v, quote=True)}"' for k, v in suite_attrs.items())
    lines.append(f"<testsuite {suite_open}>")
    for case in summary.get("cases", []):
        case_attrs = {
            "name": str(case.get("id") or case.get("name") or "unknown"),
            "classname": str(summary.get("skill") or "skill-evals"),
            "time": str(case.get("timeout_sec") or 0),
        }
        case_open = " ".join(f'{k}="{html.escape(v, quote=True)}"' for k, v in case_attrs.items())
        lines.append(f"  <testcase {case_open}>")
        if case.get("tier1_failed"):
            detail = "\n".join(case.get("tier1_failures") or []) or "tier1 failure"
            lines.append('    <failure message="tier1 failure">')
            lines.append(html.escape(detail))
            lines.append("    </failure>")
        elif case.get("tier2_failed"):
            detail = "\n".join(case.get("tier2_findings") or []) or "tier2 findings"
            if tier2_fail_mode:
                lines.append('    <failure message="tier2 findings in fail mode">')
                lines.append(html.escape(detail))
                lines.append("    </failure>")
            else:
                lines.append('    <skipped message="tier2 findings in warn/off mode">')
                lines.append(html.escape(detail))
                lines.append("    </skipped>")

        chunks: List[str] = []
        if case.get("warnings"):
            chunks.append("warnings:\n" + "\n".join(case["warnings"]))
        if case.get("tier2_findings"):
            chunks.append("tier2_findings:\n" + "\n".join(case["tier2_findings"]))
        if case.get("dir"):
            chunks.append(f"artifacts_dir:\n{case['dir']}")
        lines.append("    <system-out>")
        lines.append(html.escape("\n\n".join(chunks)))
        lines.append("    </system-out>")
        lines.append("  </testcase>")
    lines.append("</testsuite>")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
        return None

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

    final_text = output_text or ""
    final_low = final_text.lower()

    explicit_negative_patterns = [
        rf"\b{re.escape(skill_l)}\b\s+is\s+overkill\b",
        rf"\boverkill\b[^\n]{{0,32}}\b{re.escape(skill_l)}\b",
        rf"\b(?:do not|don't|did not|didn't|not)\b[^\n]{{0,32}}\b(?:use|trigger|select|invoke)\b[^\n]{{0,48}}\b{re.escape(skill_l)}\b",
    ]
    if any(re.search(p, final_low, flags=re.IGNORECASE) for p in explicit_negative_patterns):
        return False

    explicit_positive_patterns = [
        rf"\${re.escape(skill_l)}\b",
        rf"\b(?:using|used|invoked|selected|triggered|routed to)\b[^\n]{{0,48}}\$?{re.escape(skill_l)}\b",
    ]
    if any(re.search(p, final_low, flags=re.IGNORECASE) for p in explicit_positive_patterns):
        return True

    blobs = [final_text, stdout_text or "", stderr_text or ""]
    if events:
        event_blob = json.dumps(events, ensure_ascii=False, sort_keys=True)
        blobs.append(event_blob)
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

    for event in events or []:
        if not isinstance(event, dict):
            continue

        for key in ("skill", "skill_name", "selected_skill", "selected", "tool_name"):
            value = event.get(key)
            if isinstance(value, str) and skill_l in value.lower():
                event_value = value.strip().lower()
                if key in {"selected", "selected_skill"}:
                    return event_value == skill_l
                if key in {"skill", "skill_name", "tool_name"}:
                    return True

        metadata = event.get("metadata")
        if isinstance(metadata, dict):
            meta_skill = metadata.get("skill") if "skill" in metadata else metadata.get("selected_skill")
            if isinstance(meta_skill, str) and skill_l in meta_skill.lower():
                return True

        tool = event.get("tool")
        if isinstance(tool, dict):
            tool_name = tool.get("name")
            if isinstance(tool_name, str) and skill_l in tool_name.lower():
                return True

    return None


def extract_rubric_metrics(parsed_json: Any) -> Optional[Dict[str, Any]]:
    """
    Extracts rubric-style metrics from a parsed JSON object.

    When the input is a mapping containing any of the keys "overall_pass", "score", or "checks",
    this returns a dictionary with the extracted metrics. The returned mapping may include:
    - "overall_pass": the boolean value from the input when present.
    - "score": the numeric score coerced to a float when present.
    - "checks_count": the number of entries in the "checks" list when present.
    - "checks_passed": count of check entries with a boolean `"pass": true`.
    - "checks_failed": count of check entries with a boolean `"pass": false`.

    Returns:
        A dict with the extracted metrics as described above, or `None` if the input is not a mapping
        or contains none of the recognized rubric fields.
    """
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


def _acceptance_skip_reason(*, exit_code: int, output_text: str) -> Optional[str]:
    """
    Return a skip reason when acceptance assertions should be skipped because the runner failed and produced no final output.

    Parameters:
        exit_code (int): The runner process exit code.
        output_text (str): The runner's final output text.

    Returns:
        Optional[str]: A human-readable skip reason when acceptance checks should be skipped, or `None` when they should be performed.
    """
    if exit_code == 0:
        return None
    if output_text.strip():
        return None
    return "skipped acceptance assertions because the runner exited non-zero and produced no final output"


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
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_codex_args: Optional[List[str]] = None,
    fallback_profile: Optional[str] = None,
) -> Tuple[int, str, str, List[str]]:
    """
    Run the Codex CLI `exec` command with the provided prompt and capture outputs and warnings.

    Parameters:
        workspace_root (Path): Working directory for the Codex subprocess.
        prompt (str): Prompt text supplied to Codex via stdin.
        output_last_message_path (Path): File path where the CLI's "last message" output will be written.
        output_schema_path (Optional[Path]): Path to an output schema file to pass via `--output-schema` (if any).
        sandbox (str): Sandbox name to pass via `--sandbox`.
        ask_for_approval (Optional[str]): Legacy value for `--ask-for-approval` when supported by the Codex CLI.
        model (Optional[str]): Model name to pass via `--model`.
        profile (Optional[str]): Active Codex profile name to pass via `--profile`.
        codex_home (Optional[Path]): Directory to set as `CODEX_HOME` in the subprocess environment.
        jsonl_path (Optional[Path]): When provided, the raw CLI stdout is written to this path as JSONL.
        codex_bin (Optional[Path]): Path to a Codex binary; its parent directory is prepended to `PATH`.
        timeout_sec (Optional[float]): Explicit timeout in seconds for the subprocess; if omitted, resolved from profile/env.
        timeout_profile (str): Timeout profile name used when `timeout_sec` is not provided.
        extra_codex_args (Optional[List[str]]): Additional CLI arguments appended to the command.
        fallback_profile (Optional[str]): If the first run fails due to unsupported reasoning.summary, retry with this profile.

    Returns:
        Tuple[int, str, str, List[str]]: A tuple of `(exit_code, stdout, stderr, warnings)`. `exit_code` may be
        127 when the Codex CLI is not found and 124 on timeout. `stdout` and `stderr` are the subprocess outputs;
        `warnings` contains non-fatal diagnostics (e.g., unsupported flags, automatic fallback retries).
    """
    warnings: List[str] = []
    env = os.environ.copy()
    if codex_home:
        env["CODEX_HOME"] = str(codex_home)
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    def _invoke(effective_profile: Optional[str]) -> Tuple[int, str, str]:
        cmd = _codex_exec_prefix(codex_bin)
        cmd.extend(["--sandbox", sandbox])

        if ask_for_approval:
            supports = _codex_supports_exec_flag(codex_bin, "--ask-for-approval")
            if supports is not False:
                cmd.extend(["--ask-for-approval", ask_for_approval])

        cmd.extend([
            "--output-last-message",
            str(output_last_message_path),
        ])

        if extra_codex_args:
            cmd.extend(extra_codex_args)

        if effective_profile:
            cmd.extend(["--profile", effective_profile])
        if model:
            cmd.extend(["--model", model])
        if output_schema_path:
            cmd.extend(["--output-schema", str(output_schema_path)])

        if jsonl_path:
            cmd.append("--json")

        cmd.append("-")

        try:
            proc = sp.run(
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
        except sp.TimeoutExpired:
            return 124, "", f"codex exec timed out after {timeout} seconds."

        if jsonl_path:
            jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            jsonl_path.write_text(proc.stdout, encoding="utf-8")

        return proc.returncode, proc.stdout, proc.stderr

    rc, stdout, stderr = _invoke(profile)

    if (
        rc != 0
        and fallback_profile
        and fallback_profile != profile
        and _is_codex_reasoning_summary_unsupported(f"{stderr}\n{stdout}")
    ):
        warnings.append(
            "Codex rejected reasoning.summary for the active profile/model; "
            f"retrying with fallback profile `{fallback_profile}`."
        )
        rc, stdout, stderr = _invoke(fallback_profile)

    return rc, stdout, stderr, warnings


def run_alt_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    codex_bin: Optional[Path],
    output_format: str,
    settings_path: Optional[Path],
    cli_command: Optional[str],
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_codex_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    command_name = (cli_command or "").strip() or "codex"
    use_shell_function = command_name != "codex"

    base_args: List[str] = [command_name, "-p"]
    if settings_path:
        base_args.extend(["--settings", str(settings_path)])
    base_args.extend(["--output-format", output_format])
    if extra_codex_args:
        base_args.extend(extra_codex_args)

    if use_shell_function:
        command_str = " ".join(shlex.quote(x) for x in base_args)
        cmd = ["zsh", "-ic", command_str]
    else:
        if codex_bin:
            cmd = [str(codex_bin), *base_args[1:]]
        else:
            cmd = base_args

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    try:
        proc = sp.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
        )
    except FileNotFoundError:
        if use_shell_function:
            return 127, "", f"{command_name} is not available in interactive zsh. Check your shell setup."
        return 127, "", "codex CLI not found on PATH. Install Codex CLI and ensure it is on PATH."
    except sp.TimeoutExpired:
        return 124, "", f"codex headless timed out after {timeout} seconds."

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr = proc.stderr or ""
    stdout = proc.stdout or ""

    if proc.returncode != 0 and ("not logged in" in stdout.lower() or "/login" in stdout.lower()):
        hint = (
            "Codex CLI appears to be unauthenticated.\n"
            "Fix:\n"
            "  1) Run `codex` interactively and execute `/login`, then re-run evals.\n"
            "  2) Or run `codex setup-token` if you use token-based auth.\n"
            "Note: if you maintain multiple Codex setups/profiles, ensure the intended one is active.\n"
        )
        stderr = (hint + "\n" + stderr).strip() + "\n"

    return proc.returncode, stdout, stderr


def run_openai_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    openai_bin: Optional[Path],
    output_format: str,
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_openai_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    if openai_bin:
        cmd = [str(openai_bin)]
    else:
        cmd = ["openai"]

    cmd.extend(["--prompt", prompt, "--output-format", output_format])
    if extra_openai_args:
        cmd.extend(extra_openai_args)

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    try:
        proc = sp.run(
            cmd,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "openai CLI not found on PATH. Install OpenAI CLI and ensure it is on PATH."
    except sp.TimeoutExpired:
        return 124, "", f"openai headless timed out after {timeout} seconds."

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _eval_timeout_seconds(
    *,
    timeout_sec: Optional[float],
    timeout_profile: str,
) -> float:
    if timeout_sec is not None:
        return float(timeout_sec)

    raw = os.environ.get("SKILL_EVAL_TIMEOUT_SEC")
    if raw is None:
        raw = os.environ.get("CODEX_EVAL_TIMEOUT_SEC")
    if raw is not None and str(raw).strip():
        return float(raw)

    if timeout_profile == "codex-heavy":
        return 180.0
    if timeout_profile == "discovery-heavy":
        return 300.0
    return 60.0


def _resolve_case_timeout(
    case: EvalCase,
    *,
    cli_timeout_sec: Optional[float],
    cli_timeout_profile: str,
) -> Tuple[Optional[float], str]:
    if cli_timeout_sec is not None:
        return float(cli_timeout_sec), cli_timeout_profile

    resolved_timeout_sec = case.timeout_sec if case.timeout_sec is not None else None
    resolved_timeout_profile = cli_timeout_profile

    if case.timeout_profile and cli_timeout_profile == "default":
        resolved_timeout_profile = case.timeout_profile

    return resolved_timeout_sec, resolved_timeout_profile


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def _rewrite_dash_prefixed_codex_args(argv: Sequence[str]) -> List[str]:
    """
    Allow ergonomic `--*-arg --flag` usage by rewriting it to
    `--*-arg=--flag` before argparse runs.

    We only rewrite when the next token is not a known script option.
    """
    out: List[str] = []
    i = 0
    n = len(argv)
    rewritable = {"--codex-arg", "--codex-arg", "--openai-arg"}
    while i < n:
        tok = argv[i]
        if tok in rewritable and i + 1 < n:
            nxt = argv[i + 1]
            if nxt.startswith("-") and nxt not in _SCRIPT_OPTIONS:
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out


def _parse_runners(raw: Sequence[str]) -> List[str]:
    expanded: List[str] = []
    for item in raw:
        for piece in str(item).split(","):
            token = piece.strip()
            if token:
                expanded.append(token)

    if not expanded:
        raise ValueError("--runners provided but no runner names were parsed.")

    invalid = [x for x in expanded if x not in _RUNNER_CHOICES]
    if invalid:
        raise ValueError(
            f"Invalid runner(s): {', '.join(invalid)}. Allowed: {', '.join(_RUNNER_CHOICES)}."
        )
    return expanded


def _parse_csv_args(raw: Sequence[str]) -> List[str]:
    expanded: List[str] = []
    for item in raw:
        for piece in str(item).split(","):
            token = piece.strip()
            if token:
                expanded.append(token)
    return expanded


def _filter_cases(
    cases: List[EvalCase],
    *,
    case_filters: Sequence[str],
    categories: Sequence[str],
) -> List[EvalCase]:
    """
    Filter eval cases by case id/name substring and by category.

    Parameters:
        case_filters (Sequence[str]): Substring terms (case-insensitive) to match against each case's `id` or `name`. An empty sequence disables id/name filtering.
        categories (Sequence[str]): Category names to include (case-insensitive). An empty sequence disables category filtering.

    Returns:
        List[EvalCase]: The subset of `cases` that match all provided filters.

    Raises:
        ValueError: If any provided category is not in the allowed set, or if no cases match the supplied filters.
    """
    if not case_filters and not categories:
        return cases

    category_set = {c.lower() for c in categories if c}
    invalid_categories = sorted(category_set - _VALID_CATEGORIES)
    if invalid_categories:
        raise ValueError(
            f"Unknown category filter(s): {', '.join(invalid_categories)}. "
            f"Allowed: {', '.join(sorted(_VALID_CATEGORIES))}."
        )

    case_terms = [term.lower() for term in case_filters if term]
    filtered: List[EvalCase] = []
    for case in cases:
        haystack = f"{case.id} {case.name}".lower()
        match_case = not case_terms or any(term in haystack for term in case_terms)
        match_category = not category_set or ((case.category or "").lower() in category_set)
        if match_case and match_category:
            filtered.append(case)

    if not filtered:
        available = ", ".join(f"{c.id}({c.category or 'uncategorized'})" for c in cases)
        raise ValueError(
            "No eval cases matched the supplied filters. "
            f"Available cases: {available}"
        )

    return filtered


def _codex_cli_prefix(codex_bin: Optional[Path]) -> List[str]:
    """
    Builds the command prefix to invoke the Codex CLI, preferring a bundled `node` executable when present.

    Parameters:
        codex_bin (Optional[Path]): Path to a specific `codex` binary. If `None`, the system `codex` command name is used.

    Returns:
        List[str]: Sequence of command tokens to run the CLI:
            - `["node", "<codex_bin>"]` if a sibling `node` executable exists next to `codex_bin`,
            - `["<codex_bin>"]` if `codex_bin` is provided without a sibling `node`,
            - `["codex"]` if `codex_bin` is `None`.
    """
    if codex_bin:
        node_bin = codex_bin.parent / "node"
        if node_bin.exists():
            return [str(node_bin), str(codex_bin)]
        return [str(codex_bin)]
    return ["codex"]


def _codex_exec_prefix(codex_bin: Optional[Path]) -> List[str]:
    """
    Build the command token prefix for invoking the Codex CLI `exec` subcommand.

    Parameters:
        codex_bin (Optional[Path]): Optional path to a specific `codex` binary to prefer; if `None` the default resolver is used.

    Returns:
        List[str]: A list of command tokens forming the prefix (e.g. `["codex", "exec"]` or `["node", "...", "codex", "exec"]`).
    """
    return [*_codex_cli_prefix(codex_bin), "exec"]


def _effective_codex_home(codex_home: Optional[Path]) -> Path:
    """
    Resolve the effective CODEX_HOME directory to use for Codex operations.

    If `codex_home` is provided, it is used; otherwise the `CODEX_HOME` environment variable is used if set; if neither is present, defaults to `~/.codex`. The returned Path is expanded and resolved to an absolute path.

    Parameters:
        codex_home (Optional[Path]): Optional override path for CODEX_HOME.

    Returns:
        Path: Absolute, expanded, resolved path to the Codex home directory.
    """
    raw = str(codex_home) if codex_home else (os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    return Path(raw).expanduser().resolve()


def _codex_env(*, codex_bin: Optional[Path], codex_home: Optional[Path]) -> Dict[str, str]:
    """
    Builds an environment mapping configured for running the Codex CLI.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary; when provided, its parent directory is prepended to the `PATH`.
        codex_home (Optional[Path]): Desired Codex home directory; when `None` an effective home is resolved via `_effective_codex_home`.

    Returns:
        Dict[str, str]: A copy of the current environment with `CODEX_HOME` set and `PATH` modified if `codex_bin` was provided.
    """
    env = os.environ.copy()
    effective_home = _effective_codex_home(codex_home)
    env["CODEX_HOME"] = str(effective_home)
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"
    return env


def _codex_auth_env_keys(env: Dict[str, str]) -> List[str]:
    """
    Return the Codex authentication environment variable names that are present and non-empty in the provided environment mapping.

    Parameters:
        env (Dict[str, str]): Mapping of environment variable names to their values (typically os.environ).

    Returns:
        List[str]: Keys from `_CODEX_AUTH_ENV_VARS` whose corresponding value in `env` is non-empty after trimming.
    """
    return [key for key in _CODEX_AUTH_ENV_VARS if str(env.get(key) or "").strip()]


def _codex_login_status(
    *,
    codex_bin: Optional[Path],
    codex_home: Optional[Path],
) -> Tuple[int, str, str]:
    """
    Check the Codex CLI authentication status by running `codex login status`.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary to use; if None the system PATH is used.
        codex_home (Optional[Path]): Codex home directory to set via the `CODEX_HOME` environment variable.

    Returns:
        Tuple[int, str, str]: A tuple of `(exit_code, stdout, stderr)`.
            - `exit_code`: the subprocess return code; `127` if the Codex CLI was not found, `124` if the command timed out.
            - `stdout`: the command's standard output as a string (empty string if none).
            - `stderr`: the command's standard error as a string (contains a user-facing message when CLI is missing or timed out).
    """
    cmd = [*_codex_cli_prefix(codex_bin), "login", "status"]
    env = _codex_env(codex_bin=codex_bin, codex_home=codex_home)
    try:
        proc = sp.run(cmd, text=True, capture_output=True, env=env, timeout=10)
    except FileNotFoundError:
        return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
    except sp.TimeoutExpired:
        return 124, "", "codex login status timed out after 10 seconds."
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _preflight_codex_live_runner(
    *,
    workspace_root: Path,
    codex_bin: Optional[Path],
    codex_home: Optional[Path],
) -> Tuple[List[str], List[str]]:
    """
    Validate that the configured Codex home/bin provide authenticated state required for live `codex exec` runs.

    Performs checks for the existence of the effective CODEX_HOME, presence of an auth.json file or auth-related environment variables, and attempts a short `codex login status` probe. Collects any blocking error messages and non-blocking warnings but does not raise exceptions.

    Parameters:
        workspace_root (Path): Repository/workspace root used to detect repo-local `.codex`.
        codex_bin (Optional[Path]): Optional path to a Codex binary to use for login status probing.
        codex_home (Optional[Path]): Optional explicit Codex home directory; if omitted an effective default is used.

    Returns:
        Tuple[List[str], List[str]]: A pair (errors, warnings).
            - errors: blocking issues that should prevent live Codex execution (e.g., missing home or missing authentication).
            - warnings: non-blocking diagnostics or guidance (e.g., env-based auth present despite login status).
    """
    errors: List[str] = []
    warnings: List[str] = []
    effective_home = _effective_codex_home(codex_home)
    env = _codex_env(codex_bin=codex_bin, codex_home=codex_home)
    auth_env_keys = _codex_auth_env_keys(env)
    auth_file = effective_home / "auth.json"
    default_home = (Path.home() / ".codex").resolve()
    default_auth_file = default_home / "auth.json"
    repo_local_home = (workspace_root / ".codex").resolve()

    if not effective_home.exists():
        errors.append(f"Selected Codex home does not exist: {effective_home}")
        return errors, warnings

    if not auth_file.exists() and not auth_env_keys:
        message = (
            f"Selected Codex home is missing authenticated Codex state for live Codex runs: {effective_home}. "
            "`--codex-home` replaces CODEX_HOME for `codex exec`."
        )
        if effective_home == repo_local_home:
            message += (
                " Repo-local `.codex` is suitable for discovery/static smoke, not full live smoke unless "
                "it is provisioned with authenticated Codex state."
            )
        if effective_home != default_home and default_auth_file.exists():
            message += (
                f" The default home {default_home} has auth.json, but the selected home does not inherit it."
            )
        message += " Use an authenticated Codex home for `--runner codex`, or omit `--codex-home` to use the default home."
        errors.append(message)
        return errors, warnings

    status_code, status_stdout, status_stderr = _codex_login_status(codex_bin=codex_bin, codex_home=effective_home)
    status_text = " ".join(part.strip() for part in (status_stdout, status_stderr) if part.strip()).strip()
    if status_code == 0:
        return errors, warnings

    if "not logged in" in status_text.lower():
        if auth_env_keys:
            warnings.append(
                "Codex login status reported 'Not logged in', but auth environment variables are present "
                f"({', '.join(auth_env_keys)}). Live exec may still work if this environment intentionally uses env-based auth."
            )
            return errors, warnings

        message = f"Selected Codex home is not logged in for live Codex runs: {effective_home}."
        if effective_home == repo_local_home:
            message += (
                " Repo-local `.codex` is suitable for discovery/static smoke, not full live smoke unless "
                "it is authenticated."
            )
        if effective_home != default_home and default_auth_file.exists():
            message += f" The default home {default_home} has auth.json, but the selected home does not inherit it."
        message += (
            " Run `CODEX_HOME=<that-home> codex login` for the selected home, or omit `--codex-home` to use the default authenticated home."
        )
        errors.append(message)
        return errors, warnings

    warnings.append(
        f"Unable to confirm Codex login status for {effective_home}: {status_text or f'exit code {status_code}'}"
    )
    return errors, warnings


def _codex_help_text(codex_bin: Optional[Path]) -> Optional[str]:
    """
    Retrieve and cache the combined help text for the Codex CLI.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary to query. If omitted, the system "codex" command will be used.

    Returns:
        Optional[str]: Combined stdout and stderr produced by running the help command, or `None` if the executable is not available or the help invocation failed.
    """
    key = str(codex_bin.resolve()) if codex_bin else "codex"
    if key in _CODEX_HELP_CACHE:
        return _CODEX_HELP_CACHE[key]

    cmd = _codex_exec_prefix(codex_bin) + ["--help"]
    env = os.environ.copy()
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    try:
        proc = sp.run(cmd, text=True, capture_output=True, env=env, timeout=10)
    except Exception:  # noqa: BLE001
        _CODEX_HELP_CACHE[key] = None
        return None

    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    _CODEX_HELP_CACHE[key] = text
    return text


def _codex_supports_exec_flag(codex_bin: Optional[Path], flag: str) -> Optional[bool]:
    help_text = _codex_help_text(codex_bin)
    if help_text is None:
        return None
    return flag in help_text


def _is_codex_untrusted_repo_error(stderr_text: str) -> bool:
    low = (stderr_text or "").lower()
    return ("not inside a trusted directory" in low) and ("skip-git-repo-check" in low)


def _is_codex_reasoning_summary_unsupported(stderr_text: str) -> bool:
    low = (stderr_text or "").lower()
    return ("unsupported parameter" in low) and ("reasoning.summary" in low)


def _has_skip_git_repo_check(extra_codex_args: Optional[Sequence[str]]) -> bool:
    if not extra_codex_args:
        return False
    return any(arg.strip() == "--skip-git-repo-check" for arg in extra_codex_args if isinstance(arg, str))


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Builds and returns the command-line argument parser for run_skill_evals.py.

    The parser includes options for selecting cases and runners, eval suite mode and categories,
    timeout and runtime configuration, Codex/Codex/OpenAI CLI overrides and extra flags,
    JSONL capture and reporting paths, and tier2 gating behavior.

    Returns:
        argparse.ArgumentParser: A parser configured with the script's CLI options.
    """
    p = argparse.ArgumentParser(
        prog="run_skill_evals.py",
        description="Run skill evals using Codex, Codex (Kimi/Zai), and/or OpenAI CLI runners.",
    )
    p.add_argument("path", help="Path to a skill directory or SKILL.md.")
    p.add_argument(
        "--list-cases",
        action="store_true",
        help="List available eval cases (respects --case/--category filters) and exit.",
    )

    p.add_argument("--runner", choices=_RUNNER_CHOICES, default="codex", help="Single-run mode runner.")
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Shortcut for `--runner discovery-smoke` for fast contract-level discovery smoke checks.",
    )
    p.add_argument(
        "--runners",
        action="append",
        default=[],
        help=(
            "Explicit runner list (repeatable or comma-separated). "
            "Examples: --runners codex,codex-kimi --runners openai"
        ),
    )
    p.add_argument("--dual-run", action="store_true", help="Run both Codex and Codex-Kimi for every eval case.")
    p.add_argument(
        "--case",
        action="append",
        default=[],
        help=(
            "Run only matching eval case ids/names (repeatable or comma-separated). "
            "Substring match against case id and name."
        ),
    )
    p.add_argument(
        "--eval-mode",
        choices=_EVAL_MODE_CHOICES,
        default="standard",
        help=(
            "Eval suite mode. `standard` preserves current behavior, "
            "`smoke` runs a faster contract/regression subset, and `release` runs the full release-grade suite."
        ),
    )
    p.add_argument(
        "--category",
        action="append",
        default=[],
        help=(
            "Run only evals in matching category (repeatable or comma-separated). "
            f"Allowed: {', '.join(sorted(_VALID_CATEGORIES))}."
        ),
    )

    p.add_argument("--workspace", default=None, help="Workspace root to run commands in (defaults to repo root guess).")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument(
        "--ask-for-approval",
        default=None,
        choices=["untrusted", "on-request", "never"],
        help=(
            "Legacy Codex approval mode flag. Prefer configuring approval policy via profile/config; "
            "ignored when the active Codex CLI does not support --ask-for-approval."
        ),
    )
    p.add_argument(
        "--timeout-sec",
        type=float,
        default=None,
        help="Per-runner subprocess timeout in seconds. Overrides env vars and timeout profile.",
    )
    p.add_argument(
        "--timeout-profile",
        choices=_TIMEOUT_PROFILE_CHOICES,
        default="default",
        help=(
            "Timeout preset. `codex-heavy` raises the default timeout for slow Codex startup paths; "
            "`discovery-heavy` is a longer preset for interview/discovery prompts."
        ),
    )
    p.add_argument("--model", default=None, help="Override model for codex exec.")
    p.add_argument("--profile", default=None, help="Codex config profile name.")
    p.add_argument(
        "--codex-fallback-profile",
        default="d",
        help=(
            "Auto-retry profile for Codex when active profile/model rejects reasoning.summary "
            "(default: d). Set empty string to disable."
        ),
    )
    p.add_argument(
        "--codex-home",
        default=None,
        help="Set CODEX_HOME. This replaces the full Codex home; live Codex runs need authenticated state in the selected home.",
    )
    p.add_argument("--codex-bin", default=None, help="Override codex CLI path.")
    p.add_argument("--openai-bin", default=None, help="Override openai CLI path.")
    p.add_argument(
        "--codex-output-format",
        choices=["text", "json"],
        default="text",
        help="Codex output format (default: text).",
    )
    p.add_argument(
        "--openai-output-format",
        choices=["text", "json", "stream-json"],
        default="text",
        help="OpenAI output format (default: text).",
    )
    p.add_argument(
        "--codex-settings",
        default=None,
        help="DEPRECATED: plain `codex` runner was removed. Use --codex-kimi-settings / --codex-zai-settings.",
    )
    p.add_argument(
        "--codex-kimi-settings",
        default="kimi_settings.json",
        help="Settings JSON used by runner `codex-kimi` (default: kimi_settings.json).",
    )
    p.add_argument(
        "--codex-zai-settings",
        default="zai_settings.json",
        help="Settings JSON used by runner `codex-zai` (default: zai_settings.json).",
    )
    p.add_argument(
        "--codex-kimi-command",
        default="codex-kimi",
        help="Interactive shell command used for runner `codex-kimi` (default: codex-kimi).",
    )
    p.add_argument(
        "--codex-zai-command",
        default="codex-zai",
        help="Interactive shell command used for runner `codex-zai` (default: codex-zai).",
    )
    p.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra flag to pass to codex CLI (repeatable; supports `--codex-arg --flag`).",
    )
    p.add_argument(
        "--openai-arg",
        action="append",
        default=[],
        help="Extra flag to pass to openai CLI (repeatable; supports `--openai-arg --flag`).",
    )
    p.add_argument(
        "--capture-jsonl",
        action="store_true",
        help="Capture Codex JSONL event stream (--json). Auto-enabled when deterministic checks or budgets are present; required for --dual-run.",
    )
    p.add_argument("--reports-dir", default="Infrastructure/artifacts/skills", help="Base directory for eval reports.")
    p.add_argument("--scorecard-out", default=None, help="Optional explicit path for merged scorecard JSON.")
    p.add_argument("--junit-out", default=None, help="Optional explicit path for JUnit XML output (default: <run>/junit.xml).")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--tier2-mode",
        choices=["warn", "fail", "off"],
        default="warn",
        help="How to treat tier-2 findings (rubric/efficiency budgets).",
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


def _resolve_path(path_like: str, *, base: Path) -> Path:
    p = Path(path_like).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (base / p).resolve()


def _make_relative(path: Optional[Path], base: Path) -> str:
    """Convert absolute path to relative path from base, or return as-is if not possible."""
    if path is None:
        return ""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


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


def _print_case_listing(cases: Sequence[EvalCase]) -> None:
    print("Available eval cases:")
    for case in cases:
        category = case.category or "uncategorized"
        smoke = case.smoke_mode or "-"
        eval_modes = ",".join(case.eval_modes) if case.eval_modes else "auto"
        timeout_profile = case.timeout_profile or "-"
        timeout_sec = (
            f"{case.timeout_sec:g}" if isinstance(case.timeout_sec, (int, float)) else "-"
        )
        print(
            f"- {case.id} [{category}] "
            f"(prepend_skill={str(case.prepend_skill).lower()}, smoke_mode={smoke}, eval_modes={eval_modes}, "
            f"timeout_profile={timeout_profile}, timeout_sec={timeout_sec})"
        )
        print(f"  name: {case.name}")


def _contains_any(text: str, patterns: Sequence[str]) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in patterns)


def _extract_first_question(text: str, patterns: Sequence[str], fallback: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split())
    return fallback


def run_discovery_smoke(
    *,
    skill_md_path: Path,
    skill_dir: Path,
    case: EvalCase,
    output_last_message_path: Path,
) -> Tuple[int, str, str, List[str]]:
    """
    Fast, deterministic smoke check for discovery-first-turn behavior.

    This bypasses external model execution and verifies that the skill contract
    encodes the expected interview UX. It emits a contract-derived first-turn
    response so normal acceptance assertions can run against it.
    """

    warnings: List[str] = [
        "discovery-smoke emitted a contract-derived response; this is a fast smoke check, not live model behavior."
    ]

    skill_text = _read_text(skill_md_path)
    discovery_ref = skill_dir / "references" / "discovery-interview.md"
    discovery_text = _read_text(discovery_ref) if discovery_ref.exists() else ""

    missing: List[str] = []
    if "## Discovery interview" not in skill_text:
        missing.append("SKILL.md missing discovery interview section")
    if not _contains_any(
        skill_text,
        [
            "ask one round at a time",
            "one round at a time",
        ],
    ):
        missing.append("SKILL.md missing one-round-at-a-time guidance")
    if not _contains_any(
        skill_text,
        [
            "plain-language question",
            "plain language question",
        ],
    ):
        missing.append("SKILL.md missing plain-language question guidance")
    if not _contains_any(
        skill_text,
        [
            "why the round matters",
            "explain why the round matters",
            "why this matters",
        ],
    ):
        missing.append("SKILL.md missing why-this-matters guidance")
    if not _contains_any(
        skill_text,
        [
            "avoid dumping the whole interview plan at once",
            "avoid dumping the full interview plan at once",
        ],
    ):
        missing.append("SKILL.md missing no-full-plan-dump guidance")
    if not discovery_text:
        missing.append("discovery-interview.md not found")
    else:
        if "## Request user input mini-templates" not in discovery_text:
            missing.append("discovery-interview.md missing mini-templates section")
        if "## Copy paste payload examples" not in discovery_text:
            missing.append("discovery-interview.md missing payload examples section")
        if not _contains_any(
            discovery_text,
            [
                "what should this skill help you do?",
                "what kind of help should this skill provide?",
                "which documentation surface should we improve first?",
                "which documentation surface should this update target first?",
                "what should this docs work help you do?",
            ],
        ):
            missing.append("discovery-interview.md missing intuitive round-1 question")

    smoke_mode = case.smoke_mode or "discovery-round-one"
    round_one_question = _extract_first_question(
        discovery_text,
        patterns=[
            r"which documentation surface should(?: we improve first| this update target first)?\?",
            r"what should this docs work help you do\?",
            r"what should this skill help you do\?",
            r"what kind of help should this skill provide\?",
        ],
        fallback="What should this work help you do?",
    )

    if smoke_mode == "discovery-round-one":
        response = "\n".join(
            [
                "## Inputs",
                "- Missing: the exact target surface, primary reader, and job-to-be-done for this documentation work.",
                "- Why this matters: keeping the goal clear prevents scope creep and makes the later validation and ownership decisions more reliable.",
                "",
                "## Outputs",
                "- After discovery confirms the goal, return a tight docs plan or patch scoped to the right surface.",
                "",
                "## Next step",
                f"- Round 1 question: {round_one_question}",
                "",
                "## Failure mode",
                "- Do not draft or rewrite the docs yet when the workflow is still underspecified; finish round 1 first.",
            ]
        )
    elif smoke_mode == "discovery-round-six":
        if "## Round 6: Confirmation" not in discovery_text:
            missing.append("discovery-interview.md missing round-6 confirmation section")
        if not _contains_any(
            discovery_text,
            [
                "does this capture it",
                "does this capture the docs work well enough for me to implement",
                "anything to add or change before i implement it",
                "anything to add or change before i build it",
            ],
        ):
            missing.append("discovery-interview.md missing explicit confirmation question guidance")
        primary_confirmation = _extract_first_question(
            discovery_text,
            patterns=[
                r"does this capture[^?]*\?",
                r"ready to implement\?",
            ],
            fallback="Does this capture the work well enough for me to implement?",
        )
        secondary_confirmation = _extract_first_question(
            discovery_text,
            patterns=[
                r"anything to add or change before i (?:implement|build) it\?",
            ],
            fallback="Anything to add or change before I implement it?",
        )
        response = "\n".join(
            [
                "## Inputs",
                "- No major discovery gaps remain; this turn is for confirmation before implementation starts.",
                "",
                "## Outputs",
                "- Provide a compact docs work summary and wait for confirmation before making edits.",
                "",
                "## Next step",
                "- Ask for confirmation before implementation begins.",
                "",
                "## Failure mode",
                "- Do not assume approval from silence; ask for confirmation before implementing.",
                "",
                "## Skill Summary: docs-expert",
                "",
                "**Goal:** Help audit or rewrite documentation with a clear target surface, reader, and verification path.",
                "**Trigger:** natural requests about improving README, docs, runbooks, or in-code documentation.",
                "**Arguments:** target doc path or surface, audience, source of truth, and validation expectations",
                "",
                "**Process:**",
                "1. Confirm the target documentation surface and audience.",
                "2. Confirm the governing source of truth and constraints.",
                "3. Confirm the validation and handoff expectations.",
                "4. Return a concise docs summary and wait for approval to implement.",
                "",
                "**Inputs:** target doc surface, audience, source material, and constraints",
                "**Outputs:** compact docs summary plus the agreed implementation path",
                "**Dependencies:** none required for the smoke example",
                "**Guardrails:** avoid inventing commands or policy and do not implement before confirmation",
                "",
                "Assumptions: this is a docs workflow summary and not the final documentation patch.",
                "",
                primary_confirmation,
                secondary_confirmation,
            ]
        )
    else:
        response = "\n".join(
            [
                "## Inputs",
                "- Missing: a supported smoke mode.",
                "",
                "## Outputs",
                "- None until the smoke mode is corrected.",
                "",
                "## Next step",
                "- Correct the smoke mode and rerun the eval.",
                "",
                "## Failure mode",
                "- Unsupported discovery smoke mode.",
            ]
        )
    output_last_message_path.write_text(response, encoding="utf-8")

    stderr = ""
    if missing:
        stderr = "discovery-smoke contract gaps: " + "; ".join(missing)
        warnings.append(stderr)
        return 2, response, stderr, warnings

    if case.smoke_mode and case.smoke_mode not in {"discovery-round-one", "discovery-round-six"}:
        msg = f"Unsupported smoke_mode for discovery-smoke runner: {case.smoke_mode}"
        warnings.append(msg)
        return 2, response, msg, warnings

    return 0, response, stderr, warnings


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Run the full skill evaluation workflow from parsed CLI arguments, execute selected runners against eval cases, and write evaluation reports.

    This function parses and validates CLI arguments (or the provided argv list), loads the skill and eval cases, selects and runs configured runners for each case (including deterministic trace evaluation when enabled), aggregates per-runner and per-case results, emits artifacts (reports, scorecard, junit, release manifest), and determines an overall pass/fail decision.

    Parameters:
        argv (Optional[Sequence[str]]): Optional list of CLI arguments to parse instead of sys.argv[1:].

    Returns:
        int: Exit code: `0` when required gates pass; `1` for configuration/IO/preflight errors; `2` when evaluation gates fail.
    """
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    normalized_argv = _rewrite_dash_prefixed_codex_args(raw_argv)
    args = build_arg_parser().parse_args(normalized_argv)

    if args.dual_run and args.runners:
        print("ERROR: --dual-run cannot be combined with --runners. Choose one mode.", file=sys.stderr)
        return 1
    if args.smoke and args.dual_run:
        print("ERROR: --smoke cannot be combined with --dual-run.", file=sys.stderr)
        return 1
    if args.smoke and args.runners:
        print("ERROR: --smoke cannot be combined with --runners. Use one shortcut or the explicit runner list.", file=sys.stderr)
        return 1
    if args.smoke and args.runner != "codex":
        print("ERROR: --smoke cannot be combined with an explicit non-default --runner. Use one or the other.", file=sys.stderr)
        return 1
    if args.codex_settings:
        print(
            "ERROR: --codex-settings is deprecated because plain `codex` runner was removed. "
            "Use --codex-kimi-settings or --codex-zai-settings.",
            file=sys.stderr,
        )
        return 1

    skill_md = _resolve_skill_md_path(args.path)
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found at: {skill_md}", file=sys.stderr)
        return 1

    skill_dir = skill_md.parent
    skill_frontmatter = load_skill_frontmatter(skill_md)
    skill_name = str(skill_frontmatter.get("name") or "").strip()
    if not skill_name:
        print(f"ERROR: SKILL.md frontmatter missing valid `name`: {skill_md}", file=sys.stderr)
        return 1

    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        print(f"ERROR: Missing evals file: {evals_path}", file=sys.stderr)
        return 1

    try:
        cases = load_evals(evals_path)
        neutral_baseline_approvals = load_neutral_baseline_approvals(evals_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    case_filters = _parse_csv_args(args.case)
    category_filters = _parse_csv_args(args.category)
    try:
        cases = _filter_cases(cases, case_filters=case_filters, categories=category_filters)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    cases = _filter_cases_for_eval_mode(cases, eval_mode=args.eval_mode)

    if args.list_cases:
        _print_case_listing(cases)
        return 0
    if not cases:
        print(f"ERROR: No eval cases matched the selected filters and eval mode `{args.eval_mode}`.", file=sys.stderr)
        return 1

    workspace_root = Path(args.workspace).expanduser().resolve() if args.workspace else _guess_repo_root(skill_dir)
    codex_home = Path(args.codex_home).expanduser().resolve() if args.codex_home else None
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and not codex_bin.exists():
        print(f"ERROR: --codex-bin not found: {codex_bin}", file=sys.stderr)
        return 1
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and not codex_bin.exists():
        print(f"ERROR: --codex-bin not found: {codex_bin}", file=sys.stderr)
        return 1
    openai_bin = Path(args.openai_bin).expanduser() if args.openai_bin else None
    if openai_bin and not openai_bin.exists():
        print(f"ERROR: --openai-bin not found: {openai_bin}", file=sys.stderr)
        return 1

    if args.runners:
        try:
            selected_runners = _parse_runners(args.runners)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    elif args.dual_run:
        selected_runners = ["codex", "codex-kimi"]
    elif args.smoke:
        selected_runners = ["discovery-smoke"]
    else:
        selected_runners = [args.runner]
    codex_fallback_profile = str(args.codex_fallback_profile or "").strip() or None
    codex_kimi_command = str(args.codex_kimi_command or "").strip() or "codex-kimi"
    codex_zai_command = str(args.codex_zai_command or "").strip() or "codex-zai"

    # Smoke-profile routing:
    # - For discovery-smoke runs, prefer cases that declare a smoke_mode.
    # - For live/model runners, ignore only smoke-only discovery contract cases.
    smoke_runners_only = bool(selected_runners) and all(r == "discovery-smoke" for r in selected_runners)
    has_smoke_cases = any(c.smoke_mode for c in cases)
    if smoke_runners_only and has_smoke_cases:
        cases = [c for c in cases if c.smoke_mode]
    elif not smoke_runners_only and has_smoke_cases:
        cases = [c for c in cases if not _is_smoke_only_case(c)]

    capture_jsonl = bool(
        args.capture_jsonl
        or any((c.deterministic_checks or c.budgets) for c in cases)
        or (args.eval_mode == "release" and "codex" in selected_runners)
    )

    if "codex" in selected_runners and args.dual_run and not capture_jsonl:
        print("ERROR: --dual-run requires --capture-jsonl for deterministic Codex checks.", file=sys.stderr)
        return 1

    codex_kimi_settings: Optional[Path] = None
    if "codex-kimi" in selected_runners:
        if codex_kimi_command == "codex":
            codex_kimi_settings = _resolve_path(args.codex_kimi_settings, base=workspace_root)
            if not codex_kimi_settings.exists():
                print(
                    f"ERROR: codex-kimi settings file not found: {codex_kimi_settings} "
                    "(override with --codex-kimi-settings)",
                    file=sys.stderr,
                )
                return 1
        else:
            candidate = _resolve_path(args.codex_kimi_settings, base=workspace_root)
            if candidate.exists():
                codex_kimi_settings = candidate

    codex_zai_settings: Optional[Path] = None
    if "codex-zai" in selected_runners:
        if codex_zai_command == "codex":
            codex_zai_settings = _resolve_path(args.codex_zai_settings, base=workspace_root)
            if not codex_zai_settings.exists():
                print(
                    f"ERROR: codex-zai settings file not found: {codex_zai_settings} "
                    "(override with --codex-zai-settings)",
                    file=sys.stderr,
                )
                return 1
        else:
            candidate = _resolve_path(args.codex_zai_settings, base=workspace_root)
            if candidate.exists():
                codex_zai_settings = candidate

    preflight_errors: List[str] = []
    preflight_warnings: List[str] = []
    if "codex" in selected_runners:
        if not (workspace_root / ".git").exists() and not _has_skip_git_repo_check(args.codex_arg):
            preflight_warnings.append(
                "Workspace does not appear to be a trusted git repository. "
                "Codex may fail with 'Not inside a trusted directory'. "
                "If this is an ephemeral directory, add --codex-arg=--skip-git-repo-check."
            )
        auth_errors, auth_warnings = _preflight_codex_live_runner(
            workspace_root=workspace_root,
            codex_bin=codex_bin,
            codex_home=codex_home,
        )
        preflight_errors.extend(auth_errors)
        preflight_warnings.extend(auth_warnings)

    if preflight_errors:
        for message in preflight_errors:
            print(f"ERROR: {message}", file=sys.stderr)
        for message in preflight_warnings:
            print(f"WARNING: {message}", file=sys.stderr)
        return 1

    reports_root = Path(args.reports_dir).expanduser().resolve() / skill_name
    reports_root.mkdir(parents=True, exist_ok=True)
    reports_base: Optional[Path] = None
    run_id = ""
    for _ in range(8):
        candidate = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        candidate_path = reports_root / candidate
        try:
            candidate_path.mkdir(parents=False, exist_ok=False)
            reports_base = candidate_path
            run_id = candidate
            break
        except FileExistsError:
            continue
    if reports_base is None or not run_id:
        print("ERROR: unable to allocate unique report directory run_id", file=sys.stderr)
        return 1
    git_meta = _git_metadata(skill_dir)


    readiness_summary: Dict[str, int] = {state: 0 for state in sorted(_READINESS_STATE_CHOICES)}
    readiness_summary["unknown"] = 0
    round_state_summary: Dict[str, int] = {state: 0 for state in sorted(_ROUND_STATE_CHOICES)}
    round_state_summary["unknown"] = 0
    comparison_review_paths: List[str] = []
    used_neutral_baseline_approvals: Set[str] = set()

    summary: Dict[str, Any] = {
        "schema_version": "2.1",
        "tool": "run_skill_evals",
        "generated_at": _utc_now_iso(),
        "skill": skill_name,
        "skill_path": _make_relative(skill_dir, workspace_root),
        "skill_release": {
            "name": skill_name,
            "version": str(skill_frontmatter.get("version") or "0.0.0+local"),
            "compatibility": skill_frontmatter.get("compatibility") or "codex",
            "release_channel": skill_frontmatter.get("release_channel") or "local",
            "schema_version": str(skill_frontmatter.get("schema_version") or "1"),
            "source_commit": git_meta.get("commit"),
            "source_branch": git_meta.get("branch"),
        },
        "workspace_root": str(workspace_root),
        "runner_mode": ",".join(selected_runners),
        "eval_mode": args.eval_mode,
        "tier2_mode": args.tier2_mode,
        "run_id": run_id,
        "case_filters": case_filters,
        "category_filters": category_filters,
        "timeout_profile": args.timeout_profile,
        "timeout_sec": _eval_timeout_seconds(timeout_sec=args.timeout_sec, timeout_profile=args.timeout_profile),
        "capture_jsonl": capture_jsonl,
        "cases": [],
        "passed": True,
        "tier1_failures": 0,
        "tier2_findings": 0,
        "preflight_warnings": preflight_warnings,
        "readiness_summary": readiness_summary,
        "round_state_summary": round_state_summary,
        "neutral_baseline_approvals_used": [],
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
        case_timeout_sec, case_timeout_profile = _resolve_case_timeout(
            c,
            cli_timeout_sec=args.timeout_sec,
            cli_timeout_profile=args.timeout_profile,
        )
        comparison_review_artifact = _resolve_optional_case_artifact_path(case_dir, c.comparison_review_artifact, workspace_root)
        neutral_baseline_approval: Optional[Dict[str, Any]] = None
        if c.baseline_type == "neutral_repo_baseline":
            approval_id = c.neutral_baseline_approval_id or ""
            neutral_baseline_approval = neutral_baseline_approvals.get(approval_id)
            if neutral_baseline_approval is None:
                print(
                    "ERROR: case "
                    f"{c.id} references missing neutral_baseline_approval_id={approval_id!r} in {evals_path}",
                    file=sys.stderr,
                )
                return 1

        case_tier1_failures: List[str] = []
        case_tier2_findings: List[str] = []
        case_warnings: List[str] = []
        runner_records: Dict[str, Any] = {}

        for runner_name in selected_runners:
            runner_dir = case_dir / runner_name
            runner_dir.mkdir(parents=True, exist_ok=True)

            output_path = runner_dir / "output_last_message.txt"
            jsonl_path = (runner_dir / "codex_events.jsonl") if (runner_name == "codex" and capture_jsonl) else None

            if runner_name in {"codex-kimi", "codex-zai"}:
                if runner_name == "codex-kimi":
                    runner_settings = codex_kimi_settings
                    runner_command = codex_kimi_command
                elif runner_name == "codex-zai":
                    runner_settings = codex_zai_settings
                    runner_command = codex_zai_command
                rc, stdout, stderr = run_alt_codex_exec(
                    workspace_root=workspace_root,
                    prompt=composed_prompt,
                    output_last_message_path=output_path,
                    codex_bin=codex_bin,
                    output_format=args.codex_output_format,
                    settings_path=runner_settings,
                    cli_command=runner_command,
                    timeout_sec=case_timeout_sec,
                    timeout_profile=case_timeout_profile,
                    extra_codex_args=args.codex_arg or None,
                )
                runner_exec_warnings: List[str] = []
            elif runner_name == "openai":
                rc, stdout, stderr = run_openai_exec(
                    workspace_root=workspace_root,
                    prompt=composed_prompt,
                    output_last_message_path=output_path,
                    openai_bin=openai_bin,
                    output_format=args.openai_output_format,
                    timeout_sec=case_timeout_sec,
                    timeout_profile=case_timeout_profile,
                    extra_openai_args=args.openai_arg or None,
                )
                runner_exec_warnings = []
            elif runner_name == "discovery-smoke":
                rc, stdout, stderr, runner_exec_warnings = run_discovery_smoke(
                    skill_md_path=skill_md,
                    skill_dir=skill_dir,
                    case=c,
                    output_last_message_path=output_path,
                )
            else:
                rc, stdout, stderr, runner_exec_warnings = run_codex_exec(
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
                    timeout_sec=case_timeout_sec,
                    timeout_profile=case_timeout_profile,
                    extra_codex_args=args.codex_arg or None,
                    fallback_profile=codex_fallback_profile,
                )

            runner_dir.mkdir(parents=True, exist_ok=True)
            (runner_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")
            (runner_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")

            output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            runner_dir.mkdir(parents=True, exist_ok=True)
            (runner_dir / "final.txt").write_text(output_text, encoding="utf-8")

            runner_tier1_failures: List[str] = []
            runner_tier2_findings: List[str] = []
            runner_warnings: List[str] = list(runner_exec_warnings)
            runner_metrics: Dict[str, Any] = {}
            events: Optional[List[Dict[str, Any]]] = None

            if rc != 0:
                runner_tier1_failures.append(f"{runner_name} returned non-zero exit code: {rc}")
                if runner_name == "codex" and _is_codex_untrusted_repo_error(stderr):
                    runner_warnings.append(
                        "Codex rejected this workspace as untrusted. "
                        "Use a trusted git repo as --workspace, or pass "
                        "--codex-arg=--skip-git-repo-check for ephemeral temp directories."
                    )

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
            acceptance_skip_reason = _acceptance_skip_reason(exit_code=rc, output_text=output_text)

            if acceptance_skip_reason is not None:
                runner_warnings.append(acceptance_skip_reason)
            else:
                if schema_path and runner_name == "codex":
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:  # noqa: BLE001
                        runner_tier1_failures.append(f"expected JSON output (schema used), but parsing failed: {e}")
                    else:
                        used_json_assertions = True
                elif runner_name in {"codex-kimi", "codex-zai"} and args.codex_output_format == "json":
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:  # noqa: BLE001
                        runner_tier1_failures.append(f"expected JSON output (Codex json format), but parsing failed: {e}")
                    else:
                        used_json_assertions = True
                elif runner_name == "openai" and args.openai_output_format == "json":
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:  # noqa: BLE001
                        runner_tier1_failures.append(f"expected JSON output (OpenAI json format), but parsing failed: {e}")
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
                    "dir": _make_relative(runner_dir, workspace_root),
                    "final": _make_relative(runner_dir / "final.txt", workspace_root),
                    "stdout": _make_relative(runner_dir / "stdout.txt", workspace_root),
                    "stderr": _make_relative(runner_dir / "stderr.txt", workspace_root),
                    "jsonl": _make_relative(jsonl_path, workspace_root) if jsonl_path else None,
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
            "eval_modes": list(c.eval_modes) if c.eval_modes else None,
            "should_trigger": c.should_trigger,
            "prepend_skill": c.prepend_skill,
            "baseline_type": c.baseline_type,
            "comparison_inputs": dict(c.comparison_inputs) if c.comparison_inputs else None,
            "iteration_round_state": c.iteration_round_state,
            "metric_availability": c.metric_availability,
            "readiness_state": c.readiness_state,
            "comparison_review_artifact": comparison_review_artifact,
            "neutral_baseline_approval": neutral_baseline_approval,
            "timeout_profile": case_timeout_profile,
            "timeout_sec": _eval_timeout_seconds(
                timeout_sec=case_timeout_sec,
                timeout_profile=case_timeout_profile,
            ),
            "dir": _make_relative(case_dir, workspace_root),
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

        if c.readiness_state:
            summary["readiness_summary"][c.readiness_state] = summary["readiness_summary"].get(c.readiness_state, 0) + 1
        else:
            summary["readiness_summary"]["unknown"] += 1

        if c.iteration_round_state:
            summary["round_state_summary"][c.iteration_round_state] = (
                summary["round_state_summary"].get(c.iteration_round_state, 0) + 1
            )
        else:
            summary["round_state_summary"]["unknown"] += 1

        if comparison_review_artifact:
            comparison_review_paths.append(comparison_review_artifact)
        if c.neutral_baseline_approval_id:
            used_neutral_baseline_approvals.add(c.neutral_baseline_approval_id)

        if case_tier1_failed:
            any_tier1_failed = True
            summary["tier1_failures"] += 1
        if case_tier2_failed:
            any_tier2_failed = True
            summary["tier2_findings"] += 1

    summary["passed"] = (not any_tier1_failed) and (
        args.tier2_mode != "fail" or (not any_tier2_failed)
    )
    summary["decision"] = "pass" if summary["passed"] else "fail"
    summary["exit_code"] = 0 if summary["passed"] else 2

    summary_path = reports_base / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    scorecard_path = Path(args.scorecard_out).expanduser().resolve() if args.scorecard_out else (reports_base / "scorecard.json")
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(workspace_root))
        except ValueError:
            return str(p)

    summary["artifacts"] = {
        "reports_base": _rel(reports_base),
        "summary": _rel(summary_path),
        "scorecard": _rel(scorecard_path),
    }
    if comparison_review_paths:
        unique_paths = sorted(set(comparison_review_paths))
        summary["artifacts"]["comparison_review"] = unique_paths[0] if len(unique_paths) == 1 else unique_paths
    summary["neutral_baseline_approvals_used"] = sorted(used_neutral_baseline_approvals)
    release_manifest_path = reports_base / "release_manifest.json"
    junit_path = Path(args.junit_out).expanduser().resolve() if args.junit_out else (reports_base / "junit.xml")
    summary["artifacts"]["release_manifest"] = _rel(release_manifest_path)
    summary["artifacts"]["junit"] = _rel(junit_path)
    _write_junit_report(summary, junit_path)
    release_manifest = {
        "schema_version": "1.0",
        "tool": "run_skill_evals",
        "generated_at": summary["generated_at"],
        "skill": summary["skill_release"],
        "run": {
            "run_id": run_id,
            "eval_mode": args.eval_mode,
            "runner_mode": summary["runner_mode"],
            "tier2_mode": args.tier2_mode,
            "capture_jsonl": capture_jsonl,
            "readiness_summary": summary["readiness_summary"],
            "round_state_summary": summary["round_state_summary"],
            "neutral_baseline_approvals_used": summary["neutral_baseline_approvals_used"],
            "reports_base": _rel(reports_base),
        },
        "artifacts": summary["artifacts"],
    }
    release_manifest_path.write_text(json.dumps(release_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Skill evals: {skill_name}")
        print(f"Reports: {reports_base}")
        print(f"Scorecard: {scorecard_path}")
        print(f"Release manifest: {release_manifest_path}")
        print(f"JUnit: {junit_path}")
        print(f"Runner mode: {summary['runner_mode']}")
        print(f"Eval mode: {args.eval_mode}")
        if case_filters:
            print(f"Case filters: {', '.join(case_filters)}")
        if category_filters:
            print(f"Category filters: {', '.join(category_filters)}")
        print(f"Timeout profile: {args.timeout_profile}")
        print(f"Timeout seconds: {summary['timeout_sec']}")
        print(f"Tier-2 mode: {args.tier2_mode}")
        for w in summary.get("preflight_warnings", []):
            print(f"WARNING: {w}")
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

    return int(summary["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
