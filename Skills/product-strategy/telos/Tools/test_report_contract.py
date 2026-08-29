"""Regression tests for the evidence-backed TELOS report contract."""

import json
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
TELOS = ROOT / "Skills/product-strategy/telos"
WORKFLOWS = TELOS / "Workflows"
TEMPLATE = TELOS / "ReportTemplate"
VALIDATOR = TELOS / "Tools/validate_report_artifacts.py"
COMPLETION_MARKER = ".telos-artifacts-complete"
COMPLETION_MARKER_BYTES = b"TELOS_REPORT_ARTIFACTS_COMPLETE_V1\n"
DOCS_WORKFLOW = ROOT / ".github/workflows/docs-governance.yml"
GENERATED_SKILL_INDEX = ROOT / "SKILL.md"
SYMLINK_GUARD_SCRIPT = """
source_real=$(cd -- "$SOURCE" && pwd -P)
if [ -L "$OUTPUT_ROOT" ]; then
  echo "output_root must not be a symlink" >&2
  exit 2
elif [ -e "$OUTPUT_ROOT" ]; then
  output_root_real=$(cd -- "$OUTPUT_ROOT" && pwd -P)
else
  output_parent_real=$(cd -- "$(dirname -- "$OUTPUT_ROOT")" && pwd -P)
  output_root_real="$output_parent_real/$(basename -- "$OUTPUT_ROOT")"
fi
case "$output_root_real/" in
  "$source_real/"*) exit 2 ;;
esac
mkdir -p "$OUTPUT_ROOT"
mkdir "$OUTPUT_DIR"
"""


def _valid_payloads() -> dict[str, object]:
    return {
        "findings.json": {"findings": []},
        "recommendations.json": {"recommendations": []},
        "roadmap.json": {"phases": []},
        "methodology.json": {"interviewCount": 0, "roles": []},
        "narrative.json": {
            "reportDate": "2026-08-29",
            "context": "context",
            "clientAsk": "ask",
            "currentState": "state",
            "whyNow": "now",
            "existentialRisks": [],
            "competitiveThreats": [],
            "timelinePressures": "none",
            "riskMatrix": [],
            "goodNews": "good",
            "requirements": [],
            "targetStateDescription": "target",
            "keyCapabilities": [],
            "successMetrics": [],
            "immediateSteps": [],
            "decisionPoints": [],
            "commitmentRequired": "commitment",
        },
    }


def _write_payloads(directory: Path, payloads: dict[str, object]) -> None:
    for filename, payload in payloads.items():
        (directory / filename).write_text(json.dumps(payload), encoding="utf-8")


def _write_completion_marker(directory: Path) -> None:
    (directory / COMPLETION_MARKER).write_bytes(COMPLETION_MARKER_BYTES)


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("telos_report_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load report validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReportContractTests(unittest.TestCase):
    def test_recommendation_title_is_a_semantic_heading(self) -> None:
        component = (TEMPLATE / "components/recommendation-card.tsx").read_text(encoding="utf-8")
        self.assertIn('<h3 className="finding-title">{recommendation.title}</h3>', component)

    def test_template_uses_strict_esm_typescript_contract(self) -> None:
        package = json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))
        tsconfig = json.loads((TEMPLATE / "tsconfig.json").read_text(encoding="utf-8"))
        options = tsconfig["compilerOptions"]

        self.assertEqual(package["type"], "module")
        self.assertEqual(options["module"], "NodeNext")
        self.assertEqual(options["moduleResolution"], "NodeNext")
        for key in (
            "verbatimModuleSyntax",
            "noUncheckedIndexedAccess",
            "exactOptionalPropertyTypes",
            "useUnknownInCatchVariables",
        ):
            self.assertIs(options[key], True)
        self.assertEqual(options["moduleDetection"], "force")
        self.assertFalse((TEMPLATE / "postcss.config.js").exists())
        self.assertIn("export default config", (TEMPLATE / "postcss.config.mjs").read_text(encoding="utf-8"))

    def test_report_has_a_real_artifact_producer_without_runtime_authority(self) -> None:
        report = (WORKFLOWS / "WriteReport.md").read_text(encoding="utf-8")
        narrative = (WORKFLOWS / "CreateNarrativePoints.md").read_text(encoding="utf-8")

        self.assertIn("`CreateNarrativePoints` MUST generate", report)
        self.assertIn("Report artifact producer contract", narrative)
        self.assertIn("`artifact_dir` | For `WriteReport`", narrative)
        self.assertIn("new sibling\nstaging directory", narrative)
        self.assertIn("writes a deterministic completion marker last", narrative)
        self.assertIn("Readers\nmust require and validate that marker", narrative)
        for filename in (
            "findings.json",
            "recommendations.json",
            "roadmap.json",
            "methodology.json",
            "narrative.json",
        ):
            self.assertIn(filename, narrative)
        self.assertNotIn("AnalyzeProjectWithGemini3", report)
        self.assertNotIn("AnalyzeProjectWithGemini3", narrative)
        self.assertNotIn("bun install", report)
        self.assertNotIn("bun dev", report)
        self.assertIn("explicit executable-app request", report)

    def test_report_binds_risk_matrix_and_preserves_epistemic_status(self) -> None:
        report = (WORKFLOWS / "WriteReport.md").read_text(encoding="utf-8")
        narrative = (WORKFLOWS / "CreateNarrativePoints.md").read_text(encoding="utf-8")

        self.assertIn("matrix: narrative.riskMatrix", report)
        self.assertIn("**observation**, **inference**, or **unknown**", narrative)
        self.assertIn("Never present an inference as an observed fact", narrative)
        self.assertIn("Preserve source qualifiers", narrative)
        self.assertNotIn("Bad news is direct, no hedging", narrative)
        self.assertNotIn('Hedge with "maybe," "perhaps," "consider"', narrative)
        self.assertNotIn("No hedging or waffling", report)

    def test_docs_workflow_covers_readme_and_enforces_vale(self) -> None:
        workflow = DOCS_WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(workflow.count('- "README.md"'), 2)
        self.assertIn("vale --config .vale.ini sync", workflow)
        self.assertIn("--minAlertLevel=error README.md SKILL.md", workflow)

    def test_generated_skill_index_uses_the_github_heading_anchor(self) -> None:
        index = GENERATED_SKILL_INDEX.read_text(encoding="utf-8")
        self.assertIn("[.Agents — Skills — .System](#agents--skills--system)", index)

    def test_telos_runtime_acceptance_keeps_projection_paths_separate(self) -> None:
        skill = (TELOS / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("retains `ReportTemplate` as the canonical source", skill)
        self.assertIn("does not ship a dashboard application", skill)
        self.assertIn("--runtime-target codex", skill)
        self.assertIn("--runtime-target agents", skill)
        self.assertIn("`~/.agents/skills/telos`", skill)
        self.assertIn("`~/.codex/skills/telos`", skill)
        self.assertIn("each receipt must expose `telos`", skill)
        self.assertIn("not an exact replacement", skill)

    def test_report_requires_caller_supplied_organization_identity(self) -> None:
        cover = (TEMPLATE / "components/cover-page.tsx").read_text(encoding="utf-8")
        data = (TEMPLATE / "lib/report-data.ts").read_text(encoding="utf-8")
        page = (TEMPLATE / "app/page.tsx").read_text(encoding="utf-8")
        workflow = (WORKFLOWS / "WriteReport.md").read_text(encoding="utf-8")

        self.assertIn("organizationName: string", cover)
        self.assertIn("{organizationName}", cover)
        self.assertIn("organizationName: string", data)
        self.assertIn("organizationName={data.organizationName}", page)
        self.assertIn('organizationName: "{organization_name}"', workflow)
        self.assertNotIn("<ORG_NAME>", cover)

    def test_report_requires_external_output_root_and_canonical_template(self) -> None:
        text = (WORKFLOWS / "WriteReport.md").read_text(encoding="utf-8")
        self.assertIn("`output_root` | Yes", text)
        self.assertIn("output_root must be outside source", text)
        self.assertIn('output_root}" ]; then', text)
        self.assertIn('mkdir "{output_dir}"', text)
        self.assertIn("validate_report_artifacts.py", text)
        self.assertIn("{REPO_ROOT}/Skills/product-strategy/telos/ReportTemplate/.", text)
        self.assertNotIn("~/.claude/skills/_TELOS/report-template", text)

    def test_interview_output_requires_approval_and_new_external_directory(self) -> None:
        text = (WORKFLOWS / "InterviewExtraction.md").read_text(encoding="utf-8")
        self.assertIn("explicit\nuser approval of that exact destination", text)
        self.assertIn("must not already exist", text)
        self.assertIn("/tmp/telos-extraction-output/", text)
        self.assertNotIn("Generates 13 output files at /path/to/interviews/", text)
        self.assertIn("OUTPUT_DIR must be outside TARGET_DIR", text)
        self.assertIn("OUTPUT_DIR must be a new directory", text)

    def test_public_report_components_document_prop_and_rendering_contracts(self) -> None:
        finding = (TEMPLATE / "components/finding-card.tsx").read_text(encoding="utf-8")
        recommendation = (TEMPLATE / "components/recommendation-card.tsx").read_text(encoding="utf-8")
        severity = (TEMPLATE / "components/severity-badge.tsx").read_text(encoding="utf-8")
        quote = (TEMPLATE / "components/quote-block.tsx").read_text(encoding="utf-8")
        section = (TEMPLATE / "components/section.tsx").read_text(encoding="utf-8")

        self.assertIn("one-based finding number", finding)
        self.assertIn("visibly renders the finding's epistemic status", finding)
        self.assertIn("{finding.epistemicStatus}", finding)
        self.assertIn("finding.qualifiers.map", finding)
        self.assertIn("aria-label=\"Source qualifiers\"", finding)
        self.assertIn("one-based recommendation number", recommendation)
        self.assertIn("Critical`, `High`, `Medium`, or `Low", severity)
        self.assertIn("role` is", quote)
        self.assertIn("semantic `h2` heading", section)

    def test_report_requires_real_artifacts_and_canonical_template(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_payloads(root, _valid_payloads())
            _write_completion_marker(root)
            result = subprocess.run(["python3", str(VALIDATOR), str(root)], check=False)
            self.assertEqual(result.returncode, 0)

    def test_artifact_producer_publishes_exact_validated_bytes_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            payloads = _valid_payloads()
            _write_payloads(drafts, payloads)
            output = root / "published"

            result = subprocess.run(
                ["python3", str(VALIDATOR), "--produce", str(drafts), str(output)],
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                set(payloads) | {COMPLETION_MARKER},
            )
            for filename in payloads:
                self.assertEqual(
                    (output / filename).read_bytes(),
                    (drafts / filename).read_bytes(),
                )

            rerun = subprocess.run(
                ["python3", str(VALIDATOR), "--produce", str(drafts), str(output)],
                check=False,
            )
            self.assertNotEqual(rerun.returncode, 0)

    def test_published_artifact_requires_completion_marker(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_payloads(root, _valid_payloads())
            with self.assertRaisesRegex(ValueError, COMPLETION_MARKER):
                validator.validate_published_artifacts(root)

    def test_artifact_producer_writes_completion_marker_last(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            _write_payloads(drafts, _valid_payloads())
            output = root / "published"
            observations: list[tuple[str, bool]] = []
            original_draft_validation = validator.validate_artifacts
            original_published_validation = validator.validate_published_artifacts

            def observe_draft_validation(path: Path) -> None:
                observations.append(("draft", (path / COMPLETION_MARKER).exists()))
                original_draft_validation(path)

            def observe_published_validation(path: Path) -> None:
                observations.append(("published", (path / COMPLETION_MARKER).exists()))
                original_published_validation(path)

            with patch.object(validator, "validate_artifacts", side_effect=observe_draft_validation):
                with patch.object(
                    validator,
                    "validate_published_artifacts",
                    side_effect=observe_published_validation,
                ):
                    validator.produce_artifacts(drafts, output)

            self.assertEqual(observations, [("draft", False), ("published", True)])
            self.assertEqual((output / COMPLETION_MARKER).read_bytes(), COMPLETION_MARKER_BYTES)

    def test_artifact_producer_rejects_invalid_drafts_without_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            payloads = _valid_payloads()
            _write_payloads(drafts, payloads)
            (drafts / "findings.json").write_text("{not-json", encoding="utf-8")
            output = root / "published"

            result = subprocess.run(
                ["python3", str(VALIDATOR), "--produce", str(drafts), str(output)],
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(output.is_dir())
            self.assertEqual(list(output.iterdir()), [])
            self.assertFalse((output / COMPLETION_MARKER).exists())
            self.assertEqual(list(root.glob(".published.*")), [])

    def test_artifact_producer_does_not_replace_destination_created_at_reservation(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            _write_payloads(drafts, _valid_payloads())
            output = root / "published"

            def external_race(destination: Path) -> None:
                destination.mkdir()
                (destination / "external-sentinel").write_text("preserve", encoding="utf-8")
                raise ValueError("producer output directory already exists")

            with patch.object(validator, "_reserve_destination", side_effect=external_race):
                with self.assertRaisesRegex(ValueError, "already exists"):
                    validator.produce_artifacts(drafts, output)

            self.assertEqual((output / "external-sentinel").read_text(encoding="utf-8"), "preserve")
            self.assertEqual(list(output.glob("*.json")), [])

    def test_artifact_producer_preserves_external_replacement_during_cleanup(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            _write_payloads(drafts, _valid_payloads())
            output = root / "published"
            moved = root / "moved-reservation"

            def rename_then_replace(_source: Path, _destination: Path) -> None:
                output.rename(moved)
                output.mkdir()
                (output / "external-sentinel").write_text("preserve", encoding="utf-8")
                raise OSError("injected population failure")

            with patch.object(validator, "copyfile", side_effect=rename_then_replace):
                with self.assertRaisesRegex(OSError, "injected population failure"):
                    validator.produce_artifacts(drafts, output)

            self.assertTrue(moved.is_dir())
            self.assertEqual((output / "external-sentinel").read_text(encoding="utf-8"), "preserve")

    def test_artifact_producer_preserves_swap_after_cleanup_identity_check(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            _write_payloads(drafts, _valid_payloads())
            output = root / "published"
            moved = root / "moved-reservation"
            original_lstat = validator.os.lstat
            swapped = False

            def swap_after_identity_check(path: Path | str, *, dir_fd: int | None = None):
                nonlocal swapped
                metadata = original_lstat(path, dir_fd=dir_fd)
                if not swapped and dir_fd is not None and path == output.name:
                    swapped = True
                    output.rename(moved)
                    output.mkdir()
                    (output / "external-sentinel").write_text("preserve", encoding="utf-8")
                return metadata

            with patch.object(validator, "copyfile", side_effect=OSError("injected population failure")):
                with patch.object(validator.os, "lstat", side_effect=swap_after_identity_check):
                    with self.assertRaisesRegex(OSError, "injected population failure"):
                        validator.produce_artifacts(drafts, output)

            self.assertTrue(swapped)
            self.assertTrue(moved.is_dir())
            self.assertEqual((output / "external-sentinel").read_text(encoding="utf-8"), "preserve")

    def test_artifact_producer_preserves_external_swap_during_bound_cleanup(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            _write_payloads(drafts, _valid_payloads())
            output = root / "published"
            moved = root / "moved-reservation"
            original_rmtree = validator.rmtree
            swapped = False

            def swap_during_bound_cleanup(path: Path | str, *, dir_fd: int | None = None):
                nonlocal swapped
                if not swapped and path == "." and dir_fd is not None:
                    swapped = True
                    output.rename(moved)
                    output.mkdir()
                    (output / "external-sentinel").write_text("preserve", encoding="utf-8")
                return original_rmtree(path, dir_fd=dir_fd)

            with patch.object(validator, "copyfile", side_effect=OSError("injected population failure")):
                with patch.object(validator, "rmtree", side_effect=swap_during_bound_cleanup):
                    with self.assertRaisesRegex(OSError, "injected population failure"):
                        validator.produce_artifacts(drafts, output)

            self.assertTrue(swapped)
            self.assertTrue(moved.is_dir())
            self.assertEqual(list(moved.iterdir()), [])
            self.assertEqual((output / "external-sentinel").read_text(encoding="utf-8"), "preserve")

    def test_artifact_producer_rolls_back_owned_reservation_on_failure(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            drafts = root / "drafts"
            drafts.mkdir()
            _write_payloads(drafts, _valid_payloads())
            output = root / "published"

            with patch.object(validator, "copyfile", side_effect=OSError("injected population failure")):
                with self.assertRaisesRegex(OSError, "injected population failure"):
                    validator.produce_artifacts(drafts, output)

            self.assertTrue(output.is_dir())
            self.assertEqual(list(output.iterdir()), [])
            self.assertFalse((output / COMPLETION_MARKER).exists())

    def test_artifact_validator_requires_epistemic_finding_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payloads = _valid_payloads()
            payloads["findings.json"] = {
                "findings": [{
                    "id": "F1",
                    "title": "Finding",
                    "description": "Description",
                    "evidence": "Evidence",
                    "source": "Interview",
                    "severity": "high",
                }],
            }
            _write_payloads(root, payloads)

            result = subprocess.run(["python3", str(VALIDATOR), str(root)], check=False)
            self.assertNotEqual(result.returncode, 0)

    def test_artifact_validator_rejects_unexpected_stale_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_payloads(root, _valid_payloads())
            (root / "stale.json").write_text("{}", encoding="utf-8")

            result = subprocess.run(["python3", str(VALIDATOR), str(root)], check=False)
            self.assertNotEqual(result.returncode, 0)

    def test_artifact_validator_rejects_symlinked_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            payloads = _valid_payloads()
            findings = root / "outside-findings.json"
            findings.write_text(json.dumps(payloads.pop("findings.json")), encoding="utf-8")
            _write_payloads(artifacts, payloads)
            (artifacts / "findings.json").symlink_to(findings)

            result = subprocess.run(["python3", str(VALIDATOR), str(artifacts)], check=False)
            self.assertNotEqual(result.returncode, 0)

    def test_artifact_validator_rejects_malformed_and_invalid_risk_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payloads = _valid_payloads()
            payloads.pop("findings.json")
            _write_payloads(root, payloads)
            (root / "findings.json").write_text("{not-json", encoding="utf-8")
            result = subprocess.run(["python3", str(VALIDATOR), str(root)], check=False)
            self.assertNotEqual(result.returncode, 0)

    def test_documented_narrative_example_passes_validator(self) -> None:
        text = (WORKFLOWS / "WriteReport.md").read_text(encoding="utf-8")
        block = re.search(r"\*\*narrative\.json:\*\*\n\n```json\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(block)
        narrative = json.loads(block.group(1))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payloads = _valid_payloads()
            payloads["narrative.json"] = narrative
            _write_payloads(root, payloads)
            _write_completion_marker(root)
            result = subprocess.run(["python3", str(VALIDATOR), str(root)], check=False)
            self.assertEqual(result.returncode, 0)

    def test_symlink_output_root_is_rejected_before_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            output_root = root / "output"
            output_root.symlink_to(source, target_is_directory=True)
            output_dir = output_root / "run"
            result = subprocess.run(
                ["bash", "-c", SYMLINK_GUARD_SCRIPT],
                env={**os.environ, "SOURCE": str(source), "OUTPUT_ROOT": str(output_root), "OUTPUT_DIR": str(output_dir)},
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output_dir.exists())

            artifacts = root / "artifact-set"
            artifacts.mkdir()
            payloads = _valid_payloads()
            narrative = payloads["narrative.json"]
            self.assertIsInstance(narrative, dict)
            narrative["riskMatrix"] = [
                {"risk": "r", "probability": "certain", "impact": "high", "mitigation": "m"},
            ]
            _write_payloads(artifacts, payloads)
            result = subprocess.run(["python3", str(VALIDATOR), str(artifacts)], check=False)
            self.assertNotEqual(result.returncode, 0)

    def test_template_assets_match_case_sensitive_css_paths(self) -> None:
        fonts = TEMPLATE / "public/fonts"
        self.assertTrue(fonts.is_dir())
        tracked = subprocess.run(
            ["git", "ls-files", "--", "Skills/product-strategy/telos/ReportTemplate/Public"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(tracked.returncode, 0)
        self.assertEqual(tracked.stdout, "")
        css = (TEMPLATE / "app/globals.css").read_text()
        for line in css.splitlines():
            if "url('/fonts/" in line:
                asset = line.split("url('/", 1)[1].split("'", 1)[0]
                self.assertTrue((TEMPLATE / "public" / asset).is_file(), asset)


if __name__ == "__main__":
    unittest.main()
