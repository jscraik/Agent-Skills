from __future__ import annotations

from ask.envelope import CallResult, ErrorObject


def receipt_result(
    command: str,
    data_key: str,
    receipt: dict,
    *,
    blocked_statuses: set[str],
    fix_suggestion: str,
) -> CallResult:
    result = CallResult()
    result.metadata["command"] = command
    result.data[data_key] = {"status": receipt["status"], "receipt": receipt}
    if receipt["status"] in blocked_statuses:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=fix_suggestion,
            )
        )
    return result
