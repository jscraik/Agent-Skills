import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = ROOT / "Plugins/harness-engineering/scripts/check_pr_safety_trace.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_pr_safety_trace", CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_inline_json_raw_thread_id_is_rejected():
    checker = load_checker()
    text = (
        'Harness Engineering Trace\n'
        '{ "thread_id": "raw-thread-123", "he_trace_id": "hetrace_20260514_demo_abcd12", '
        '"provenance_source": "manual", "provenance_status": "found", '
        '"redaction_status": "safe_summary" }\n'
    )

    result = checker.validate_text(Path("sample.md"), text)

    assert result["status"] == "fail"
    assert any(
        finding["message"] == "raw local Codex/session provenance appears in public trace text"
        for finding in result["findings"]
    )


def test_inline_json_hash_thread_id_is_allowed():
    checker = load_checker()
    text = (
        'Harness Engineering Trace\n'
        '{ "thread_id": "hash:abcdef", "he_trace_id": "hetrace_20260514_demo_abcd12", '
        '"provenance_source": "manual", "provenance_status": "found", '
        '"redaction_status": "safe_summary" }\n'
    )

    result = checker.validate_text(Path("sample.md"), text)

    assert result["status"] == "pass"
    assert result["findings"] == []
