#!/usr/bin/env python3
"""Tests for the runtime-separation checks added to validate_all.sh.

These tests focus exclusively on the new code block in validate_all.sh that
was introduced in the PR: the runtime_separation_current path selection logic,
the runtime_consumer_scan_cmd construction, and the eight new run_check calls
for runtime-separation validation steps.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import stat
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_ALL_SH = REPO_ROOT / "scripts" / "validate_all.sh"

# Slugs introduced by the new code block, in order.
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(*cmd: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def _make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")


def _make_python_stub(path: Path, *, exit_code: int = 0) -> None:
    """Create a Python stub that records its argv.

    The exit code is determined by checking for a companion
    ``<path>.exit_code`` file; if present its content is used, otherwise
    *exit_code* is the default.
    """
    _write(
        path,
        f"""\
        #!/usr/bin/env python3
        import json, sys
        from pathlib import Path
        me = Path(__file__)
        me.with_suffix(me.suffix + ".recorded_args.json").write_text(
            json.dumps(sys.argv), encoding="utf-8"
        )
        ec_file = me.with_suffix(me.suffix + ".exit_code")
        code = int(ec_file.read_text().strip()) if ec_file.exists() else {exit_code}
        sys.exit(code)
        """,
    )
    _make_executable(path)


def _make_bash_stub(path: Path, *, exit_code: int = 0) -> None:
    """Create a bash stub that records its args.

    The exit code is determined by checking for a companion
    ``<path without .sh>.exit_code`` file; if present its content is used,
    otherwise *exit_code* is the default.
    """
    _write(
        path,
        f"""\
        #!/usr/bin/env bash
        printf '%s\\n' "$@" > "${{0%.*}}.recorded_args.txt"
        ec_file="${{0%.*}}.exit_code"
        if [[ -f "$ec_file" ]]; then
          exit "$(cat "$ec_file")"
        fi
        exit {exit_code}
        """,
    )
    _make_executable(path)


def _make_recording_python_dispatcher(path: Path) -> None:
    """Create a Python dispatcher used as PYTHON_BIN.

    When called as ``$PYTHON_BIN scripts/foo.py <args>`` it:

    * records ``sys.argv`` to ``<scripts_dir>/foo.py.recorded_args.json``
    * checks for a ``<scripts_dir>/foo.py.exit_code`` file and uses it if
      present
    * otherwise exits 0
    """
    _write(
        path,
        """\
        #!/usr/bin/env python3
        import json, sys
        from pathlib import Path

        argv = sys.argv  # [dispatcher_path, script_path, ...args]
        if len(argv) >= 2:
            script_path = Path(argv[1])
            record = script_path.with_suffix(script_path.suffix + ".recorded_args.json")
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text(json.dumps(argv), encoding="utf-8")
            ec_file = script_path.with_suffix(script_path.suffix + ".exit_code")
            if ec_file.exists():
                sys.exit(int(ec_file.read_text().strip()))
        sys.exit(0)
        """,
    )
    _make_executable(path)


def _extract_run_dir(stdout: str) -> Path | None:
    """Parse the ephemeral run_dir from validate_all.sh stdout."""
    for line in stdout.splitlines():
        m = re.search(r"Validation logs:\s+(\S+)", line)
        if m:
            return Path(m.group(1))
    return None


def _parse_check_results_tsv(tsv_path: Path) -> list[dict[str, str]]:
    rows = []
    for line in tsv_path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) == 4:
            rows.append(
                {
                    "slug": parts[0],
                    "mode": parts[1],
                    "outcome": parts[2],
                    "log_file": parts[3],
                }
            )
    return rows


class FakeRepo:
    """Minimal fake repository layout for running validate_all.sh in isolation.

    All scripts that validate_all.sh calls are replaced with recording stubs
    so the test can inspect which arguments were forwarded to each script.
    """

    # Python scripts called via $python_cmd
    _PY_SCRIPTS = [
        "scripts/verify_recursive_skill_graph_artifacts.py",
        "scripts/docs_lint.py",
        "scripts/verify_verify_work_scope_flags.py",
        "scripts/verify_question_lifecycle_contract.py",
        "scripts/test_skill_lifecycle_validation.py",
        "scripts/verify_skill_catalog_freshness.py",
        "scripts/gotcha_pipeline.py",
        "scripts/verify_selection_contract.py",
        "scripts/verify_router_schema.py",
        "scripts/verify_ask_cli_modularity.py",
        "scripts/validate_runtime_separation_manifest.py",
        "scripts/scan_runtime_separation_consumers.py",
        "scripts/verify_runtime_separation_reader_compat.py",
        "scripts/build_runtime_separation_current.py",
        "scripts/compare_runtime_separation_baseline.py",
        "scripts/verify_selection_gate_severity.py",
    ]

    # Bash scripts called directly via `bash scripts/...`
    _BASH_SCRIPTS = [
        "scripts/validate_plan_graphs.sh",
        "scripts/check_plugin_skill_shadowing.sh",
        "scripts/validate_projection_integrity.sh",
        "scripts/check_path_ownership_boundaries.sh",
        "scripts/lint_skill_types.sh",
        "scripts/lint_openai_skill_format.sh",
        "scripts/lint_progressive_disclosure.sh",
        "scripts/validate_skill_authoring_family.sh",
        "scripts/verify_wrapper_contract_fixtures.sh",
        "scripts/verify_runtime_separation_writer_mutations.sh",
        "scripts/validate_runtime_separation_profile_home.sh",
    ]

    def __init__(self, root: Path) -> None:
        self.root = root
        self._dispatcher = root / "bin" / "python_stub"
        self._last_run_dir: Path | None = None
        self._build()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Python dispatcher used as PYTHON_BIN
        self._dispatcher.parent.mkdir(parents=True, exist_ok=True)
        _make_recording_python_dispatcher(self._dispatcher)

        # Stub all Python scripts
        for rel in self._PY_SCRIPTS:
            _make_python_stub(self.root / rel)

        # Stub all Bash scripts
        for rel in self._BASH_SCRIPTS:
            _make_bash_stub(self.root / rel)

        # Copy the real validate_all.sh (read-only; we don't modify it)
        dst = self.root / "scripts" / "validate_all.sh"
        dst.write_bytes(VALIDATE_ALL_SH.read_bytes())
        _make_executable(dst)

        # Directories referenced by validate_all.sh
        (self.root / "GOVERNANCE" / "runtime-separation" / "fixtures").mkdir(
            parents=True, exist_ok=True
        )
        # Dummy files referenced by reader-compat check
        (self.root / "GOVERNANCE" / "runtime-separation" / "slices.yaml").write_text(
            "{}\n", encoding="utf-8"
        )
        (
            self.root
            / "GOVERNANCE"
            / "runtime-separation"
            / "fixtures"
            / "schema-prev.yaml"
        ).write_text("{}\n", encoding="utf-8")
        (self.root / "GOVERNANCE" / "runtime-separation" / "baseline.json").write_text(
            "{}\n", encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Run helpers
    # ------------------------------------------------------------------

    def run(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "PYTHON_BIN": str(self._dispatcher)}
        proc = _run(
            "bash", "scripts/validate_all.sh", *extra_args,
            cwd=self.root,
            env=env,
        )
        self._last_run_dir = _extract_run_dir(proc.stdout)
        return proc

    def set_script_exit_code(self, script_rel: str, code: int) -> None:
        """Make a stub exit with *code* on next invocation.

        Works for both Python (``scripts/foo.py``) and bash
        (``scripts/foo.sh``) stubs.
        """
        p = self.root / script_rel
        if script_rel.endswith(".sh"):
            ec_path = p.with_suffix("").with_suffix(".exit_code")
        else:
            ec_path = p.with_suffix(p.suffix + ".exit_code")
        ec_path.write_text(str(code), encoding="utf-8")

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def check_results(self) -> list[dict[str, str]]:
        """Parse check-results.tsv from the most recent run."""
        if self._last_run_dir and (self._last_run_dir / "check-results.tsv").exists():
            return _parse_check_results_tsv(self._last_run_dir / "check-results.tsv")
        # Fallback: search under repo root (persistent mode)
        for tsv in self.root.rglob("check-results.tsv"):
            return _parse_check_results_tsv(tsv)
        return []

    def recorded_args_for(self, script_name: str) -> list[str] | None:
        """Return the recorded argv list for a Python script stub, or None."""
        p = self.root / script_name
        record_path = p.with_suffix(p.suffix + ".recorded_args.json")
        if not record_path.exists():
            return None
        return json.loads(record_path.read_text(encoding="utf-8"))

    def recorded_bash_args_for(self, script_name: str) -> list[str] | None:
        """Return the recorded args list for a bash script stub, or None."""
        p = self.root / script_name
        record_path = p.with_suffix("").with_suffix(".recorded_args.txt")
        if not record_path.exists():
            return None
        return record_path.read_text(encoding="utf-8").splitlines()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class RuntimeSeparationCurrentPathTests(unittest.TestCase):
    """Verify runtime_separation_current path selection logic."""

    def test_ephemeral_mode_uses_run_dir_path(self) -> None:
        """In ephemeral mode runtime_separation_current must be inside the temp run_dir."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/build_runtime_separation_current.py")
            self.assertIsNotNone(args, "build_runtime_separation_current.py was not called")
            output_idx = args.index("--output") + 1
            output_path = args[output_idx]
            self.assertNotIn(
                "GOVERNANCE",
                output_path,
                "Ephemeral mode must not use GOVERNANCE path for runtime_separation_current",
            )
            self.assertTrue(
                output_path.endswith("runtime-separation-current.json"),
                f"Expected output path to end with runtime-separation-current.json, got {output_path!r}",
            )

    def test_persistent_mode_uses_governance_path(self) -> None:
        """In persistent mode runtime_separation_current must be GOVERNANCE/.../current.json."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            (repo.root / "artifacts" / "validation").mkdir(parents=True, exist_ok=True)
            repo.run("--persistent")
            args = repo.recorded_args_for("scripts/build_runtime_separation_current.py")
            self.assertIsNotNone(args, "build_runtime_separation_current.py was not called")
            output_idx = args.index("--output") + 1
            output_path = args[output_idx]
            self.assertEqual(
                output_path,
                "GOVERNANCE/runtime-separation/current.json",
                f"Persistent mode must use GOVERNANCE path, got {output_path!r}",
            )

    def test_ephemeral_and_persistent_current_paths_differ(self) -> None:
        """Ephemeral and persistent modes must produce different runtime_separation_current paths."""
        with TemporaryDirectory() as tmp1, TemporaryDirectory() as tmp2:
            repo_e = FakeRepo(Path(tmp1))
            repo_p = FakeRepo(Path(tmp2))
            (repo_p.root / "artifacts" / "validation").mkdir(parents=True, exist_ok=True)
            repo_e.run("--ephemeral")
            repo_p.run("--persistent")
            args_e = repo_e.recorded_args_for("scripts/build_runtime_separation_current.py")
            args_p = repo_p.recorded_args_for("scripts/build_runtime_separation_current.py")
            self.assertIsNotNone(args_e)
            self.assertIsNotNone(args_p)
            path_e = args_e[args_e.index("--output") + 1]
            path_p = args_p[args_p.index("--output") + 1]
            self.assertNotEqual(path_e, path_p)


class RuntimeConsumerScanCmdTests(unittest.TestCase):
    """Verify runtime_consumer_scan_cmd construction."""

    def test_ephemeral_mode_omits_emit_digests(self) -> None:
        """In ephemeral mode --emit-digests must NOT appear in scan_runtime_separation_consumers args."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/scan_runtime_separation_consumers.py")
            self.assertIsNotNone(args, "scan_runtime_separation_consumers.py was not called")
            self.assertNotIn(
                "--emit-digests",
                args,
                "Ephemeral mode must not pass --emit-digests to scan_runtime_separation_consumers.py",
            )

    def test_ephemeral_mode_includes_required_flags(self) -> None:
        """In ephemeral mode the scan command must include --emit-readers, --emit-path-consumers, --strict."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/scan_runtime_separation_consumers.py")
            self.assertIsNotNone(args)
            self.assertIn("--emit-readers", args)
            self.assertIn("--emit-path-consumers", args)
            self.assertIn("--strict", args)

    def test_persistent_mode_includes_emit_digests(self) -> None:
        """In persistent mode --emit-digests must be passed to scan_runtime_separation_consumers.py."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            (repo.root / "artifacts" / "validation").mkdir(parents=True, exist_ok=True)
            repo.run("--persistent")
            args = repo.recorded_args_for("scripts/scan_runtime_separation_consumers.py")
            self.assertIsNotNone(args, "scan_runtime_separation_consumers.py was not called")
            self.assertIn(
                "--emit-digests",
                args,
                "Persistent mode must pass --emit-digests to scan_runtime_separation_consumers.py",
            )

    def test_persistent_mode_retains_required_flags(self) -> None:
        """In persistent mode the base flags must still be present alongside --emit-digests."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            (repo.root / "artifacts" / "validation").mkdir(parents=True, exist_ok=True)
            repo.run("--persistent")
            args = repo.recorded_args_for("scripts/scan_runtime_separation_consumers.py")
            self.assertIsNotNone(args)
            self.assertIn("--emit-readers", args)
            self.assertIn("--emit-path-consumers", args)
            self.assertIn("--strict", args)
            self.assertIn("--emit-digests", args)

    def test_scan_cmd_script_name_is_scan_runtime_separation_consumers(self) -> None:
        """The consumer scan check must invoke scan_runtime_separation_consumers.py (not a different script)."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/scan_runtime_separation_consumers.py")
            self.assertIsNotNone(
                args,
                "scan_runtime_separation_consumers.py must be the script invoked for the consumers check",
            )
            # argv[1] is the script path
            self.assertIn("scan_runtime_separation_consumers.py", args[1])


class RuntimeSeparationCheckResultsTests(unittest.TestCase):
    """Verify all 8 runtime-separation run_check calls appear in check-results.tsv.

    Uses --persistent mode so check-results.tsv is written to
    artifacts/validation/<run_id>/ which persists across the run (unlike
    --ephemeral mode which deletes the run_dir on success).
    """

    def _run_persistent(self, tmpdir: str) -> tuple[FakeRepo, list[dict[str, str]]]:
        repo = FakeRepo(Path(tmpdir))
        (repo.root / "artifacts" / "validation").mkdir(parents=True, exist_ok=True)
        repo.run("--persistent")
        return repo, repo.check_results()

    def test_all_eight_slugs_present(self) -> None:
        """All 8 runtime-separation slugs must appear in check-results.tsv."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            recorded_slugs = {r["slug"] for r in rows}
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(
                    slug,
                    recorded_slugs,
                    f"Expected slug {slug!r} in check-results.tsv",
                )

    def test_all_eight_slugs_registered_as_required(self) -> None:
        """All runtime-separation checks must be registered with mode=required."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            slug_to_row = {r["slug"]: r for r in rows}
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(slug, slug_to_row)
                self.assertEqual(
                    slug_to_row[slug]["mode"],
                    "required",
                    f"Expected {slug!r} to have mode=required",
                )

    def test_all_eight_slugs_pass_with_stubs(self) -> None:
        """When all stubs exit 0, all runtime-separation checks must record outcome=pass."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            slug_to_row = {r["slug"]: r for r in rows}
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(slug, slug_to_row)
                self.assertEqual(
                    slug_to_row[slug]["outcome"],
                    "pass",
                    f"Expected {slug!r} to have outcome=pass when stub exits 0",
                )

    def test_runtime_separation_checks_follow_ask_cli_modularity(self) -> None:
        """runtime-separation checks must appear after ask-cli-modularity in the TSV."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            slugs_in_order = [r["slug"] for r in rows]
            self.assertIn("ask-cli-modularity", slugs_in_order, "ask-cli-modularity must be in check-results.tsv")
            ask_cli_idx = slugs_in_order.index("ask-cli-modularity")
            for slug in RUNTIME_SEPARATION_SLUGS:
                rt_idx = slugs_in_order.index(slug)
                self.assertGreater(
                    rt_idx,
                    ask_cli_idx,
                    f"{slug!r} must appear after ask-cli-modularity in check-results.tsv",
                )

    def test_runtime_separation_checks_precede_selection_gate_severity(self) -> None:
        """runtime-separation checks must appear before selection-gate-severity in the TSV."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            slugs_in_order = [r["slug"] for r in rows]
            self.assertIn("selection-gate-severity", slugs_in_order, "selection-gate-severity must be in check-results.tsv")
            gate_idx = slugs_in_order.index("selection-gate-severity")
            for slug in RUNTIME_SEPARATION_SLUGS:
                rt_idx = slugs_in_order.index(slug)
                self.assertLess(
                    rt_idx,
                    gate_idx,
                    f"{slug!r} must appear before selection-gate-severity in check-results.tsv",
                )

    def test_runtime_separation_slugs_appear_in_declared_order(self) -> None:
        """The eight slugs must appear in the exact order declared in the script."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            slugs_in_order = [r["slug"] for r in rows if r["slug"] in RUNTIME_SEPARATION_SLUGS]
            self.assertEqual(
                slugs_in_order,
                RUNTIME_SEPARATION_SLUGS,
                "runtime-separation slugs must appear in the exact order declared in validate_all.sh",
            )

    def test_each_runtime_separation_check_has_a_log_file_path(self) -> None:
        """Each runtime-separation entry in the TSV must have a non-empty log_file path."""
        with TemporaryDirectory() as tmpdir:
            _, rows = self._run_persistent(tmpdir)
            slug_to_row = {r["slug"]: r for r in rows}
            for slug in RUNTIME_SEPARATION_SLUGS:
                self.assertIn(slug, slug_to_row)
                log_file = slug_to_row[slug]["log_file"]
                self.assertTrue(
                    log_file.endswith(f"{slug}.log"),
                    f"Expected log_file for {slug!r} to end with {slug}.log, got {log_file!r}",
                )


class RuntimeSeparationFailurePropagationTests(unittest.TestCase):
    """Verify that a failing runtime-separation check causes validate_all.sh to exit 1."""

    def test_manifest_failure_causes_exit_1(self) -> None:
        """A failure in runtime-separation-manifest must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/validate_runtime_separation_manifest.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(
                proc.returncode,
                1,
                "validate_all.sh must exit 1 when runtime-separation-manifest fails",
            )

    def test_consumers_failure_causes_exit_1(self) -> None:
        """A failure in runtime-separation-consumers must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/scan_runtime_separation_consumers.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_reader_compat_failure_causes_exit_1(self) -> None:
        """A failure in runtime-separation-reader-compat must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/verify_runtime_separation_reader_compat.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_baseline_compare_failure_causes_exit_1(self) -> None:
        """A failure in runtime-separation-baseline-compare must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/compare_runtime_separation_baseline.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_manifest_failure_records_fail_in_tsv(self) -> None:
        """A failing runtime-separation check must be recorded as outcome=fail in the TSV."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/validate_runtime_separation_manifest.py", 1)
            repo.run("--ephemeral")
            rows = repo.check_results()
            slug_to_row = {r["slug"]: r for r in rows}
            self.assertEqual(
                slug_to_row.get("runtime-separation-manifest", {}).get("outcome"),
                "fail",
                "Failed check must record outcome=fail in check-results.tsv",
            )

    def test_only_failed_check_records_fail_others_pass(self) -> None:
        """When only one runtime-separation check fails, the others must still record pass."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/validate_runtime_separation_manifest.py", 1)
            repo.run("--ephemeral")
            rows = repo.check_results()
            slug_to_row = {r["slug"]: r for r in rows}
            for slug in RUNTIME_SEPARATION_SLUGS:
                if slug == "runtime-separation-manifest":
                    continue
                self.assertEqual(
                    slug_to_row.get(slug, {}).get("outcome"),
                    "pass",
                    f"{slug!r} should still pass when only runtime-separation-manifest fails",
                )

    def test_multiple_runtime_separation_failures_are_all_recorded(self) -> None:
        """Multiple failing runtime-separation checks are all recorded as fail in the TSV."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/validate_runtime_separation_manifest.py", 1)
            repo.set_script_exit_code("scripts/compare_runtime_separation_baseline.py", 1)
            repo.run("--ephemeral")
            rows = repo.check_results()
            slug_to_row = {r["slug"]: r for r in rows}
            self.assertEqual(slug_to_row["runtime-separation-manifest"]["outcome"], "fail")
            self.assertEqual(slug_to_row["runtime-separation-baseline-compare"]["outcome"], "fail")


class RuntimeSeparationSpecificArgTests(unittest.TestCase):
    """Verify specific arguments forwarded to individual runtime-separation scripts."""

    def test_manifest_check_uses_strict_flag(self) -> None:
        """validate_runtime_separation_manifest.py must be called with --strict."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/validate_runtime_separation_manifest.py")
            self.assertIsNotNone(args, "validate_runtime_separation_manifest.py was not called")
            self.assertIn("--strict", args)

    def test_reader_compat_receives_schema_current_arg(self) -> None:
        """verify_runtime_separation_reader_compat.py must receive --schema-current."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args, "verify_runtime_separation_reader_compat.py was not called")
            self.assertIn("--schema-current", args)
            sc_idx = args.index("--schema-current") + 1
            self.assertIn(
                "slices.yaml",
                args[sc_idx],
                "--schema-current value must reference slices.yaml",
            )

    def test_reader_compat_receives_schema_prev_arg(self) -> None:
        """verify_runtime_separation_reader_compat.py must receive --schema-prev."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args)
            self.assertIn("--schema-prev", args)
            sp_idx = args.index("--schema-prev") + 1
            self.assertIn(
                "schema-prev.yaml",
                args[sp_idx],
                "--schema-prev value must reference schema-prev.yaml",
            )

    def test_reader_compat_schema_current_references_governance_path(self) -> None:
        """--schema-current must reference the GOVERNANCE/runtime-separation/slices.yaml path."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args)
            sc_idx = args.index("--schema-current") + 1
            self.assertIn("GOVERNANCE/runtime-separation/slices.yaml", args[sc_idx])

    def test_reader_compat_schema_prev_references_fixtures_path(self) -> None:
        """--schema-prev must reference the GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml path."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args)
            sp_idx = args.index("--schema-prev") + 1
            self.assertIn(
                "GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml",
                args[sp_idx],
            )

    def test_baseline_compare_receives_baseline_arg(self) -> None:
        """compare_runtime_separation_baseline.py must receive --baseline."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/compare_runtime_separation_baseline.py")
            self.assertIsNotNone(args, "compare_runtime_separation_baseline.py was not called")
            self.assertIn("--baseline", args)
            bl_idx = args.index("--baseline") + 1
            self.assertIn(
                "baseline.json",
                args[bl_idx],
                "--baseline value must reference baseline.json",
            )

    def test_baseline_compare_baseline_references_governance_path(self) -> None:
        """--baseline must reference the GOVERNANCE/runtime-separation/baseline.json path."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/compare_runtime_separation_baseline.py")
            self.assertIsNotNone(args)
            bl_idx = args.index("--baseline") + 1
            self.assertIn("GOVERNANCE/runtime-separation/baseline.json", args[bl_idx])

    def test_baseline_compare_receives_current_arg(self) -> None:
        """compare_runtime_separation_baseline.py must receive --current."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/compare_runtime_separation_baseline.py")
            self.assertIsNotNone(args)
            self.assertIn("--current", args)
            curr_idx = args.index("--current") + 1
            current_val = args[curr_idx]
            self.assertTrue(
                current_val.endswith("runtime-separation-current.json"),
                f"--current must point to runtime-separation-current.json, got {current_val!r}",
            )

    def test_build_current_receives_output_arg(self) -> None:
        """build_runtime_separation_current.py must receive --output."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("scripts/build_runtime_separation_current.py")
            self.assertIsNotNone(args, "build_runtime_separation_current.py was not called")
            self.assertIn("--output", args)

    def test_baseline_compare_current_path_matches_build_output_path(self) -> None:
        """The --current arg of baseline_compare must equal the --output of build_current."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            build_args = repo.recorded_args_for("scripts/build_runtime_separation_current.py")
            compare_args = repo.recorded_args_for("scripts/compare_runtime_separation_baseline.py")
            self.assertIsNotNone(build_args)
            self.assertIsNotNone(compare_args)
            build_output = build_args[build_args.index("--output") + 1]
            compare_current = compare_args[compare_args.index("--current") + 1]
            self.assertEqual(
                build_output,
                compare_current,
                "The --output of build_runtime_separation_current must equal the --current of compare_runtime_separation_baseline",
            )

    def test_profile_home_receives_repo_current_and_output_args(self) -> None:
        """validate_runtime_separation_profile_home.sh must receive --repo-current and --output."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_bash_args_for("scripts/validate_runtime_separation_profile_home.sh")
            self.assertIsNotNone(
                args,
                "validate_runtime_separation_profile_home.sh was not called",
            )
            self.assertIn("--repo-current", args)
            self.assertIn("--output", args)

    def test_writer_mutations_receives_strict_flag(self) -> None:
        """verify_runtime_separation_writer_mutations.sh must receive --strict."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_bash_args_for("scripts/verify_runtime_separation_writer_mutations.sh")
            self.assertIsNotNone(
                args,
                "verify_runtime_separation_writer_mutations.sh was not called",
            )
            self.assertIn("--strict", args)

    def test_wrapper_fixtures_receives_runtime_separation_flag(self) -> None:
        """verify_wrapper_contract_fixtures.sh must receive --runtime-separation."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_bash_args_for("scripts/verify_wrapper_contract_fixtures.sh")
            self.assertIsNotNone(
                args,
                "verify_wrapper_contract_fixtures.sh was not called",
            )
            self.assertIn("--runtime-separation", args)


class RuntimeSeparationProfileHomePathTests(unittest.TestCase):
    """Verify the output path for the profile-home artifact."""

    def test_profile_home_output_in_run_dir_ephemeral(self) -> None:
        """In ephemeral mode, profile-home --output must point into the run_dir temp directory."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_bash_args_for("scripts/validate_runtime_separation_profile_home.sh")
            self.assertIsNotNone(args)
            output_idx = args.index("--output") + 1
            output_val = args[output_idx]
            self.assertTrue(
                output_val.endswith("runtime-separation-profile-home.json"),
                f"--output must end with runtime-separation-profile-home.json, got {output_val!r}",
            )
            # The path must NOT be a static GOVERNANCE path
            self.assertNotIn("GOVERNANCE", output_val)

    def test_profile_home_repo_current_matches_runtime_separation_current(self) -> None:
        """profile-home --repo-current must be the same path as runtime_separation_current."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            profile_home_args = repo.recorded_bash_args_for(
                "scripts/validate_runtime_separation_profile_home.sh"
            )
            build_current_args = repo.recorded_args_for(
                "scripts/build_runtime_separation_current.py"
            )
            self.assertIsNotNone(profile_home_args)
            self.assertIsNotNone(build_current_args)
            repo_current = profile_home_args[profile_home_args.index("--repo-current") + 1]
            build_output = build_current_args[build_current_args.index("--output") + 1]
            self.assertEqual(
                repo_current,
                build_output,
                "--repo-current of profile_home must match --output of build_runtime_separation_current",
            )


class RuntimeSeparationOverallExitCodeTests(unittest.TestCase):
    """Verify validate_all.sh overall exit code when runtime-separation checks pass/fail."""

    def test_exit_0_when_all_runtime_separation_checks_pass(self) -> None:
        """validate_all.sh must exit 0 when all runtime-separation checks succeed."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            proc = repo.run("--ephemeral")
            self.assertEqual(
                proc.returncode,
                0,
                f"Expected exit 0 with all stubs passing.\nstdout: {proc.stdout}\nstderr: {proc.stderr}",
            )

    def test_exit_1_when_writer_mutations_fails(self) -> None:
        """A failure in runtime-separation-writer-mutations must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/verify_runtime_separation_writer_mutations.sh", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_wrapper_fixtures_fails(self) -> None:
        """A failure in runtime-separation-wrapper-fixtures must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/verify_wrapper_contract_fixtures.sh", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_profile_home_fails(self) -> None:
        """A failure in runtime-separation-profile-home must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/validate_runtime_separation_profile_home.sh", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_reader_compat_fails(self) -> None:
        """A failure in runtime-separation-reader-compat must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/verify_runtime_separation_reader_compat.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_build_current_fails(self) -> None:
        """A failure in runtime-separation-current (build step) must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/build_runtime_separation_current.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_manifest_fails_regression(self) -> None:
        """Regression: manifest check failure must bubble up to exit 1 (required mode check)."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("scripts/validate_runtime_separation_manifest.py", 1)
            proc = repo.run("--ephemeral")
            self.assertNotEqual(
                proc.returncode,
                0,
                "Manifest failure must not be silently swallowed",
            )
            self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()