"""Minimal safe wrapper around ``xml.etree.ElementTree``.

The repo only needs a small subset of the upstream ``defusedxml.ElementTree``
surface. This wrapper rejects XML payloads that contain DTD or ENTITY
declarations before delegating to the standard library parser.
"""

from __future__ import annotations

import importlib
import io
import re
from pathlib import Path
from typing import Any

_ET = importlib.import_module("xml.etree.ElementTree")
_UNSAFE_DECL_RE = re.compile(br"<!DOCTYPE|<!ENTITY", re.IGNORECASE)

ParseError = _ET.ParseError
Element = _ET.Element
SubElement = _ET.SubElement
ElementTree = _ET.ElementTree
QName = _ET.QName
TreeBuilder = _ET.TreeBuilder
tostring = _ET.tostring
indent = _ET.indent
register_namespace = _ET.register_namespace


def _ensure_safe_xml(data: bytes) -> None:
    if _UNSAFE_DECL_RE.search(data):
        raise ParseError("DTD and ENTITY declarations are not allowed")


def _read_source_bytes(source: Any) -> bytes:
    if isinstance(source, (str, bytes, Path)):
        return Path(source).read_bytes()

    if hasattr(source, "read"):
        cursor = source.tell() if hasattr(source, "tell") else None
        data = source.read()
        if cursor is not None and hasattr(source, "seek"):
            source.seek(cursor)
        if isinstance(data, str):
            return data.encode("utf-8")
        return data

    raise TypeError(f"Unsupported XML source: {type(source)!r}")


def XMLParser(*args: Any, **kwargs: Any) -> Any:
    return _ET.XMLParser(*args, **kwargs)


def parse(source: Any, parser: Any | None = None) -> Any:
    data = _read_source_bytes(source)
    _ensure_safe_xml(data)
    return _ET.parse(io.BytesIO(data), parser=parser)


def fromstring(text: bytes | str, parser: Any | None = None) -> Any:
    data = text.encode("utf-8") if isinstance(text, str) else text
    _ensure_safe_xml(data)
    return _ET.fromstring(data, parser=parser)


def XML(text: bytes | str, parser: Any | None = None) -> Any:
    return fromstring(text, parser=parser)


def __getattr__(name: str) -> Any:
    return getattr(_ET, name)

