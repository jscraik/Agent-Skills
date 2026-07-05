from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from ask.skills_sdk.package_build import build_package_digest_receipt


PACKAGE_SECURITY_SIGNATURE_SCHEMA_VERSION = "skills-sdk.package-security-signature-receipt.v0"
PACKAGE_SECURITY_SIGNATURE_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/package-security-signature-receipt.v0.schema.json"
)
PACKAGE_SECURITY_SIGNATURE_ACCEPTANCE_TRACE = ["PU-033", "FR-008", "SA-004", "SEC-001", "VP-033"]

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
}
SCRIPT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".ps1"}

SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?(?:key|token)|access[_-]?token|auth[_-]?token|secret|password|credential)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{8,}"
)
SUSPICIOUS_URL_RE = re.compile(
    r"https?://[^\s)'\"]*(?:raw\.githubusercontent\.com|gist\.githubusercontent\.com|bit\.ly|tinyurl\.com|\.sh\b|\.py\b|\.js\b|\.zip\b|\.tgz\b|\.tar\.gz\b|\.dmg\b|\.pkg\b|\.exe\b)[^\s)'\"]*",
    re.IGNORECASE,
)
PIPE_TO_SHELL_RE = re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(sh|bash|zsh|python|node)\b", re.IGNORECASE)
RUNTIME_FETCH_RE = re.compile(
    r'\b(fetch|download|curl|wget|retrieve)\b[^\n]{0,80}(?:\b(instruction|prompt|rule|skill|agent)\b|https?://[^\s)\'"]+)',
    re.IGNORECASE,
)
INSECURE_CREDENTIAL_OUTPUT_RE = re.compile(
    r"(?i)\b(print|echo|log|stdout|stderr|trace)\b[^\n]{0,80}\b(secret|token|password|credential|api key)\b"
)
UNTRUSTED_CONTENT_RE = re.compile(
    r"(?i)\b(untrusted|arbitrary url|third[- ]party|unknown website|social media|forum|reddit|browser content|web page)\b"
)
SYSTEM_SERVICE_RE = re.compile(r"(?i)\b(launchctl|systemctl|crontab|sudo)\b|/Library/LaunchAgents|/etc/")
DESTRUCTIVE_RE = re.compile(r"(?i)\brm\s+-rf\b|\bdelete all\b|\bdrop table\b|\bwipe\s+(?:the\s+)?(?:repo|disk|database)")
EXTERNAL_WRITE_RE = re.compile(r"(?i)\b(webhook|post to|send to|upload|publish|deploy|push)\b")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _digest_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.name


def _package_root(source_path: Path) -> Path:
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    return source.parent


def _is_script_context(path: Path) -> bool:
    return "scripts" in path.parts


def _read_text(path: Path) -> tuple[str | None, bool]:
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "SKILL.md" and not _is_script_context(path):
        return None, True
    try:
        return path.read_text(encoding="utf-8"), False
    except UnicodeDecodeError:
        return None, True


def _file_kind(path: Path, is_binary: bool) -> str:
    if is_binary:
        return "binary"
    if path.name == "SKILL.md":
        return "skill_md"
    if path.suffix.lower() in SCRIPT_SUFFIXES or _is_script_context(path):
        return "script"
    return "resource"


def _indicator(indicator_id: str, evidence_ref: str, reason: str) -> dict[str, str]:
    return {"id": indicator_id, "evidence_ref": evidence_ref, "reason": reason}


def _has_hidden_unicode(text: str) -> bool:
    for char in text:
        if char in "\n\r\t":
            continue
        if unicodedata.category(char) in {"Cf", "Cc"}:
            return True
    return False


def _text_indicators(text: str, evidence_ref: str) -> list[dict[str, str]]:
    indicators: list[dict[str, str]] = []
    if _has_hidden_unicode(text):
        indicators.append(
            _indicator("hidden_unicode_obfuscation", evidence_ref, "Contains invisible control or format characters.")
        )
    if PIPE_TO_SHELL_RE.search(text):
        indicators.append(_indicator("pipe_to_shell_download", evidence_ref, "Downloads content and pipes it to an interpreter."))
    if SUSPICIOUS_URL_RE.search(text):
        indicators.append(_indicator("suspicious_download_url", evidence_ref, "References a high-risk download URL pattern."))
    if RUNTIME_FETCH_RE.search(text):
        indicators.append(
            _indicator("runtime_instruction_fetch", evidence_ref, "Fetches remote content or instructions at runtime.")
        )
    if SECRET_ASSIGNMENT_RE.search(text):
        indicators.append(_indicator("hardcoded_secret_literal", evidence_ref, "Contains a secret-like assignment pattern."))
    if INSECURE_CREDENTIAL_OUTPUT_RE.search(text):
        indicators.append(
            _indicator("insecure_credential_output", evidence_ref, "Suggests printing or logging credential material.")
        )
    if UNTRUSTED_CONTENT_RE.search(text):
        indicators.append(_indicator("untrusted_content_ingestion", evidence_ref, "Consumes untrusted third-party content."))
    if SYSTEM_SERVICE_RE.search(text):
        indicators.append(_indicator("system_service_modification", evidence_ref, "Touches system service or privileged OS surfaces."))
    if DESTRUCTIVE_RE.search(text):
        indicators.append(_indicator("destructive_local_capability", evidence_ref, "Contains destructive local operation language."))
    if UNTRUSTED_CONTENT_RE.search(text) and (SECRET_ASSIGNMENT_RE.search(text) or EXTERNAL_WRITE_RE.search(text)):
        indicators.append(
            _indicator("composed_capability_risk", evidence_ref, "Combines untrusted content with secret handling or external writes.")
        )
    return indicators


def _file_security_record(repo_root: Path, path: Path) -> dict[str, Any]:
    evidence_ref = _repo_relative(repo_root, path)
    text, is_binary = _read_text(path)
    kind = _file_kind(path, is_binary)
    indicators = [] if text is None else _text_indicators(text, evidence_ref)
    return {
        "path": evidence_ref,
        "kind": kind,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
        "indicators": indicators,
    }


def _included_paths(repo_root: Path, package_receipt: dict[str, Any], package_root: Path) -> list[Path]:
    paths: list[Path] = []
    external = not package_root.resolve(strict=False).is_relative_to(repo_root.resolve(strict=False))
    for path_ref in package_receipt["included_files"]:
        path = package_root / path_ref if external else repo_root / path_ref
        if path.is_file():
            paths.append(path)
    return sorted(paths, key=lambda item: item.as_posix())


def _indicator_summary(file_results: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for result in file_results:
        for indicator in result["indicators"]:
            summary[indicator["id"]] = summary.get(indicator["id"], 0) + 1
    return dict(sorted(summary.items()))


def build_package_security_signature_receipt(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    """Build a non-executing package security signature over declared skill package files."""
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    package_root = _package_root(source)
    package_receipt = build_package_digest_receipt(repo_root, source_path=source, query=query)
    paths = _included_paths(repo_root, package_receipt, package_root)
    file_results = [_file_security_record(repo_root, path) for path in paths]
    indicator_summary = _indicator_summary(file_results)
    indicators = [indicator for result in file_results for indicator in result["indicators"]]
    text_file_count = sum(1 for result in file_results if result["kind"] != "binary")
    script_file_count = sum(1 for result in file_results if result["kind"] == "script")
    binary_file_count = sum(1 for result in file_results if result["kind"] == "binary")
    resource_file_count = sum(1 for result in file_results if result["kind"] == "resource")
    signature_material = {
        "package_digest": package_receipt["package_digest"],
        "file_results": file_results,
        "indicator_summary": indicator_summary,
    }
    return {
        "schema_version": PACKAGE_SECURITY_SIGNATURE_SCHEMA_VERSION,
        "schema_uri": PACKAGE_SECURITY_SIGNATURE_SCHEMA_URI,
        "status": "pass",
        "operation": "package_security_signature_preview",
        "query": query,
        "package_id": package_receipt["package_id"],
        "package_digest": package_receipt["package_digest"],
        "source_digest": package_receipt["source_digest"],
        "package_security_signature_digest": _digest_json(signature_material),
        "inspected_file_count": len(file_results),
        "text_file_count": text_file_count,
        "script_file_count": script_file_count,
        "resource_file_count": resource_file_count,
        "binary_file_count": binary_file_count,
        "redaction_performed": True,
        "redacted_content_emitted": False,
        "binary_content_embedded": False,
        "indicator_summary": indicator_summary,
        "indicators": indicators,
        "file_results": file_results,
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": PACKAGE_SECURITY_SIGNATURE_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"package security signature inspected {package_receipt['package_id']} across {len(file_results)} "
            f"declared file(s) and found {len(indicators)} indicator(s) without execution, scanners, network, "
            "credentials, raw content emission, or mutation."
        ),
    }
