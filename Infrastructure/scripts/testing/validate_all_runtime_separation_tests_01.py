from validate_all_runtime_separation_tests_core import *  # noqa: F403

class RuntimeSeparationFailurePropagationTests(unittest.TestCase):
    """Verify that a failing runtime-separation check causes validate_all.sh to exit 1."""

    def test_manifest_failure_causes_exit_1(self) -> None:
        """
        Ensure validate_all.sh exits with code 1 when the runtime-separation-manifest check fails.

        Creates a FakeRepo, configures the manifest check stub to exit 1, runs validate_all.sh in ephemeral mode and asserts the overall process return code equals 1.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(
                proc.returncode,
                1,
                "validate_all.sh must exit 1 when runtime-separation-manifest fails",
            )

    def test_consumers_failure_causes_exit_1(self) -> None:
        """
        Verify that a non-zero exit from the runtime-separation consumers check causes validate_all.sh to exit with code 1.

        Sets the consumers stub to exit 1, runs validate_all.sh in ephemeral mode, and asserts the overall process exit code is 1.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/scan_runtime_separation_consumers.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_reader_compat_failure_causes_exit_1(self) -> None:
        """
        Ensure validate_all.sh exits with code 1 when the runtime-separation reader-compat check fails.

        Sets the reader-compat stub to exit with code 1 and asserts the overall validation run returns exit code 1.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_baseline_compare_failure_causes_exit_1(self) -> None:
        """A failure in runtime-separation-baseline-compare must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_manifest_failure_records_fail_in_tsv(self) -> None:
        """A failing runtime-separation check must be recorded as outcome=fail in the TSV."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py", 1)
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
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py", 1)
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
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py", 1)
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py", 1)
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
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py")
            self.assertIsNotNone(args, "validate_runtime_separation_manifest.py was not called")
            self.assertIn("--strict", args)

    def test_reader_compat_receives_schema_current_arg(self) -> None:
        """verify_runtime_separation_reader_compat.py must receive --schema-current."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args, "verify_runtime_separation_reader_compat.py was not called")
            self.assertIn("--schema-current", args)
            sc_idx = args.index("--schema-current") + 1
            self.assertIn(
                "slices.yaml",
                args[sc_idx],
                "--schema-current value must reference slices.yaml",
            )

    def test_reader_compat_receives_schema_prev_arg(self) -> None:
        """
        Ensure verify_runtime_separation_reader_compat.py is invoked with --schema-prev referencing schema-prev.yaml.

        Runs validate_all.sh in ephemeral mode and asserts the recorded argv for the reader-compat script contains the `--schema-prev` flag and that its following value includes 'schema-prev.yaml'.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args)
            self.assertIn("--schema-prev", args)
            sp_idx = args.index("--schema-prev") + 1
            self.assertIn(
                "schema-prev.yaml",
                args[sp_idx],
                "--schema-prev value must reference schema-prev.yaml",
            )

    def test_reader_compat_schema_current_references_governance_path(self) -> None:
        """
        Ensure the `--schema-current` argument passed to the reader-compat check references
        GOVERNANCE/runtime-separation/slices.yaml.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py")
            self.assertIsNotNone(args)
            sc_idx = args.index("--schema-current") + 1
            self.assertIn("GOVERNANCE/runtime-separation/slices.yaml", args[sc_idx])

    def test_reader_compat_schema_prev_references_fixtures_path(self) -> None:
        """
        Ensure the reader-compat check is invoked with `--schema-prev` pointing to GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py")
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
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py")
            self.assertIsNotNone(args, "compare_runtime_separation_baseline.py was not called")
            self.assertIn("--baseline", args)
            bl_idx = args.index("--baseline") + 1
            self.assertIn(
                "baseline.json",
                args[bl_idx],
                "--baseline value must reference baseline.json",
            )

    def test_baseline_compare_baseline_references_governance_path(self) -> None:
        """
        Ensure compare_runtime_separation_baseline is invoked with `--baseline` pointing to GOVERNANCE/runtime-separation/baseline.json.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py")
            self.assertIsNotNone(args)
            bl_idx = args.index("--baseline") + 1
            self.assertIn("GOVERNANCE/runtime-separation/baseline.json", args[bl_idx])

    def test_baseline_compare_receives_current_arg(self) -> None:
        """
        Verify compare_runtime_separation_baseline.py is invoked with --current pointing to a runtime-separation-current.json path.

        Runs validate_all.sh in ephemeral mode and asserts the recorded argv for
        Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py contains `--current` followed by
        a value that ends with `runtime-separation-current.json`.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py")
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
            args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py")
            self.assertIsNotNone(args, "build_runtime_separation_current.py was not called")
            self.assertIn("--output", args)

    def test_baseline_compare_current_path_matches_build_output_path(self) -> None:
        """
        Assert that compare_runtime_separation_baseline's `--current` argument equals build_runtime_separation_current's `--output`.

        Runs validate_all.sh in an ephemeral fake repository and compares the paths forwarded to the two scripts to ensure they reference the same runtime-separation current artefact.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            build_args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py")
            compare_args = repo.recorded_args_for("Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py")
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
            args = repo.recorded_bash_args_for("Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh")
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
            args = repo.recorded_bash_args_for("Infrastructure/scripts/runtime-separation/verify_runtime_separation_writer_mutations.sh")
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
            args = repo.recorded_bash_args_for("Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.sh")
            self.assertIsNotNone(
                args,
                "verify_wrapper_contract_fixtures.sh was not called",
            )
            self.assertIn("--runtime-separation", args)


class RuntimeSeparationProfileHomePathTests(unittest.TestCase):
    """Verify the output path for the profile-home artifact."""

    def test_profile_home_output_in_run_dir_ephemeral(self) -> None:
        """
        Ensure the profile-home output file is placed in the ephemeral run directory.

        Runs validate_all.sh with --ephemeral and asserts that the --output argument passed to
        Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh ends with "runtime-separation-profile-home.json"
        and does not reference the repository's GOVERNANCE path.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.run("--ephemeral")
            args = repo.recorded_bash_args_for("Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh")
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
                "Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh"
            )
            build_current_args = repo.recorded_args_for(
                "Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py"
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
        """
        Verify validate_all.sh exits with status 0 when every runtime-separation check succeeds.

        Runs validate_all.sh in an isolated fake repository with all runtime-separation scripts replaced by passing stubs (ephemeral mode) and asserts the process return code is 0.
        """
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
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/verify_runtime_separation_writer_mutations.sh", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_wrapper_fixtures_fails(self) -> None:
        """A failure in runtime-separation-wrapper-fixtures must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.sh", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_profile_home_fails(self) -> None:
        """A failure in runtime-separation-profile-home must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_reader_compat_fails(self) -> None:
        """A failure in runtime-separation-reader-compat must cause exit code 1."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_build_current_fails(self) -> None:
        """
        Ensure validate_all.sh exits with code 1 when the runtime-separation current build step fails.

        Sets the build_runtime_separation_current.py stub to exit with code 1, runs validate_all.sh in ephemeral mode, and asserts the process return code is 1.
        """
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py", 1)
            proc = repo.run("--ephemeral")
            self.assertEqual(proc.returncode, 1)

    def test_exit_1_when_manifest_fails_regression(self) -> None:
        """Regression: manifest check failure must bubble up to exit 1 (required mode check)."""
        with TemporaryDirectory() as tmpdir:
            repo = FakeRepo(Path(tmpdir))
            repo.set_script_exit_code("Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py", 1)
            proc = repo.run("--ephemeral")
            self.assertNotEqual(
                proc.returncode,
                0,
                "Manifest failure must not be silently swallowed",
            )
            self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()

__all__ = [name for name in globals() if not name.startswith("__")]
