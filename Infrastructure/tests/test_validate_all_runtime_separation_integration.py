"""
Tests for runtime-separation checks added to Infrastructure/scripts/validate_all.sh.

These tests cover the new code block introduced in the PR:
  - runtime_separation_current path resolution based on output_mode
  - runtime_consumer_scan_cmd --emit-digests flag based on output_mode
  - All 8 new required run_check calls are registered in check-results.tsv
"""

import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_ALL_SH = REPO_ROOT / "Infrastructure" / "scripts" / "validate_all.sh"

# The 8 new slugs added by the PR, in expected order
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

# Bash scripts called by the new run_check calls (need stubs in tmpdir)
NEW_BASH_SCRIPTS = [
    "Infrastructure/scripts/verify_wrapper_contract_fixtures.sh",
    "Infrastructure/scripts/verify_runtime_separation_writer_mutations.sh",
    "Infrastructure/scripts/validate_runtime_separation_profile_home.sh",
]

# Python scripts called by the new run_check calls (handled via PYTHON_BIN stub)
NEW_PYTHON_SCRIPTS = [
    "Infrastructure/scripts/validate_runtime_separation_manifest.py",
    "Infrastructure/scripts/scan_runtime_separation_consumers.py",
    "Infrastructure/scripts/verify_runtime_separation_reader_compat.py",
    "Infrastructure/scripts/build_runtime_separation_current.py",
    "Infrastructure/scripts/compare_runtime_separation_baseline.py",
]


def _make_executable(path: str) -> None:
    """
    Set the file at `path` to be executable by user, group and others.
    
    Parameters:
        path (str): Filesystem path of the file whose mode will be modified.
    
    Notes:
        The existing permission bits are preserved; this function adds execute bits for user, group and others.
    """
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _write_executable(path: str, content: str) -> None:
    """
    Create a file at `path` with `content`, ensure its parent directories exist, and make it executable.
    
    Parameters:
        path (str): Filesystem path to write.
        content (str): File content to write.
    
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    _make_executable(path)


class TestRuntimeSeparationCurrentPath(unittest.TestCase):
    """Tests the runtime_separation_current variable path logic (lines 164-167)."""

    def _eval_path(self, output_mode: str, run_dir: str) -> str:
        """
        Compute the resolved runtime_separation_current path for the given output mode and run directory.

        Evaluates the same bash conditional used by Infrastructure/scripts/validate_all.sh: when `output_mode` is exactly "persistent"
        the governance canonical path `GOVERNANCE/runtime-separation/current.json` is used; otherwise the path is
        `<run_dir>/runtime-separation-current.json`.

        Parameters:
            output_mode (str): The output mode string to evaluate (exact match against "persistent").
            run_dir (str): The run directory used to construct the ephemeral path when not persistent.

        Returns:
            runtime_separation_current (str): The resolved path for the runtime separation "current" file.
        """
        script = textwrap.dedent(f"""\
            output_mode={output_mode!r}
            run_dir={run_dir!r}

            runtime_separation_current="$run_dir/runtime-separation-current.json"
            if [[ "$output_mode" == "persistent" ]]; then
              runtime_separation_current="GOVERNANCE/runtime-separation/current.json"
            fi

            echo "$runtime_separation_current"
        """)
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"bash fragment failed: {result.stderr}")
        return result.stdout.strip()

    def test_ephemeral_mode_uses_run_dir(self):
        """In ephemeral mode, runtime_separation_current must be inside run_dir."""
        run_dir = "/tmp/test-run-dir"
        path = self._eval_path("ephemeral", run_dir)
        self.assertEqual(path, f"{run_dir}/runtime-separation-current.json")

    def test_persistent_mode_uses_governance_path(self):
        """In persistent mode, runtime_separation_current must be the GOVERNANCE canonical path."""
        run_dir = "/tmp/test-run-dir"
        path = self._eval_path("persistent", run_dir)
        self.assertEqual(path, "GOVERNANCE/runtime-separation/current.json")

    def test_persistent_mode_ignores_run_dir(self):
        """In persistent mode, the run_dir value should have no effect on the path."""
        path_a = self._eval_path("persistent", "/tmp/dir-a")
        path_b = self._eval_path("persistent", "/tmp/dir-b")
        self.assertEqual(path_a, path_b)
        self.assertNotIn("/tmp/dir-a", path_a)
        self.assertNotIn("/tmp/dir-b", path_b)

    def test_ephemeral_path_contains_correct_filename(self):
        """In ephemeral mode, the filename must be runtime-separation-current.json."""
        run_dir = "/var/run/validate"
        path = self._eval_path("ephemeral", run_dir)
        self.assertTrue(path.endswith("/runtime-separation-current.json"))

    def test_ephemeral_path_is_under_run_dir(self):
        """
        Assert that when output_mode is 'ephemeral' the computed runtime_separation_current path is located under the provided run_dir (i.e. it starts with run_dir + '/').
        """
        run_dir = "/some/custom/run/dir"
        path = self._eval_path("ephemeral", run_dir)
        self.assertTrue(path.startswith(run_dir + "/"))

    def test_other_output_mode_not_treated_as_persistent(self):
        """Modes other than 'persistent' should fall through to the ephemeral path."""
        run_dir = "/var/run/validate-fallback"
        # Simulate an unexpected mode value - should not use the governance path
        path = self._eval_path("unexpected", run_dir)
        self.assertNotEqual(path, "GOVERNANCE/runtime-separation/current.json")

    def test_governance_path_does_not_use_run_dir_prefix(self):
        """The persistent mode governance path must be a repo-relative path, not absolute."""
        path = self._eval_path("persistent", "/absolute/run/dir")
        self.assertFalse(path.startswith("/"))


class TestRuntimeConsumerScanCommand(unittest.TestCase):
    """Tests the runtime_consumer_scan_cmd array construction (lines 169-178)."""

    def _build_cmd(self, output_mode: str, python_bin: str = "python3") -> list[str]:
        """
        Construct the runtime_consumer_scan_cmd array for a given output mode and return its elements.

        Builds the command array consisting of the Python executable, the consumer scan script path and the base flags
        `--emit-readers`, `--emit-path-consumers` and `--strict`. When `output_mode` is exactly "persistent" the
        flag `--emit-digests` is appended as the final element.

        Parameters:
            output_mode (str): The output mode to evaluate; only the exact string "persistent" triggers `--emit-digests`.
            python_bin (str): Python executable to use as the first element of the command (defaults to "python3").

        Returns:
            list[str]: The command elements in order; `--emit-digests` is included and last only when `output_mode == "persistent"`.
        """
        script = textwrap.dedent(f"""\
            output_mode={output_mode!r}
            python_cmd=({python_bin!r})

            runtime_consumer_scan_cmd=(
              "${{python_cmd[@]}}"
              Infrastructure/scripts/scan_runtime_separation_consumers.py
              --emit-readers
              --emit-path-consumers
              --strict
            )
            if [[ "$output_mode" == "persistent" ]]; then
              runtime_consumer_scan_cmd+=(--emit-digests)
            fi

            printf '%s\\n' "${{runtime_consumer_scan_cmd[@]}}"
        """)
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"bash fragment failed: {result.stderr}")
        return [line for line in result.stdout.splitlines() if line]

    def test_ephemeral_mode_omits_emit_digests(self):
        """
        Ensure the consumer scan command does not include --emit-digests for ephemeral output mode.
        
        Asserts that when output_mode is 'ephemeral' the constructed runtime_consumer_scan_cmd omits the `--emit-digests` flag.
        """
        cmd = self._build_cmd("ephemeral")
        self.assertNotIn("--emit-digests", cmd)

    def test_persistent_mode_includes_emit_digests(self):
        """In persistent mode, --emit-digests MUST be in the scan command."""
        cmd = self._build_cmd("persistent")
        self.assertIn("--emit-digests", cmd)

    def test_emit_digests_is_last_in_persistent_mode(self):
        """In persistent mode, --emit-digests should be appended as the last argument."""
        cmd = self._build_cmd("persistent")
        self.assertEqual(cmd[-1], "--emit-digests")

    def test_base_flags_always_present_in_ephemeral(self):
        """Base flags --emit-readers, --emit-path-consumers, --strict must be present in ephemeral mode."""
        cmd = self._build_cmd("ephemeral")
        self.assertIn("--emit-readers", cmd)
        self.assertIn("--emit-path-consumers", cmd)
        self.assertIn("--strict", cmd)

    def test_base_flags_always_present_in_persistent(self):
        """Base flags --emit-readers, --emit-path-consumers, --strict must be present in persistent mode."""
        cmd = self._build_cmd("persistent")
        self.assertIn("--emit-readers", cmd)
        self.assertIn("--emit-path-consumers", cmd)
        self.assertIn("--strict", cmd)

    def test_target_script_always_present(self):
        """The scan script path must appear in the command regardless of mode."""
        for mode in ("ephemeral", "persistent"):
            with self.subTest(mode=mode):
                cmd = self._build_cmd(mode)
                self.assertIn("Infrastructure/scripts/scan_runtime_separation_consumers.py", cmd)

    def test_python_bin_is_first_element(self):
        """The command must start with the python binary."""
        cmd = self._build_cmd("ephemeral", "python3")
        self.assertEqual(cmd[0], "python3")

    def test_flag_count_ephemeral_vs_persistent(self):
        """Persistent mode should have exactly one more argument than ephemeral (--emit-digests)."""
        ephemeral_cmd = self._build_cmd("ephemeral")
        persistent_cmd = self._build_cmd("persistent")
        self.assertEqual(len(persistent_cmd), len(ephemeral_cmd) + 1)


class TestRuntimeSeparationIntegration(unittest.TestCase):
    """Integration tests: run validate_all.sh with stubs and verify the 8 new checks."""

    @classmethod
    def _create_python_stub(cls, stub_path: str, args_log_dir: str) -> None:
        """
        Write an executable Python stub to stub out Python scripts during integration tests.
        
        The generated launcher records its invocation arguments (excluding the launcher itself) as JSON into a per-script file named "<script_basename>.args.json" under `args_log_dir`, and exits with status 0.
        
        Parameters:
            stub_path (str): Filesystem path where the executable stub is written.
            args_log_dir (str): Directory where per-invocation JSON argument logs are created; the directory is created if it does not exist.
        """
        stub = textwrap.dedent(f"""\
            #!/usr/bin/env python3
            import sys
            import os
            import json

            log_dir = {args_log_dir!r}
            os.makedirs(log_dir, exist_ok=True)

            # Use the script name as the log file key
            script_name = os.path.basename(sys.argv[1]) if len(sys.argv) > 1 else "unknown"
            log_path = os.path.join(log_dir, script_name + ".args.json")
            with open(log_path, "w") as fh:
                json.dump(sys.argv[1:], fh)

            sys.exit(0)
        """)
        _write_executable(stub_path, stub)

    @classmethod
    def _create_bash_stub(cls, stub_path: str, args_log_dir: str) -> None:
        """
        Create an executable bash stub that records its invocation arguments to a log file and exits successfully.
        
        The created script ensures the log directory exists and writes its CLI arguments, one per line, to
        <args_log_dir>/<script_name>.args where <script_name> is the basename of the invoked script.
        
        Parameters:
            stub_path (str): Filesystem path where the stub script will be written.
            args_log_dir (str): Directory where the stub will create per-invocation argument logs.
        """
        stub = textwrap.dedent(f"""\
            #!/usr/bin/env bash
            mkdir -p {args_log_dir!r}
            script_name="$(basename "$0")"
            printf '%s\\n' "$@" > "{args_log_dir}/$script_name.args"
            exit 0
        """)
        _write_executable(stub_path, stub)

    def _setup_tmpdir(self, tmpdir: str) -> dict:
        """
        Prepare a minimal fake repository in tmpdir for integration tests of validate_all.sh.
        
        Parameters:
            tmpdir (str): Path to a temporary directory to be populated with the minimal repo layout.
        
        Returns:
            dict: Paths created for the test environment:
                - python_stub (str): Path to the executable Python stub that records argv.
                - args_log_dir (str): Directory where stub invocation logs are written.
                - scripts_dir (str): Path to the created Infrastructure/scripts/ directory.
                - governance_dir (str): Path to the created GOVENANCE/runtime-separation directory.
        """
        scripts_dir = os.path.join(tmpdir, "scripts")
        governance_dir = os.path.join(tmpdir, "GOVERNANCE", "runtime-separation")
        fixtures_dir = os.path.join(governance_dir, "fixtures")
        config_dir = os.path.join(tmpdir, "config", "schemas")
        args_log_dir = os.path.join(tmpdir, "_stub_logs")
        python_stub = os.path.join(tmpdir, "python_stub.py")

        os.makedirs(scripts_dir, exist_ok=True)
        os.makedirs(governance_dir, exist_ok=True)
        os.makedirs(fixtures_dir, exist_ok=True)
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(args_log_dir, exist_ok=True)

        # Python stub
        self._create_python_stub(python_stub, args_log_dir)

        # Stub bash scripts needed by new run_check calls
        for rel_path in NEW_BASH_SCRIPTS:
            self._create_bash_stub(os.path.join(tmpdir, rel_path), args_log_dir)

        # Create minimal stub for ./Infrastructure/scripts/validate_plan_graphs.sh (called with ./ prefix)
        self._create_bash_stub(os.path.join(scripts_dir, "validate_plan_graphs.sh"), args_log_dir)

        # Create minimal GOVERNANCE files expected by reader-compat check
        Path(os.path.join(governance_dir, "slices.yaml")).write_text("slices: []\n")
        Path(os.path.join(governance_dir, "baseline.json")).write_text("{}\n")
        Path(os.path.join(fixtures_dir, "schema-prev.yaml")).write_text("slices: []\n")

        # Create minimal config schema file expected by selection-gate-severity
        schema_path = os.path.join(config_dir, "selection-gate-severity.v1.schema.json")
        Path(schema_path).write_text("{}\n")

        return {
            "python_stub": python_stub,
            "args_log_dir": args_log_dir,
            "scripts_dir": scripts_dir,
            "governance_dir": governance_dir,
        }

    def _run_validate_all(self, tmpdir: str, python_stub: str, mode: str) -> subprocess.CompletedProcess:
        """
        Run the repository's validate_all.sh inside tmpdir using the supplied Python stub.
        
        Parameters:
            tmpdir (str): Filesystem path used as the working directory for the run.
            python_stub (str): Path to an executable Python stub to set in the `PYTHON_BIN` environment variable.
            mode (str): Validation mode to pass to the script (e.g. "ephemeral" or "persistent").
        
        Returns:
            result (subprocess.CompletedProcess): Completed process containing `returncode`, `stdout` and `stderr`.
        """
        env = os.environ.copy()
        env["PYTHON_BIN"] = python_stub
        # Suppress mise/uv detection by ensuring PYTHON_BIN is set
        result = subprocess.run(
            ["bash", str(VALIDATE_ALL_SH), f"--{mode}"],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env=env,
            timeout=60,
            check=False,
        )
        return result

    def _read_tsv_slugs(self, tmpdir: str, mode: str) -> list[tuple[str, str, str]]:
        """Read check-results.tsv and return list of (slug, check_mode, outcome) tuples."""
        if mode == "ephemeral":
            # Find the temp run_dir created by the script
            # The TSV path is written to stdout
            tsv_candidates = list(Path(tmpdir).rglob("check-results.tsv"))
            # Filter to exclude subdirs of Infrastructure/artifacts/ (persistent)
            tsv_candidates = [p for p in tsv_candidates if "artifacts" not in str(p)]
            if not tsv_candidates:
                # Also check /tmp since ephemeral uses mktemp
                import glob
                tmp_tsvs = glob.glob("/tmp/agent-skills-validate-all.*/check-results.tsv")
                tsv_candidates = [Path(p) for p in tmp_tsvs]
        else:
            tsv_candidates = list((Path(tmpdir) / "artifacts" / "validation").rglob("check-results.tsv"))

        entries = []
        for tsv_path in tsv_candidates:
            for line in tsv_path.read_text().splitlines():
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    entries.append((parts[0], parts[1], parts[2]))
        return entries

    def _get_tsv_from_stdout(self, stdout: str, tmpdir: str, _mode: str) -> list[tuple[str, str, str]]:
        """
        Locate the "Validation logs" run directory from stdout, read its check-results.tsv, and return each row as a (slug, check_mode, outcome) tuple.
        
        The function looks for a line in stdout containing "Validation logs: <path>", resolves a relative path against tmpdir, and parses check-results.tsv if present. Lines with at least three tab-separated fields are returned as tuples (first three fields); missing file or missing marker yields an empty list.
        
        Returns:
            list[tuple[str, str, str]]: Parsed TSV entries as (slug, check_mode, outcome).
        """
        # Extract run_dir from stdout line "📁 Validation logs: <path>"
        run_dir = None
        for line in stdout.splitlines():
            if "Validation logs:" in line:
                # Extract the path after the emoji and label
                parts = line.split("Validation logs:")
                if len(parts) == 2:
                    run_dir = parts[1].strip()
                    break

        if run_dir is None:
            return []

        # run_dir may be absolute (ephemeral uses mktemp) or relative (persistent uses
        # Infrastructure/artifacts/validation/<timestamp> relative to cwd=tmpdir)
        run_dir_path = Path(run_dir)
        if not run_dir_path.is_absolute():
            run_dir_path = Path(tmpdir) / run_dir_path

        tsv_path = run_dir_path / "check-results.tsv"
        if not tsv_path.exists():
            return []

        entries = []
        for line in tsv_path.read_text().splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                entries.append((parts[0], parts[1], parts[2]))
        return entries

    def test_ephemeral_mode_registers_all_eight_new_checks(self):
        """All 8 new runtime-separation slugs must appear in check-results.tsv in ephemeral mode."""
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            result = self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            entries = self._get_tsv_from_stdout(result.stdout, tmpdir, "ephemeral")
            registered_slugs = [slug for slug, _, _ in entries]

            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(
                    slug,
                    registered_slugs,
                    f"Slug '{slug}' not found in check-results.tsv.\n"
                    f"Registered slugs: {registered_slugs}\n"
                    f"stdout: {result.stdout[-2000:]}\n"
                    f"stderr: {result.stderr[-1000:]}",
                )

    def test_persistent_mode_registers_all_eight_new_checks(self):
        """All 8 new runtime-separation slugs must appear in check-results.tsv in persistent mode."""
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            # Need Infrastructure/artifacts/validation dir for persistent mode
            os.makedirs(os.path.join(tmpdir, "artifacts", "validation"), exist_ok=True)

            result = self._run_validate_all(tmpdir, paths["python_stub"], "persistent")

            entries = self._get_tsv_from_stdout(result.stdout, tmpdir, "persistent")
            registered_slugs = [slug for slug, _, _ in entries]

            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(
                    slug,
                    registered_slugs,
                    f"Slug '{slug}' not found in check-results.tsv in persistent mode.\n"
                    f"Registered slugs: {registered_slugs}\n"
                    f"stdout: {result.stdout[-2000:]}\n"
                    f"stderr: {result.stderr[-1000:]}",
                )

    def test_all_new_checks_are_required_mode(self):
        """
        Assert that each of the eight runtime-separation checks is registered with mode "required".
        
        Runs validate_all in ephemeral mode against a temporary stubbed repository, reads the produced check-results.tsv, and verifies every expected runtime-separation slug (if present) has check mode equal to "required".
        """
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            result = self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            entries = self._get_tsv_from_stdout(result.stdout, tmpdir, "ephemeral")
            tsv_map = {slug: (check_mode, outcome) for slug, check_mode, outcome in entries}
            runtime_rows = [slug for slug in tsv_map if slug in RUNTIME_SEPARATION_SLUGS]
            self.assertCountEqual(
                runtime_rows,
                RUNTIME_SEPARATION_SLUGS,
                f"Missing runtime-separation rows. Expected {RUNTIME_SEPARATION_SLUGS}, got {runtime_rows}",
            )

            for slug in RUNTIME_SEPARATION_SLUGS:
                check_mode, _ = tsv_map[slug]
                self.assertEqual(
                    check_mode,
                    "required",
                    f"Slug '{slug}' has mode '{check_mode}', expected 'required'",
                )

    def test_new_checks_ordering_in_tsv(self):
        """
        Verify the eight new runtime-separation check slugs appear in the same relative order in check-results.tsv as defined by RUNTIME_SEPARATION_SLUGS.
        
        Runs validate_all.sh in a temporary minimal repository with stubbed scripts (ephemeral mode), extracts the TSV entries from the reported run directory, filters to the runtime-separation slugs present, and asserts their relative ordering matches the expected sequence.
        """
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            result = self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            entries = self._get_tsv_from_stdout(result.stdout, tmpdir, "ephemeral")
            all_slugs = [slug for slug, _, _ in entries]

            # Filter to only the new runtime-separation slugs
            runtime_slugs_in_tsv = [s for s in all_slugs if s in RUNTIME_SEPARATION_SLUGS]
            self.assertEqual(
                runtime_slugs_in_tsv,
                RUNTIME_SEPARATION_SLUGS,
                f"Runtime-separation slugs appear out of order.\n"
                f"Expected order: {RUNTIME_SEPARATION_SLUGS}\n"
                f"Actual order in TSV: {runtime_slugs_in_tsv}",
            )

    def test_new_checks_succeed_with_stubs(self):
        """All 8 new runtime-separation checks should pass when their stub scripts succeed."""
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            result = self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            entries = self._get_tsv_from_stdout(result.stdout, tmpdir, "ephemeral")
            tsv_map = {slug: outcome for slug, _, outcome in entries}
            runtime_rows = [slug for slug in tsv_map if slug in RUNTIME_SEPARATION_SLUGS]
            self.assertCountEqual(
                runtime_rows,
                RUNTIME_SEPARATION_SLUGS,
                f"Missing runtime-separation rows. Expected {RUNTIME_SEPARATION_SLUGS}, got {runtime_rows}",
            )

            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertEqual(
                    tsv_map[slug],
                    "pass",
                    f"Slug '{slug}' has outcome '{tsv_map[slug]}', expected 'pass'.\n"
                    f"This means the stub did not exit 0 or was not found.",
                )

    def test_python_stub_receives_build_current_output_flag_ephemeral(self):
        """
        Assert that build_runtime_separation_current.py is invoked with an --output path under the run directory when running in ephemeral mode.
        
        Reads the run directory from the validate_all.sh stdout, loads the python stub's recorded argv, and verifies:
        - the `--output` flag is present,
        - the output value contains `runtime-separation-current.json`,
        - the output is not the GOVERNANCE canonical path `GOVERNANCE/runtime-separation/current.json`,
        - if a run directory was found in stdout, the output path either starts with that run directory or at least contains the expected filename.
        """
        import json

        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            result = self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            # Find the run_dir from stdout
            run_dir = None
            for line in result.stdout.splitlines():
                if "Validation logs:" in line:
                    run_dir = line.split("Validation logs:")[-1].strip()
                    break

            # Find the args log for build_runtime_separation_current.py
            args_log = os.path.join(paths["args_log_dir"], "build_runtime_separation_current.py.args.json")
            self.assertTrue(
                os.path.exists(args_log),
                "build_runtime_separation_current.py was not invoked in ephemeral mode",
            )

            with open(args_log) as fh:
                recorded_args = json.load(fh)

            # --output flag should be followed by a path inside run_dir
            self.assertIn("--output", recorded_args, f"--output flag not found in args: {recorded_args}")
            output_idx = recorded_args.index("--output")
            output_path = recorded_args[output_idx + 1]
            self.assertIn("runtime-separation-current.json", output_path)
            # In ephemeral mode, path should NOT be the GOVERNANCE canonical path
            self.assertNotEqual(output_path, "GOVERNANCE/runtime-separation/current.json")
            self.assertTrue(run_dir, "run_dir was not found in validate_all.sh stdout")
            self.assertTrue(
                output_path.startswith(run_dir),
                f"Output path '{output_path}' not under run_dir '{run_dir}'",
            )

    def test_python_stub_receives_build_current_output_flag_persistent(self):
        """build_runtime_separation_current.py must be called with --output pointing to GOVERNANCE path in persistent mode."""
        import json

        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            os.makedirs(os.path.join(tmpdir, "artifacts", "validation"), exist_ok=True)

            self._run_validate_all(tmpdir, paths["python_stub"], "persistent")

            args_log = os.path.join(paths["args_log_dir"], "build_runtime_separation_current.py.args.json")
            self.assertTrue(
                os.path.exists(args_log),
                "build_runtime_separation_current.py was not invoked in persistent mode",
            )

            with open(args_log) as fh:
                recorded_args = json.load(fh)

            self.assertIn("--output", recorded_args, f"--output flag not found: {recorded_args}")
            output_idx = recorded_args.index("--output")
            output_path = recorded_args[output_idx + 1]
            self.assertEqual(
                output_path,
                "GOVERNANCE/runtime-separation/current.json",
                f"In persistent mode, output must be GOVERNANCE path. Got: {output_path}",
            )

    def test_consumer_scan_receives_emit_digests_in_persistent_mode(self):
        """
        Assert that scan_runtime_separation_consumers.py is invoked with --emit-digests when validate_all runs in persistent mode.
        
        Runs validate_all.sh in a temporary fake repository with a python stub that records argv and verifies the recorded arguments include '--emit-digests'.
        """
        import json

        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            os.makedirs(os.path.join(tmpdir, "artifacts", "validation"), exist_ok=True)

            self._run_validate_all(tmpdir, paths["python_stub"], "persistent")

            args_log = os.path.join(
                paths["args_log_dir"], "scan_runtime_separation_consumers.py.args.json"
            )
            self.assertTrue(
                os.path.exists(args_log),
                "scan_runtime_separation_consumers.py was not invoked in persistent mode",
            )

            with open(args_log) as fh:
                recorded_args = json.load(fh)

            self.assertIn(
                "--emit-digests",
                recorded_args,
                f"--emit-digests must be passed in persistent mode. Got args: {recorded_args}",
            )

    def test_consumer_scan_omits_emit_digests_in_ephemeral_mode(self):
        """
        Verify that scan_runtime_separation_consumers.py is not passed `--emit-digests` when output mode is "ephemeral".
        
        If the stub invocation log for the script is missing, the test is skipped.
        """
        import json

        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            args_log = os.path.join(
                paths["args_log_dir"], "scan_runtime_separation_consumers.py.args.json"
            )
            self.assertTrue(
                os.path.exists(args_log),
                "scan_runtime_separation_consumers.py was not invoked in ephemeral mode",
            )

            with open(args_log) as fh:
                recorded_args = json.load(fh)

            self.assertNotIn(
                "--emit-digests",
                recorded_args,
                f"--emit-digests must NOT be passed in ephemeral mode. Got args: {recorded_args}",
            )

    def test_consumer_scan_always_receives_base_flags(self):
        """scan_runtime_separation_consumers.py must receive base flags in both modes."""
        import json

        required_flags = ["--emit-readers", "--emit-path-consumers", "--strict"]
        for mode in ("ephemeral", "persistent"):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
                    paths = self._setup_tmpdir(tmpdir)
                    if mode == "persistent":
                        os.makedirs(os.path.join(tmpdir, "artifacts", "validation"), exist_ok=True)

                    self._run_validate_all(tmpdir, paths["python_stub"], mode)

                    args_log = os.path.join(
                        paths["args_log_dir"], "scan_runtime_separation_consumers.py.args.json"
                    )
                    self.assertTrue(
                        os.path.exists(args_log),
                        f"scan_runtime_separation_consumers.py was not invoked for mode={mode}",
                    )

                    with open(args_log) as fh:
                        recorded_args = json.load(fh)

                    for flag in required_flags:
                        self.assertIn(
                            flag,
                            recorded_args,
                            f"Flag '{flag}' missing in {mode} mode. Got args: {recorded_args}",
                        )

    def test_reader_compat_receives_correct_schema_paths(self):
        """verify_runtime_separation_reader_compat.py must use GOVERNANCE canonical schema paths."""
        import json

        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            args_log = os.path.join(
                paths["args_log_dir"], "verify_runtime_separation_reader_compat.py.args.json"
            )
            self.assertTrue(
                os.path.exists(args_log),
                "verify_runtime_separation_reader_compat.py was not invoked",
            )

            with open(args_log) as fh:
                recorded_args = json.load(fh)

            self.assertIn(
                "--schema-current",
                recorded_args,
                f"--schema-current not found in args: {recorded_args}",
            )
            schema_current_idx = recorded_args.index("--schema-current")
            self.assertEqual(
                recorded_args[schema_current_idx + 1],
                "GOVERNANCE/runtime-separation/slices.yaml",
            )

            self.assertIn(
                "--schema-prev",
                recorded_args,
                f"--schema-prev not found in args: {recorded_args}",
            )
            schema_prev_idx = recorded_args.index("--schema-prev")
            self.assertEqual(
                recorded_args[schema_prev_idx + 1],
                "GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml",
            )

    def test_baseline_compare_receives_correct_flags(self):
        """compare_runtime_separation_baseline.py must receive the GOVERNANCE baseline and correct current path."""
        import json

        for mode in ("ephemeral", "persistent"):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
                    paths = self._setup_tmpdir(tmpdir)
                    if mode == "persistent":
                        os.makedirs(os.path.join(tmpdir, "artifacts", "validation"), exist_ok=True)

                    result = self._run_validate_all(tmpdir, paths["python_stub"], mode)

                    args_log = os.path.join(
                        paths["args_log_dir"], "compare_runtime_separation_baseline.py.args.json"
                    )
                    self.assertTrue(
                        os.path.exists(args_log),
                        f"compare_runtime_separation_baseline.py was not invoked for mode={mode}",
                    )

                    with open(args_log) as fh:
                        recorded_args = json.load(fh)

                    # --baseline must always point to GOVERNANCE canonical path
                    self.assertIn("--baseline", recorded_args)
                    baseline_idx = recorded_args.index("--baseline")
                    self.assertEqual(
                        recorded_args[baseline_idx + 1],
                        "GOVERNANCE/runtime-separation/baseline.json",
                    )

                    # --current must match runtime_separation_current for this mode
                    self.assertIn("--current", recorded_args)
                    current_idx = recorded_args.index("--current")
                    current_path = recorded_args[current_idx + 1]

                    if mode == "persistent":
                        self.assertEqual(current_path, "GOVERNANCE/runtime-separation/current.json")
                    else:
                        run_dir = None
                        for line in result.stdout.splitlines():
                            if "Validation logs:" in line:
                                run_dir = line.split("Validation logs:")[-1].strip()
                                break
                        self.assertTrue(run_dir, "run_dir was not found in validate_all.sh stdout")
                        self.assertTrue(
                            current_path.startswith(run_dir),
                            f"Current path '{current_path}' not under run_dir '{run_dir}'",
                        )
                        self.assertIn("runtime-separation-current.json", current_path)
                        self.assertNotEqual(current_path, "GOVERNANCE/runtime-separation/current.json")

    def test_manifest_check_uses_strict_flag(self):
        """validate_runtime_separation_manifest.py must receive --strict flag."""
        import json

        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            args_log = os.path.join(
                paths["args_log_dir"], "validate_runtime_separation_manifest.py.args.json"
            )
            self.assertTrue(
                os.path.exists(args_log),
                "validate_runtime_separation_manifest.py was not invoked",
            )

            with open(args_log) as fh:
                recorded_args = json.load(fh)

            self.assertIn(
                "--strict",
                recorded_args,
                f"--strict flag missing from manifest validation. Got args: {recorded_args}",
            )

    def test_validate_all_continues_after_preexisting_check_failures(self):
        """validate_all.sh must continue executing runtime-separation checks even when earlier checks fail."""
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            # We don't stub any pre-existing checks, so they may fail.
            # The script should continue and still register runtime-separation slugs.
            result = self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            entries = self._get_tsv_from_stdout(result.stdout, tmpdir, "ephemeral")
            registered_slugs = [slug for slug, _, _ in entries]

            # At least some of the new runtime-separation checks should appear
            found = [s for s in RUNTIME_SEPARATION_SLUGS if s in registered_slugs]
            self.assertGreater(
                len(found),
                0,
                f"No runtime-separation slugs found even with stubs present.\n"
                f"All registered slugs: {registered_slugs}\n"
                f"stdout: {result.stdout[-2000:]}\n"
                f"stderr: {result.stderr[-500:]}",
            )

    def test_wrapper_fixtures_check_receives_runtime_separation_flag(self):
        """
        Assert the wrapper fixtures verification script is invoked with the `--runtime-separation` flag.
        
        Runs validate_all.sh in an ephemeral test repository and checks the stub's recorded arguments for `--runtime-separation`; skips the test if the stub log file is not present.
        """
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            # The bash stub writes args to a file
            args_file = os.path.join(
                paths["args_log_dir"], "verify_wrapper_contract_fixtures.sh.args"
            )
            self.assertTrue(
                os.path.exists(args_file),
                "verify_wrapper_contract_fixtures.sh was not invoked",
            )

            args_content = Path(args_file).read_text()
            self.assertIn(
                "--runtime-separation",
                args_content,
                f"--runtime-separation flag missing from wrapper fixtures check. Got: {args_content!r}",
            )

    def test_writer_mutations_check_receives_strict_flag(self):
        """
        Assert the writer-mutations runtime-separation check is invoked with the --strict flag.
        
        Runs validate_all in a temporary fake repository and inspects the stub's recorded arguments; the test is skipped if the stub log is not present.
        """
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            args_file = os.path.join(
                paths["args_log_dir"], "verify_runtime_separation_writer_mutations.sh.args"
            )
            self.assertTrue(
                os.path.exists(args_file),
                "verify_runtime_separation_writer_mutations.sh was not invoked",
            )

            args_content = Path(args_file).read_text()
            self.assertIn(
                "--strict",
                args_content,
                f"--strict flag missing from writer mutations check. Got: {args_content!r}",
            )

    def test_profile_home_check_receives_output_flag(self):
        """
        Assert the profile-home check stub is invoked with an output path that contains
        the runtime-separation profile filename.
        
        Runs validate_all in ephemeral mode with stubs and checks the stub's args log
        for 'runtime-separation-profile-home.json', skipping the test if the log is missing.
        """
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            args_file = os.path.join(
                paths["args_log_dir"], "validate_runtime_separation_profile_home.sh.args"
            )
            self.assertTrue(
                os.path.exists(args_file),
                "validate_runtime_separation_profile_home.sh was not invoked",
            )

            args_content = Path(args_file).read_text()
            self.assertIn(
                "runtime-separation-profile-home.json",
                args_content,
                f"Output file not found in profile-home args. Got: {args_content!r}",
            )

    def test_profile_home_check_receives_repo_current_flag(self):
        """
        Assert that the profile-home validation check is invoked with a `--repo-current` argument that references the runtime-separation current file.
        
        This test runs `validate_all.sh` in an ephemeral mode against a stubbed repository, reads the stubbed invocation log for
        `validate_runtime_separation_profile_home.sh`, and verifies the presence of the `--repo-current` flag and the string
        `runtime-separation-current.json`. If the stub log is not present the test is skipped.
        """
        with tempfile.TemporaryDirectory(prefix="validate-all-test-") as tmpdir:
            paths = self._setup_tmpdir(tmpdir)
            self._run_validate_all(tmpdir, paths["python_stub"], "ephemeral")

            args_file = os.path.join(
                paths["args_log_dir"], "validate_runtime_separation_profile_home.sh.args"
            )
            self.assertTrue(
                os.path.exists(args_file),
                "validate_runtime_separation_profile_home.sh was not invoked",
            )

            args_content = Path(args_file).read_text()
            self.assertIn(
                "--repo-current",
                args_content,
                f"--repo-current flag missing. Got: {args_content!r}",
            )
            self.assertIn(
                "runtime-separation-current.json",
                args_content,
                f"runtime-separation-current.json not in args. Got: {args_content!r}",
            )


class TestValidateAllOutputModeEnvVar(unittest.TestCase):
    """Tests the VALIDATE_ALL_OUTPUT_MODE environment variable and CLI arg interaction."""

    def _run_validate_all_from_env_mode(self, mode: str) -> tuple[list[str], list[str]]:
        """
        Run validate_all.sh without CLI mode flags and drive output mode via VALIDATE_ALL_OUTPUT_MODE.

        Returns:
            tuple[list[str], list[str]]: Recorded args for build_runtime_separation_current.py
            and scan_runtime_separation_consumers.py, respectively.
        """
        import json

        harness = TestRuntimeSeparationIntegration(methodName="runTest")
        with tempfile.TemporaryDirectory(prefix="validate-all-env-mode-") as tmpdir:
            paths = harness._setup_tmpdir(tmpdir)
            if mode == "persistent":
                os.makedirs(os.path.join(tmpdir, "artifacts", "validation"), exist_ok=True)

            env = os.environ.copy()
            env["PYTHON_BIN"] = paths["python_stub"]
            env["VALIDATE_ALL_OUTPUT_MODE"] = mode

            result = subprocess.run(
                ["/bin/bash", str(VALIDATE_ALL_SH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                env=env,
                timeout=60,
                check=False,
            )

            build_args_log = os.path.join(
                paths["args_log_dir"], "build_runtime_separation_current.py.args.json"
            )
            scan_args_log = os.path.join(
                paths["args_log_dir"], "scan_runtime_separation_consumers.py.args.json"
            )

            self.assertTrue(
                os.path.exists(build_args_log),
                "build_runtime_separation_current.py was not invoked when reading VALIDATE_ALL_OUTPUT_MODE "
                f"for mode={mode!r}. returncode={result.returncode}",
            )
            self.assertTrue(
                os.path.exists(scan_args_log),
                "scan_runtime_separation_consumers.py was not invoked when reading VALIDATE_ALL_OUTPUT_MODE "
                f"for mode={mode!r}. returncode={result.returncode}",
            )

            with open(build_args_log) as fh:
                build_args = json.load(fh)
            with open(scan_args_log) as fh:
                scan_args = json.load(fh)

        return build_args, scan_args

    def test_runtime_separation_current_path_logic_from_env_mode(self):
        """Validate --output path behavior when mode is sourced from VALIDATE_ALL_OUTPUT_MODE."""
        for mode in ("ephemeral", "persistent"):
            with self.subTest(mode=mode):
                build_args, _ = self._run_validate_all_from_env_mode(mode)
                self.assertIn("--output", build_args, f"--output missing from args: {build_args}")
                output_idx = build_args.index("--output")
                output_path = build_args[output_idx + 1]
                if mode == "persistent":
                    self.assertEqual(output_path, "GOVERNANCE/runtime-separation/current.json")
                else:
                    self.assertIn("runtime-separation-current.json", output_path)
                    self.assertNotEqual(output_path, "GOVERNANCE/runtime-separation/current.json")

    def test_emit_digests_conditional_matches_output_mode_precisely(self):
        """Verify --emit-digests is present only when env mode equals exactly 'persistent'."""
        cases = [
            ("persistent", True),
            ("Persistent", False),
            ("PERSISTENT", False),
            ("persist", False),
            ("persistent_extra", False),
            ("", True),
        ]
        for mode, should_emit in cases:
            with self.subTest(mode=repr(mode)):
                _, scan_args = self._run_validate_all_from_env_mode(mode)
                if should_emit:
                    self.assertIn("--emit-digests", scan_args)
                else:
                    self.assertNotIn(
                        "--emit-digests",
                        scan_args,
                        f"--emit-digests should not appear for output_mode={mode!r}",
                    )


if __name__ == "__main__":
    unittest.main()