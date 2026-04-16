#!/usr/bin/env python3
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class Issue:
    severity: str  # "ERROR" | "WARN"
    message: str
    line: Optional[int] = None

    def format(self) -> str:
        if self.line is None:
            return f"{self.severity}: {self.message}"
        return f"{self.severity}: L{self.line}: {self.message}"


@dataclass
class Heading:
    level: int
    title: str
    start_idx: int
    end_idx: int
    line: int


HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.*)\s*$")
H2_RE = re.compile(r"(?m)^##\s+")
NA_BARE_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?N\/A\s*$")
EVIDENCE_LINE_RE = re.compile(r"(?im)^\s*Evidence:\s+|^\s*Evidence gap:\s+")
EVIDENCE_GAP_RE = re.compile(r"(?im)\bGap:\b|\bEvidence gap\b")

PRD_REQUIRED = [
    ("Template Metadata", [r"\bTemplate Metadata\b"]),
    ("Executive Summary", [r"\bExecutive Summary\b"]),
    ("Problem / Opportunity", [r"\bProblem\b.*\bOpportunity\b|\bProblem Statement\b|\bProblem / Opportunity\b"]),
    ("Target Users / Personas", [r"\bTarget Users\b|\bPersonas\b"]),
    ("User Stories", [r"\bUser Stories\b|\bUse Cases\b"]),
    ("Acceptance Criteria", [r"\bAcceptance Criteria\b"]),
    ("Decision Log / ADRs", [r"\bDecision Log\b|\bADRs\b"]),
    ("Data Lifecycle & Retention", [r"\bData Lifecycle\b|\bData Lifecycle & Retention\b|\bLifecycle & Retention\b"]),
    ("Functional Requirements", [r"\bFunctional Requirements\b"]),
    ("Non-Functional Requirements", [r"\bNon[- ]Functional Requirements\b"]),
    ("Success Metrics / KPIs", [r"\bSuccess Metrics\b|\bKPIs\b"]),
    ("Scope", [r"^Scope\b|\bScope\b"]),
    ("Feature Creep Guardrails", [r"\bFeature Creep Guardrails\b"]),
    ("Scope Decision Log", [r"\bScope Decision Log\b"]),
    ("Dependencies", [r"\bDependencies\b"]),
    ("Risks", [r"\bRisks\b"]),
    ("Launch & Rollback Guardrails", [r"\bLaunch\b.*\bRollback\b|\bRollback Guardrails\b"]),
    ("Post-Launch Monitoring Plan", [r"\bPost[- ]Launch\b.*\bMonitoring\b"]),
    ("Support / Ops Impact", [r"\bSupport\b.*\bOps\b|\bOps Impact\b"]),
    ("Compliance & Regulatory Review Triggers", [r"\bCompliance\b.*\bRegulatory\b|\bRegulatory Review Triggers\b|\bCompliance & Regulatory Review Triggers\b"]),
    ("Ownership & RACI", [r"\bOwnership\b.*\bRACI\b|\bRACI\b"]),
    ("Security & Privacy Classification", [r"\bSecurity\b.*\bPrivacy\b.*\bClassification\b|\bSecurity & Privacy Classification\b"]),
    ("Dependency SLAs & Vendor Risk", [r"\bDependency SLAs\b|\bVendor Risk\b"]),
    ("Cost Model & Budget Guardrails", [r"\bCost Model\b|\bBudget Guardrails\b"]),
    ("Localization & Internationalization", [r"\bLocalization\b|\bInternationalization\b|\bI18n\b"]),
    ("Backward Compatibility & Deprecation", [r"\bBackward Compatibility\b|\bDeprecation\b"]),
    ("Experimentation & Feature Flags", [r"\bExperimentation\b|\bFeature Flags?\b"]),
    ("Kill Criteria", [r"\bKill Criteria\b|\bStop conditions\b"]),
    ("Evidence Gaps", [r"\bEvidence Gaps\b"]),
    ("Evidence Map", [r"\bEvidence Map\b"]),
    ("Assumptions & Open Questions", [r"\bAssumptions\b.*\bOpen Questions\b|\bOpen Questions\b"]),
    ("PRD Integrity Rule", [r"\bPRD Integrity\b|\bIntegrity Rule\b"]),
]

TECH_REQUIRED = [
    ("Overview / Context", [r"\bOverview\b|\bContext\b"]),
    ("Goals and Non-Goals", [r"\bGoals\b.*\bNon[- ]Goals\b|\bGoals and Non[- ]Goals\b"]),
    ("Template Metadata", [r"\bTemplate Metadata\b"]),
    ("Scope", [r"^Scope\b|\bScope\b"]),
    ("Feature Creep Guardrails", [r"\bFeature Creep Guardrails\b"]),
    ("Scope Decision Log", [r"\bScope Decision Log\b"]),
    ("Acceptance Criteria", [r"\bAcceptance Criteria\b"]),
    ("Decision Log / ADRs", [r"\bDecision Log\b|\bADRs\b"]),
    ("Data Lifecycle & Retention", [r"\bData Lifecycle\b|\bData Lifecycle & Retention\b|\bLifecycle & Retention\b"]),
    ("System Architecture", [r"\bSystem Architecture\b|\bArchitecture\b"]),
    ("Component Design", [r"\bComponent Design\b"]),
    ("API Design", [r"\bAPI Design\b"]),
    ("Data Models", [r"\bData Models\b|\bDatabase Schema\b"]),
    ("Infrastructure Requirements", [r"\bInfrastructure Requirements\b"]),
    ("Security Considerations", [r"\bSecurity Considerations\b|\bSecurity\b"]),
    ("Error Handling Strategy", [r"\bError Handling\b"]),
    ("Performance Requirements", [r"\bPerformance\b|\bSLAs?\b|\bSLOs?\b"]),
    ("Observability", [r"\bObservability\b"]),
    ("Testing Strategy", [r"\bTesting Strategy\b|\bTesting\b"]),
    ("Deployment Strategy", [r"\bDeployment Strategy\b|\bDeployment\b"]),
    ("Launch & Rollback Guardrails", [r"\bLaunch\b.*\bRollback\b|\bRollback Guardrails\b"]),
    ("Post-Launch Monitoring Plan", [r"\bPost[- ]Launch\b.*\bMonitoring\b"]),
    ("Support / Ops Impact", [r"\bSupport\b.*\bOps\b|\bOps Impact\b"]),
    ("Compliance & Regulatory Review Triggers", [r"\bCompliance\b.*\bRegulatory\b|\bRegulatory Review Triggers\b|\bCompliance & Regulatory Review Triggers\b"]),
    ("Ownership & RACI", [r"\bOwnership\b.*\bRACI\b|\bRACI\b"]),
    ("Security & Privacy Classification", [r"\bSecurity\b.*\bPrivacy\b.*\bClassification\b|\bSecurity & Privacy Classification\b"]),
    ("Dependency SLAs & Vendor Risk", [r"\bDependency SLAs\b|\bVendor Risk\b"]),
    ("Cost Model & Budget Guardrails", [r"\bCost Model\b|\bBudget Guardrails\b"]),
    ("Localization & Internationalization", [r"\bLocalization\b|\bInternationalization\b|\bI18n\b"]),
    ("Backward Compatibility & Deprecation", [r"\bBackward Compatibility\b|\bDeprecation\b"]),
    ("Experimentation & Feature Flags", [r"\bExperimentation\b|\bFeature Flags?\b"]),
    ("Kill Criteria", [r"\bKill Criteria\b|\bStop conditions\b"]),
    ("Evidence Gaps", [r"\bEvidence Gaps\b"]),
    ("Evidence Map", [r"\bEvidence Map\b"]),
    ("Open Questions", [r"\bOpen Questions\b|\bFuture Considerations\b"]),
]

PRD_TECH_LEAK_KEYWORDS = [
    "postgres", "mysql", "sqlite", "mongodb", "dynamodb", "redis", "memcached",
    "kubernetes", "k8s", "helm", "docker", "terraform", "pulumi",
    "aws", "gcp", "azure", "lambda", "cloudformation",
    "grpc", "protobuf", "kafka", "rabbitmq", "kinesis", "pubsub",
]


def parse_headings(text: str) -> List[Heading]:
    headings: List[Heading] = []
    for m in HEADING_RE.finditer(text):
        hashes = m.group(1)
        title = m.group(2).strip()
        start = m.start()
        end = m.end()
        line = text.count("\n", 0, start) + 1
        headings.append(Heading(level=len(hashes), title=title, start_idx=start, end_idx=end, line=line))
    return headings


def find_heading(headings: List[Heading], patterns: List[str]) -> Optional[Heading]:
    for h in headings:
        for pat in patterns:
            if re.search(pat, h.title, flags=re.IGNORECASE):
                return h
    return None


def section_text(text: str, headings: List[Heading], heading: Heading) -> str:
    start = heading.end_idx
    end = len(text)
    for h in headings:
        if h.start_idx <= heading.start_idx:
            continue
        if h.level <= heading.level:
            end = h.start_idx
            break
    return text[start:end]


def infer_doc_type(text: str) -> str:
    if re.search(r"(?i)\bTechnical Specification\b|\bTech Spec\b", text):
        return "tech"
    if re.search(r"(?i)\bPRD\b|Product Requirements Document|#\s*PRD", text):
        return "prd"
    if re.search(r"(?i)\bSystem Architecture\b|\bComponent Design\b|\bObservability\b", text):
        return "tech"
    return "prd"


def check_bare_na(text: str) -> List[Issue]:
    issues: List[Issue] = []
    for m in NA_BARE_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        issues.append(Issue("ERROR", "Found bare 'N/A' with no explanation. Add 1–2 lines explaining why.", line))
    return issues


def split_blocks(text: str) -> List[Tuple[int, str]]:
    blocks: List[Tuple[int, str]] = []
    lines = text.split("\n")
    buf: List[str] = []
    start_line = 1
    in_code = False
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and line.strip() == "":
            if buf:
                blocks.append((start_line, "\n".join(buf)))
                buf = []
            start_line = i + 1
            continue
        if not buf:
            start_line = i
        buf.append(line)
    if buf:
        blocks.append((start_line, "\n".join(buf)))
    return blocks


def is_substantive_block(block: str) -> bool:
    stripped = block.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return False
    if re.match(r"^\|.*\|$", stripped):
        return False
    if all(line.strip().startswith("|") or line.strip().startswith("-|") for line in stripped.split("\n")):
        return False
    return True


def check_evidence_lines(text: str) -> List[Issue]:
    issues: List[Issue] = []
    for line_no, block in split_blocks(text):
        if not is_substantive_block(block):
            continue
        if not EVIDENCE_LINE_RE.search(block):
            issues.append(Issue("ERROR", "Missing Evidence line in paragraph block.", line_no))
    return issues


def check_evidence_sections(text: str, headings: List[Heading], strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    h_map = find_heading(headings, [r"\bEvidence Map\b"])
    if h_map:
        sec = section_text(text, headings, h_map)
        if re.search(r"\|\s*Section\s*/\s*Claim\s*\|\s*Evidence\s*\|", sec, flags=re.IGNORECASE) is None:
            issues.append(Issue("ERROR" if strict else "WARN", "Evidence Map section missing table header.", h_map.line))
    h_gaps = find_heading(headings, [r"\bEvidence Gaps\b"])
    if h_gaps:
        sec = section_text(text, headings, h_gaps)
        if EVIDENCE_GAP_RE.search(sec) is None:
            issues.append(Issue("ERROR" if strict else "WARN", "Evidence Gaps section appears empty.", h_gaps.line))
    return issues


def extract_story_blocks(text: str) -> List[Tuple[int, int, int]]:
    start_re = re.compile(r"(?im)^\s*(?:\d+[\)\.]|[-*])\s*(?:\*\*Story:\*\*|Story:)\s*")
    starts = [m.start() for m in start_re.finditer(text)]
    blocks: List[Tuple[int, int, int]] = []
    if not starts:
        return blocks

    for i, s in enumerate(starts):
        candidates = []
        if i + 1 < len(starts):
            candidates.append(starts[i + 1])
        h2 = H2_RE.search(text, pos=s + 1)
        if h2:
            candidates.append(h2.start())
        e = min(candidates) if candidates else len(text)
        line = text.count("\n", 0, s) + 1
        blocks.append((s, e, line))
    return blocks


def check_story_quality_prd(text: str, strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    blocks = extract_story_blocks(text)

    if blocks:
        for s, e, line in blocks:
            blk = text[s:e]
            if not re.search(r"(?is)\bAs an?\b.*?\bI want\b.*?\bso that\b", blk):
                issues.append(Issue("ERROR", "User story missing required 'As a..., I want..., so that...' format.", line))
            if not re.search(r"(?i)Acceptance criteria", blk):
                issues.append(Issue("ERROR", "User story missing 'Acceptance criteria:' section.", line))
            if not re.search(r"(?m)^\s*[-*]\s*\[\s*\]\s+\S+", blk):
                issues.append(Issue("ERROR", "Acceptance criteria missing checkbox items '- [ ] ...'.", line))
    else:
        if not re.search(r"(?is)\bAs an?\b.*?\bI want\b.*?\bso that\b", text):
            issues.append(Issue("WARN", "No recognizable user story blocks found. Consider using 'Story:' blocks for linting."))
        if strict and not re.search(r"(?i)Acceptance criteria", text):
            issues.append(Issue("ERROR", "Strict mode: no 'Acceptance criteria' found anywhere."))

    return issues


def check_metrics_numeric(text: str, headings: List[Heading], doc_type: str, strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    if doc_type == "prd":
        h = find_heading(headings, [r"\bSuccess Metrics\b|\bKPIs\b"])
        if not h:
            return issues
        sec = section_text(text, headings, h)
        has_digit = bool(re.search(r"\d", sec))
        if not has_digit:
            msg = "Success metrics section contains no digits. Add numeric targets (or mark clearly as placeholder)."
            issues.append(Issue("ERROR" if strict else "WARN", msg, h.line))
    else:
        h = find_heading(headings, [r"\bPerformance\b|\bSLA\b|\bSLO\b"])
        if not h:
            return issues
        sec = section_text(text, headings, h)
        has_digit = bool(re.search(r"\d", sec))
        if not has_digit:
            msg = "Performance section contains no digits. Add numeric latency/throughput/availability targets."
            issues.append(Issue("ERROR" if strict else "WARN", msg, h.line))
    return issues


def check_template_metadata(text: str, headings: List[Heading]) -> List[Issue]:
    issues: List[Issue] = []
    h = find_heading(headings, [r"\bTemplate Metadata\b"])
    if not h:
        issues.append(Issue("ERROR", "Missing required section: Template Metadata"))
        return issues

    sec = section_text(text, headings, h)
    required_fields = [
        ("name", r"\bname\s*:\s*\S+"),
        ("description", r"\bdescription\s*:\s*\S+"),
        ("title_template", r"\btitle_template\s*:\s*.+"),
        ("acceptance_criteria", r"\bacceptance_criteria\s*:"),
        ("priority", r"\bpriority\s*:\s*\S+"),
        ("variables", r"\bvariables\s*:\s*[\[\(].*[\]\)]|\bvariables\s*:\s*\S+"),
        ("metadata", r"\bmetadata\s*:\s*[\{\[]|\bmetadata\s*:\s*\S+"),
    ]

    for field, pattern in required_fields:
        if re.search(pattern, sec, flags=re.IGNORECASE) is None:
            issues.append(Issue("ERROR", f"Template Metadata missing '{field}'.", h.line))

    if re.search(r"\btitle_template\s*:\s*.*\{[^}]+\}", sec, flags=re.IGNORECASE) is None:
        issues.append(Issue("ERROR", "Template Metadata 'title_template' must include {variable} placeholders.", h.line))

    if re.search(r"(?im)^\s*[-*]\s+\S+", sec) is None:
        issues.append(Issue("WARN", "Template Metadata acceptance_criteria list appears empty.", h.line))

    return issues


def check_prd_impl_leak(text: str) -> List[Issue]:
    issues: List[Issue] = []
    lower = text.lower()
    hits = [kw for kw in PRD_TECH_LEAK_KEYWORDS if kw in lower]
    if hits:
        issues.append(Issue(
            "WARN",
            "Possible implementation details present in PRD (keep PRD WHAT/WHY/WHO). Found: " + ", ".join(sorted(set(hits)))
        ))
    return issues


def check_tech_components_state_machines(text: str, strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    comp_re = re.compile(r"(?im)^###\s+Component:\s+(.+)\s*$")
    comps = list(comp_re.finditer(text))
    if not comps:
        return issues

    for i, m in enumerate(comps):
        name = m.group(1).strip()
        start = m.start()
        end = comps[i + 1].start() if i + 1 < len(comps) else len(text)
        blk = text[start:end]
        line = text.count("\n", 0, start) + 1

        has_state = ("stateDiagram" in blk) or re.search(r"(?i)State machine:\s*N\/A", blk) is not None
        if not has_state:
            issues.append(Issue(
                "ERROR" if strict else "WARN",
                f"Component '{name}' missing state machine (stateDiagram) or 'State machine: N/A (stateless)'.",
                line
            ))
    return issues


def check_tech_deployment_rollback(text: str, headings: List[Heading], strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    h = find_heading(headings, [r"\bDeployment Strategy\b|\bDeployment\b"])
    if not h:
        return issues
    sec = section_text(text, headings, h)
    if not re.search(r"(?i)\brollback\b", sec):
        issues.append(Issue(
            "ERROR" if strict else "WARN",
            "Deployment section missing explicit rollback strategy.",
            h.line
        ))
    return issues


def check_required_sections(text: str, headings: List[Heading], required: List[Tuple[str, List[str]]]) -> List[Issue]:
    issues: List[Issue] = []
    for name, patterns in required:
        h = find_heading(headings, patterns)
        if not h:
            issues.append(Issue("ERROR", f"Missing required section: {name}"))
    return issues


def check_feature_creep_guardrails(text: str, headings: List[Heading], strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    h = find_heading(headings, [r"\bFeature Creep Guardrails\b"])
    if not h:
        return issues
    sec = section_text(text, headings, h)

    checks = [
        ("Core problem validated", r"(?i)Core problem validated\?\s*.+"),
        ("Smallest shippable version", r"(?i)Smallest shippable version:\s*.+"),
        ("What we are NOT building", r"(?i)NOT building.*:\s*.+"),
        ("Success measure", r"(?i)Success measure.*:\s*.+"),
        ("48-hour rule", r"(?i)48[- ]hour rule.*:\s*.+"),
    ]
    for label, pat in checks:
        if re.search(pat, sec) is None:
            issues.append(Issue("ERROR" if strict else "WARN", f"Feature creep guardrails missing: {label}.", h.line))

    if re.search(r"https?://|\b\w+\.md\b", sec, flags=re.IGNORECASE) is None:
        issues.append(Issue("WARN", "Feature creep guardrails should cite evidence (link or doc path).", h.line))

    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", sec) is None:
        issues.append(Issue("WARN", "Feature creep guardrails should include a date for the 48-hour rule.", h.line))

    return issues


def check_scope_decision_log(text: str, headings: List[Heading], strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    h = find_heading(headings, [r"\bScope Decision Log\b"])
    if not h:
        return issues
    sec = section_text(text, headings, h)
    if re.search(r"(?m)^\|\s*\d{4}-\d{2}-\d{2}\s*\|", sec) is None:
        issues.append(Issue("ERROR" if strict else "WARN", "Scope Decision Log missing any dated entries.", h.line))
    return issues


def check_adr_links(text: str, headings: List[Heading], strict: bool) -> List[Issue]:
    issues: List[Issue] = []
    h = find_heading(headings, [r"\bDecision Log\b|\bADRs\b"])
    if not h:
        return issues
    sec = section_text(text, headings, h)
    if re.search(r"(?i)ADR link:\s*.+", sec) is None:
        issues.append(Issue("ERROR" if strict else "WARN", "Decision Log missing 'ADR link' entry.", h.line))
    if re.search(r"https?://|\b\w+\.md\b", sec, flags=re.IGNORECASE) is None:
        issues.append(Issue("WARN", "Decision Log should include a path or URL to ADR.", h.line))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint PRDs and Tech Specs for completeness and quality gates.")
    ap.add_argument("file", help="Markdown file to lint (e.g., spec-output.md)")
    ap.add_argument("--type", choices=["prd", "tech"], help="Document type. If omitted, inferred.")
    ap.add_argument("--strict", action="store_true", help="Treat important warnings as errors.")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    headings = parse_headings(text)

    doc_type = args.type or infer_doc_type(text)
    strict = args.strict

    issues: List[Issue] = []
    issues.extend(check_bare_na(text))
    issues.extend(check_evidence_lines(text))

    if doc_type == "prd":
        issues.extend(check_template_metadata(text, headings))
        issues.extend(check_required_sections(text, headings, PRD_REQUIRED))
        issues.extend(check_story_quality_prd(text, strict=strict))
        issues.extend(check_metrics_numeric(text, headings, doc_type="prd", strict=strict))
        issues.extend(check_feature_creep_guardrails(text, headings, strict=strict))
        issues.extend(check_scope_decision_log(text, headings, strict=strict))
        issues.extend(check_adr_links(text, headings, strict=strict))
        issues.extend(check_prd_impl_leak(text))
        issues.extend(check_evidence_sections(text, headings, strict=strict))
    else:
        issues.extend(check_template_metadata(text, headings))
        issues.extend(check_required_sections(text, headings, TECH_REQUIRED))
        issues.extend(check_metrics_numeric(text, headings, doc_type="tech", strict=strict))
        issues.extend(check_feature_creep_guardrails(text, headings, strict=strict))
        issues.extend(check_scope_decision_log(text, headings, strict=strict))
        issues.extend(check_adr_links(text, headings, strict=strict))
        issues.extend(check_tech_components_state_machines(text, strict=strict))
        issues.extend(check_tech_deployment_rollback(text, headings, strict=strict))
        issues.extend(check_evidence_sections(text, headings, strict=strict))

    errors = [i for i in issues if i.severity == "ERROR"]
    warns = [i for i in issues if i.severity == "WARN"]

    for i in issues:
        print(i.format())

    print(f"\nSummary: {len(errors)} error(s), {len(warns)} warning(s) [{doc_type}]")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
