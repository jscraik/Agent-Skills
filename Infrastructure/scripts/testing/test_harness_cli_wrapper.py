from __future__ import annotations

import re
from pathlib import Path


WRAPPER = Path(__file__).resolve().parents[1] / "harness-cli.sh"


def test_harness_fallback_pin_is_the_approved_release() -> None:
    source = WRAPPER.read_text(encoding="utf-8")

    assert re.findall(r'FALLBACK_PACKAGE="@brainwav/coding-harness@([^\"]+)"', source) == [
        "0.15.0"
    ]
    assert source.count("@brainwav/coding-harness@") == 1
