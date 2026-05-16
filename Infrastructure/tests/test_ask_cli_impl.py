import unittest
import subprocess
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock


def _run_cli(cmd: list[str], **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, **kwargs)


class TestAskCLI(unittest.TestCase):
    def test_json_envelope_format(self):
        """CA1: Verify ask --json returns a valid CallResult envelope."""
        # Using -p to pass a dummy command if needed, or just root --json
        cmd = [sys.executable, "Infrastructure/bin/ask", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"CLI failed with stderr: {result.stderr}")

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("CLI output was not valid JSON")

        # Verify mandatory envelope fields
        self.assertIn("status", output)
        self.assertIn("trace_id", output)
        self.assertIn("metadata", output)
        self.assertEqual(output["status"], "success")
        self.assertIn("version", output["metadata"])

    def test_repo_status_discovery(self):
        """CA1: Verify ask repo status correctly identifies the repo root."""
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("repo_root", output["data"])
        # Verify it found the actual current directory or a parent
        # Handle redacted paths by substituting back the home directory
        repo_root = output["data"]["repo_root"]
        if "<USER_HOME>" in repo_root:
            repo_root = repo_root.replace("<USER_HOME>", os.path.expanduser("~"))
        self.assertTrue(os.path.isdir(repo_root), f"repo_root is not a directory: {repo_root}")

    def test_skills_list(self):
        """
        Validate that the CLI `ask skills list --json` exposes a skills catalogue with the expected envelope and fields.

        Checks:
        - the process exits successfully (return code 0),
        - top-level `status` equals "success",
        - `data.skills` is present and is a list,
        - if the list is non-empty, the first skill contains `name` and `path`.
        """
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("skills", output["data"])
        self.assertIsInstance(output["data"]["skills"], list)
        if len(output["data"]["skills"]) > 0:
            skill = output["data"]["skills"][0]
            self.assertIn("name", skill)
            self.assertIn("path", skill)

    def test_skills_list_advanced_flag(self):
        """CA1: Verify ask skills list --advanced toggles advanced_mode in JSON output."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--advanced", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("advanced_mode"))

    def test_skills_route_json_contract(self):
        """CA1: Verify ask skills route exposes selection-decision fields."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "route", "create-auth", "--json"]
        result = _run_cli(cmd)

        # Route may exit non-zero for unresolved ambiguity/no-candidate, but should emit envelope JSON.
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("data", output)
        self.assertIn("decision", output["data"])
        decision = output["data"]["decision"]
        self.assertIn("decision_status", decision)
        self.assertIn("policy_identity", decision)
        self.assertIn("considered_limit", decision)
        self.assertIn("selected_candidates", decision)

    def test_skills_handles_json_contract(self):
        """Verify ask skills handles exposes the command-surface contract."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "handles", "--check", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        surface = output["data"]["command_surface"]
        self.assertEqual(surface["schema_version"], "command-surface.v1")
        self.assertEqual(surface["status"], "pass")
        self.assertGreater(surface["handle_count"], 0)

    def test_skills_handles_projection_dry_run_contract(self):
        """Verify ask can preview the generated command-surface projection."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "handles",
            "--write-projection",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        write = output["data"]["command_surface_projection_write"]
        self.assertEqual(write["status"], "pass")
        self.assertTrue(write["dry_run"])
        self.assertEqual(write["path"], ".skillsets/command-surface.json")

    def test_skills_handles_command_handle_dry_run_contract(self):
        """Verify ask can preview generated runtime command handles."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "handles",
            "--write-command-handles",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        write = output["data"]["command_handle_write"]
        self.assertEqual(write["status"], "pass")
        self.assertTrue(write["dry_run"])
        self.assertGreater(write["command_handle_count"], 0)
        paths = {row["path"] for row in write["writes"] if row["handle"] == "he-heartbeat"}
        self.assertEqual(
            paths,
            {
                ".agents/skills/he-heartbeat/SKILL.md",
                ".agents/skills/he-heartbeat/agents/openai.yaml",
            },
        )

    def test_skills_resolve_json_contract(self):
        """Verify ask skills resolve returns a latent source path for a command handle."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "resolve", "he-heartbeat", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output["data"]["resolution"]
        self.assertEqual(resolution["status"], "ok")
        self.assertEqual(resolution["handle"], "he-heartbeat")
        self.assertEqual(resolution["command_visibility"], "target")
        self.assertEqual(resolution["invoke_via"], "harness-engineering")

    def test_skills_proof_json_contract(self):
        """Verify ask skills proof separates resolver, command handle, and runtime-link gates."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "proof", "he-heartbeat", "--json"]
        result = _run_cli(cmd)

        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        proof = output["data"]["proof"]
        self.assertEqual(proof["schema_version"], "command-handle-proof.v1")
        self.assertEqual(proof["handle"], "he-heartbeat")
        self.assertIn("resolver", proof["gates"])
        self.assertIn("generated_command_handle_check", proof["gates"])
        self.assertIn("workspace_command_handle_exists", proof["gates"])
        self.assertIn("codex_user_link", proof["gates"])
        self.assertIn("codex_user_link", proof["gate_policy"]["required"])
        self.assertIn("agents_user_link", proof["gate_policy"]["supporting_runtime_diagnostics"])
        self.assertEqual(proof["live_codex_invocation"]["status"], "manual_session_gate")

    def test_skills_proof_human_output(self):
        """Verify ask skills proof has a useful non-JSON success render."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "proof", "he-heartbeat"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skill handle proof: $he-heartbeat", result.stdout)
        self.assertIn("live invocation: manual_session_gate", result.stdout)

    def test_skills_prove_json_contract(self):
        """Verify ask skills prove separates reachability, quality, analytics, and outcome proof."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "he-heartbeat", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["schema_version"], "skill-proof-scorecard.v1")
        self.assertEqual(skill_proof["handle"], "he-heartbeat")
        self.assertIn("reachability", skill_proof)
        self.assertIn("structural_quality", skill_proof)
        self.assertIn("analytics", skill_proof)
        self.assertIn("outcome_proof", skill_proof)
        self.assertEqual(skill_proof["analytics"]["status"], "unavailable_or_legacy")
        self.assertIn("command_handle_proof", output["data"])

    def test_skills_prove_maps_golden_path_taxonomy_for_he_handle(self):
        """Verify prove exposes the stable proof taxonomy without adding schemas."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "he-spec", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["schema_version"], "skill-proof-scorecard.v1")
        self.assertEqual(skill_proof["handle"], "he-spec")
        self.assertEqual(skill_proof["reachability"]["status"], "pass")
        self.assertEqual(skill_proof["reachability"]["source"], "command_handle_proof")
        self.assertEqual(skill_proof["structural_quality"]["status"], "pass")
        self.assertEqual(skill_proof["analytics"]["evidence_class"], "native_skill_invocation_projection")
        self.assertEqual(skill_proof["outcome_proof"]["evidence_class"], "outcome_proof")
        self.assertIn(
            skill_proof["proof_status"],
            {"reachable_without_outcome_proof", "pass"},
        )
        self.assertIn("command_handle_proof", output["data"])

    def test_skills_prove_uses_skill_invocation_projection(self):
        """Verify ask skills prove consumes ASK-local skill invocation analytics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, "telemetry")
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, "skill-invocations.jsonl"), "w", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "skill_id": "he-heartbeat",
                            "plugin_id": "harness-engineering",
                            "turn_id_hash": "turn_123",
                            "thread_id_hash": "thread_123",
                            "invoke_type": "skill",
                            "scope": "workspace",
                            "model_slug": "gpt-5.3-codex",
                            "product_client_id_hash": "client_123",
                            "repository_hash": "repo_123",
                            "timestamp": "2026-05-07T10:00:00Z",
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )

            env = os.environ.copy()
            env["SKILL_TELEMETRY_DIR"] = telemetry_dir
            cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "he-heartbeat", "--json"]
            result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        analytics = output["data"]["skill_proof"]["analytics"]
        self.assertEqual(analytics["status"], "available")
        self.assertEqual(analytics["matching_invocation_count"], 1)
        self.assertEqual(analytics["latest_invocation"]["plugin_id"], "harness-engineering")
        self.assertEqual(analytics["latest_invocation"]["turn_id_hash"], "turn_123")

    def test_skills_prove_reports_projection_parse_warning(self):
        """Verify ask skills prove preserves valid projection rows with parse warnings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, "telemetry")
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, "skill-invocations.jsonl"), "w", encoding="utf-8") as handle:
                handle.write("{not-json\n")
                handle.write(json.dumps({"skill_id": "other-skill", "timestamp": "2026-05-07T10:00:00Z"}) + "\n")

            with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": telemetry_dir}):
                lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
                sys.path.insert(0, lib_path)
                try:
                    from ask.skill_analytics import skill_invocation_analytics

                    analytics = skill_invocation_analytics(Path.cwd(), "he-heartbeat")
                finally:
                    sys.path.remove(lib_path)

        self.assertEqual(analytics["status"], "parse_warning")
        self.assertEqual(analytics["invocation_count"], 1)
        self.assertEqual(analytics["matching_invocation_count"], 0)
        self.assertEqual(analytics["parse_error_count"], 1)

    def test_skills_prove_reports_parse_warning_with_matching_record(self):
        """Verify parse warnings are visible even when the target skill has evidence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, "telemetry")
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, "skill-invocations.jsonl"), "w", encoding="utf-8") as handle:
                handle.write("{not-json\n")
                handle.write(json.dumps({"skill_id": "he-heartbeat", "timestamp": "2026-05-07T10:00:00Z"}) + "\n")

            env = os.environ.copy()
            env["SKILL_TELEMETRY_DIR"] = telemetry_dir
            cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "he-heartbeat", "--json"]
            result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        analytics = output["data"]["skill_proof"]["analytics"]
        self.assertEqual(analytics["status"], "parse_warning")
        self.assertEqual(analytics["matching_invocation_count"], 1)
        self.assertEqual(analytics["parse_error_count"], 1)

    def test_skill_invocation_analytics_relative_override_uses_repo_root(self):
        """Verify relative telemetry overrides are anchored to the repository root."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask import skill_analytics

            repo_root = Path("/tmp/agent-skills-repo")
            with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": "generated/telemetry"}):
                telemetry_dir = skill_analytics.skill_telemetry_dir(repo_root)
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(telemetry_dir, repo_root / "generated" / "telemetry")

    def test_skill_invocation_analytics_handles_projection_read_errors(self):
        """Verify projection read errors return an unavailable summary."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask import skill_analytics

            with tempfile.TemporaryDirectory() as temp_dir:
                telemetry_dir = Path(temp_dir) / "telemetry"
                telemetry_dir.mkdir(parents=True)
                projection = telemetry_dir / "skill-invocations.jsonl"
                projection.write_text("", encoding="utf-8")
                original_open = Path.open

                def selective_open(path_self, *args, **kwargs):
                    if path_self == projection:
                        raise PermissionError("permission denied")
                    return original_open(path_self, *args, **kwargs)

                with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(telemetry_dir)}), mock.patch.object(
                    Path,
                    "open",
                    selective_open,
                ):
                    analytics = skill_analytics.skill_invocation_analytics(Path.cwd(), "he-heartbeat")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(analytics["status"], "unavailable_or_legacy")
        self.assertEqual(analytics["parse_error_count"], 1)
        self.assertIn("permission denied", analytics["parse_errors"][0]["message"])

    def test_skills_prove_goal_fallback_json_contract(self):
        """Verify ask skills prove routes or clearly blocks a goal query."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "prove",
            "fix",
            "PR",
            "review",
            "comments",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["schema_version"], "skill-proof-scorecard.v1")
        self.assertEqual(skill_proof["query"], "fix PR review comments")
        self.assertIn(
            skill_proof["proof_status"],
            ("blocked_goal_resolution", "blocked_reachability", "reachable_without_outcome_proof"),
        )
        self.assertIn("goal_resolution", skill_proof)
        self.assertIn("recommended_capability", skill_proof["goal_resolution"])

    def test_skills_prove_single_token_goal_uses_improve_fallback(self):
        """Verify one-word goals use the same improvement route as phrase goals."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            failed_reachability = CallResult(status="error")
            goal_result = CallResult()
            goal_result.data["improvement"] = {
                "recommended_capability": {"handle": "security-reviewer"},
                "next_command": "./bin/ask skills proof security-reviewer --json --robot",
            }
            reachable_result = CallResult()
            reachable_result.data["proof"] = {
                "status": "pass",
                "handle": "security-reviewer",
                "resolution": {
                    "handle": "security-reviewer",
                    "source_path": "Plugins/harness-engineering/skills/he-heartbeat/SKILL.md",
                },
            }

            with mock.patch.object(
                skills_commands,
                "skills_proof",
                side_effect=[failed_reachability, reachable_result],
            ), mock.patch.object(
                skills_commands,
                "improve_skills",
                return_value=goal_result,
            ) as improve_mock, mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ):
                result = skills_commands.skills_prove(Path.cwd(), "security")
        finally:
            sys.path.remove(lib_path)

        improve_mock.assert_called_once()
        self.assertEqual(result.data["skill_proof"]["handle"], "security-reviewer")
        self.assertIn("goal_resolution", result.data["skill_proof"])

    def test_skills_prove_resolved_handle_failure_does_not_use_goal_fallback(self):
        """Verify a resolved handle with broken reachability stays on the requested handle."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult, ErrorObject

            failed_reachability = CallResult(status="error")
            failed_reachability.data["proof"] = {
                "status": "fail",
                "handle": "he-heartbeat",
                "resolution": {
                    "status": "ok",
                    "handle": "he-heartbeat",
                    "source_path": "Plugins/harness-engineering/skills/he-heartbeat/SKILL.md",
                },
            }
            failed_reachability.errors.append(
                ErrorObject(code="ERR_VALIDATION", message="reachability failed")
            )

            with mock.patch.object(
                skills_commands,
                "skills_proof",
                return_value=failed_reachability,
            ), mock.patch.object(
                skills_commands,
                "improve_skills",
            ) as improve_mock, mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ), mock.patch.object(
                skills_commands,
                "skill_invocation_analytics",
                return_value={"status": "unavailable_or_legacy"},
            ):
                result = skills_commands.skills_prove(Path.cwd(), "he-heartbeat")
        finally:
            sys.path.remove(lib_path)

        improve_mock.assert_not_called()
        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["skill_proof"]["handle"], "he-heartbeat")
        self.assertEqual(result.data["skill_proof"]["proof_status"], "blocked_reachability")

    def test_skills_prove_workout_candidates_require_explicit_metadata_match(self):
        """Verify workout outcome candidates are not inferred from directory names."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills import _skill_workout_candidates

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                false_positive = repo_root / ".workouts" / "he-heartbeat-but-not-referenced"
                false_positive.mkdir(parents=True)
                false_positive.joinpath("workout.yaml").write_text(
                    "id: unrelated\nskills:\n  - other-skill\n",
                    encoding="utf-8",
                )
                explicit_match = repo_root / ".workouts" / "explicit-outcome"
                explicit_match.mkdir(parents=True)
                explicit_match.joinpath("workout.yaml").write_text(
                    "id: outcome\nhandles:\n  - he-heartbeat\n",
                    encoding="utf-8",
                )
                target_module_match = repo_root / ".workouts" / "target-module-outcome"
                target_module_match.mkdir(parents=True)
                target_module_match.joinpath("workout.yaml").write_text(
                    "id: outcome-target\ntarget_module: he-heartbeat\n",
                    encoding="utf-8",
                )

                candidates = _skill_workout_candidates(repo_root, "he_heartbeat")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(candidates, ["explicit-outcome", "target-module-outcome"])

    def test_skill_invocation_analytics_resolves_relative_telemetry_dir_from_repo_root(self):
        """Verify relative SKILL_TELEMETRY_DIR overrides are repo-root relative."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.skill_analytics import skill_invocation_analytics

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                telemetry_dir = repo_root / "telemetry"
                telemetry_dir.mkdir(parents=True)
                telemetry_dir.joinpath("skill-invocations.jsonl").write_text(
                    json.dumps({"skill_id": "he-heartbeat", "timestamp": "2026-05-07T10:00:00Z"}) + "\n",
                    encoding="utf-8",
                )
                with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": "telemetry"}):
                    analytics = skill_invocation_analytics(repo_root, "he-heartbeat")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(analytics["status"], "available")
        self.assertEqual(analytics["matching_invocation_count"], 1)

    def test_skills_explain_json_contract(self):
        """Verify ask skills explain returns concise agent-facing skill guidance."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "explain", "autofix", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        skills_explain = output["data"]["skills_explain"]
        self.assertEqual(skills_explain["schema_version"], "skills-explain.v1")
        self.assertEqual(skills_explain["query"], "autofix")
        self.assertEqual(skills_explain["canonical_source"], "Skills/agent-ops/autofix/SKILL.md")
        self.assertEqual(skills_explain["generated_handle"], ".agents/skills/autofix/SKILL.md")
        self.assertIn("validation", skills_explain)
        self.assertIn("when_not_to_use", skills_explain)

        explanation = output["data"]["explanation"]
        self.assertEqual(explanation["schema_version"], "skill-explanation.v1")
        self.assertEqual(explanation["handle"], "autofix")
        self.assertEqual(explanation["status"], "resolved")
        for field in (
            "agent_summary",
            "canonical_source_path",
            "runtime_projection_path",
            "command_handles",
            "required_validation",
            "validation_commands",
            "known_limitations",
            "reachability",
            "next_command",
        ):
            self.assertIn(field, explanation)
        self.assertIsInstance(explanation["reachability"], dict)

    def test_skills_explain_golden_path_fields_for_he_and_non_he_handles(self):
        """Verify explain exposes source, runtime, validation, and proof handoff."""
        for handle, canonical_source, owner in (
            ("he-spec", "Plugins/harness-engineering/skills/he-spec/SKILL.md", "harness-engineering"),
            ("simplify", "Skills/agent-ops/simplify/SKILL.md", "agent-ops"),
        ):
            with self.subTest(handle=handle):
                cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "explain", handle, "--json", "--robot"]
                result = _run_cli(cmd)

                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                skills_explain = output["data"]["skills_explain"]
                self.assertEqual(skills_explain["query"], handle)
                self.assertEqual(skills_explain["canonical_source"], canonical_source)
                self.assertEqual(skills_explain["generated_handle"], f".agents/skills/{handle}/SKILL.md")
                self.assertEqual(skills_explain["runtime_projection"], "rooted")
                self.assertEqual(skills_explain["runtime_visibility"], "latent")
                self.assertEqual(skills_explain["owner"], owner)
                self.assertIn("validation", skills_explain)
                self.assertIn("ambiguity_notes", skills_explain)

                explanation = output["data"]["explanation"]
                self.assertEqual(explanation["canonical_source_path"], canonical_source)
                self.assertEqual(explanation["runtime_projection_path"], f".agents/skills/{handle}/SKILL.md")
                self.assertEqual(
                    explanation["command_handles"],
                    [{"handle": handle, "path": f".agents/skills/{handle}/SKILL.md", "invoke_via": owner}],
                )
                self.assertTrue(explanation["validation_commands"])
                self.assertIn("known_limitations", explanation)
                self.assertEqual(explanation["reachability"]["status"], "pass")
                self.assertEqual(
                    explanation["reachability"]["proof_command"],
                    f"./bin/ask skills proof {handle} --json --robot",
                )
                self.assertEqual(explanation["next_command"], f"./bin/ask skills proof {handle} --json --robot")

    def test_skills_explain_rejects_out_of_repo_source_path(self):
        """Verify explain validates resolved skill paths before reading skill files."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "escaped",
                    "source_path": "../outside/SKILL.md",
                    "description": "outside repo",
                },
            ):
                result = skills_commands.explain_skill(Path.cwd(), "escaped")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_PATH_TRAVERSAL")

    def test_skills_explain_rejects_missing_source_path(self):
        """Verify explain rejects resolved handles that omit the source path."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "missing-source",
                    "description": "missing source",
                },
            ):
                result = skills_commands.explain_skill(Path.cwd(), "missing-source")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("without a canonical source path", result.errors[0].message)

    def test_skills_explain_rejects_nonexistent_source_file(self):
        """Verify explain rejects stale handles before reading source sections."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "stale-source",
                    "source_path": "Skills/agent-ops/nope/SKILL.md",
                    "description": "stale source",
                },
            ):
                result = skills_commands.explain_skill(Path.cwd(), "stale-source")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("is missing", result.errors[0].message)

    def test_skills_explain_rejects_unreadable_source_file(self):
        """Verify explain rejects source files that cannot be read."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "description": "autofix",
                },
            ), mock.patch.object(
                skills_commands,
                "_skill_sections",
                side_effect=PermissionError("permission denied"),
            ):
                result = skills_commands.explain_skill(Path.cwd(), "autofix")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("could not be read", result.errors[0].message)

    def test_reviewers_resolve_json_contract(self):
        """Verify ask reviewers resolve exposes the reviewer handle namespace."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "resolve", "skillinspector", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output["data"]["resolution"]
        self.assertEqual(resolution["status"], "ok")
        self.assertEqual(resolution["kind"], "reviewer")
        self.assertEqual(resolution["command_visibility"], "reviewer")
        self.assertEqual(resolution["canonical_handle"], "skill-inspector")

    def test_reviewers_resolve_human_output(self):
        """Verify ask reviewers resolve has a useful non-JSON success render."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "resolve", "skillinspector"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Reviewer handle: @skill-inspector", result.stdout)
        self.assertIn("codex/agents/skill-inspector/skill-inspector.toml", result.stdout)

    def test_skills_invalid_action_mentions_proof(self):
        """Verify invalid skill-action guidance includes the public proof command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "nonsense", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        suggestion = output["errors"][0]["fix_suggestion"]
        self.assertIn("proof", suggestion)

    def test_skills_goal_json_contract(self):
        """
        Ensure the `ask skills goal create` CLI returns a JSON envelope containing a `goal_decision` with required fields.

        Asserts the top-level `status` and `data` keys exist and that `data.goal_decision` includes `schema_version`, `decision_status`, `policy_identity`, `recommended_candidate`, and `alternative_candidates`.
        """
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "goal", "create auth integration", "--json"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("data", output)
        self.assertIn("goal_decision", output["data"])
        goal = output["data"]["goal_decision"]
        self.assertEqual(goal.get("schema_version"), "goal-decision.v1")
        self.assertIn("decision_status", goal)
        self.assertIn("policy_identity", goal)
        self.assertIn("recommended_candidate", goal)
        self.assertIn("alternative_candidates", goal)

    def test_skills_improve_json_contract(self):
        """Verify `ask skills improve` returns an agent-facing recommendation envelope."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "skills",
            "improve",
            "autofix",
            "--robot",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        improvement = output.get("data", {}).get("improvement", {})
        self.assertEqual(improvement.get("schema_version"), "skill-improvement-recommendation.v1")
        self.assertIn(improvement.get("route_state"), {"resolved", "resolved_with_fallback"})
        self.assertIn("route_state_reason", improvement)
        self.assertIn("goal_decision_status", improvement)
        self.assertIn("agent_summary", improvement)
        self.assertIn("recommended_capability", improvement)
        self.assertIn("why", improvement)
        self.assertIn("reachability", improvement)
        self.assertIn("proof", improvement)
        self.assertIn("why", improvement)
        self.assertIn("next_command", improvement)

    def test_repo_doctor_catalog_json_contract(self):
        """
        Verify `ask repo doctor-catalog --json` returns a catalog parity payload with required fields.

        Asserts the CLI emits non-empty JSON and that `data.catalog_parity` contains `schema_version`, `drift_detected` and `surfaces`.
        """
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "doctor-catalog", "--json"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("catalog_parity", output.get("data", {}))
        report = output["data"]["catalog_parity"]
        self.assertEqual(report.get("schema_version"), "catalog-parity.v1")
        self.assertIn("drift_detected", report)
        self.assertIn("surfaces", report)

    def test_repo_doctor_json_contract(self):
        """Verify `ask repo doctor --json` exposes the golden-path payload."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "doctor",
            "--robot",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        doctor = output.get("data", {}).get("doctor", {})
        self.assertIn("agent_summary", doctor)
        self.assertIn("blocking", doctor)
        self.assertIn("blockers", doctor)
        self.assertIn("next_command", doctor)
        self.assertIn("signals", doctor)
        self.assertIn("diagnostic_debt", doctor)

    def test_repo_doctor_help_mentions_agent_health_entrypoint(self):
        """Verify `ask repo doctor --help` exposes the agent health wording."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "doctor", "--help"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Agent-facing repository health entrypoint", result.stdout)

    def test_repo_closeout_json_contract(self):
        """Verify `ask repo closeout --changed --json` exposes readiness fields."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "closeout",
            "--changed",
            "--robot",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        closeout = output.get("data", {}).get("repo_closeout", {})
        self.assertIn("changed_files", closeout)
        self.assertIn("sync", closeout)
        self.assertIn("runtime_budget", closeout)
        self.assertIn("surface_policy", closeout)
        self.assertIn("focused_validation", closeout)
        self.assertIn("commit_readiness", closeout)
        self.assertIn("next_command", closeout)

    def test_repo_closeout_help_mentions_completion_readiness(self):
        """Verify `ask repo closeout --help` exposes completion-readiness wording."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "closeout", "--help"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("commit readiness", result.stdout)

    def test_goal_alias_normalization(self):
        """
        Ensure the `goal create` CLI alias returns a skills-style goal decision in the JSON envelope.

        Runs `bin/ask goal create auth integration --json`, asserts stdout contains JSON and that `data.goal_decision` exists.
        """
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "goal", "create auth integration", "--json"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("goal_decision", output.get("data", {}))

    def test_goal_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json goal alias maps to ask skills goal."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "--json", "goal", "create auth integration"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("goal_decision", output.get("data", {}))

    def test_doctor_catalog_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json doctor catalog alias maps to repo doctor-catalog."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "--json", "doctor", "catalog"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("catalog_parity", output.get("data", {}))

    def test_skills_starter_mode(self):
        """
        Verify the CLI `skills starter` command returns starter-mode catalogue metadata for the chosen archetype.

        Runs `bin/ask skills starter --archetype delivery --limit 5 --json` and asserts the process exits with code 0, the JSON envelope `status` is `"success"`, `data.starter_mode` is truthy, `data.starter_archetype` equals `"delivery"`, and `data.skills` is a list.
        """
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "skills", "starter", "--archetype", "delivery", "--limit", "5", "--json"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f"skills starter failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("starter_mode"))
        self.assertEqual(output["data"].get("starter_archetype"), "delivery")
        self.assertIsInstance(output["data"].get("skills"), list)

    def test_skills_package_command(self):
        """Verify ask skills package exposes package readiness metadata."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "package", "skill-builder", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        package = output["data"]["skill_package"]
        self.assertEqual(package["schema_version"], "skill-package-readiness.v1")
        self.assertEqual(package["target_summary"]["handle"], "skill-builder")
        self.assertEqual(package["target_summary"]["target_kind"], package["target_kind"])
        self.assertIn("version", package["package_contract"]["required_fields"]["present"])
        self.assertEqual(package["readiness_summary"]["readiness_level"], package["package_contract"]["readiness_level"])
        self.assertIn("version", package["readiness_summary"]["present_fields"])
        self.assertEqual(
            package["readiness_summary"]["missing_field_count"],
            len(package["package_contract"]["required_fields"]["missing"]),
        )
        self.assertEqual(package["gate_summary"]["promotion_status"], "blocked_validation")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        self.assertFalse(package["package_contract"]["install_gate"]["install_ready"])
        self.assertEqual(package["package_contract"]["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(package["package_contract"]["promotion_gate"]["status"], "blocked_validation")
        self.assertFalse(package["package_contract"]["promotion_gate"]["promotion_ready"])
        self.assertEqual(package["contract_schemas"]["package"], "skill-package-readiness.v1")
        self.assertEqual(package["contract_schemas"]["profiles"], "skill-operation-profiles.v1")
        self.assertEqual(package["operation_context"]["primary_profile"], "package-review")
        self.assertEqual(package["operation_context"]["promotion_profile"], "plugin-share")
        self.assertIn("metadata contract", package["operation_context"]["profiles"]["package-review"]["required_evidence"])
        self.assertIn(
            "./bin/ask skills package <handle-or-path> --json --robot",
            package["operation_context"]["events"]["package_readiness_checked"]["producer_commands"],
        )
        self.assertIn(
            "./bin/ask skills events package_readiness_checked --json --robot",
            package["operation_context"]["validation_commands"],
        )
        self.assertEqual(package["lifecycle_events"][1]["details"]["gate_summary"], package["gate_summary"])
        self.assertEqual(package["lifecycle_events"][1]["event_identity"]["event_type"], "package_readiness_checked")
        self.assertEqual(package["lifecycle_events"][1]["event_identity"]["subject_key"], "skill-builder")
        self.assertEqual(
            package["lifecycle_events"][1]["contract_schemas"]["lifecycle_event"],
            "capability-lifecycle-event.v1",
        )
        self.assertEqual(
            package["lifecycle_events"][1]["producer_command"],
            "./bin/ask skills package <handle-or-path> --json --robot",
        )
        self.assertEqual(
            package["lifecycle_events"][1]["observer_command"],
            "./bin/ask skills events package_readiness_checked --json --robot",
        )
        self.assertIn("package_readiness_checked", package["lifecycle_event_types"])

    def test_skills_package_human_output(self):
        """Verify ask skills package has a useful non-JSON readiness render."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "package", "skill-builder", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill package: skill-builder", result.stdout)
        self.assertIn("Install ready:", result.stdout)
        self.assertIn("Promotion:", result.stdout)
        self.assertIn("Next:", result.stdout)

    def test_skills_package_checkout_test_command_records_evidence(self):
        """Verify ask skills package --checkout-test records local install-gate evidence."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "skill-builder",
            "--checkout-test",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package checkout output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        package = output["data"]["skill_package"]
        checkout = package["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "blocked_validation")
        self.assertEqual(package["gate_summary"]["checkout_test_status"], "blocked_validation")
        self.assertEqual(package["gate_summary"]["promotion_status"], "blocked_validation")
        self.assertIn("source_readable:true", checkout["evidence"])
        self.assertTrue(any(item.startswith("missing_package_metadata:") for item in checkout["evidence"]))

    def test_skills_package_strict_command_blocks_metadata_gaps(self):
        """Verify ask skills package --strict fails closed in JSON and exit status."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "package", "skill-builder", "--strict", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills package strict output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        package = output["data"]["skill_package"]
        self.assertTrue(package["strict"])
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(package["blockers"][0]["class"], "blocked_validation")
        self.assertIn("compatible_roles", package["package_contract"]["required_fields"]["missing"])
        self.assertIn("compatible_roles", package["package_contract"]["install_gate"]["blocked_reasons"])
        self.assertIn("package_readiness_checked", package["lifecycle_event_types"])

    def test_skills_doctor_command_exposes_lifecycle_and_readiness(self):
        """Verify ask skills doctor exposes lifecycle and readiness contracts."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "doctor", "Skills/agent-ops/autofix", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills doctor failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        doctor = output["data"]["skill_doctor"]
        self.assertEqual(doctor["schema_version"], "skill-doctor.v1")
        self.assertEqual(doctor["target_kind"], "canonical_source_path")
        self.assertEqual(doctor["target_summary"]["query"], "Skills/agent-ops/autofix")
        self.assertEqual(doctor["target_summary"]["canonical_source_path"], doctor["canonical_source_path"])
        self.assertIn("canonical_source", doctor["check_summary"]["check_names"])
        self.assertEqual(doctor["check_summary"]["check_count"], len(doctor["checks"]))
        self.assertIn("missing", doctor["check_summary"]["status_counts"])
        self.assertEqual(doctor["lifecycle_event"]["schema_version"], "capability-lifecycle-event.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_type"], "skill_doctor_completed")
        self.assertEqual(doctor["lifecycle_event"]["contract_schemas"]["events"], "skill-events.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_identity"]["target_kind"], "canonical_source_path")
        self.assertEqual(doctor["lifecycle_event"]["event_identity"]["subject_key"], "Skills/agent-ops/autofix")
        self.assertEqual(
            doctor["lifecycle_event"]["producer_command"],
            "./bin/ask skills doctor <handle-or-path> --json --robot",
        )
        self.assertEqual(
            doctor["lifecycle_event"]["observer_command"],
            "./bin/ask skills events skill_doctor_completed --json --robot",
        )
        self.assertIn("blocked_user_input", doctor["readiness_taxonomy"]["blockers"])
        self.assertEqual(doctor["contract_schemas"]["doctor"], "skill-doctor.v1")
        self.assertEqual(doctor["contract_schemas"]["events"], "skill-events.v1")
        self.assertEqual(doctor["operation_context"]["primary_profile"], "authoring")
        self.assertIn("package-review", doctor["operation_context"]["next_profiles"])
        self.assertIn("skill audit", doctor["operation_context"]["profiles"]["authoring"]["required_evidence"])
        self.assertIn(
            "./bin/ask skills doctor <handle-or-path> --json --robot",
            doctor["operation_context"]["events"]["skill_doctor_completed"]["producer_commands"],
        )
        self.assertIn(
            "./bin/ask skills events skill_doctor_completed --json --robot",
            doctor["operation_context"]["validation_commands"],
        )
        self.assertIn("eval_blocked", doctor["lifecycle_event_types"])
        package_readiness = doctor["checks"]["capability_metadata"]["package_readiness"]
        self.assertIn("version", package_readiness["required_fields"]["present"])
        self.assertFalse(package_readiness["promotion_gate"]["share_ready"])
        package_contract = doctor["checks"]["capability_metadata"]["package_contract"]
        self.assertEqual(package_contract["role_compatibility"], package_readiness["role_compatibility"])
        self.assertEqual(package_contract["runtime_contract"], package_readiness["runtime_contract"])
        self.assertEqual(package_contract["install_gate"], package_readiness["install_gate"])
        self.assertEqual(package_contract["promotion_gate"], package_readiness["promotion_gate"])

    def test_skills_profiles_command_returns_selected_profile(self):
        """Verify ask skills profiles exposes one operation-mode contract."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "eval", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills profiles failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        profiles = output["data"]["skill_profiles"]
        self.assertEqual(profiles["schema_version"], "skill-operation-profiles.v1")
        self.assertEqual(profiles["selected_profile"], "eval")
        self.assertEqual(profiles["profile_names"], ["eval"])
        self.assertIn("package-review", profiles["available_profiles"])
        self.assertEqual(profiles["profile_summary"]["profile_count"], 1)
        self.assertIn("artifact_write_only", profiles["profile_summary"]["by_write_policy"])
        self.assertIn("repo_read", profiles["profile_summary"]["by_permission"])
        self.assertEqual(list(profiles["profiles"]), ["eval"])
        self.assertEqual(profiles["operation_context"]["profile_model"], "profile-v2-inspired")
        self.assertEqual(profiles["operation_context"]["contract_schemas"]["doctor"], "skill-doctor.v1")
        self.assertEqual(profiles["operation_context"]["contract_schemas"]["memory"], "skill-memory-provider.v1")
        self.assertIn("eval", profiles["operation_context"]["routing_contracts"]["events"])
        self.assertEqual(
            profiles["operation_context"]["consumer_commands"]["events"],
            "./bin/ask skills events --json --robot",
        )
        self.assertIn("Skills", profiles["workspace_roots"]["canonical_skill_roots"])
        self.assertIn(".agents/skills", profiles["workspace_roots"]["runtime_projection_roots"])
        self.assertIn("timeout_no_output", profiles["profiles"]["eval"]["stop_conditions"])
        self.assertIn("timeout_no_output", profiles["profiles"]["eval"]["stop_condition_definitions"])
        self.assertIn("blocked_user_input", profiles["profiles"]["eval"]["eval_blocker_classes"])
        self.assertEqual(
            profiles["profiles"]["eval"]["effective_roots"],
            ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        )

    def test_skills_profiles_human_output(self):
        """Verify ask skills profiles has a useful non-JSON selected-profile render."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "package-review", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills profiles output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill profiles: pass", result.stdout)
        self.assertIn("Profile: package-review", result.stdout)
        self.assertIn("Intent: Check a skill or plugin package before promotion.", result.stdout)
        self.assertIn("Write policy: reports_only_unless_fix_requested", result.stdout)

    def test_skills_profiles_command_blocks_unknown_profile(self):
        """Verify ask skills profiles fails closed for unknown operation modes."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "unsafe-live-linear", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills profiles output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        profiles = output["data"]["skill_profiles"]
        self.assertEqual(profiles["status"], "blocked")
        self.assertEqual(profiles["requested_profile"], "unsafe-live-linear")
        self.assertIn("live-mutation", profiles["available_profiles"])

    def test_skills_events_command_returns_lifecycle_contract(self):
        """Verify ask skills events exposes the lifecycle event contract."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills events failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        events = output["data"]["skill_events"]
        self.assertEqual(events["schema_version"], "skill-events.v1")
        self.assertEqual(events["event_schema"], "capability-lifecycle-event.v1")
        self.assertEqual(events["contract_schemas"]["profiles"], "skill-operation-profiles.v1")
        self.assertEqual(events["contract_schemas"]["package"], "skill-package-readiness.v1")
        self.assertGreaterEqual(events["event_count"], 8)
        self.assertIn("eval_blocked", events["event_names"])
        self.assertIn("skill_loaded", events["available_event_types"])
        self.assertEqual(events["event_summary"]["event_count"], events["event_count"])
        self.assertGreaterEqual(events["event_summary"]["by_profile"]["eval"], 1)
        self.assertIn("./bin/ask skills events --json --robot", events["validation_commands"])
        self.assertIn("eval_blocked", events["event_types"])
        self.assertIn("eval", events["event_consumers"]["eval_blocked"]["profiles"])
        self.assertIn("./bin/ask skills prove <handle> --json --robot", events["event_consumers"]["eval_completed"]["producer_commands"])
        self.assertIn("blocked_user_input", events["eval_blocker_classes"])
        self.assertIn("timeout_partial_output", events["eval_blocker_classes"])
        self.assertEqual(events["blocker_taxonomy"]["blocked_auth"], events["eval_blocker_classes"]["blocked_auth"])
        self.assertIn("strict_audit_not_run", events["warning_taxonomy"])
        self.assertIn("skill_doctor_completed", events["event_order"])
        self.assertEqual(events["selected_event_type"], None)

    def test_skills_events_command_returns_selected_event(self):
        """Verify ask skills events can narrow to a single event type."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "eval_blocked", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills events failed: {result.stderr}")
        output = json.loads(result.stdout)
        events = output["data"]["skill_events"]
        self.assertEqual(events["selected_event_type"], "eval_blocked")
        self.assertEqual(events["event_names"], ["eval_blocked"])
        self.assertIn("eval_completed", events["available_event_types"])
        self.assertEqual(events["event_summary"]["event_count"], 1)
        self.assertEqual(list(events["event_types"]), ["eval_blocked"])
        self.assertEqual(list(events["event_consumers"]), ["eval_blocked"])
        self.assertEqual(events["contract_schemas"]["events"], "skill-events.v1")
        self.assertIn("blocker", events["event_types"]["eval_blocked"])
        self.assertIn("eval", events["event_consumers"]["eval_blocked"]["profiles"])
        self.assertIn("blocked_auth", events["eval_blocker_classes"])

    def test_skills_events_human_output(self):
        """Verify ask skills events has a useful non-JSON selected-event render."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "eval_blocked", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills events output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill events: pass", result.stdout)
        self.assertIn("Event: eval_blocked", result.stdout)
        self.assertIn("Definition:", result.stdout)

    def test_skills_events_command_blocks_unknown_event(self):
        """Verify ask skills events fails closed for unknown event types."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "made_up_event", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills events output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        events = output["data"]["skill_events"]
        self.assertEqual(events["status"], "blocked")
        self.assertEqual(events["requested_event_type"], "made_up_event")
        self.assertIn("eval_blocked", events["available_event_types"])

    def test_skills_memory_search_command_returns_provider_entries(self):
        """Verify ask skills memory search exposes provenance-bearing entries."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "memory", "search", "projection", "--limit", "3", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory search failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["schema_version"], "skill-memory-provider.v1")
        self.assertEqual(memory["provider_model"], "extension-like-read-only")
        self.assertEqual(memory["contract_schemas"]["memory"], "skill-memory-provider.v1")
        self.assertEqual(memory["contract_schemas"]["profiles"], "skill-operation-profiles.v1")
        self.assertEqual(memory["operation_context"]["provider_model"], "extension-like-read-only")
        self.assertEqual(memory["operation_context"]["provider_contract"]["mutation_policy"], "read_only")
        self.assertIn("provenance", memory["operation_context"]["provider_contract"]["required_entry_fields"])
        self.assertIn("eval", memory["operation_context"]["consumer_profiles"])
        self.assertIn("./bin/ask memory search projection --json --robot", memory["operation_context"]["validation_commands"])
        self.assertGreaterEqual(memory["source_summary"]["source_count"], 1)
        self.assertEqual(memory["mode"], "search")
        self.assertGreaterEqual(memory["entry_count"], 1)
        self.assertEqual(memory["entry_summary"]["returned_count"], memory["entry_count"])
        self.assertGreaterEqual(memory["entry_summary"]["total_count"], memory["entry_count"])
        self.assertIn("provenance", memory["entries"][0])
        self.assertIn("freshness", memory["entries"][0])

    def test_skills_memory_search_command_blocks_missing_query(self):
        """Verify ask skills memory search requires a query from the CLI path."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "memory", "search", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills memory output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["status"], "blocked")
        self.assertEqual(memory["mode"], "search")
        self.assertIn("requires a non-empty query", memory["agent_summary"])

    def test_skills_memory_search_command_blocks_negative_limit(self):
        """Verify ask skills memory search rejects negative limits."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "search",
            "projection",
            "--limit",
            "-1",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills memory output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["status"], "blocked")
        self.assertEqual(memory["mode"], "search")
        self.assertIn("limit must be non-negative", memory["agent_summary"])

    def test_skills_memory_list_source_filter_limits_entries(self):
        """Verify ask skills memory list preserves provider source filtering."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "list",
            "--source",
            "harness-solutions",
            "--limit",
            "2",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["entry_count"], 2)
        self.assertGreaterEqual(memory["total_count"], 2)
        self.assertIn("./bin/ask skills memory search <query> --json --robot", memory["operation_context"]["follow_up_commands"])
        self.assertTrue(all(entry["source_id"] == "harness-solutions" for entry in memory["entries"]))

    def test_skills_memory_read_command_returns_content_and_provenance(self):
        """Verify ask skills memory read exposes durable content with provenance."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "read",
            ".harness/memory/LEARNINGS.md",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["mode"], "read")
        entry = memory["entry"]
        self.assertEqual(entry["path"], ".harness/memory/LEARNINGS.md")
        self.assertEqual(entry["provenance"]["provider"], "harness-memory")
        self.assertIn("# Learnings", entry["content"])

    def test_skills_memory_read_command_blocks_missing_identifier(self):
        """Verify ask skills memory read fails closed without an entry id."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "memory", "read", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["status"], "blocked")
        self.assertEqual(memory["mode"], "read")
        self.assertIn("requires an entry id", memory["agent_summary"])

    def test_memory_search_command_returns_provider_entries(self):
        """Verify ask memory search exposes the same provenance-bearing provider entries."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "search", "projection", "--limit", "1", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory search failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        memory = output["data"]["memory"]
        self.assertEqual(memory["schema_version"], "memory-provider.v1")
        self.assertEqual(memory["count"], 1)
        entry = memory["results"][0]
        self.assertEqual(entry["provenance"]["provider"], entry["source_id"])
        self.assertEqual(entry["provenance"]["repo_relative_path"], entry["path"])

    def test_memory_search_human_output_lists_entry_paths(self):
        """Verify ask memory search has a useful non-JSON provider render."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "search", "projection", "--limit", "1", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Found 1 memory entry.", result.stdout)
        self.assertIn("docs-agent-guidance:docs-agents-04-validation-md", result.stdout)
        self.assertIn("Docs/agents/04-validation.md", result.stdout)

    def test_memory_list_source_filter_limits_entries(self):
        """Verify ask memory list honors source filtering from the CLI path."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "memory",
            "list",
            "--source",
            "harness-solutions",
            "--limit",
            "2",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["memory"]
        self.assertEqual(memory["count"], 2)
        self.assertGreaterEqual(memory["total_count"], 2)
        self.assertTrue(all(entry["source_id"] == "harness-solutions" for entry in memory["entries"]))

    def test_memory_list_command_blocks_negative_limit(self):
        """Verify ask memory list rejects negative limits."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "list", "--limit", "-1", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("limit must be non-negative", output["errors"][0]["message"])

    def test_memory_read_command_returns_content_and_provenance(self):
        """Verify ask memory read exposes durable content with provenance."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "memory",
            "read",
            ".harness/memory/LEARNINGS.md",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["memory"]
        entry = memory["entry"]
        self.assertEqual(entry["path"], ".harness/memory/LEARNINGS.md")
        self.assertEqual(entry["provenance"]["provider"], "harness-memory")
        self.assertIn("# Learnings", entry["content"])

    def test_memory_read_command_blocks_missing_identifier(self):
        """Verify ask memory read parser reports the missing identifier clearly."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "read", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("arguments are required: identifier", output["errors"][0]["message"])
        self.assertIn("ask memory read .harness/memory/LEARNINGS.md --json", output["errors"][0]["message"])

    def test_memory_command_blocks_missing_action(self):
        """Verify ask memory fails closed when no provider mode is selected."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])

    def test_plugins_list_state(self):
        """CA1: Verify ask plugins list returns lifecycle state groups."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "list", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins list failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("installed_state", output["data"])
        self.assertIn("activation_state", output["data"])
        self.assertIn("health_state", output["data"])

    def test_skills_sync_dry_run(self):
        """CA2: Verify ask skills sync --dry-run returns a plan without changes."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "sync", "--dry-run", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("plan", output["data"])
        self.assertIn("symlinks", output["data"]["plan"])

    def test_runtime_surface_json_contract(self):
        """Verify ask runtime surface exposes the runtime report under an obvious topic."""
        # Pin projection mode so assertions remain deterministic regardless of ambient runtime.
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "surface", "--json"]
            result = _run_cli(cmd)

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "success")
            report = output["data"]["runtime_surface"]
            self.assertIn(report["projection_mode"], {"flat", "rooted"})
            self.assertIn("first_level_default_entries", report)
            self.assertIn("hidden_system_entries", report)
            self.assertIn("estimated_description_tokens", report)
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_runtime_budget_json_contract(self):
        """Verify ask runtime budget remains a first-class budget gate command."""
        # Pin SYNC_SKILLS_PROJECTION_MODE to ensure deterministic test behavior.
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "budget", "--json"]
            result = _run_cli(cmd)

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "success")
            self.assertEqual(output["data"]["runtime_budget"]["status"], "pass")
            self.assertEqual(output["data"]["runtime_surface"]["status"], "pass")
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_skills_sync_projection_reaches_engine(self):
        """Verify --projection is dispatched and cannot be silently ignored."""
        for mode in ("flat", "rooted"):
            with self.subTest(mode=mode):
                cmd = [
                    "python3",
                    "Infrastructure/bin/ask",
                    "skills",
                    "sync",
                    "--scope",
                    "workspace",
                    "--projection",
                    mode,
                    "--dry-run",
                    "--json",
                ]
                result = _run_cli(cmd)

                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                self.assertEqual(output["status"], "success")
                self.assertEqual(output["data"]["projection_mode"], mode)
                self.assertEqual(output["data"]["projection"]["engine"], "projection_engine.py")

    def test_skills_sync_rooted_alias_dry_run_reports_canonical_mode(self):
        """Rooted aliases must report the canonical projection mode in dry-run plans."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "skill-tree",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["projection_mode"], "rooted")
        self.assertEqual(output["data"]["projection"]["requested_mode"], "skill-tree")
        self.assertEqual(output["data"]["plan"]["validation_status"], "pass")

    def test_skills_sync_rejects_deferred_hybrid_projection(self):
        """Hybrid remains out of mutating scope until a named consumer exists."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "hybrid",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIsNone(output["data"]["projection_mode"])
        self.assertEqual(output["data"]["requested_projection_mode"], "hybrid")
        self.assertEqual(output["errors"][0]["code"], "ERR_DEFERRED_PROJECTION_MODE")

    def test_skills_install_dry_run(self):
        """CA2: Verify ask skills install --dry-run returns a plan without making changes."""
        # Using --dry-run to avoid actual network calls and mutations
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "install", "https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication", "--dry-run", "--json"]
        result = _run_cli(cmd)

        # Dry run should succeed and return installation plan
        output = json.loads(result.stdout)
        self.assertIn(output["status"], ["success", "error"])
        if output["status"] == "success":
            self.assertIn("skill_name", output["data"])
            self.assertTrue(output["data"].get("dry_run", False), "Expected dry_run to be True")
            intake = output["data"].get("intake_decision")
            self.assertIsInstance(intake, dict)
            self.assertEqual(intake.get("schema_version"), "skill-install-intake.v1")
            self.assertIn(intake.get("outcome"), intake.get("allowed_outcomes", []))
            self.assertIn("post_install_gates", intake)
            readiness = output["data"].get("readiness_policy")
            self.assertTrue(readiness.get("full_evals_required_before_promotion"))
            self.assertTrue(readiness.get("external_skill_install_is_intake_not_copy"))

    def test_trace_id_from_env(self):
        """CA2: ASK_TRACE_ID environment variable propagates to output."""
        env = os.environ.copy()
        env["ASK_TRACE_ID"] = "test-trace-123"
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json"]
        result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["trace_id"], "test-trace-123")

    def test_trace_id_flag_overrides_env(self):
        """CA2: --trace-id flag overrides ASK_TRACE_ID environment variable."""
        env = os.environ.copy()
        env["ASK_TRACE_ID"] = "env-trace-456"
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json", "--trace-id", "flag-trace-789"]
        result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["trace_id"], "flag-trace-789")  # Flag wins

    def test_robot_mode_recovers_swapped_topic_action(self):
        """Robot mode should recover clear intent when topic/action are swapped."""
        cmd = ["python3", "Infrastructure/bin/ask", "list", "skills", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"Expected success, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("skills", output.get("data", {}))
        self.assertIn("correction_note", output.get("metadata", {}))

    def test_robot_mode_recovers_action_after_flags(self):
        """Robot mode should recover when action token is after option flags."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "--advanced", "ls", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"Expected success, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("advanced_mode"))
        self.assertIn("correction_note", output.get("metadata", {}))

    def test_robot_mode_returns_detailed_error_for_ambiguous_intent(self):
        """Robot mode should return rich guidance when intent cannot be resolved."""
        cmd = ["python3", "Infrastructure/bin/ask", "status", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        message = output["errors"][0]["message"]
        self.assertIn("Guidance", message)
        self.assertIn("Try one of these", message)
        self.assertIn("repo status", message)

    def test_robot_mode_returns_argument_guidance_when_intent_clear(self):
        """Robot mode should explain missing arguments with command-specific examples."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "audit", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        message = output["errors"][0]["message"]
        self.assertIn("Command intent was understood", message)
        self.assertIn("ask skills audit --help", message)
        self.assertIn("Valid examples", message)
        self.assertIn("skills audit", message)

    def test_skills_validate_openai_format_json_contract(self):
        """Verify ask exposes OpenAI skill format as a first-class validation surface."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-openai-format",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        gate = output["data"]["openai_skill_format"]
        self.assertEqual(gate["exit_code"], 0)
        self.assertIn("lint_openai_skill_format.sh", " ".join(gate["command"]))

    def test_skills_validate_skill_gate_json_contract(self):
        """Verify ask exposes skill gate as a first-class validation surface."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-skill-gate",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        gate = output["data"]["skill_gate"]
        self.assertEqual(gate["exit_code"], 0)
        self.assertTrue(any("skill_gate.py" in part for part in gate["command"]))

    def test_skills_validate_boundaries_json_contract(self):
        """Verify ask exposes canonical-versus-projection ownership as a first-class check."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-boundaries",
            "he-heartbeat",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        boundary = output["data"]["boundary_check"]
        self.assertEqual(boundary["status"], "pass")
        self.assertEqual(boundary["handle"], "he-heartbeat")
        self.assertIn(".agents/skills/", boundary["command_handle_path"])
        self.assertTrue(boundary["canonical_skill_path"])

if __name__ == "__main__":
    unittest.main()
