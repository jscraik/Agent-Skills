from ask_evals_command_tests_07 import *  # noqa: F403

def test_review_dashboard_renders_review_mode_details(tmp_path: Path) -> None:
    report_path = tmp_path / "review.json"
    output_path = tmp_path / "review.html"
    report_path.write_text(
        json.dumps({
            "status": "success",
            "errors": [],
            "data": {
                "target": "Skills/example/example-skill",
                "policy": {
                    "mode": "local_internal_only",
                    "primary_gate": "local_eval_ask_audit",
                    "plugin_eval_min_acceptable_grade": "B+",
                    "snyk_default": "disabled_until_requested",
                },
                "review_mode_details": {
                    "local_evals": {
                        "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
                        "role": "dynamic run-trace behavior checks",
                    },
                    "plugin_eval": {
                        "command": "plugin-eval analyze <path> --format markdown",
                        "role": "budget and ergonomics guardrail",
                    },
                    "tessl_lint": {
                        "command": "tessl plugin lint <temporary-plugin-wrapper>",
                        "role": "disposable .tessl-plugin/plugin.json package-shape check",
                    },
                    "tessl_review": {
                        "command": "tessl skill review <temporary-skill-directory>",
                        "role": "local best-practice/content review",
                    },
                    "snyk": {
                        "command": "./bin/ask skills external-review <path> --include-snyk --json --robot",
                        "role": "opt-in local dependency security screening; release-required for manifest-backed candidates",
                        "release_required": "manifest-backed candidates",
                    },
                },
                "ask_audit": {
                    "data": {
                        "openclaw": {
                            "status": "success",
                            "stdout": "RESULT: PASS\n0 critical · 0 warn · 0 info\n",
                        }
                    }
                },
            },
        }),
        encoding="utf-8",
    )

    render_skill_review_dashboard(report_path, output_path, tmp_path)

    html_text = output_path.read_text(encoding="utf-8")
    assert "Review Lanes" in html_text
    assert "dynamic run-trace behavior checks" in html_text
    assert "budget and ergonomics guardrail" in html_text
    assert "disposable .tessl-plugin/plugin.json package-shape check" in html_text
    assert "local best-practice/content review" in html_text
    assert "opt-in local dependency security screening" in html_text
    assert "release-required for manifest-backed candidates" in html_text


def test_dashboard_report_uses_canonical_skill_builder_scripts(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="Dashboard JSON: out.json\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.dashboard_report(tmp_path)

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert cmd[1] == "Plugins/skill-factory/scripts/skill-builder/build_skill_eval_dashboard.py"


def test_tessl_live_evidence_rejects_symlinked_repo_evidence_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    external = tmp_path / "external-evidence"
    external.mkdir()
    evidence_parent = repo_root / ".harness" / "evidence"
    evidence_parent.mkdir(parents=True)
    os.symlink(external, evidence_parent / "tessl")

    path = evals._tessl_live_evidence_file(repo_root, "Skills/example/SKILL.md", "run-123", "view.json")

    assert path is None

__all__ = [name for name in globals() if not name.startswith("__")]
