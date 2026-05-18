from ask.envelope import ErrorCode, ErrorObject, ExitCode


ERROR_MAP = {
    ErrorCode.SUCCESS: ExitCode.SUCCESS,
    ErrorCode.ERR_RUNTIME: ExitCode.ERR_RUNTIME,
    ErrorCode.ERR_VALIDATION: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_PI_GUARD: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_PATH_TRAVERSAL: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_SCHEMA_INVALID: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_INVALID_HANDOFF: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_INVALID_STATE: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_INVALID_SCOPE: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_INVALID_PROJECTION_MODE: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_DEFERRED_PROJECTION_MODE: ExitCode.ERR_VALIDATION,
    ErrorCode.ERR_DEPENDENCY: ExitCode.ERR_DEPENDENCY,
    ErrorCode.ERR_CONFLICT: ExitCode.ERR_CONFLICT,
    ErrorCode.ERR_REDUNDANCY: ExitCode.ERR_CONFLICT,
    ErrorCode.ERR_AUTH: ExitCode.ERR_AUTH,
}


def exit_code_for_errors(errors: list[ErrorObject]) -> int:
    error_code = errors[0].code if errors else ErrorCode.ERR_RUNTIME
    return int(ERROR_MAP.get(error_code, ExitCode.ERR_RUNTIME))
