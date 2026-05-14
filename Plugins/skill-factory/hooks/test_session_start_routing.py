#!/usr/bin/env python3
"""Tests for the Skill Factory SessionStart hook."""

from __future__ import annotations

import json

import session_start_routing


def test_context_mentions_canonical_sources_and_router() -> None:
    assert "canonical sources under Plugins/skill-factory/skills" in session_start_routing.CONTEXT
    assert "route_skillset.py with --skill-set skill-factory" in session_start_routing.CONTEXT


def test_main_emits_session_start_payload(capsys) -> None:
    session_start_routing.main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["continue"] is True
    assert payload["suppressOutput"] is True
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert payload["hookSpecificOutput"]["additionalContext"] == session_start_routing.CONTEXT
