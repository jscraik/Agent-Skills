from __future__ import annotations

from collections.abc import Callable
import sys
import json
import os
import subprocess
import tempfile
import unittest
import urllib.error
from unittest.mock import patch
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.cloud_catalog_probe import probe_catalog  # noqa: E402
from ask.skills_sdk.ab_profile_contracts import AbLanePreflight  # noqa: E402
from ask.skills_sdk.eval_ab_preflight import (  # noqa: E402
    _approved_cloud_auth_fact,
    _cloud_catalog_fact,
    _cloud_runtime_fact,
    _catalog_probe_result,
    build_lane_preflight,
    declared_profile_preflight,
)
from ask.skills_sdk.eval_profiles import select_judge_profile  # noqa: E402


class _CustomBoundarySignal(BaseException):
    pass


class _HostileEnvelope:
    returncode = 0
    stderr = ""

    def __init__(self, target: str, raised: BaseException, stdout: str) -> None:
        self._target = target
        self._raised = raised
        self.stdout = stdout

    def __getattribute__(self, name: str) -> object:
        if name in {"returncode", "stdout", "stderr"}:
            target = object.__getattribute__(self, "_target")
            if name == target:
                raised = object.__getattribute__(self, "_raised")
                raise raised
        return object.__getattribute__(self, name)


class TestSkillsSdkAbPreflight(unittest.TestCase):
    @staticmethod
    def _codex_fixture(root: Path, version: str = "codex-cli 1.2.3") -> Path:
        binary = root / "codex"
        binary.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
        binary.chmod(0o755)
        return binary

    @staticmethod
    def _catalog_process(
        payload: dict[str, object], returncode: int = 0, stderr: str = "",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            ["op", "run"], returncode, stdout=json.dumps(payload), stderr=stderr,
        )

    @staticmethod
    def _catalog_payload(result_class: str = "pass", **fields: object) -> dict[str, object]:
        return {
            "result_class": result_class,
            "network_accessed": True,
            "http_status": 200,
            "catalog_digest": "sha256:" + "a" * 64,
            "matched_model": "minimax-m2.7:cloud" if result_class == "pass" else None,
            "match_count": 1 if result_class == "pass" else 0,
            "secret_value_observed": False,
            "secret_not_observed": True,
            "generation_performed": False,
            "provider_invoked": False,
            "codex_exec_invoked": False,
            **fields,
        }

    @staticmethod
    def _cloud_runtime_not_applicable(candidate: dict[str, object]) -> dict[str, object]:
        facts = declared_profile_preflight(candidate)
        facts["runtime"] = _cloud_runtime_fact(
            str(candidate["model"]),
            Path("/mock/oss-cloud.config.toml"),
        )
        return facts

    @classmethod
    def _typed_catalog_blocker_payload(cls, result_class: str) -> dict[str, object]:
        if result_class == "model_ambiguous":
            return cls._catalog_payload(result_class=result_class, match_count=2)
        if result_class == "auth_missing":
            return cls._catalog_payload(
                result_class=result_class, network_accessed=False, http_status=None,
                catalog_digest=None, match_count=None,
            )
        if result_class == "http_failure":
            return cls._catalog_payload(
                result_class=result_class, http_status=403,
                catalog_digest=None, match_count=None,
            )
        if result_class in {"timeout", "network_failure"}:
            return cls._catalog_payload(
                result_class=result_class, http_status=None,
                catalog_digest=None, match_count=None,
            )
        if result_class in {"payload_too_large", "malformed_json", "malformed_catalog"}:
            return cls._catalog_payload(
                result_class=result_class, catalog_digest=None, match_count=None,
            )
        return cls._catalog_payload(result_class=result_class)

    def test_default_preflight_blocks_when_runtime_surfaces_are_absent(self) -> None:
        empty_environment = {"HOME": "/tmp/skills-sdk-empty-home", "PATH": "/tmp/skills-sdk-empty-bin"}
        with patch.dict("os.environ", empty_environment, clear=True):
            local = build_lane_preflight(select_judge_profile("oss-local"))
            cloud = build_lane_preflight(select_judge_profile("oss-cloud"))
        self.assertEqual(local["admission"]["status"], "blocked")
        self.assertEqual(cloud["admission"]["status"], "blocked")
        self.assertIn(
            "profile_config_missing_or_invalid",
            {item["blocker_class"] for item in local["admission"]["blockers"]},
        )
        self.assertIn(
            "profile_config_missing_or_invalid",
            {item["blocker_class"] for item in cloud["admission"]["blockers"]},
        )

    def test_installed_local_profile_catalog_and_runtime_inventory_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            catalog = root / "catalog.json"
            catalog.write_text(json.dumps({"models": [{"slug": "qwen3.5:9b-mlx"}]}), encoding="utf-8")
            (root / "oss-local.config.toml").write_text(
                f'model = "qwen3.5:9b-mlx"\nmodel_provider = "ollama"\nmodel_catalog_json = "{catalog}"\n',
                encoding="utf-8",
            )
            environment = {"CODEX_HOME": str(root), "HOME": str(root), "PATH": "/mock/bin"}
            inventory = subprocess.CompletedProcess(
                ["/mock/bin/ollama", "list"], 0,
                stdout="NAME ID SIZE MODIFIED\nqwen3.5:9b-mlx abc 9GB now\n", stderr="",
            )
            with (
                patch.dict("os.environ", environment, clear=True),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", side_effect=lambda name: f"/mock/bin/{name}"),
                patch("ask.skills_sdk.eval_ab_preflight.subprocess.run", return_value=inventory),
            ):
                admitted = build_lane_preflight(select_judge_profile("oss-local"))
            self.assertEqual(admitted["admission"]["status"], "pass")
            missing_model = subprocess.CompletedProcess(
                ["/mock/bin/ollama", "list"], 0,
                stdout="NAME ID SIZE MODIFIED\nother-model abc 9GB now\n", stderr="",
            )
            with (
                patch.dict("os.environ", environment, clear=True),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", side_effect=lambda name: f"/mock/bin/{name}"),
                patch("ask.skills_sdk.eval_ab_preflight.subprocess.run", return_value=missing_model),
            ):
                blocked = build_lane_preflight(select_judge_profile("oss-local"))
            self.assertIn(
                "local_model_unavailable",
                {item["blocker_class"] for item in blocked["admission"]["blockers"]},
            )

    def test_declared_profile_facts_record_configured_provider_and_model(self) -> None:
        local = declared_profile_preflight(select_judge_profile("oss-local"))
        cloud = declared_profile_preflight(select_judge_profile("oss-cloud"))
        self.assertEqual(local["profile_config"]["configured_model_id"], "qwen3.5:9b-mlx")
        self.assertEqual(local["profile_config"]["configured_provider_id"], "ollama")
        self.assertEqual(cloud["profile_config"]["configured_model_id"], "minimax-m2.7:cloud")
        self.assertEqual(cloud["profile_config"]["configured_provider_id"], "ollama-cloud")

    def test_required_typed_blockers_are_preserved(self) -> None:
        matrix = {
            "profile_config_missing_or_invalid": "profile_config",
            "model_catalog_entry_missing": "model_catalog",
            "local_runtime_unavailable": "runtime",
            "codex_cli_unavailable": "runtime",
            "local_runtime_binary_unavailable": "runtime",
            "local_runtime_service_unavailable": "runtime",
            "local_model_unavailable": "runtime",
            "cloud_auth_unavailable": "auth",
            "cloud_catalog_unavailable": "catalog",
            "selected_model_unavailable": "runtime",
            "preflight_evidence_missing": "catalog",
        }
        profile = select_judge_profile("oss-local")
        for blocker_class, field in matrix.items():
            with self.subTest(blocker_class=blocker_class):
                def probe(candidate: dict[str, object]) -> dict[str, object]:
                    facts = declared_profile_preflight(candidate)
                    facts[field] = {
                        **facts[field], "status": "blocked",
                        "blocker": {"blocker_class": blocker_class, "reason": "deterministic fixture"},
                    }
                    return facts
                receipt = build_lane_preflight(profile, probe)
                classes = {item["blocker_class"] for item in receipt["admission"]["blockers"]}
                self.assertIn(blocker_class, classes)
                self.assertEqual(receipt["admission"]["status"], "blocked")

    def test_required_facts_cannot_use_not_applicable_for_lane_admission(self) -> None:
        required_facts_by_lane = {
            "oss-local": ("profile_config", "model_catalog", "runtime", "catalog"),
            "oss-cloud": ("profile_config", "model_catalog", "catalog"),
        }
        for lane, required_facts in required_facts_by_lane.items():
            profile = select_judge_profile(lane)
            for fact_name in required_facts:
                with self.subTest(lane=lane, fact=fact_name):
                    def probe(candidate: dict[str, object]) -> dict[str, object]:
                        facts = declared_profile_preflight(candidate)
                        facts[fact_name] = {
                            **facts[fact_name],
                            "status": "not_applicable",
                            "blocker": None,
                        }
                        return facts
                    receipt = build_lane_preflight(profile, probe)
                    self.assertEqual(receipt["admission"]["status"], "blocked")
                    self.assertIn(
                        "preflight_evidence_missing",
                        {item["blocker_class"] for item in receipt["admission"]["blockers"]},
                    )

    def test_only_proven_cloud_endpoint_runtime_may_use_not_applicable(self) -> None:
        profile = select_judge_profile("oss-cloud")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            binary = self._codex_fixture(root)
            with patch.dict(os.environ, {"PATH": temp_dir}):
                receipt = build_lane_preflight(profile, self._cloud_runtime_not_applicable)
                self.assertEqual(receipt["admission"]["status"], "pass")
                AbLanePreflight.model_validate(receipt)
                substitutions = (
                    {"evidence_source": "/definitely/not/an/installed/codex"},
                    {"evidence_source": "PATH:codex"},
                    {"evidence_source": str(root / "alternate-codex")},
                    {"codex_executable_identity": "sha256:" + "0" * 64},
                    {"evidence_digest": "sha256:" + "0" * 64},
                    {"availability_kind": "local_model"},
                    {"selected_model_id": "fast"},
                    {"codex_executable_identity_copy": "sha256:" + "1" * 64},
                )
                for override in substitutions:
                    with self.subTest(override=override):
                        blocked = build_lane_preflight(
                            profile, self._forged_cloud_runtime(override),
                        )
                        self.assertEqual(blocked["admission"]["status"], "blocked")
                missing = build_lane_preflight(
                    profile, self._forged_cloud_runtime({}, missing_identity=True),
                )
                self.assertEqual(missing["admission"]["status"], "blocked")
                symlink = root / "alternate-codex"
                symlink.symlink_to(binary)
                substituted = build_lane_preflight(
                    profile, self._forged_cloud_runtime({"evidence_source": str(symlink)}),
                )
                self.assertEqual(substituted["admission"]["status"], "blocked")

    def test_changed_executable_content_invalidates_stored_cloud_identity(self) -> None:
        profile = select_judge_profile("oss-cloud")
        with tempfile.TemporaryDirectory() as temp_dir:
            binary = self._codex_fixture(Path(temp_dir))
            with patch.dict(os.environ, {"PATH": temp_dir}):
                receipt = build_lane_preflight(profile, self._cloud_runtime_not_applicable)
                self.assertEqual(receipt["admission"]["status"], "pass")
                AbLanePreflight.model_validate(receipt)
                binary.write_text("#!/bin/sh\n# changed bytes\nprintf '%s\\n' 'codex-cli 1.2.3'\n", encoding="utf-8")
                binary.chmod(0o755)
                with self.assertRaises(ValueError):
                    AbLanePreflight.model_validate(receipt)
                facts = {key: value for key, value in receipt.items() if key != "admission"}
                rebuilt = build_lane_preflight(profile, lambda _candidate: facts)
                self.assertEqual(rebuilt["admission"]["status"], "blocked")
                rebuilt["admission"] = {"status": "pass", "blockers": [], "secret_values_observed": False}
                with self.assertRaises(ValueError):
                    AbLanePreflight.model_validate(rebuilt)

    def test_invalid_codex_version_is_rejected_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._codex_fixture(Path(temp_dir), "not-codex 1.2.3")
            with patch.dict(os.environ, {"PATH": temp_dir}):
                receipt = build_lane_preflight(
                    select_judge_profile("oss-cloud"), self._cloud_runtime_not_applicable,
                )
        self.assertEqual(receipt["admission"]["status"], "blocked")

    def _forged_cloud_runtime(
        self, override: dict[str, object], *, missing_identity: bool = False,
    ) -> Callable[[dict[str, object]], dict[str, object]]:
        def probe(candidate: dict[str, object]) -> dict[str, object]:
            facts = self._cloud_runtime_not_applicable(candidate)
            facts["runtime"] = {**facts["runtime"], **override}
            if missing_identity:
                facts["runtime"].pop("codex_executable_identity", None)
            return facts
        return probe

    def test_local_lane_cannot_use_installed_cloud_runtime_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._codex_fixture(Path(temp_dir))
            def probe(candidate: dict[str, object]) -> dict[str, object]:
                facts = declared_profile_preflight(candidate)
                facts["runtime"] = _cloud_runtime_fact(
                    str(candidate["model"]), Path("/mock/oss-local.config.toml"),
                )
                return facts
            with patch.dict(os.environ, {"PATH": temp_dir}):
                receipt = build_lane_preflight(select_judge_profile("oss-local"), probe)
        self.assertEqual(receipt["admission"]["status"], "blocked")

    def test_only_local_auth_may_use_not_applicable(self) -> None:
        local = build_lane_preflight(select_judge_profile("oss-local"), declared_profile_preflight)
        self.assertEqual(local["auth"]["status"], "not_applicable")
        self.assertEqual(local["admission"]["status"], "pass")
        def cloud_auth_not_applicable(candidate: dict[str, object]) -> dict[str, object]:
            facts = declared_profile_preflight(candidate)
            facts["auth"] = {
                **facts["auth"],
                "status": "not_applicable",
                "auth_reference": "none",
                "auth_source": "not_applicable",
                "blocker": None,
            }
            return facts
        cloud = build_lane_preflight(
            select_judge_profile("oss-cloud"),
            cloud_auth_not_applicable,
        )
        self.assertEqual(cloud["admission"]["status"], "blocked")
        self.assertIn(
            "preflight_evidence_missing",
            {item["blocker_class"] for item in cloud["admission"]["blockers"]},
        )

    def test_missing_evidence_and_profile_model_mismatch_fail_closed(self) -> None:
        profile = select_judge_profile("oss-cloud")
        def probe(candidate: dict[str, object]) -> dict[str, object]:
            facts = declared_profile_preflight(candidate)
            facts.pop("catalog")
            facts["profile_config"]["profile_id"] = "oss-local"
            facts["model_catalog"]["selected_model_id"] = "missing-model"
            facts["auth"]["auth_reference"] = "none"
            return facts
        receipt = build_lane_preflight(profile, probe)
        classes = {item["blocker_class"] for item in receipt["admission"]["blockers"]}
        self.assertTrue({
            "preflight_evidence_missing",
            "profile_config_missing_or_invalid",
            "selected_model_unavailable",
            "cloud_auth_unavailable",
        }.issubset(classes))
        self.assertFalse(receipt["admission"]["secret_values_observed"])

    def test_cloud_catalog_probe_uses_exact_authenticated_get_without_secret_output(self) -> None:
        captured: dict[str, object] = {}
        class Response:
            def __enter__(self) -> "Response":
                return self
            def __exit__(self, *_args: object) -> None:
                return None
            @staticmethod
            def getcode() -> int:
                return 200
            @staticmethod
            def read(_limit: int) -> bytes:
                return json.dumps({"models": [{"name": "minimax-m2.7:cloud"}]}).encode()
        def opener(request: object, *, timeout: int) -> Response:
            captured["request"] = request
            captured["timeout"] = timeout
            return Response()
        with patch.dict(os.environ, {"OLLAMA_API_KEY": "fixture-secret"}, clear=True):
            result = probe_catalog(
                url="https://ollama.com/api/tags",
                selected_model="minimax-m2.7:cloud",
                timeout_s=10,
                opener=opener,
            )
        request = captured["request"]
        self.assertEqual(request.get_method(), "GET")  # type: ignore[union-attr]
        self.assertEqual(request.get_header("Authorization"), "Bearer fixture-secret")  # type: ignore[union-attr]
        self.assertEqual(result["result_class"], "pass")
        self.assertEqual(result["matched_model"], "minimax-m2.7:cloud")
        self.assertTrue(result["network_accessed"])
        self.assertFalse(result["generation_performed"])
        self.assertFalse(result["provider_invoked"])
        self.assertNotIn("fixture-secret", json.dumps(result))

    def test_cloud_catalog_probe_rejects_missing_duplicate_and_fast_substitution(self) -> None:
        class Response:
            def __init__(self, names: list[str]) -> None:
                self.names = names
            def __enter__(self) -> "Response":
                return self
            def __exit__(self, *_args: object) -> None:
                return None
            @staticmethod
            def getcode() -> int:
                return 200
            def read(self, _limit: int) -> bytes:
                return json.dumps({"models": [{"name": name} for name in self.names]}).encode()
        with patch.dict(os.environ, {"OLLAMA_API_KEY": "fixture-secret"}, clear=True):
            missing = probe_catalog(
                url="https://ollama.com/api/tags", selected_model="minimax-m2.7:cloud",
                timeout_s=10, opener=lambda *_args, **_kwargs: Response(["fast"]),
            )
            duplicate = probe_catalog(
                url="https://ollama.com/api/tags", selected_model="minimax-m2.7:cloud",
                timeout_s=10,
                opener=lambda *_args, **_kwargs: Response(["minimax-m2.7:cloud", "minimax-m2.7:cloud"]),
            )
        self.assertEqual(missing["result_class"], "model_missing")
        self.assertEqual(duplicate["result_class"], "model_ambiguous")

    def test_cloud_catalog_probe_classifies_http_timeout_network_and_malformed_payloads(self) -> None:
        class Response:
            def __enter__(self) -> "Response":
                return self
            def __exit__(self, *_args: object) -> None:
                return None
            @staticmethod
            def getcode() -> int:
                return 200
            @staticmethod
            def read(_limit: int) -> bytes:
                return b"not-json"
        cases = {
            "http_failure": lambda *_args, **_kwargs: (_ for _ in ()).throw(
                urllib.error.HTTPError("https://ollama.com/api/tags", 403, "denied", {}, None)
            ),
            "timeout": lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError()),
            "network_failure": lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError()),
            "malformed_json": lambda *_args, **_kwargs: Response(),
        }
        with patch.dict(os.environ, {"OLLAMA_API_KEY": "fixture-secret"}, clear=True):
            for expected, opener in cases.items():
                with self.subTest(expected=expected):
                    result = probe_catalog(
                        url="https://ollama.com/api/tags", selected_model="minimax-m2.7:cloud",
                        timeout_s=10, opener=opener,
                    )
                    self.assertEqual(result["result_class"], expected)
                    self.assertNotIn("fixture-secret", json.dumps(result))

    def test_cloud_auth_fifo_is_never_read_and_op_run_is_the_only_catalog_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "cloud-env"
            os.mkfifo(env_file)
            environment = {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}
            with (
                patch.dict(os.environ, environment, clear=True),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"),
                patch.object(Path, "read_text", side_effect=AssertionError("opaque env stream was read")),
            ):
                auth = _approved_cloud_auth_fact("minimax-m2.7:cloud")
                seen: list[list[str]] = []
                def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
                    seen.append(command)
                    return self._catalog_process(self._catalog_payload())
                fact = _cloud_catalog_fact(
                    "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), auth, runner,
                )
        self.assertEqual(auth["status"], "pass")
        self.assertEqual(auth["auth_source"], "op_fifo")
        self.assertEqual(fact["status"], "pass")
        self.assertEqual(seen[0][:3], ["/mock/bin/op", "run", "--env-file"])
        self.assertEqual(seen[0][3], str(env_file))
        self.assertEqual(seen[0][4], "--")
        serialized = json.dumps(fact)
        self.assertNotIn(str(env_file), serialized)
        self.assertNotIn("Authorization", serialized)

    def test_cloud_catalog_has_no_unauthenticated_fallback_and_redacts_probe_failures(self) -> None:
        auth = {
            "status": "blocked", "auth_source": "missing_or_invalid",
            "auth_reference": "codex_cli_auth", "secret_value_observed": False,
        }
        def forbidden_runner(_command: list[str]) -> subprocess.CompletedProcess[str]:
            raise AssertionError("catalog runner must not start without op auth")
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            blocked = _cloud_catalog_fact(
                "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), auth, forbidden_runner,
            )
        self.assertEqual(blocked["blocker"]["blocker_class"], "cloud_auth_unavailable")
        self.assertFalse(blocked["network_accessed"])
        approved = {**auth, "status": "pass", "auth_source": "op_fifo"}
        secret = "should-never-appear"
        malformed = subprocess.CompletedProcess(["op", "run"], 2, stdout="", stderr=secret)
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            failure = _cloud_catalog_fact(
                "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), approved,
                lambda _command: malformed,
            )
        self.assertEqual(failure["blocker"]["blocker_class"], "cloud_catalog_unavailable")
        self.assertNotIn(secret, json.dumps(failure))

    def test_cloud_catalog_blocks_missing_op_and_rejects_self_claimed_unsafe_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "opaque-env"
            env_file.touch()
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}, clear=True),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value=None),
            ):
                auth = _approved_cloud_auth_fact("minimax-m2.7:cloud")
        self.assertEqual(auth["blocker"]["blocker_class"], "cloud_auth_unavailable")
        approved = {
            "status": "pass", "auth_source": "op_fifo",
            "auth_reference": "codex_cli_auth", "secret_value_observed": False,
        }
        unsafe = self._catalog_payload(secret_value_observed=True)
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            fact = _cloud_catalog_fact(
                "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), approved,
                lambda _command: self._catalog_process(unsafe),
            )
        self.assertEqual(fact["status"], "blocked")
        self.assertEqual(fact["blocker"]["blocker_class"], "cloud_catalog_unavailable")

    def test_cloud_catalog_rejects_nonzero_self_claimed_pass_and_extra_fields(self) -> None:
        approved = {
            "status": "pass", "auth_source": "op_fifo",
            "auth_reference": "codex_cli_auth", "secret_value_observed": False,
        }
        cases = (
            self._catalog_process(self._catalog_payload(), returncode=2),
            self._catalog_process(self._catalog_payload(untrusted_extra="ignored-child-claim")),
        )
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            for completed in cases:
                with self.subTest(returncode=completed.returncode):
                    fact = _cloud_catalog_fact(
                        "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), approved,
                        lambda _command, result=completed: result,
                    )
                    self.assertEqual(fact["status"], "blocked")
                    self.assertNotIn("untrusted_extra", json.dumps(fact))

    def test_cloud_catalog_preserves_typed_nonzero_blocker_payloads(self) -> None:
        result_classes = (
            "model_missing", "model_ambiguous", "auth_missing", "http_failure",
            "timeout", "network_failure", "payload_too_large", "malformed_json",
            "malformed_catalog",
        )
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            for result_class in result_classes:
                with self.subTest(result_class=result_class):
                    payload = self._typed_catalog_blocker_payload(result_class)
                    expected_blocker = (
                        "selected_model_unavailable" if result_class.startswith("model_")
                        else "cloud_auth_unavailable" if result_class == "auth_missing"
                        else "cloud_catalog_unavailable"
                    )
                    completed = self._catalog_process(payload, returncode=2)
                    fact = self._catalog_fact_for_process(completed)
                    parsed, failure, evidence = _catalog_probe_result(
                        ["op", "run"], lambda _command, result=completed: result,
                    )
                    self.assertEqual(parsed, payload)
                    self.assertIsNone(failure)
                    self.assertEqual(evidence["probe_exit_code"], 2)
                    self.assertEqual(fact["status"], "blocked")
                    self.assertEqual(fact["blocker"]["blocker_class"], expected_blocker)
                    self.assertIn(str(payload["result_class"]), fact["blocker"]["reason"])
                    self.assertEqual(fact["http_status"], payload["http_status"])
                    self.assertEqual(fact["catalog_digest"], payload["catalog_digest"])
                    self.assertEqual(fact["matched_model"], payload["matched_model"])
                    self.assertFalse(fact["secret_value_observed"])

    def test_cloud_catalog_rejects_mismatched_payload_and_exit_semantics(self) -> None:
        cases = (
            self._catalog_process(self._catalog_payload(), returncode=2),
            self._catalog_process(self._catalog_payload(result_class="model_missing"), returncode=0),
            self._catalog_process(self._catalog_payload(result_class="model_missing"), returncode=1),
        )
        for completed in cases:
            with self.subTest(returncode=completed.returncode):
                payload, failure, evidence = _catalog_probe_result(
                    ["op", "run"], lambda _command, result=completed: result,
                )
                self.assertIsNone(payload)
                self.assertEqual(failure, "probe_exit_contract_mismatch")
                self.assertEqual(evidence["probe_exit_code"], completed.returncode)

    def test_cloud_catalog_rejects_typed_blocker_with_nonempty_stderr(self) -> None:
        secret = "catalog-probe-secret-text"
        completed = self._catalog_process(
            self._catalog_payload(result_class="model_missing"),
            returncode=2,
            stderr=secret,
        )
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNone(payload)
        self.assertEqual(failure, "probe_stderr_nonempty")
        self.assertNotIn(secret, json.dumps(evidence))

    def test_cloud_catalog_requires_exact_integer_zero_process_exit(self) -> None:
        class IntSubclass(int):
            pass
        invalid_values = (False, True, 0.0, "0", None, IntSubclass(0))
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            for returncode in invalid_values:
                with self.subTest(returncode_type=type(returncode).__name__):
                    self._assert_invalid_catalog_returncode(returncode)
            for returncode in (-9, 1, 255):
                with self.subTest(returncode=returncode):
                    self._assert_nonzero_catalog_returncode(returncode)

    def test_cloud_catalog_requires_closed_transport_envelope(self) -> None:
        class StringSubclass(str):
            pass
        class MissingReturncode:
            stdout = json.dumps(self._catalog_payload())
            stderr = ""
        class RaisingAttribute:
            @property
            def returncode(self) -> int:
                raise RuntimeError("secret-like exception text")
            stdout = json.dumps(self._catalog_payload())
            stderr = ""
        valid_stdout = json.dumps(self._catalog_payload())
        cases = (
            subprocess.CompletedProcess(["op", "run"], 0, stdout=valid_stdout.encode(), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=bytearray(valid_stdout.encode()), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=memoryview(valid_stdout.encode()), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=None, stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=valid_stdout, stderr=None),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=StringSubclass(valid_stdout), stderr=""),
            subprocess.CompletedProcess(["op", "run"], 0, stdout=valid_stdout, stderr=StringSubclass("")),
            {"returncode": 0, "stdout": valid_stdout, "stderr": ""},
            (0, valid_stdout, ""),
            MissingReturncode(),
            RaisingAttribute(),
        )
        for completed in cases:
            with self.subTest(transport_type=type(completed).__name__):
                payload, failure, evidence = _catalog_probe_result(
                    ["op", "run"], lambda _command, result=completed: result,  # type: ignore[arg-type,return-value]
                )
                self.assertIsNone(payload)
                self.assertEqual(failure, "invalid_probe_transport_envelope")
                self.assertEqual(evidence["probe_transport_class"], "invalid")
                self.assertNotIn("secret-like", json.dumps(evidence))

    def test_cloud_catalog_contains_hostile_attribute_base_exceptions(self) -> None:
        exception_cases = (
            KeyboardInterrupt("keyboard-secret-text"),
            SystemExit("system-secret-text"),
            GeneratorExit("generator-secret-text"),
            RuntimeError("runtime-secret-text"),
            _CustomBoundarySignal("custom-secret-text"),
        )
        valid_stdout = json.dumps(self._catalog_payload())
        for attribute in ("returncode", "stdout", "stderr"):
            for raised in exception_cases:
                with self.subTest(attribute=attribute):
                    completed = _HostileEnvelope(attribute, raised, valid_stdout)
                    payload, failure, evidence = _catalog_probe_result(
                        ["op", "run"], lambda _command, result=completed: result,
                    )
                    self.assertIsNone(payload)
                    self.assertEqual(failure, "invalid_probe_transport_envelope")
                    self.assertEqual(evidence["probe_transport_class"], "invalid")
                    self.assertEqual(
                        evidence[f"probe_{attribute}_class"], "attribute_access_failure",
                    )
                    rendered = json.dumps(evidence)
                    self.assertNotIn("secret-text", rendered)
                    self.assertNotIn("BoundarySignal", rendered)

    def test_cloud_catalog_rejects_oversized_and_control_framed_stdout(self) -> None:
        valid_stdout = json.dumps(self._catalog_payload())
        cases = (
            valid_stdout + "x" * (1024 * 1024),
            "\x00" + valid_stdout,
            valid_stdout + "\t",
            valid_stdout + "\r",
            valid_stdout + "\n\n",
        )
        for stdout in cases:
            completed = subprocess.CompletedProcess(["op", "run"], 0, stdout=stdout, stderr="")
            with self.subTest(suffix=repr(stdout[-2:])):
                payload, failure, evidence = _catalog_probe_result(
                    ["op", "run"], lambda _command, result=completed: result,
                )
                self.assertIsNone(payload)
                self.assertEqual(failure, "invalid_probe_transport_envelope")
                self.assertEqual(evidence["probe_transport_class"], "invalid")

        completed = subprocess.CompletedProcess(
            ["op", "run"], 0, stdout=valid_stdout + "\n", stderr="",
        )
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNotNone(payload)
        self.assertIsNone(failure)
        self.assertEqual(evidence["probe_stdout_class"], "bounded_json_text")

    def _assert_invalid_catalog_returncode(self, returncode: object) -> None:
        completed = subprocess.CompletedProcess(
            ["op", "run"], returncode,
            stdout=json.dumps(self._catalog_payload()), stderr="",
        )
        fact = self._catalog_fact_for_process(completed)
        self.assertEqual(fact["status"], "blocked")
        self.assertIn("invalid_probe_transport_envelope", fact["blocker"]["reason"])
        self.assertIsInstance(json.dumps(fact), str)
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNone(payload)
        self.assertEqual(failure, "invalid_probe_transport_envelope")
        self.assertEqual(evidence["probe_returncode_class"], "invalid_type")

    def _assert_nonzero_catalog_returncode(self, returncode: int) -> None:
        completed = self._catalog_process(self._catalog_payload(), returncode=returncode)
        fact = self._catalog_fact_for_process(completed)
        self.assertEqual(fact["status"], "blocked")
        payload, failure, evidence = _catalog_probe_result(
            ["op", "run"], lambda _command: completed,
        )
        self.assertIsNone(payload)
        self.assertEqual(failure, "probe_exit_contract_mismatch")
        self.assertEqual(evidence["probe_exit_class"], "nonzero")
        self.assertEqual(evidence["probe_exit_code"], returncode)

    def _catalog_fact_for_process(
        self, completed: subprocess.CompletedProcess[str],
    ) -> dict[str, object]:
        approved = {
            "status": "pass", "auth_source": "op_fifo",
            "auth_reference": "codex_cli_auth", "secret_value_observed": False,
        }
        return _cloud_catalog_fact(
            "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), approved,
            lambda _command: completed,
        )

    def test_cloud_catalog_rejects_malformed_or_contradictory_child_contracts(self) -> None:
        approved = {
            "status": "pass", "auth_source": "op_fifo",
            "auth_reference": "codex_cli_auth", "secret_value_observed": False,
        }
        duplicate = json.dumps(self._catalog_payload()).replace(
            '"result_class": "pass"', '"result_class": "pass", "result_class": "pass"',
        )
        raw_cases = (
            "{}",
            duplicate,
            json.dumps(self._catalog_payload()) + " {}",
            json.dumps(self._catalog_payload(http_status=True)),
            json.dumps(self._catalog_payload(match_count=True)),
            json.dumps(self._catalog_payload(http_status=float("nan"))),
            json.dumps(self._catalog_payload(network_accessed=False)),
            json.dumps(self._catalog_payload(matched_model=None)),
            json.dumps(self._catalog_payload(catalog_digest="sha256:not-a-digest")),
            json.dumps(self._catalog_payload(result_class="model_missing", match_count=1)),
        )
        completed_cases = [
            subprocess.CompletedProcess(["op", "run"], 0, stdout=raw, stderr="")
            for raw in raw_cases
        ]
        completed_cases.append(self._catalog_process(self._catalog_payload(), stderr="unexpected"))
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            for index, completed in enumerate(completed_cases):
                with self.subTest(index=index):
                    fact = _cloud_catalog_fact(
                        "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), approved,
                        lambda _command, result=completed: result,
                    )
                    self.assertEqual(fact["status"], "blocked")
                    self.assertFalse(fact["secret_value_observed"])


if __name__ == "__main__":
    unittest.main()
