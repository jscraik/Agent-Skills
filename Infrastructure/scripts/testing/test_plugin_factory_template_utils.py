from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "_template_utils.py"
)

SPEC = importlib.util.spec_from_file_location("template_utils", MODULE_PATH)
if SPEC is None:
    raise RuntimeError(f"Unable to build import spec for {MODULE_PATH}")
if SPEC.loader is None:
    raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_key_value_parses_key_and_value() -> None:
    assert MODULE.parse_key_value("FOO=bar=baz") == ("FOO", "bar=baz")


def test_parse_key_value_rejects_missing_equals() -> None:
    with pytest.raises(MODULE.TemplateRenderError):
        MODULE.parse_key_value("NOVALUE")


def test_parse_key_value_rejects_invalid_key() -> None:
    with pytest.raises(MODULE.TemplateRenderError):
        MODULE.parse_key_value("not_upper=value")


def test_render_template_replaces_placeholders() -> None:
    rendered = MODULE.render_template(
        "Hello {{ NAME }}",
        {"NAME": "Jamie"},
    )
    assert rendered == "Hello Jamie"


def test_render_template_raises_on_missing_placeholder() -> None:
    with pytest.raises(MODULE.TemplateRenderError):
        MODULE.render_template("Hello {{ NAME }}", {})


def test_load_json_context_casts_values_to_strings(tmp_path: Path) -> None:
    context_path = tmp_path / "context.json"
    context_path.write_text('{"A": 1, "B": true}', encoding="utf-8")
    loaded = MODULE.load_json_context(context_path)
    assert loaded == {"A": "1", "B": "True"}
