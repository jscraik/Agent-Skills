from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ask.skills_sdk.lenses import LensCatalogError, _parse_minimal_yaml


SCHEMA_VERSION = "skills-sdk-knowledge-ingest.v1"
ROUTING_TEXT = (
    "Load `references/knowledge-capsule.manifest.yaml` when an audit needs "
    "pack-backed harness or principal-engineering judgment. Prefer harness "
    "capsules for evidence, proof, routing, review feedback, PR lifecycle, and "
    "brownfield-readiness gaps. Prefer Ryan capsules for environment design, "
    "repo knowledge, mechanical boundaries, safety policy, operating model, and "
    "long-term coherence. Do not load all capsules by default; select the "
    "smallest relevant capsule from the manifest."
)
EVAL_ROUTING_TEXT = (
    "When checking behavior proof, use the KnowledgeOS eval scenario IDs wired "
    "through `references/evals.yaml`; the vendored scenario files are evidence, "
    "not an alternate eval runner."
)


def build_knowledge_ingest(
    repo_root: Path,
    *,
    extraction: str,
    skill: str,
    apply: bool,
    run_proof: bool = False,
    preflight_security: bool = True,
) -> dict[str, Any]:
    extraction_root = Path(extraction).expanduser().resolve()
    skill_dir = _resolve_skill_dir(repo_root, skill)
    source_files = _collect_reference_files(extraction_root)
    plan = _load_yaml(extraction_root / "extraction-plan.yaml", label="extraction-plan.yaml")
    demand = _load_yaml(extraction_root / "knowledge-demand.yaml", label="knowledge-demand.yaml")
    vendored_demand = _load_yaml(
        extraction_root / "references" / "knowledge-demand.yaml",
        label="references/knowledge-demand.yaml",
    )
    manifest = _load_yaml(
        extraction_root / "references" / "knowledge-capsule.manifest.yaml",
        label="references/knowledge-capsule.manifest.yaml",
    )

    skill_name = _skill_name(skill_dir / "SKILL.md")
    findings: list[str] = []
    _validate_skill_identity(
        skill_name=skill_name,
        skill_rel=_repo_relative(repo_root, skill_dir),
        plan=plan,
        demand=demand,
        manifest=manifest,
        findings=findings,
    )
    _validate_runtime_policy(demand, findings, label="knowledge-demand")
    _validate_runtime_policy(vendored_demand, findings, label="references/knowledge-demand")
    if vendored_demand != demand:
        findings.append("references/knowledge-demand:differs_from_root_knowledge-demand")
    _validate_source_files(extraction_root, source_files, findings)
    preflight = (
        _preflight_security_gate(repo_root, skill_dir, extraction_root, source_files, manifest=manifest)
        if preflight_security and not findings
        else None
    )
    if preflight and preflight["status"] != "pass":
        findings.append("staged_security_gate_failed")

    copied: list[dict[str, Any]] = []
    eval_routes = _eval_reference_routes(extraction_root, source_files)
    for source_file in source_files:
        relative = source_file.relative_to(extraction_root).as_posix()
        target = skill_dir / relative
        copied.append(
            {
                "source": relative,
                "target": _repo_relative(repo_root, target),
                "sha256": _sha256(source_file),
                "bytes": source_file.stat().st_size,
                "action": "write" if apply else "preview",
            }
        )

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "blocked" if findings else ("applied" if apply else "preview"),
        "owner_boundary": {
            "producer": "KnowledgeOS",
            "consumer": "Skills SDK",
            "runtime_dependency": "vendored_skill_references_only",
        },
        "extraction": {
            "path": str(extraction_root),
            "schema_version": plan.get("schema_version"),
            "upstream_packs": plan.get("upstream_packs") or [],
        },
        "skill": {
            "name": skill_name,
            "path": _repo_relative(repo_root, skill_dir),
        },
        "copied_files": copied,
        "routing_updates": _routing_updates(repo_root, skill_dir, apply=apply),
        "validation_commands": [
            f"./bin/ask skills audit {_repo_relative(repo_root, skill_dir)} --level strict --json --robot",
            f"./bin/ask skills package verify {_repo_relative(repo_root, skill_dir)} --json --robot",
        ],
        "proof_results": [],
        "staged_preflight": preflight,
        "findings": findings,
    }
    if findings:
        return receipt
    if not apply:
        return receipt

    _apply_knowledge_ingest(skill_dir, extraction_root, source_files, eval_routes=eval_routes, manifest=manifest)
    if run_proof:
        receipt["proof_results"] = _run_proof(repo_root, receipt["validation_commands"])
        if any(item["status"] != "pass" for item in receipt["proof_results"]):
            receipt["status"] = "applied_with_failed_proof"
    return receipt


def _routing_updates(repo_root: Path, skill_dir: Path, *, apply: bool) -> list[dict[str, str]]:
    action = "write" if apply else "preview"
    return [
        {
            "path": _repo_relative(repo_root, skill_dir / "SKILL.md"),
            "description": "knowledge capsule progressive-disclosure routing",
            "action": action,
        },
        {
            "path": _repo_relative(repo_root, skill_dir / "references" / "source-context.yaml"),
            "description": "source-context entries for vendored KnowledgeOS capsule references",
            "action": action,
        },
        {
            "path": _repo_relative(repo_root, skill_dir / "references" / "knowledge-capsule-routing.md"),
            "description": "first-party routing index for vendored KnowledgeOS capsules",
            "action": action,
        },
    ]


def _apply_knowledge_ingest(
    skill_dir: Path,
    extraction_root: Path,
    source_files: list[Path],
    *,
    eval_routes: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    for source_file in source_files:
        target = _safe_skill_package_path(skill_dir, source_file.relative_to(extraction_root), label="knowledge reference")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
    _update_knowledge_routing_files(skill_dir, eval_routes=eval_routes, manifest=manifest)


def _update_knowledge_routing_files(
    skill_dir: Path,
    *,
    eval_routes: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    _update_skill_routing(_safe_skill_package_path(skill_dir, Path("SKILL.md"), label="skill routing"), eval_routes=eval_routes)
    _update_source_context(
        _safe_skill_package_path(skill_dir, Path("references/source-context.yaml"), label="source context"),
        eval_routes=eval_routes,
    )
    _update_capsule_routing_index(
        _safe_skill_package_path(
            skill_dir,
            Path("references/knowledge-capsule-routing.md"),
            label="capsule routing index",
        ),
        manifest=manifest,
    )


def _safe_skill_package_path(skill_dir: Path, relative_path: Path, *, label: str) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(f"{label} path must stay inside the skill package.")
    skill_root = skill_dir.resolve()
    target = (skill_dir / relative_path).resolve(strict=False)
    try:
        target.relative_to(skill_root)
    except ValueError as exc:
        raise ValueError(f"{label} path must stay inside the skill package.") from exc
    return target


def _resolve_skill_dir(repo_root: Path, skill: str) -> Path:
    if not skill:
        raise ValueError("skill is required.")
    candidate = Path(skill).expanduser()
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved = candidate.resolve()
    repo_resolved = repo_root.resolve()
    try:
        resolved.relative_to(repo_resolved)
    except ValueError as exc:
        raise ValueError("skill must resolve inside the repository root.") from exc
    if resolved.name == "SKILL.md":
        resolved = resolved.parent
    skill_md = resolved / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError("skill must point at a skill directory or SKILL.md inside the repository.")
    return resolved


def _collect_reference_files(extraction_root: Path) -> list[Path]:
    if not extraction_root.is_dir():
        raise ValueError("extraction must be an existing KnowledgeOS extraction directory.")
    references_root = extraction_root / "references"
    if not references_root.is_dir():
        raise ValueError("KnowledgeOS extraction must contain a references directory.")
    files = sorted(path for path in references_root.rglob("*") if _safe_extraction_reference_file(extraction_root, path))
    if not files:
        raise ValueError("KnowledgeOS extraction references directory is empty.")
    return files


def _safe_extraction_reference_file(extraction_root: Path, path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    try:
        path.resolve(strict=True).relative_to(extraction_root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _eval_reference_routes(extraction_root: Path, source_files: list[Path]) -> dict[str, bool]:
    routes = {"scenarios": False, "fixtures": False}
    for source_file in source_files:
        relative = source_file.relative_to(extraction_root).as_posix()
        if relative == "references/eval-scenarios.json":
            routes["scenarios"] = True
        elif relative.startswith("references/evals/"):
            routes["fixtures"] = True
    return routes


def _load_yaml(path: Path, *, label: str) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"{label}:symlink_not_allowed")
    try:
        loaded = _yaml_safe_load_text(path.read_text(encoding="utf-8"), label=label) or {}
    except FileNotFoundError as exc:
        raise ValueError(f"KnowledgeOS extraction is missing {label}.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8 YAML.") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a YAML object.")
    return loaded


def _skill_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must contain YAML frontmatter.")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed.")
    frontmatter = _yaml_safe_load_text(text[4:end], label="SKILL.md frontmatter") or {}
    if not isinstance(frontmatter, dict) or not frontmatter.get("name"):
        raise ValueError("SKILL.md frontmatter must include name.")
    return str(frontmatter["name"])


def _validate_skill_identity(
    *,
    skill_name: str,
    skill_rel: str,
    plan: dict[str, Any],
    demand: dict[str, Any],
    manifest: dict[str, Any],
    findings: list[str],
) -> None:
    for label, payload in (("extraction-plan", plan), ("knowledge-demand", demand), ("manifest", manifest)):
        skill_payload = payload.get("skill") if isinstance(payload.get("skill"), dict) else {}
        declared = str(skill_payload.get("skill_id") or skill_payload.get("declared_name") or "")
        writable_root = str(skill_payload.get("writable_root") or "")
        if declared and declared != skill_name:
            findings.append(f"{label}:skill_id_mismatch:{declared}!={skill_name}")
        if writable_root and writable_root != skill_rel:
            findings.append(f"{label}:writable_root_mismatch:{writable_root}!={skill_rel}")


def _validate_runtime_policy(demand: dict[str, Any], findings: list[str], *, label: str) -> None:
    policy = demand.get("runtime_dependency_policy")
    if not isinstance(policy, dict):
        findings.append(f"{label}:missing_runtime_dependency_policy")
        return
    if policy.get("requires_knowledge_os_at_runtime") is not False:
        findings.append(f"{label}:requires_knowledge_os_at_runtime_not_false")
    if policy.get("raw_sources_included") is not False:
        findings.append(f"{label}:raw_sources_included_not_false")
    if policy.get("local_absolute_paths_required") is not False:
        findings.append(f"{label}:local_absolute_paths_required_not_false")


def _validate_source_files(extraction_root: Path, source_files: list[Path], findings: list[str]) -> None:
    allowed_names = {
        "references/knowledge-demand.yaml",
        "references/knowledge-capsule.manifest.yaml",
        "references/knowledge-capsule-routing.md",
        "references/eval-scenarios.json",
    }
    for source_file in source_files:
        if source_file.is_symlink():
            findings.append(f"references:symlink_not_allowed:{source_file.name}")
            continue
        relative = source_file.relative_to(extraction_root).as_posix()
        if relative in allowed_names:
            pass
        elif relative.startswith("references/knowledge-capsules/") and relative.endswith(".md"):
            pass
        elif relative.startswith("references/evals/") and relative.endswith(".md"):
            pass
        else:
            findings.append(f"references:unsupported_file:{relative}")
        try:
            text = source_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"references:invalid_utf8:{relative}")
            continue
        if "/Users/" in text or "/private/" in text or "/Volumes/" in text:
            findings.append(f"references:local_absolute_path_leak:{relative}")
        if relative == "references/eval-scenarios.json":
            _validate_eval_scenarios_json(text, findings, relative=relative)


def _validate_eval_scenarios_json(text: str, findings: list[str], *, relative: str) -> None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        findings.append(f"references:invalid_eval_scenarios_json:{relative}:{exc.msg}")
        return
    if not isinstance(payload, list):
        findings.append(f"references:invalid_eval_scenarios_json:{relative}:not_list")
        return
    seen_ids: set[str] = set()
    for index, scenario in enumerate(payload):
        if not isinstance(scenario, dict):
            findings.append(f"references:invalid_eval_scenarios_json:{relative}:{index}:not_object")
            continue
        scenario_id = scenario.get("id")
        scenario_payload = scenario.get("payload")
        if not isinstance(scenario_id, str) or not scenario_id.startswith("eval."):
            findings.append(f"references:invalid_eval_scenarios_json:{relative}:{index}:missing_eval_id")
        elif scenario_id in seen_ids:
            findings.append(f"references:invalid_eval_scenarios_json:{relative}:{index}:duplicate_eval_id:{scenario_id}")
        else:
            seen_ids.add(scenario_id)
        if not isinstance(scenario_payload, dict):
            findings.append(f"references:invalid_eval_scenarios_json:{relative}:{index}:missing_payload")


def _update_skill_routing(skill_md: Path, *, eval_routes: dict[str, bool]) -> None:
    text = skill_md.read_text(encoding="utf-8")
    routing_text = _routing_text(eval_routes=eval_routes)
    if routing_text in text:
        return
    marker = _routing_insertion_marker(text)
    if marker is None:
        reference_marker = "## References\n"
        capsule_section = "## Knowledge Capsules\n\n" + routing_text + "\n\n"
        if reference_marker in text:
            before_refs, refs = text.split(reference_marker, 1)
            updated = before_refs.rstrip() + "\n\n" + capsule_section + reference_marker + refs
        else:
            updated = text.rstrip() + "\n\n" + capsule_section
        skill_md.write_text(
            _append_reference_links(updated, eval_routes=eval_routes),
            encoding="utf-8",
        )
        return
    before, after = text.split(marker, 1)
    next_heading = after.find("\n## ")
    if next_heading == -1:
        procedure = after.rstrip() + "\n\n" + routing_text + "\n"
        updated = before + marker + procedure
    else:
        procedure = after[:next_heading].rstrip() + "\n\n" + routing_text + "\n"
        updated = before + marker + procedure + after[next_heading:]
    skill_md.write_text(
        _append_reference_links(updated, eval_routes=eval_routes),
        encoding="utf-8",
    )


def _routing_insertion_marker(text: str) -> str | None:
    for heading in ("Procedure", "Workflow", "Runtime Activation"):
        marker = f"## {heading}\n"
        if marker in text:
            return marker
    return None


def _routing_text(*, eval_routes: dict[str, bool]) -> str:
    if eval_routes["scenarios"] and eval_routes["fixtures"]:
        return ROUTING_TEXT + " " + EVAL_ROUTING_TEXT
    return ROUTING_TEXT


def _update_capsule_routing_index(path: Path, *, manifest: dict[str, Any]) -> None:
    capsules = manifest.get("capsules")
    upstream_pack = manifest.get("upstream_pack")
    if isinstance(upstream_pack, dict):
        default_pack_id = str(upstream_pack.get("pack_id") or "").strip()
    else:
        default_pack_id = str(manifest.get("pack_id") or "").strip()
    selected_asset_ids = manifest.get("selected_asset_ids")
    default_asset_count = len(selected_asset_ids) if isinstance(selected_asset_ids, list) else 0
    lines = [
        "# Knowledge Capsule Routing",
        "",
        "This first-party index promotes vendored capsule routing into the skill package.",
        "Use it before opening generated capsule bodies so capsule guidance is not hidden",
        "inside second-order references.",
        "",
        "## Capsules",
        "",
    ]
    if isinstance(capsules, list):
        for capsule in capsules:
            lines.extend(_capsule_routing_lines(capsule, default_pack_id, default_asset_count))
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_capsule_routing_index(path, "\n".join(lines).rstrip() + "\n")


def _write_capsule_routing_index(path: Path, value: str) -> None:
    references_root_real = os.path.realpath(path.parent)
    routing_path_real = os.path.realpath(path)
    if os.path.commonpath([references_root_real, routing_path_real]) != references_root_real:
        raise ValueError("Knowledge capsule routing path escaped the references directory.")
    if path.is_symlink():
        raise ValueError("Knowledge capsule routing path must not be a symlink.")
    with Path(routing_path_real).open("w", encoding="utf-8") as handle:
        handle.write(value)


def _capsule_routing_lines(capsule: object, default_pack_id: str, default_asset_count: int) -> list[str]:
    normalized = _capsule_routing_entry(capsule)
    if normalized is None or not normalized["target_path"]:
        return []
    tick = chr(96)
    pack_id = normalized["pack_id"] or default_pack_id or "unknown"
    asset_count = normalized["asset_count"]
    if asset_count is None:
        asset_count = default_asset_count
    return [
        "- " + tick + str(normalized["target_path"]) + tick,
        "  - facet: " + str(normalized["facet"]),
        "  - pack: " + str(pack_id),
        "  - selected_asset_count: " + str(asset_count),
        "  - load_when: task signals match this facet; load only this capsule before adding more.",
    ]


def _capsule_routing_entry(capsule: object) -> dict[str, Any] | None:
    if isinstance(capsule, str) and capsule.strip().startswith("target_path:"):
        return {
            "target_path": capsule.split(":", 1)[1].strip(),
            "facet": "capsule",
            "pack_id": "",
            "asset_count": None,
        }
    if not isinstance(capsule, dict):
        return None
    asset_ids = capsule.get("asset_ids")
    return {
        "target_path": str(capsule.get("target_path") or "").strip(),
        "facet": str(capsule.get("facet_id") or capsule.get("role") or "capsule").strip(),
        "pack_id": str(capsule.get("pack_id") or "").strip(),
        "asset_count": len(asset_ids) if isinstance(asset_ids, list) else None,
    }


def _append_reference_links(text: str, *, eval_routes: dict[str, bool]) -> str:
    reference_marker = "## References\n"
    updated = text
    if reference_marker in updated:
        before_refs, refs = updated.split(reference_marker, 1)
        reference_links = [
            "- `references/knowledge-demand.yaml`",
            "- `references/knowledge-capsule.manifest.yaml`",
            "- `references/knowledge-capsule-routing.md`",
            "- `references/knowledge-capsules/`",
        ]
        if eval_routes["scenarios"]:
            reference_links.append("- `references/eval-scenarios.json`")
        if eval_routes["fixtures"]:
            reference_links.append("- `references/evals/`")
        for ref in reference_links:
            if ref not in refs:
                refs = refs.rstrip() + "\n" + ref + "\n"
        updated = before_refs + reference_marker + refs
    return updated.rstrip() + "\n"


def _update_source_context(source_context: Path, *, eval_routes: dict[str, bool]) -> None:
    if source_context.is_file():
        loaded = _load_yaml(source_context, label="references/source-context.yaml")
    else:
        skill_dir = source_context.parent.parent
        loaded = {
            "schema_version": 1,
            "skill": _skill_name(skill_dir / "SKILL.md"),
            "references": [],
        }
    references = loaded.setdefault("references", [])
    if not isinstance(references, list):
        raise ValueError("references/source-context.yaml references must be a list.")
    entries = [
        {
            "path": "references/knowledge-demand.yaml",
            "kind": "knowledge_profile",
            "provenance": "vendored KnowledgeOS extraction",
            "load_when": "deciding which pack-backed capsule is relevant",
            "allowed_claims": ["knowledge demand profile for this skill"],
            "forbidden_claims": ["target repo readiness", "raw source availability"],
            "freshness": "knowledge_os_snapshot",
            "context_budget": "small",
            "claim_scope": "knowledge_profile",
            "bounded_unit": True,
        },
        {
            "path": "references/knowledge-capsule.manifest.yaml",
            "kind": "capsule_manifest",
            "provenance": "vendored KnowledgeOS extraction",
            "load_when": "selecting a bounded KnowledgeOS capsule",
            "allowed_claims": ["selected capsules and upstream pack snapshot digests"],
            "forbidden_claims": ["raw source completeness", "runtime dependency on KnowledgeOS"],
            "freshness": "knowledge_os_snapshot",
            "context_budget": "small",
            "claim_scope": "capsule_manifest",
            "bounded_unit": True,
        },
        {
            "path": "references/knowledge-capsules/",
            "kind": "generated_knowledge_capsules",
            "provenance": "vendored KnowledgeOS extraction",
            "load_when": "only after the manifest selects the relevant capsule",
            "allowed_claims": ["bounded expert viewpoint or evidence lane captured in the selected capsule"],
            "forbidden_claims": ["load all capsules by default", "claims outside selected capsule text"],
            "freshness": "knowledge_os_snapshot",
            "context_budget": "selective",
            "claim_scope": "bounded_capsules",
            "bounded_unit": True,
        },
    ]
    if eval_routes["scenarios"]:
        entries.append(
            {
                "path": "references/eval-scenarios.json",
                "kind": "knowledge_eval_scenarios",
                "provenance": "vendored KnowledgeOS extraction",
                "load_when": "checking selected KnowledgeOS eval scenario metadata",
                "allowed_claims": ["selected eval scenario IDs, prompts, and expected failure modes"],
                "forbidden_claims": [
                    "runtime dependency on KnowledgeOS",
                    "Tessl result quality without execution evidence",
                ],
                "freshness": "knowledge_os_snapshot",
                "context_budget": "small",
                "claim_scope": "eval_scenarios",
                "bounded_unit": True,
            }
        )
    if eval_routes["fixtures"]:
        entries.append(
            {
                "path": "references/evals/",
                "kind": "knowledge_eval_fixtures",
                "provenance": "vendored KnowledgeOS extraction",
                "load_when": "only when a selected scenario fixture needs detail beyond references/evals.yaml",
                "allowed_claims": ["fixture detail for selected KnowledgeOS eval scenarios"],
                "forbidden_claims": ["load all fixtures by default", "claims outside selected fixture text"],
                "freshness": "knowledge_os_snapshot",
                "context_budget": "selective",
                "claim_scope": "eval_fixture_detail",
                "bounded_unit": True,
            }
        )
    existing_paths = {str(item.get("path")) for item in references if isinstance(item, dict)}
    for entry in entries:
        if entry["path"] not in existing_paths:
            references.append(entry)
    allowed_claims = loaded.setdefault("allowed_claims", [])
    if (
        isinstance(allowed_claims, list)
        and "KnowledgeOS capsules are vendored references, not runtime dependencies" not in allowed_claims
    ):
        allowed_claims.append("KnowledgeOS capsules are vendored references, not runtime dependencies")
    if (
        eval_routes["scenarios"]
        and eval_routes["fixtures"]
        and isinstance(allowed_claims, list)
        and "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof"
        not in allowed_claims
    ):
        allowed_claims.append(
            "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof"
        )
    source_context.write_text(_yaml_safe_dump_data(loaded), encoding="utf-8")


def _run_proof(repo_root: Path, commands: list[str]) -> list[dict[str, Any]]:
    results = []
    for command in commands:
        process = subprocess.run(
            command.split(),
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        results.append(
            {
                "command": command,
                "status": "pass" if process.returncode == 0 else "fail",
                "exit_code": process.returncode,
                "stdout_excerpt": process.stdout[:4000],
                "stderr_excerpt": process.stderr[:4000],
            }
        )
    return results


def _preflight_security_gate(
    repo_root: Path,
    skill_dir: Path,
    extraction_root: Path,
    source_files: list[Path],
    *,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ask-knowledge-ingest-") as tmp:
        staged_parent = Path(tmp)
        staged_skill = staged_parent / skill_dir.name
        shutil.copytree(skill_dir, staged_skill, symlinks=False)
        for source_file in source_files:
            target = staged_skill / source_file.relative_to(extraction_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target)
        eval_routes = _eval_reference_routes(extraction_root, source_files)
        _update_knowledge_routing_files(staged_skill, eval_routes=eval_routes, manifest=manifest)
        gate_script = _resolve_skill_gate_script(repo_root)
        process = subprocess.run(
            [
                sys.executable,
                str(gate_script),
                str(staged_skill),
                "--require-security-evals",
                "--pi-high-fail",
                "--require-fail-fast",
            ],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return {
            "command": "skill_gate.py <staged-skill> --require-security-evals --pi-high-fail --require-fail-fast",
            "status": "pass" if process.returncode == 0 else "fail",
            "exit_code": process.returncode,
            "stdout_excerpt": process.stdout[:4000],
            "stderr_excerpt": process.stderr[:4000],
        }


def _resolve_skill_gate_script(repo_root: Path) -> Path:
    for plugins_root in ("Plugins", "plugins"):
        repo_local = repo_root / plugins_root / "skill-factory" / "scripts" / "skill-builder" / "skill_gate.py"
        if repo_local.is_file():
            return repo_local
    module_repo = Path(__file__).resolve().parents[5]
    for plugins_root in ("Plugins", "plugins"):
        module_local = module_repo / plugins_root / "skill-factory" / "scripts" / "skill-builder" / "skill_gate.py"
        if module_local.is_file():
            return module_local
    raise ValueError("skill-factory security gate script is missing.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _yaml() -> Any | None:
    try:
        import yaml
    except ModuleNotFoundError:
        return None
    return yaml


def _yaml_safe_load_text(text: str, *, label: str) -> Any:
    yaml = _yaml()
    if yaml is not None:
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"{label} is invalid YAML: {exc}") from exc
    ruby = _run_ruby_yaml_helper(
        "require 'yaml'; require 'json'; print JSON.generate(YAML.safe_load(STDIN.read, permitted_classes: [], aliases: false))",
        text,
    )
    if ruby is not None:
        return json.loads(ruby.stdout)
    try:
        return _parse_minimal_yaml(text)
    except LensCatalogError as exc:
        raise ValueError(f"{label} requires YAML syntax unsupported by the built-in parser.") from exc


def _yaml_safe_dump_data(data: Any) -> str:
    yaml = _yaml()
    if yaml is not None:
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    ruby = _run_ruby_yaml_helper(
        "require 'yaml'; require 'json'; print JSON.parse(STDIN.read).to_yaml",
        json.dumps(data),
    )
    if ruby is not None:
        return ruby.stdout
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _run_ruby_yaml_helper(code: str, stdin: str) -> subprocess.CompletedProcess[str] | None:
    try:
        process = subprocess.run(
            ["ruby", "-e", code],
            input=stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None
    return process if process.returncode == 0 else None


def main() -> int:
    payload = build_knowledge_ingest(
        Path.cwd(),
        extraction=sys.argv[1],
        skill=sys.argv[2],
        apply="--apply" in sys.argv,
        run_proof="--run-proof" in sys.argv,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"preview", "applied"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
