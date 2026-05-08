"""Markdown document parser and field helpers for HE eval report validation."""

from __future__ import annotations

from dataclasses import dataclass
import re

from report_contract import YES_NO_VALUES


@dataclass(frozen=True)
class ReportDocument:
    """Parsed eval report with markdown parsing hidden behind a small API."""

    text: str
    sections: dict[str, str]

    @classmethod
    def parse(cls, text: str) -> "ReportDocument":
        matches = list(re.finditer(r"(?m)^#{1,3}\s+(.+?)\s*$", text))
        sections: dict[str, str] = {}
        for index, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections.setdefault(title, text[start:end].strip("\n"))
        return cls(text=text, sections=sections)

    def section_present(self, section: str) -> bool:
        return section in self.sections

    def section_body(self, section: str) -> str:
        return self.sections.get(section, "")

    def field_value(self, field: str, *, section: str | None = None) -> str | None:
        body = self.section_body(section) if section else self.text
        return field_value(body, field)

    def gate_entries(self) -> list[dict[str, str]]:
        body = self.section_body("Eval Gate Matrix")
        entries: list[dict[str, str]] = []
        current: dict[str, str] | None = None
        for line in body.splitlines():
            value = field_value(line, "Gate:")
            if value is not None:
                if current is not None:
                    entries.append(current)
                current = {"Gate:": value}
                continue
            if current is None:
                continue
            for field in (
                "Expected:",
                "Actual:",
                "Status:",
                "Evidence:",
                "Confidence:",
                "Blocks Closure:",
                "Required Action:",
            ):
                field_line = field_value(line, field)
                if field_line is not None:
                    current[field] = field_line
        if current is not None:
            entries.append(current)
        return entries


def ensure_document(document: ReportDocument | str) -> ReportDocument:
    if isinstance(document, ReportDocument):
        return document
    return ReportDocument.parse(document)


def section_present(document: ReportDocument | str, section: str):
    return ensure_document(document).section_present(section)


def section_body(document: ReportDocument | str, section: str):
    return ensure_document(document).section_body(section)


def field_value(text: str, field: str):
    match = re.search(rf"(?mi)^{re.escape(field)}\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else None


def is_blankish(value: str | None):
    if value is None:
        return True
    return value.strip().lower() in {"", "n/a", "na", "none", "unknown", "tbd", "todo"}


def validate_required_fields(
    body: str,
    fields: list[str],
    errors: list[str],
    label: str,
    *,
    enforce_values: bool,
    optional_blank_fields: set[str] | None = None,
):
    optional_blank_fields = optional_blank_fields or set()
    for field in fields:
        value = field_value(body, field)
        if value is None:
            errors.append(f"{label} section is missing field: {field}")
            continue
        if field in optional_blank_fields:
            continue
        if enforce_values and is_blankish(value):
            errors.append(f"{label} field is blank: {field}")
