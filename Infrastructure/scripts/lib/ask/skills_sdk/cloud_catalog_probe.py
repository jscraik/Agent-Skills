from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable


DEFAULT_CATALOG_URL = "https://ollama.com/api/tags"
MAX_CATALOG_BYTES = 5 * 1024 * 1024
UrlOpen = Callable[..., Any]


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _safe_result(result_class: str, **fields: object) -> dict[str, object]:
    result: dict[str, object] = {
        "result_class": result_class,
        "network_accessed": False,
        "http_status": None,
        "catalog_digest": None,
        "matched_model": None,
        "match_count": None,
        "secret_value_observed": False,
        "secret_not_observed": True,
        "generation_performed": False,
        "provider_invoked": False,
        "codex_exec_invoked": False,
    }
    result.update(fields)
    return result


def _catalog_names(payload: object) -> list[str] | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        return None
    names: list[str] = []
    for row in payload["models"]:
        if not isinstance(row, dict):
            return None
        name = row.get("name") or row.get("model")
        if not isinstance(name, str) or not name:
            return None
        names.append(name)
    return names


def _is_expected_catalog_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    expected = urllib.parse.urlparse(DEFAULT_CATALOG_URL)
    return (
        parsed.scheme == "https"
        and parsed.netloc == expected.netloc
        and parsed.path == expected.path
        and parsed.params == ""
        and parsed.query == ""
        and parsed.fragment == ""
    )


def _fetch_catalog(
    request: urllib.request.Request, timeout_s: int, opener: UrlOpen,
) -> tuple[int | None, bytes | None, dict[str, object] | None]:
    try:
        with opener(request, timeout=timeout_s) as response:
            final_url = response.geturl() if hasattr(response, "geturl") else request.full_url
            if final_url != DEFAULT_CATALOG_URL:
                return None, None, _safe_result("redirect_rejected", network_accessed=True, http_status=None)
            status = int(response.getcode())
            body = response.read(MAX_CATALOG_BYTES + 1)
    except urllib.error.HTTPError as exc:
        return None, None, _safe_result("http_failure", network_accessed=True, http_status=exc.code)
    except (TimeoutError, socket.timeout):
        return None, None, _safe_result("timeout", network_accessed=True, http_status=None)
    except (OSError, urllib.error.URLError):
        return None, None, _safe_result("network_failure", network_accessed=True, http_status=None)
    return status, body, None


def _classify_catalog(body: bytes, status: int, selected_model: str) -> dict[str, object]:
    if status < 200 or status >= 300:
        return _safe_result("http_failure", network_accessed=True, http_status=status)
    if len(body) > MAX_CATALOG_BYTES:
        return _safe_result("payload_too_large", network_accessed=True, http_status=status)
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _safe_result("malformed_json", network_accessed=True, http_status=status)
    names = _catalog_names(payload)
    if names is None:
        return _safe_result("malformed_catalog", network_accessed=True, http_status=status)
    matches = [name for name in names if name == selected_model]
    common = {
        "network_accessed": True,
        "http_status": status,
        "catalog_digest": _digest(payload),
        "match_count": len(matches),
    }
    if not matches:
        return _safe_result("model_missing", matched_model=None, **common)
    if len(matches) != 1:
        return _safe_result("model_ambiguous", matched_model=None, **common)
    return _safe_result("pass", matched_model=matches[0], **common)


def probe_catalog(
    *,
    url: str,
    selected_model: str,
    timeout_s: int,
    opener: UrlOpen = urllib.request.urlopen,
) -> dict[str, object]:
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        return _safe_result("auth_missing", network_accessed=False, http_status=None)
    if not _is_expected_catalog_url(url):
        return _safe_result("invalid_catalog_url", network_accessed=False, http_status=None)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )
    request.add_unredirected_header("Authorization", f"Bearer {api_key}")
    status, body, failure = _fetch_catalog(request, timeout_s, opener)
    if failure is not None:
        return failure
    assert status is not None and body is not None
    return _classify_catalog(body, status, selected_model)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe the authenticated Ollama Cloud model catalog.")
    parser.add_argument("--url", default=DEFAULT_CATALOG_URL)
    parser.add_argument("--model", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds < 1:
        raise SystemExit("--timeout-seconds must be positive")
    result = probe_catalog(
        url=args.url,
        selected_model=args.model,
        timeout_s=args.timeout_seconds,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["result_class"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
