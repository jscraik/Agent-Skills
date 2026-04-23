# Skill security checks report

Date: 2026-01-28
Scope: skill-builder + skill-installer prompt-injection and attachment scanning

## Summary
- Added warn-only prompt-injection and risky-command scanning for skill content.
- Added interactive warning gate (Investigate / Continue / Stop) before installs.
- Added `.skillignore` support so scans cover bundled attachments only.
- Added configurable regex list via `Infrastructure/references/prompt-injection-patterns.json`.
- Added severity levels (low/medium/high) surfaced in warning output.
- Added automatic read-only investigation summary for the Investigate option.
- Added investigation triage labels and macOS `open` helper.
- Added local allow/blocklist support (outside repo) via `~/.codex/skill-security/allow-block.json` or `CODEX_SKILL_SECURITY_CONFIG`.
- Added Codex headless runner support to `run_skill_evals.py` (default runner); Codex optional.

## Files updated
- `Skills/skill-builder/Infrastructure/scripts/skill_gate.py`
- `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`
- `Skills/skill-builder/SKILL.md`
- `Skills/skill-builder/Infrastructure/references/prompt-injection-patterns.json`
- `Skills/skill-builder/Infrastructure/references/evals.yaml`
- `Skills/skill-installer/Infrastructure/scripts/install-skill-from-github.py`
- `Skills/skill-installer/SKILL.md`
- `Skills/skill-installer/Infrastructure/references/prompt-injection-patterns.json`
- `Skills/skill-installer/Infrastructure/references/evals.yaml`
- `Infrastructure/reports/skill-security-checks.md`

## Verification
- `skill_gate.py` (warn-only findings, PASS)
- `quick_validate.py` (PASS)
- Interactive installer demo (A/B/C prompt)
- Codex evals (skill-builder, timeout 180s): PASS (20260128-185229)
- Codex evals (skill-installer, timeout 180s): PASS (20260128-193416)

## Notes
- Binary attachments are flagged for manual review.
- Non-interactive installs can use `--on-warning continue|stop`.
- Severity is optional; invalid values default to `medium` with a warning.
- Investigate option prints a read-only summary (file counts, largest files, binary attachments).
- Investigation includes triage labels and an `open` helper.
- Allow/block config is local-only and not committed to repo.
