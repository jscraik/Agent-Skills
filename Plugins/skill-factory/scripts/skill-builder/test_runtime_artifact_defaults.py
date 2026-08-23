#!/usr/bin/env python3
"""Prevent skill-quality tooling from regenerating tracked reports."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import refresh_benchmark_policy


class RuntimeArtifactDefaultTests(unittest.TestCase):
    def test_benchmark_refresh_defaults_are_runtime_owned(self) -> None:
        with patch.object(sys, "argv", ["refresh_benchmark_policy.py"]):
            args = refresh_benchmark_policy.parse_args()

        self.assertEqual(
            args.benchmark_json,
            ".tmp/agent-skills-artifacts/industry-benchmark-latest.json",
        )
        self.assertEqual(
            args.report_json,
            ".tmp/agent-skills-artifacts/benchmark-policy-refresh-report.json",
        )


if __name__ == "__main__":
    unittest.main()
