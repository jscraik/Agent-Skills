from scenario_quality_test_support import *  # noqa: F403


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_builder_blocks_missing_evals_yaml(self) -> None:
        with self.assertRaises(ScenarioQualityError) as raised:
            build_scenario_quality_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / INVALID_SKILL / "SKILL.md",
                query=INVALID_SKILL,
            )

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["scenario_count"], 0)
        self.assertTrue(any(check["id"] == "evals_yaml_present" for check in receipt["blockers"]))

    def test_builder_blocks_direct_registry_reference_in_evals_without_adaptation_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml())

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(
            any(check["id"] == "registry_reference_requires_sdk_adaptation_receipt" for check in receipt["blockers"])
        )

    def test_builder_allows_registry_reference_after_sdk_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)
        quality_check_ids = {check["id"]: check["status"] for check in receipt["quality_checks"]}
        self.assertEqual(quality_check_ids["registry_reference_requires_sdk_adaptation_receipt"], "pass")

    def test_builder_allows_repo_relative_target_skill_path_in_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            target_path = skill_dir.relative_to(REPO_ROOT).as_posix()
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                target_path=target_path,
            )

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)

    def test_builder_blocks_basename_only_target_skill_path_in_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                target_path=skill_dir.name,
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("target_skill_mismatch", evidence)

    def test_builder_blocks_wrong_package_id_in_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                package_id="other-skill",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("target_skill_mismatch", evidence)

    def test_builder_allows_nested_registry_reference_after_sdk_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)

    def test_builder_allows_nested_registry_source_after_sdk_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_source_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)

    def test_builder_blocks_registry_source_digest_mismatch(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _registry_source_evals_yaml(registry_id, digest="sha256:expected"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                digest="sha256:stale",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_nested_registry_source_version_mismatch(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _nested_registry_source_evals_yaml(registry_id, version="0.2.0"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                version="0.1.0",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_nested_registry_source_digest_mismatch(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _nested_registry_source_evals_yaml(registry_id, digest="sha256:expected"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                digest="sha256:stale",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_pass_adaptation_receipt_with_failed_validation_row(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                validation_status="fail",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("schema_invalid", evidence)
        self.assertIn("validation[0].status:const", evidence)

    def test_builder_blocks_registry_source_id_prefix_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _nested_registry_reference_evals_yaml("registry://shared/proof-boundary-v2"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id="registry://shared/proof-boundary",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_partial_adaptation_receipt_missing_schema_required_fields(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                include_full_schema_fields=False,
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("receipt_missing_required_fields", evidence)
        self.assertIn("operation", evidence)

    def test_builder_blocks_adaptation_receipt_missing_full_schema_fields(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            receipt_path = _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)
            payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            payload.pop("validation")
            payload.pop("mutation_manifest")
            receipt_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        evidence = "\n".join(
            evidence
            for check in raised.exception.receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("receipt_missing_required_fields", evidence)
        self.assertIn("validation", evidence)
        self.assertIn("mutation_manifest", evidence)

    def test_builder_blocks_text_duplicate_when_pinned_registry_source_digest_mismatches(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _mixed_pinned_and_text_registry_source_evals_yaml(registry_id, digest="sha256:expected"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                digest="sha256:stale",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        evidence = "\n".join(
            evidence
            for check in raised.exception.receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_direct_registry_reference_in_skill_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _plain_evals_yaml())
            (skill_dir / "SKILL.md").write_text(
                "---\nname: sample\n---\n# Sample\nLoad registry://shared/proof-boundary directly.\n",
                encoding="utf-8",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        self.assertTrue(
            any(check["id"] == "registry_reference_not_in_skill_entrypoint" for check in receipt["blockers"])
        )

    def test_no_direct_registry_validator_blocks_unauthenticated_ad_hoc_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml())
            process = subprocess.run(
                [
                    sys.executable,
                    "Infrastructure/scripts/validation-and-linting/validate_no_direct_registry_scenario_use.py",
                    skill_dir.as_posix(),
                    "--json",
                ],
                cwd=REPO_ROOT,
                env=_command_env(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(process.returncode, 1)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["blockers"][0]["id"], "registry_reference_requires_sdk_adaptation_receipt")

    def test_yaml_fallback_parses_fixture_without_subprocess(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = (REPO_ROOT / FIXTURE_SKILL / "references/evals.yaml").read_text(encoding="utf-8")
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        self.assertEqual(payload["cases"][0]["id"], "happy-scenario-quality")
        self.assertEqual(payload["cases"][0]["eval_modes"], ["smoke"])
        self.assertIsInstance(payload["cases"][0]["deterministic_checks"], dict)

    def test_yaml_fallback_ignores_claims_and_parses_root_aligned_cases(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: '2.0'
skill_name: sample
claims:
- id: sample.claim
  statement: ignored by fallback
cases:
- id: root-aligned-case
  category: pressure
  realistic: true
  eval_modes:
  - smoke
  prompt: Check the root-aligned case parser.
  acceptance:
  - type: expected_signal
    value: parsed
      continuation
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        self.assertEqual(payload["cases"][0]["id"], "root-aligned-case")
        self.assertEqual(payload["cases"][0]["eval_modes"], ["smoke"])
        self.assertEqual(payload["cases"][0]["acceptance"][0]["value"], "parsed continuation")
        self.assertEqual(payload["cases"][0]["claim_ids"], ["sample.claim"])
        self.assertIsInstance(payload["cases"][0]["deterministic_checks"], dict)

    def test_yaml_fallback_parses_legacy_expect_lists(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: 1
skill: sample
claims:
- id: sample.claim
  statement: ignored by fallback
cases:
- id: x-writer-style-case
  claim_ids:
  - sample.claim
  input: |-
    Turn this brief into an X launch thread.
  expect:
  - Includes two hook variants.
  - Keeps publication status draft-only when request_user_input
    is unavailable.
  - Keeps implementation ownership clear: Codex writes code; Jamie validates.
  prompt: |-
    Can you turn this brief into an X launch thread?
  acceptance:
  - type: regex
    value: "(?is)(claim_authority.*limited to supplied brief|no external factual claims)"
  eval_modes:
  - smoke
  deterministic_checks:
    forbidden_commands:
    - rm -rf
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        case = payload["cases"][0]
        self.assertEqual(case["id"], "x-writer-style-case")
        self.assertEqual(case["expect"][0], "Includes two hook variants.")
        self.assertEqual(case["expect"][1], "Keeps publication status draft-only when request_user_input is unavailable.")
        self.assertEqual(case["expect"][2], "Keeps implementation ownership clear: Codex writes code; Jamie validates.")
        self.assertEqual(case["eval_modes"], ["smoke"])
        self.assertEqual(case["claim_ids"], ["sample.claim"])
        self.assertIsInstance(case["deterministic_checks"], dict)

    def test_yaml_fallback_rejects_invalid_scalar_continuation(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: '2.0'
cases:
- id: invalid-continuation
  realistic: true
    continuation
"""
        with (
            mock.patch("builtins.__import__", side_effect=import_without_yaml),
            mock.patch("ask.skills_sdk.scenario_quality.subprocess.run", side_effect=FileNotFoundError()),
        ):
            with self.assertRaises(ValueError):
                _yaml_safe_load(evals_text)

    def test_builder_blocks_pyyaml_parse_errors(self) -> None:
        class FakeYAMLError(Exception):
            pass

        class FakeYaml:
            YAMLError = FakeYAMLError

            @staticmethod
            def safe_load(_text: str) -> object:
                raise FakeYAMLError("bad yaml")

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                "cases:\n- id: malformed\n  prompt: [unterminated\n",
            )
            with (
                mock.patch.dict(sys.modules, {"yaml": FakeYaml}),
                self.assertRaises(ScenarioQualityError) as raised,
            ):
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("evals_yaml_parse", blocker_ids)

    def test_builder_blocks_malformed_text_field_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: 1
cases:
- id: malformed-text-field
  eval_modes:
  - smoke
  prompt: Check structured output.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: text_field_in
    value: draft_only
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("typed_text_field_assertions_valid", blocker_ids)

    def test_builder_blocks_typed_field_assertions_with_empty_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: 1
cases:
- id: malformed-empty-values
  eval_modes:
  - smoke
  prompt: Check structured output.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: text_field_in
    field: status
    values: []
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("typed_text_field_assertions_valid", blocker_ids)

    def test_builder_blocks_regex_against_known_structured_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: 1
cases:
- id: regex-structured-field
  eval_modes:
  - smoke
  prompt: Check structured output.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: 'publication_gate_status:\\s*draft_only'
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("structured_fields_use_typed_assertions", blocker_ids)

    def test_builder_blocks_tessl_quality_mismatch_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: keyword-only-mismatch
  category: happy
  eval_modes:
  - smoke
  realistic: true
  prompt: Ask for an evidence-backed validation summary.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: '(?is)(evidence|validation)'
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:keyword_only_acceptance", blocker_ids)
        self.assertIn("platform_tessl_quality:missing_scenario_context", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

