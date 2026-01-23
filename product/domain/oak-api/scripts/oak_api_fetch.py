#!/usr/bin/env python3
"""
Minimal Oak Curriculum API fetch helper.

- Uses env var OAK_API_KEY (optional) for auth.
- Requires explicit header name via OAK_API_KEY_HEADER or --api-key-header.
- Supports offset/limit pagination.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Iterable, List, Tuple

DEFAULT_BASE_URL = "https://open-api.thenational.academy/api/v0"


def parse_params(items: Iterable[str]) -> List[Tuple[str, str]]:
    params: List[Tuple[str, str]] = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid param '{item}', expected key=value")
        key, value = item.split("=", 1)
        params.append((key, value))
    return params


def build_url(base_url: str, path: str, params: List[Tuple[str, str]]) -> str:
    base = base_url.rstrip("/")
    path_part = path if path.startswith("/") else f"/{path}"
    url = f"{base}{path_part}"
    if params:
        query = urllib.parse.urlencode(params, doseq=True)
        url = f"{url}?{query}"
    return url


def build_headers(api_key: str | None, header_name: str | None, prefix: str | None) -> dict:
    headers: dict = {"Accept": "application/json"}
    if api_key:
        if not header_name:
            raise ValueError(
                "OAK_API_KEY is set but no header name provided. "
                "Set OAK_API_KEY_HEADER (e.g., 'X-API-Key' or 'Authorization') "
                "or pass --api-key-header."
            )
        value = api_key
        if prefix:
            value = f"{prefix}{api_key}"
        headers[header_name] = value
    return headers


def fetch_json(url: str, headers: dict) -> object:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Oak Curriculum API data.")
    parser.add_argument("path", help="Endpoint path, e.g. /lessons/{lesson}/summary")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--param", action="append", default=[], help="Query param key=value")
    parser.add_argument("--paginate", action="store_true", help="Use offset/limit pagination")
    parser.add_argument("--limit", type=int, help="Page size when paginating")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--api-key-header", help="Header name for API key")
    parser.add_argument("--api-key-prefix", help="Prefix for API key (e.g., 'Bearer ')")

    args = parser.parse_args()

    api_key = os.environ.get("OAK_API_KEY")
    header_name = args.api_key_header or os.environ.get("OAK_API_KEY_HEADER")
    prefix = args.api_key_prefix or os.environ.get("OAK_API_KEY_PREFIX")

    try:
        params = parse_params(args.param)
        headers = build_headers(api_key, header_name, prefix)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.paginate and args.limit is None:
        print("error: --paginate requires --limit", file=sys.stderr)
        return 2

    if not args.paginate:
        url = build_url(args.base_url, args.path, params)
        data = fetch_json(url, headers)
        print(json.dumps(data, indent=2, ensure_ascii=True))
        return 0

    offset = args.offset
    pages = 0
    results: List[object] = []
    while pages < args.max_pages:
        page_params = list(params)
        page_params.append(("offset", str(offset)))
        page_params.append(("limit", str(args.limit)))
        url = build_url(args.base_url, args.path, page_params)
        data = fetch_json(url, headers)

        if isinstance(data, list):
            results.extend(data)
            if len(data) < args.limit:
                break
        else:
            results.append(data)
            break

        offset += args.limit
        pages += 1

    print(json.dumps(results, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
