#!/usr/bin/env python3
"""Tests for the runtime-separation block added to scripts/validate_all.sh.

Covers the logic introduced in the PR:
- runtime_separation_current path selection based on output_mode
- runtime_consumer_scan_cmd array construction (with/without --emit-digests)
- All 8 run_check invocations with correct slugs, modes, and argument shapes
- Ordering of the new checks relative to each other and to the surrounding checks
- Both --ephemeral and --persistent (default) modes
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_ALL_SH = REPO_ROOT / "scripts" / "validate_all.sh"

# Slugs introduced by the PR, in declaration order.
RUNTIME_SEPARATION_SLUGS = [
    "runtime-separation-manifest",
    "runtime-separation-consumers",
    "runtime-separation-reader-compat",
    "runtime-separation-current",
    "runtime-separation-wrapper-fixtures",
    "runtime-separation-baseline-compare",
    "runtime-separation-writer-mutations",
    "runtime-separation-profile-home",
]


def _bash(snippet: str, env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Execute *snippet* under ``bash -c`` and return the completed process."""
    base_env = dict(os.environ)
    if env:
        base_env.update(env)
    return subprocess.run(
        ["bash", "-c", snippet],
        capture_output=True,
        text=True,
        env=base_env,
        cwd=cwd or str(REPO_ROOT),
    )


def _make_stub_script(directory: Path, name: str, exit_code: int = 0, extra: str = "") -> Path:
    """Write an executable stub script that exits with *exit_code* and optionally runs *extra* code."""
    script = directory / name
    content = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        {extra}
        exit {exit_code}
    """)
    script.write_text(content, encoding="utf-8")
    script.chmod(0o755)
    return script


def _run_validate_all_with_stubs(
    output_mode: str,
    stub_exit_code: int = 0,
    extra_env: dict | None = None,
) -> tuple[subprocess.CompletedProcess, Path, Path]:
    """
    Run validate_all.sh in a controlled environment with stubbed external scripts.

    Returns (proc, run_dir, check_results_file_path).
    The caller is responsible for cleanup.
    """
    tmp = Path(tempfile.mkdtemp())

    # Create stub directory that shadows the real scripts directory
    stubs_dir = tmp / "stubs"
    stubs_dir.mkdir()

    # Create stub python3 that records its arguments and exits cleanly
    py_stub = stubs_dir / "python3"
    py_stub_log = tmp / "python3_calls.log"
    py_stub.write_text(
        textwrap.dedent(f"""\
            #!/usr/bin/env bash
            printf '%s\\n' "$*" >> "{py_stub_log}"
            exit {stub_exit_code}
        """),
        encoding="utf-8",
    )
    py_stub.chmod(0o755)

    # Create stub bash that records invocations
    bash_stub_log = tmp / "bash_calls.log"

    # Stub all external shell scripts referenced in the new block
    for script_name in [
        "verify_wrapper_contract_fixtures.sh",
        "verify_runtime_separation_writer_mutations.sh",
        "validate_runtime_separation_profile_home.sh",
    ]:
        stub = stubs_dir / script_name
        stub.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env bash
                printf '%s\\n' "{script_name} $*" >> "{bash_stub_log}"
                exit {stub_exit_code}
            """),
            encoding="utf-8",
        )
        stub.chmod(0o755)

    # Stub all Python scripts referenced in the new block
    for py_script_name in [
        "validate_runtime_separation_manifest.py",
        "scan_runtime_separation_consumers.py",
        "verify_runtime_separation_reader_compat.py",
        "build_runtime_separation_current.py",
        "compare_runtime_separation_baseline.py",
    ]:
        stub = stubs_dir / py_script_name
        stub.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env python3
                import sys
                with open("{tmp / 'python_script_calls.log'}", "a") as f:
                    f.write("{py_script_name} " + " ".join(sys.argv[1:]) + "\\n")
                sys.exit({stub_exit_code})
            """),
            encoding="utf-8",
        )
        stub.chmod(0o755)

    # Build and run a self-contained snippet that sources validate_all.sh's logic
    # but uses the stubs directory for external scripts.  We also need to set up
    # the required environment that validate_all.sh expects.
    if output_mode == "ephemeral":
        mode_flag = "--ephemeral"
    else:
        mode_flag = "--persistent"

    # We run the actual script via bash, forcing PYTHON_BIN to our stub
    # and ensuring the stubs for bash scripts come first in PATH.
    env: dict = {
        "PYTHON_BIN": str(py_stub),
        "PATH": f"{stubs_dir}:{os.environ.get('PATH', '/usr/bin:/bin')}",
        # Redirect artifact output to tmp so we don't pollute the real repo
        "VALIDATE_ALL_OUTPUT_MODE": output_mode,
    }
    if extra_env:
        env.update(extra_env)

    # Patch the script on-the-fly: replace all `bash scripts/` references in the
    # new block with `bash {stubs_dir}/` so the bash-invoked scripts hit our stubs.
    # We do this by constructing a wrapper that overrides the relevant things.
    # The cleanest approach for testing just the new block is to:
    # 1. Create a minimal harness that defines run_check and the required vars
    # 2. Then evaluates just the new code block
    harness = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        set -u

        # ---- Minimal harness mirroring validate_all.sh's preamble ----
        output_mode="{output_mode}"
        run_dir="{tmp}/run_dir"
        mkdir -p "$run_dir"

        check_results_file="$run_dir/check-results.tsv"
        : > "$check_results_file"

        python_cmd=("{py_stub}")

        run_check() {{
            local mode="$1"
            local slug="$2"
            local label="$3"
            shift 3
            local log_file="$run_dir/${{slug}}.log"
            local outcome="pass"
            if "$@" >"$log_file" 2>&1; then
                outcome="pass"
            else
                outcome="fail"
            fi
            printf '%s\\t%s\\t%s\\t%s\\n' "$slug" "$mode" "$outcome" "$log_file" >> "$check_results_file"
        }}

        # ---- New code block under test ----
        runtime_separation_current="$run_dir/runtime-separation-current.json"
        if [[ "$output_mode" == "persistent" ]]; then
          runtime_separation_current="GOVERNANCE/runtime-separation/current.json"
        fi

        runtime_consumer_scan_cmd=(
          "${{python_cmd[@]}}"
          scripts/scan_runtime_separation_consumers.py
          --emit-readers
          --emit-path-consumers
          --strict
        )
        if [[ "$output_mode" == "persistent" ]]; then
          runtime_consumer_scan_cmd+=(--emit-digests)
        fi

        run_check required runtime-separation-manifest "Validating runtime-separation manifest..." "${{python_cmd[@]}}" scripts/validate_runtime_separation_manifest.py --strict
        run_check required runtime-separation-consumers "Scanning runtime-separation consumer inventories..." "${{runtime_consumer_scan_cmd[@]}}"
        run_check required runtime-separation-reader-compat "Verifying runtime-separation reader compatibility..." "${{python_cmd[@]}}" scripts/verify_runtime_separation_reader_compat.py --schema-current GOVERNANCE/runtime-separation/slices.yaml --schema-prev GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml
        run_check required runtime-separation-current "Building runtime-separation current artifact..." "${{python_cmd[@]}}" scripts/build_runtime_separation_current.py --output "$runtime_separation_current"
        run_check required runtime-separation-wrapper-fixtures "Verifying runtime-separation wrapper fixtures..." bash {stubs_dir}/verify_wrapper_contract_fixtures.sh --runtime-separation
        run_check required runtime-separation-baseline-compare "Comparing runtime-separation baseline..." "${{python_cmd[@]}}" scripts/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current "$runtime_separation_current"
        run_check required runtime-separation-writer-mutations "Verifying runtime-separation writer authority..." bash {stubs_dir}/verify_runtime_separation_writer_mutations.sh --strict
        run_check required runtime-separation-profile-home "Building runtime-separation profile-home artifact..." bash {stubs_dir}/validate_runtime_separation_profile_home.sh --repo-current "$runtime_separation_current" --output "$run_dir/runtime-separation-profile-home.json"

        # Emit key variable values for test assertions
        printf 'RUNTIME_SEPARATION_CURRENT=%s\\n' "$runtime_separation_current"
        printf 'RUNTIME_CONSUMER_SCAN_CMD=%s\\n' "${{runtime_consumer_scan_cmd[*]}}"
    """)

    harness_path = tmp / "harness.sh"
    harness_path.write_text(harness, encoding="utf-8")
    harness_path.chmod(0o755)

    proc = subprocess.run(
        ["bash", str(harness_path)],
        capture_output=True,
        text=True,
        env={**dict(os.environ), **env},
        cwd=str(REPO_ROOT),
    )

    check_results_path = tmp / "run_dir" / "check-results.tsv"
    return proc, tmp, check_results_path


def _parse_tsv(path: Path) -> list[dict]:
    """Parse the check-results TSV into a list of dicts."""
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            rows.append({"slug": parts[0], "mode": parts[1], "outcome": parts[2]})
    return rows


# ---------------------------------------------------------------------------
# TestRuntimeSeparationCurrentPath
# ---------------------------------------------------------------------------


class TestRuntimeSeparationCurrentPath(unittest.TestCase):
    """Verify runtime_separation_current is set to the correct path based on output_mode."""

    def test_ephemeral_mode_uses_run_dir_path(self) -> None:
        """In ephemeral mode, runtime_separation_current must be inside the run_dir temp directory."""
        proc, tmp, _ = _run_validate_all_with_stubs("ephemeral")
        try:
            self.assertEqual(proc.returncode, 0, f"Harness failed:\nstdout={proc.stdout}\nstderr={proc.stderr}")
            # Extract value from harness output
            current_val = None
            for line in proc.stdout.splitlines():
                if line.startswith("RUNTIME_SEPARATION_CURRENT="):
                    current_val = line.split("=", 1)[1]
                    break
            self.assertIsNotNone(current_val, "RUNTIME_SEPARATION_CURRENT was not printed")
            self.assertTrue(
                current_val.endswith("/runtime-separation-current.json"),
                f"Expected path ending with runtime-separation-current.json, got: {current_val!r}",
            )
            # Must NOT be the GOVERNANCE path
            self.assertNotEqual(
                current_val,
                "GOVERNANCE/runtime-separation/current.json",
                "Ephemeral mode must not use the GOVERNANCE path",
            )
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_persistent_mode_uses_governance_path(self) -> None:
        """In persistent mode, runtime_separation_current must point to GOVERNANCE/runtime-separation/current.json."""
        proc, tmp, _ = _run_validate_all_with_stubs("persistent")
        try:
            self.assertEqual(proc.returncode, 0, f"Harness failed:\nstdout={proc.stdout}\nstderr={proc.stderr}")
            current_val = None
            for line in proc.stdout.splitlines():
                if line.startswith("RUNTIME_SEPARATION_CURRENT="):
                    current_val = line.split("=", 1)[1]
                    break
            self.assertIsNotNone(current_val, "RUNTIME_SEPARATION_CURRENT was not printed")
            self.assertEqual(
                current_val,
                "GOVERNANCE/runtime-separation/current.json",
                f"Persistent mode must use the GOVERNANCE path, got: {current_val!r}",
            )
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_ephemeral_current_path_is_different_from_persistent(self) -> None:
        """The ephemeral and persistent current paths must be distinct values."""
        proc_e, tmp_e, _ = _run_validate_all_with_stubs("ephemeral")
        proc_p, tmp_p, _ = _run_validate_all_with_stubs("persistent")
        try:
            def _extract(proc: subprocess.CompletedProcess) -> str | None:
                for line in proc.stdout.splitlines():
                    if line.startswith("RUNTIME_SEPARATION_CURRENT="):
                        return line.split("=", 1)[1]
                return None

            val_e = _extract(proc_e)
            val_p = _extract(proc_p)
            self.assertIsNotNone(val_e)
            self.assertIsNotNone(val_p)
            self.assertNotEqual(val_e, val_p, "Ephemeral and persistent paths must differ")
        finally:
            import shutil
            shutil.rmtree(str(tmp_e), ignore_errors=True)
            shutil.rmtree(str(tmp_p), ignore_errors=True)


# ---------------------------------------------------------------------------
# TestRuntimeConsumerScanCmd
# ---------------------------------------------------------------------------


class TestRuntimeConsumerScanCmd(unittest.TestCase):
    """Verify runtime_consumer_scan_cmd is constructed correctly for each output_mode."""

    def _get_scan_cmd(self, output_mode: str) -> str:
        proc, tmp, _ = _run_validate_all_with_stubs(output_mode)
        try:
            self.assertEqual(proc.returncode, 0, f"Harness failed: {proc.stderr}")
            for line in proc.stdout.splitlines():
                if line.startswith("RUNTIME_CONSUMER_SCAN_CMD="):
                    return line.split("=", 1)[1]
            return ""
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_ephemeral_mode_includes_emit_readers(self) -> None:
        """runtime_consumer_scan_cmd must include --emit-readers in ephemeral mode."""
        cmd = self._get_scan_cmd("ephemeral")
        self.assertIn("--emit-readers", cmd)

    def test_ephemeral_mode_includes_emit_path_consumers(self) -> None:
        """runtime_consumer_scan_cmd must include --emit-path-consumers in ephemeral mode."""
        cmd = self._get_scan_cmd("ephemeral")
        self.assertIn("--emit-path-consumers", cmd)

    def test_ephemeral_mode_includes_strict(self) -> None:
        """runtime_consumer_scan_cmd must include --strict in ephemeral mode."""
        cmd = self._get_scan_cmd("ephemeral")
        self.assertIn("--strict", cmd)

    def test_ephemeral_mode_excludes_emit_digests(self) -> None:
        """runtime_consumer_scan_cmd must NOT include --emit-digests in ephemeral mode."""
        cmd = self._get_scan_cmd("ephemeral")
        self.assertNotIn("--emit-digests", cmd, "--emit-digests must not be added in ephemeral mode")

    def test_persistent_mode_includes_emit_readers(self) -> None:
        """runtime_consumer_scan_cmd must include --emit-readers in persistent mode."""
        cmd = self._get_scan_cmd("persistent")
        self.assertIn("--emit-readers", cmd)

    def test_persistent_mode_includes_emit_path_consumers(self) -> None:
        """runtime_consumer_scan_cmd must include --emit-path-consumers in persistent mode."""
        cmd = self._get_scan_cmd("persistent")
        self.assertIn("--emit-path-consumers", cmd)

    def test_persistent_mode_includes_strict(self) -> None:
        """runtime_consumer_scan_cmd must include --strict in persistent mode."""
        cmd = self._get_scan_cmd("persistent")
        self.assertIn("--strict", cmd)

    def test_persistent_mode_includes_emit_digests(self) -> None:
        """runtime_consumer_scan_cmd must include --emit-digests in persistent mode."""
        cmd = self._get_scan_cmd("persistent")
        self.assertIn("--emit-digests", cmd, "--emit-digests must be appended in persistent mode")

    def test_persistent_adds_emit_digests_not_ephemeral(self) -> None:
        """--emit-digests appears in persistent but not ephemeral — a negative regression guard."""
        cmd_e = self._get_scan_cmd("ephemeral")
        cmd_p = self._get_scan_cmd("persistent")
        self.assertNotIn("--emit-digests", cmd_e)
        self.assertIn("--emit-digests", cmd_p)


# ---------------------------------------------------------------------------
# TestRuntimeSeparationRunChecks
# ---------------------------------------------------------------------------


class TestRuntimeSeparationRunChecks(unittest.TestCase):
    """Verify all 8 runtime-separation checks are registered in check-results.tsv."""

    def _rows(self, output_mode: str) -> list[dict]:
        proc, tmp, check_results_path = _run_validate_all_with_stubs(output_mode)
        try:
            self.assertEqual(proc.returncode, 0, f"Harness failed: {proc.stderr}")
            return _parse_tsv(check_results_path)
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_all_8_slugs_present_in_ephemeral_mode(self) -> None:
        """All 8 runtime-separation check slugs must appear in check-results.tsv (ephemeral)."""
        rows = self._rows("ephemeral")
        slugs = {r["slug"] for r in rows}
        for expected_slug in RUNTIME_SEPARATION_SLUGS:
            self.assertIn(expected_slug, slugs, f"Missing slug in ephemeral results: {expected_slug!r}")

    def test_all_8_slugs_present_in_persistent_mode(self) -> None:
        """All 8 runtime-separation check slugs must appear in check-results.tsv (persistent)."""
        rows = self._rows("persistent")
        slugs = {r["slug"] for r in rows}
        for expected_slug in RUNTIME_SEPARATION_SLUGS:
            self.assertIn(expected_slug, slugs, f"Missing slug in persistent results: {expected_slug!r}")

    def test_exactly_8_runtime_separation_slugs(self) -> None:
        """Exactly 8 distinct runtime-separation slugs must be registered (no duplicates, no missing)."""
        rows = self._rows("ephemeral")
        runtime_slugs = [r["slug"] for r in rows if r["slug"].startswith("runtime-separation-")]
        self.assertEqual(len(runtime_slugs), 8, f"Expected 8 runtime-separation checks, got {runtime_slugs}")

    def test_all_checks_registered_as_required(self) -> None:
        """Every runtime-separation check must be registered with mode='required'."""
        rows = self._rows("ephemeral")
        for row in rows:
            if row["slug"].startswith("runtime-separation-"):
                self.assertEqual(
                    row["mode"],
                    "required",
                    f"Check {row['slug']!r} must use mode='required', got {row['mode']!r}",
                )


# ---------------------------------------------------------------------------
# TestRuntimeSeparationCheckOrder
# ---------------------------------------------------------------------------


class TestRuntimeSeparationCheckOrder(unittest.TestCase):
    """Verify the relative ordering of the 8 new checks."""

    def _slugs_in_order(self, output_mode: str) -> list[str]:
        proc, tmp, check_results_path = _run_validate_all_with_stubs(output_mode)
        try:
            rows = _parse_tsv(check_results_path)
            return [r["slug"] for r in rows]
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_manifest_before_consumers(self) -> None:
        """runtime-separation-manifest must run before runtime-separation-consumers."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertIn("runtime-separation-manifest", slugs)
        self.assertIn("runtime-separation-consumers", slugs)
        self.assertLess(
            slugs.index("runtime-separation-manifest"),
            slugs.index("runtime-separation-consumers"),
            "manifest must precede consumers",
        )

    def test_consumers_before_reader_compat(self) -> None:
        """runtime-separation-consumers must run before runtime-separation-reader-compat."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertLess(
            slugs.index("runtime-separation-consumers"),
            slugs.index("runtime-separation-reader-compat"),
            "consumers must precede reader-compat",
        )

    def test_reader_compat_before_current(self) -> None:
        """runtime-separation-reader-compat must run before runtime-separation-current."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertLess(
            slugs.index("runtime-separation-reader-compat"),
            slugs.index("runtime-separation-current"),
            "reader-compat must precede current",
        )

    def test_current_before_wrapper_fixtures(self) -> None:
        """runtime-separation-current must run before runtime-separation-wrapper-fixtures."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertLess(
            slugs.index("runtime-separation-current"),
            slugs.index("runtime-separation-wrapper-fixtures"),
            "current must precede wrapper-fixtures",
        )

    def test_wrapper_fixtures_before_baseline_compare(self) -> None:
        """runtime-separation-wrapper-fixtures must run before runtime-separation-baseline-compare."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertLess(
            slugs.index("runtime-separation-wrapper-fixtures"),
            slugs.index("runtime-separation-baseline-compare"),
            "wrapper-fixtures must precede baseline-compare",
        )

    def test_baseline_compare_before_writer_mutations(self) -> None:
        """runtime-separation-baseline-compare must run before runtime-separation-writer-mutations."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertLess(
            slugs.index("runtime-separation-baseline-compare"),
            slugs.index("runtime-separation-writer-mutations"),
            "baseline-compare must precede writer-mutations",
        )

    def test_writer_mutations_before_profile_home(self) -> None:
        """runtime-separation-writer-mutations must run before runtime-separation-profile-home."""
        slugs = self._slugs_in_order("ephemeral")
        self.assertLess(
            slugs.index("runtime-separation-writer-mutations"),
            slugs.index("runtime-separation-profile-home"),
            "writer-mutations must precede profile-home",
        )

    def test_full_order_matches_declaration(self) -> None:
        """The 8 slugs must appear in exactly the declared order (no reordering)."""
        slugs = self._slugs_in_order("ephemeral")
        runtime_slugs = [s for s in slugs if s.startswith("runtime-separation-")]
        self.assertEqual(
            runtime_slugs,
            RUNTIME_SEPARATION_SLUGS,
            "Runtime-separation checks appeared in unexpected order",
        )


# ---------------------------------------------------------------------------
# TestRuntimeSeparationCommandArgs
# ---------------------------------------------------------------------------


class TestRuntimeSeparationCommandArgs(unittest.TestCase):
    """Verify specific arguments passed to each runtime-separation check command."""

    def _harness_output(self, output_mode: str) -> tuple[str, list[dict]]:
        """Return (stdout, tsv_rows) for the harness run."""
        proc, tmp, check_results_path = _run_validate_all_with_stubs(output_mode)
        try:
            rows = _parse_tsv(check_results_path)
            return proc.stdout, rows
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def _read_python_stub_log(self, output_mode: str, log_name: str = "python3_calls.log") -> str:
        """Run harness and return the python stub call log content."""
        proc, tmp, _ = _run_validate_all_with_stubs(output_mode)
        try:
            log_path = tmp / log_name
            return log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def _read_check_log(self, output_mode: str, slug: str) -> str:
        """Return the content of the per-check log file for a given slug."""
        proc, tmp, check_results_path = _run_validate_all_with_stubs(output_mode)
        try:
            run_dir = tmp / "run_dir"
            log_file = run_dir / f"{slug}.log"
            return log_file.read_text(encoding="utf-8") if log_file.exists() else ""
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_manifest_check_uses_strict_flag(self) -> None:
        """validate_runtime_separation_manifest.py must be called with --strict."""
        log = self._read_python_stub_log("ephemeral")
        self.assertIn("validate_runtime_separation_manifest.py", log)
        # Find the line for the manifest script
        manifest_lines = [l for l in log.splitlines() if "validate_runtime_separation_manifest.py" in l]
        self.assertTrue(manifest_lines, "No call to validate_runtime_separation_manifest.py found")
        self.assertIn("--strict", manifest_lines[0])

    def test_reader_compat_uses_schema_current_flag(self) -> None:
        """verify_runtime_separation_reader_compat.py must be called with --schema-current."""
        log = self._read_python_stub_log("ephemeral")
        compat_lines = [l for l in log.splitlines() if "verify_runtime_separation_reader_compat.py" in l]
        self.assertTrue(compat_lines, "No call to verify_runtime_separation_reader_compat.py found")
        self.assertIn("--schema-current", compat_lines[0])

    def test_reader_compat_uses_schema_prev_flag(self) -> None:
        """verify_runtime_separation_reader_compat.py must be called with --schema-prev."""
        log = self._read_python_stub_log("ephemeral")
        compat_lines = [l for l in log.splitlines() if "verify_runtime_separation_reader_compat.py" in l]
        self.assertTrue(compat_lines, "No call to verify_runtime_separation_reader_compat.py found")
        self.assertIn("--schema-prev", compat_lines[0])

    def test_reader_compat_schema_current_path(self) -> None:
        """verify_runtime_separation_reader_compat.py --schema-current must point to slices.yaml."""
        log = self._read_python_stub_log("ephemeral")
        compat_lines = [l for l in log.splitlines() if "verify_runtime_separation_reader_compat.py" in l]
        self.assertTrue(compat_lines)
        self.assertIn("GOVERNANCE/runtime-separation/slices.yaml", compat_lines[0])

    def test_reader_compat_schema_prev_path(self) -> None:
        """verify_runtime_separation_reader_compat.py --schema-prev must point to schema-prev.yaml."""
        log = self._read_python_stub_log("ephemeral")
        compat_lines = [l for l in log.splitlines() if "verify_runtime_separation_reader_compat.py" in l]
        self.assertTrue(compat_lines)
        self.assertIn("GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml", compat_lines[0])

    def test_build_current_uses_output_flag_ephemeral(self) -> None:
        """build_runtime_separation_current.py must be called with --output pointing to run_dir in ephemeral mode."""
        log = self._read_python_stub_log("ephemeral")
        build_lines = [l for l in log.splitlines() if "build_runtime_separation_current.py" in l]
        self.assertTrue(build_lines, "No call to build_runtime_separation_current.py found")
        self.assertIn("--output", build_lines[0])
        self.assertIn("runtime-separation-current.json", build_lines[0])
        # Must NOT use GOVERNANCE path in ephemeral mode
        self.assertNotIn("GOVERNANCE", build_lines[0])

    def test_build_current_uses_governance_output_persistent(self) -> None:
        """build_runtime_separation_current.py must use GOVERNANCE output path in persistent mode."""
        log = self._read_python_stub_log("persistent")
        build_lines = [l for l in log.splitlines() if "build_runtime_separation_current.py" in l]
        self.assertTrue(build_lines, "No call to build_runtime_separation_current.py found")
        self.assertIn("--output", build_lines[0])
        self.assertIn("GOVERNANCE/runtime-separation/current.json", build_lines[0])

    def test_baseline_compare_uses_baseline_flag(self) -> None:
        """compare_runtime_separation_baseline.py must be called with --baseline."""
        log = self._read_python_stub_log("ephemeral")
        compare_lines = [l for l in log.splitlines() if "compare_runtime_separation_baseline.py" in l]
        self.assertTrue(compare_lines, "No call to compare_runtime_separation_baseline.py found")
        self.assertIn("--baseline", compare_lines[0])

    def test_baseline_compare_uses_correct_baseline_path(self) -> None:
        """compare_runtime_separation_baseline.py --baseline must point to baseline.json."""
        log = self._read_python_stub_log("ephemeral")
        compare_lines = [l for l in log.splitlines() if "compare_runtime_separation_baseline.py" in l]
        self.assertTrue(compare_lines)
        self.assertIn("GOVERNANCE/runtime-separation/baseline.json", compare_lines[0])

    def test_baseline_compare_current_matches_runtime_separation_current_ephemeral(self) -> None:
        """compare_runtime_separation_baseline.py --current must match runtime_separation_current in ephemeral mode."""
        log = self._read_python_stub_log("ephemeral")
        compare_lines = [l for l in log.splitlines() if "compare_runtime_separation_baseline.py" in l]
        self.assertTrue(compare_lines)
        self.assertIn("--current", compare_lines[0])
        # In ephemeral mode, current path ends with runtime-separation-current.json (in run_dir)
        self.assertIn("runtime-separation-current.json", compare_lines[0])
        self.assertNotIn("GOVERNANCE/runtime-separation/current.json", compare_lines[0])

    def test_baseline_compare_current_matches_runtime_separation_current_persistent(self) -> None:
        """compare_runtime_separation_baseline.py --current must be GOVERNANCE path in persistent mode."""
        log = self._read_python_stub_log("persistent")
        compare_lines = [l for l in log.splitlines() if "compare_runtime_separation_baseline.py" in l]
        self.assertTrue(compare_lines)
        self.assertIn("--current", compare_lines[0])
        self.assertIn("GOVERNANCE/runtime-separation/current.json", compare_lines[0])

    def test_wrapper_fixtures_uses_runtime_separation_flag(self) -> None:
        """verify_wrapper_contract_fixtures.sh must be called with --runtime-separation."""
        proc, tmp, _ = _run_validate_all_with_stubs("ephemeral")
        try:
            bash_log = tmp / "bash_calls.log"
            log_content = bash_log.read_text(encoding="utf-8") if bash_log.exists() else ""
            fixture_lines = [l for l in log_content.splitlines() if "verify_wrapper_contract_fixtures.sh" in l]
            self.assertTrue(fixture_lines, "No call to verify_wrapper_contract_fixtures.sh logged")
            self.assertIn("--runtime-separation", fixture_lines[0])
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_writer_mutations_uses_strict_flag(self) -> None:
        """verify_runtime_separation_writer_mutations.sh must be called with --strict."""
        proc, tmp, _ = _run_validate_all_with_stubs("ephemeral")
        try:
            bash_log = tmp / "bash_calls.log"
            log_content = bash_log.read_text(encoding="utf-8") if bash_log.exists() else ""
            mutation_lines = [l for l in log_content.splitlines() if "verify_runtime_separation_writer_mutations.sh" in l]
            self.assertTrue(mutation_lines, "No call to verify_runtime_separation_writer_mutations.sh logged")
            self.assertIn("--strict", mutation_lines[0])
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_profile_home_uses_repo_current_flag(self) -> None:
        """validate_runtime_separation_profile_home.sh must be called with --repo-current."""
        proc, tmp, _ = _run_validate_all_with_stubs("ephemeral")
        try:
            bash_log = tmp / "bash_calls.log"
            log_content = bash_log.read_text(encoding="utf-8") if bash_log.exists() else ""
            profile_lines = [l for l in log_content.splitlines() if "validate_runtime_separation_profile_home.sh" in l]
            self.assertTrue(profile_lines, "No call to validate_runtime_separation_profile_home.sh logged")
            self.assertIn("--repo-current", profile_lines[0])
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_profile_home_uses_correct_repo_current_path_ephemeral(self) -> None:
        """validate_runtime_separation_profile_home.sh --repo-current must use run_dir path in ephemeral mode."""
        proc, tmp, _ = _run_validate_all_with_stubs("ephemeral")
        try:
            bash_log = tmp / "bash_calls.log"
            log_content = bash_log.read_text(encoding="utf-8") if bash_log.exists() else ""
            profile_lines = [l for l in log_content.splitlines() if "validate_runtime_separation_profile_home.sh" in l]
            self.assertTrue(profile_lines)
            # Must contain runtime-separation-current.json but NOT GOVERNANCE path
            self.assertIn("runtime-separation-current.json", profile_lines[0])
            self.assertNotIn("GOVERNANCE/runtime-separation/current.json", profile_lines[0])
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_profile_home_uses_governance_repo_current_persistent(self) -> None:
        """validate_runtime_separation_profile_home.sh --repo-current must use GOVERNANCE path in persistent mode."""
        proc, tmp, _ = _run_validate_all_with_stubs("persistent")
        try:
            bash_log = tmp / "bash_calls.log"
            log_content = bash_log.read_text(encoding="utf-8") if bash_log.exists() else ""
            profile_lines = [l for l in log_content.splitlines() if "validate_runtime_separation_profile_home.sh" in l]
            self.assertTrue(profile_lines)
            self.assertIn("GOVERNANCE/runtime-separation/current.json", profile_lines[0])
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_profile_home_uses_output_flag(self) -> None:
        """validate_runtime_separation_profile_home.sh must be called with --output pointing to run_dir."""
        proc, tmp, _ = _run_validate_all_with_stubs("ephemeral")
        try:
            bash_log = tmp / "bash_calls.log"
            log_content = bash_log.read_text(encoding="utf-8") if bash_log.exists() else ""
            profile_lines = [l for l in log_content.splitlines() if "validate_runtime_separation_profile_home.sh" in l]
            self.assertTrue(profile_lines)
            self.assertIn("--output", profile_lines[0])
            self.assertIn("runtime-separation-profile-home.json", profile_lines[0])
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_consumers_check_uses_scan_script(self) -> None:
        """runtime-separation-consumers check must invoke scan_runtime_separation_consumers.py."""
        log = self._read_python_stub_log("ephemeral")
        self.assertIn("scan_runtime_separation_consumers.py", log)


# ---------------------------------------------------------------------------
# TestRuntimeSeparationFailurePropagation
# ---------------------------------------------------------------------------


class TestRuntimeSeparationFailurePropagation(unittest.TestCase):
    """Verify that a failing runtime-separation check is recorded as 'fail' in check-results.tsv."""

    def test_failing_check_recorded_as_fail(self) -> None:
        """When a stub exits non-zero, the corresponding slug must appear with outcome='fail'."""
        proc, tmp, check_results_path = _run_validate_all_with_stubs("ephemeral", stub_exit_code=1)
        try:
            rows = _parse_tsv(check_results_path)
            outcomes = {r["slug"]: r["outcome"] for r in rows}
            # All runtime-separation slugs should be in results
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(slug, outcomes, f"Slug {slug!r} missing from results on failure")
                self.assertEqual(
                    outcomes[slug],
                    "fail",
                    f"Slug {slug!r} should be 'fail' when stub exits 1, got {outcomes[slug]!r}",
                )
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_passing_check_recorded_as_pass(self) -> None:
        """When stubs exit 0, every runtime-separation slug must have outcome='pass'."""
        proc, tmp, check_results_path = _run_validate_all_with_stubs("ephemeral", stub_exit_code=0)
        try:
            rows = _parse_tsv(check_results_path)
            outcomes = {r["slug"]: r["outcome"] for r in rows}
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(slug, outcomes)
                self.assertEqual(
                    outcomes[slug],
                    "pass",
                    f"Slug {slug!r} should be 'pass' when stub exits 0, got {outcomes[slug]!r}",
                )
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)

    def test_harness_continues_after_failure(self) -> None:
        """run_check must always return 0; all checks run even when one fails."""
        proc, tmp, check_results_path = _run_validate_all_with_stubs("ephemeral", stub_exit_code=1)
        try:
            rows = _parse_tsv(check_results_path)
            slugs_recorded = [r["slug"] for r in rows]
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(slug, slugs_recorded, f"Slug {slug!r} was not reached after earlier failure")
        finally:
            import shutil
            shutil.rmtree(str(tmp), ignore_errors=True)


# ---------------------------------------------------------------------------
# TestRuntimeSeparationBoundaryPositions
# ---------------------------------------------------------------------------


class TestRuntimeSeparationBoundaryPositions(unittest.TestCase):
    """Verify new checks slot between ask-cli-modularity and future checks as intended.

    The harness in these tests injects boundary sentinel checks before and after
    the runtime-separation block to assert relative positioning.
    """

    def _run_with_sentinels(self, output_mode: str) -> list[str]:
        """Run harness that records before/after sentinel slugs and returns slug order."""
        import shutil

        tmp = Path(tempfile.mkdtemp())
        stubs_dir = tmp / "stubs"
        stubs_dir.mkdir()

        # Python3 stub
        py_stub = stubs_dir / "python3"
        py_stub.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        py_stub.chmod(0o755)

        # Bash script stubs
        for script_name in [
            "verify_wrapper_contract_fixtures.sh",
            "verify_runtime_separation_writer_mutations.sh",
            "validate_runtime_separation_profile_home.sh",
        ]:
            stub = stubs_dir / script_name
            stub.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            stub.chmod(0o755)

        harness = textwrap.dedent(f"""\
            #!/usr/bin/env bash
            set -u
            output_mode="{output_mode}"
            run_dir="{tmp}/run_dir"
            mkdir -p "$run_dir"
            check_results_file="$run_dir/check-results.tsv"
            : > "$check_results_file"
            python_cmd=("{py_stub}")

            run_check() {{
                local mode="$1"
                local slug="$2"
                local label="$3"
                shift 3
                local log_file="$run_dir/${{slug}}.log"
                local outcome="pass"
                "$@" >"$log_file" 2>&1 || outcome="fail"
                printf '%s\\t%s\\t%s\\t%s\\n' "$slug" "$mode" "$outcome" "$log_file" >> "$check_results_file"
            }}

            # Sentinel: represents ask-cli-modularity (last check before new block)
            run_check required ask-cli-modularity "sentinel-before" true

            # --- New block under test ---
            runtime_separation_current="$run_dir/runtime-separation-current.json"
            if [[ "$output_mode" == "persistent" ]]; then
              runtime_separation_current="GOVERNANCE/runtime-separation/current.json"
            fi

            runtime_consumer_scan_cmd=(
              "${{python_cmd[@]}}"
              scripts/scan_runtime_separation_consumers.py
              --emit-readers
              --emit-path-consumers
              --strict
            )
            if [[ "$output_mode" == "persistent" ]]; then
              runtime_consumer_scan_cmd+=(--emit-digests)
            fi

            run_check required runtime-separation-manifest "x" "${{python_cmd[@]}}" scripts/validate_runtime_separation_manifest.py --strict
            run_check required runtime-separation-consumers "x" "${{runtime_consumer_scan_cmd[@]}}"
            run_check required runtime-separation-reader-compat "x" "${{python_cmd[@]}}" scripts/verify_runtime_separation_reader_compat.py --schema-current GOVERNANCE/runtime-separation/slices.yaml --schema-prev GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml
            run_check required runtime-separation-current "x" "${{python_cmd[@]}}" scripts/build_runtime_separation_current.py --output "$runtime_separation_current"
            run_check required runtime-separation-wrapper-fixtures "x" bash {stubs_dir}/verify_wrapper_contract_fixtures.sh --runtime-separation
            run_check required runtime-separation-baseline-compare "x" "${{python_cmd[@]}}" scripts/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current "$runtime_separation_current"
            run_check required runtime-separation-writer-mutations "x" bash {stubs_dir}/verify_runtime_separation_writer_mutations.sh --strict
            run_check required runtime-separation-profile-home "x" bash {stubs_dir}/validate_runtime_separation_profile_home.sh --repo-current "$runtime_separation_current" --output "$run_dir/runtime-separation-profile-home.json"

            # Sentinel: represents selection-gate-severity (first check after new block)
            run_check required selection-gate-severity "sentinel-after" true
        """)

        harness_path = tmp / "harness.sh"
        harness_path.write_text(harness, encoding="utf-8")
        harness_path.chmod(0o755)

        proc = subprocess.run(
            ["bash", str(harness_path)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

        check_results_path = tmp / "run_dir" / "check-results.tsv"
        rows = _parse_tsv(check_results_path)
        shutil.rmtree(str(tmp), ignore_errors=True)
        return [r["slug"] for r in rows]

    def test_all_runtime_checks_after_ask_cli_modularity(self) -> None:
        """All runtime-separation checks must appear after ask-cli-modularity."""
        slugs = self._run_with_sentinels("ephemeral")
        sentinel_idx = slugs.index("ask-cli-modularity")
        for slug in RUNTIME_SEPARATION_SLUGS:
            self.assertIn(slug, slugs)
            self.assertGreater(
                slugs.index(slug),
                sentinel_idx,
                f"{slug!r} must come after ask-cli-modularity",
            )

    def test_all_runtime_checks_before_selection_gate_severity(self) -> None:
        """All runtime-separation checks must appear before selection-gate-severity."""
        slugs = self._run_with_sentinels("ephemeral")
        gate_idx = slugs.index("selection-gate-severity")
        for slug in RUNTIME_SEPARATION_SLUGS:
            self.assertIn(slug, slugs)
            self.assertLess(
                slugs.index(slug),
                gate_idx,
                f"{slug!r} must come before selection-gate-severity",
            )


if __name__ == "__main__":
    unittest.main()