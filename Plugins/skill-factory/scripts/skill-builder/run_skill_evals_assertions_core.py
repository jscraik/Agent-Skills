from run_skill_evals_loading import *  # noqa: F403

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
        riteway = case.get("riteway") if isinstance(case.get("riteway"), dict) else None
        if riteway:
            chunks.append(
                "riteway_failure_report:\n"
                f"unit: {riteway.get('unit') or ''}\n"
                f"given: {riteway.get('given') or ''}\n"
                f"should: {riteway.get('should') or ''}\n"
                f"actual: {riteway.get('actual') or ''}\n"
                f"expected: {riteway.get('expected') or ''}\n"
                f"reproduce: {riteway.get('reproduce') or ''}"
            )
        if case.get("dir"):
            chunks.append(f"artifacts_dir:\n{case['dir']}")
        lines.append("    <system-out>")
        lines.append(html.escape("\n\n".join(chunks)))
        lines.append("    </system-out>")
        lines.append("  </testcase>")
    lines.append("</testsuite>")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mark_no_case_evidence_blocked(summary: Dict[str, Any]) -> bool:
    if summary.get("cases"):
        return False
    summary["blocked_class_summary"]["blocked_validation"] = (
        summary["blocked_class_summary"].get("blocked_validation", 0) + 1
    )
    summary["no_case_evidence"] = True
    return True


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
        bare_match = re.match(r"^(contains|not_contains|regex|not_regex)\s+(.+)$", s, flags=re.IGNORECASE)
        if bare_match:
            assertion_type = bare_match.group(1).lower()
            value = bare_match.group(2).strip()
            if value.startswith(("'", '"')):
                try:
                    parts = shlex.split(value)
                except ValueError as exc:
                    raise ValueError(f"Invalid quoted assertion value: {value!r}") from exc
                if len(parts) != 1:
                    raise ValueError(
                        f"Assertion shorthand expects one value for {assertion_type}, "
                        f"got {len(parts)} tokens: {value!r}"
                    )
                value = parts[0]
            return {"type": assertion_type, "value": value}
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


def _contains_text(haystack: str, needle: str) -> bool:
    return _normalized_match_text(needle) in _normalized_match_text(haystack)


def _normalized_match_text(value: str) -> str:
    return value.replace("`", "").replace("**", "").casefold()


def _normalize_text_field_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().casefold()).strip("_")


def _text_field_map(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\\s+", "", line)
        line = line.replace(chr(96), "").replace("**", "")
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = _normalize_text_field_key(key)
        if normalized_key:
            fields[normalized_key] = value.strip().strip("'\\\"")
    return fields


def _text_field_candidate_keys(assertion: Dict[str, Any]) -> List[str]:
    raw_fields = assertion.get("fields")
    candidates: List[str] = []
    if isinstance(raw_fields, list):
        candidates.extend(str(item) for item in raw_fields if str(item).strip())
    path = assertion.get("path") or assertion.get("field") or assertion.get("key")
    if isinstance(path, str) and path.strip():
        candidates.append(path)
    return candidates


def _evaluate_text_field_assertion(text: str, assertion: Dict[str, Any]) -> Optional[str]:
    t = str(assertion.get("type") or "")
    candidates = _text_field_candidate_keys(assertion)
    if not candidates:
        return f"{t} missing field/path"
    fields = _text_field_map(text)
    normalized_candidates = [_normalize_text_field_key(path) for path in candidates]
    present_key = next((key for key in normalized_candidates if key in fields), "")
    present = bool(present_key)
    path_label = "|".join(candidates)
    if t == "text_field_present":
        return None if present else f"text_field_present missing field: {path_label}"
    if t == "text_field_absent":
        return f"text_field_absent found field: {path_label}" if present else None
    if not present:
        return f"{t} missing field: {path_label}"
    got = fields[present_key]
    if t == "text_field_equals":
        expected = _to_text_blob(assertion.get("value", ""))
        if got.casefold() != expected.casefold():
            return f"text_field_equals failed at {path_label}: got={got!r} expected={expected!r}"
        return None
    if t == "text_field_in":
        values = assertion.get("values", assertion.get("value", []))
        if not isinstance(values, list):
            values = [values]
        expected_values = [_to_text_blob(value) for value in values]
        if got.casefold() not in {value.casefold() for value in expected_values}:
            return f"text_field_in failed at {path_label}: got={got!r} expected one of {expected_values!r}"
        return None
    return f"unsupported text field assertion type: {t!r}"


def _json_text_field_map(obj: Any) -> Dict[str, str]:
    fields: Dict[str, str] = {}

    def visit(value: Any, prefix: str = "") -> None:
        if isinstance(value, dict):
            for raw_key, child in value.items():
                key = str(raw_key)
                normalized_key = _normalize_text_field_key(key)
                dotted_key = f"{prefix}.{key}" if prefix else key
                normalized_dotted_key = _normalize_text_field_key(dotted_key)
                if not isinstance(child, (dict, list)):
                    text_value = _to_text_blob(child)
                    if normalized_key:
                        fields.setdefault(normalized_key, text_value)
                    if normalized_dotted_key:
                        fields.setdefault(normalized_dotted_key, text_value)
                visit(child, dotted_key)
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{prefix}[{index}]" if prefix else f"[{index}]")

    visit(obj)
    return fields


def _evaluate_json_text_field_assertion(obj: Any, assertion: Dict[str, Any]) -> Optional[str]:
    t = str(assertion.get("type") or "")
    candidates = _text_field_candidate_keys(assertion)
    if not candidates:
        return f"{t} missing field/path"
    fields = _json_text_field_map(obj)
    normalized_candidates = [_normalize_text_field_key(path) for path in candidates]
    present_key = next((key for key in normalized_candidates if key in fields), "")
    present = bool(present_key)
    path_label = "|".join(candidates)
    if t == "text_field_present":
        return None if present else f"text_field_present missing field: {path_label}"
    if t == "text_field_absent":
        return f"text_field_absent found field: {path_label}" if present else None
    if not present:
        return f"{t} missing field: {path_label}"
    got = fields[present_key]
    if t == "text_field_equals":
        expected = _to_text_blob(assertion.get("value", ""))
        if got.casefold() != expected.casefold():
            return f"text_field_equals failed at {path_label}: got={got!r} expected={expected!r}"
        return None
    if t == "text_field_in":
        values = assertion.get("values", assertion.get("value", []))
        if not isinstance(values, list):
            values = [values]
        expected_values = [_to_text_blob(value) for value in values]
        if got.casefold() not in {value.casefold() for value in expected_values}:
            return f"text_field_in failed at {path_label}: got={got!r} expected one of {expected_values!r}"
        return None
    return f"unsupported text field assertion type: {t!r}"


_EXPECTED_SIGNAL_STOPWORDS = {
    "about",
    "after",
    "against",
    "available",
    "before",
    "being",
    "between",
    "could",
    "does",
    "from",
    "into",
    "instead",
    "keeps",
    "names",
    "should",
    "that",
    "their",
    "them",
    "then",
    "this",
    "treats",
    "until",
    "when",
    "with",
    "without",
}

__all__ = [name for name in globals() if not name.startswith("__")]
