# Skill security checks report

Date: 2026-01-28
Scope: skill-creator + skill-installer prompt-injection and attachment scanning

## Summary
- Added warn-only prompt-injection and risky-command scanning for skill content.
- Added interactive warning gate (Investigate / Continue / Stop) before installs.
- Added `.skillignore` support so scans cover bundled attachments only.
- Added configurable regex list via `references/prompt-injection-patterns.json`.
- Added severity levels (low/medium/high) surfaced in warning output.
- Added automatic read-only investigation summary for the Investigate option.
- Added investigation triage labels and macOS `open` helper.
- Added local allow/blocklist support (outside repo) via `~/.codex/skill-security/allow-block.json` or `CODEX_SKILL_SECURITY_CONFIG`.
- Added Claude headless runner support to `run_skill_evals.py` (default runner); Codex optional.

## Files updated
- `utilities/skill-creator/scripts/skill_gate.py`
- `utilities/skill-creator/scripts/run_skill_evals.py`
- `utilities/skill-creator/SKILL.md`
- `utilities/skill-creator/references/prompt-injection-patterns.json`
- `utilities/skill-creator/references/evals.yaml`
- `utilities/skill-installer/scripts/install-skill-from-github.py`
- `utilities/skill-installer/SKILL.md`
- `utilities/skill-installer/references/prompt-injection-patterns.json`
- `utilities/skill-installer/references/evals.yaml`
- `reports/skill-security-checks.md`

## Verification
- `skill_gate.py` (warn-only findings, PASS)
- `quick_validate.py` (PASS)
- Interactive installer demo (A/B/C prompt)
- Claude evals (skill-creator, timeout 180s): PASS (20260128-185229)
- Claude evals (skill-installer, timeout 180s): PASS (20260128-193416)

## Notes
- Binary attachments are flagged for manual review.
- Non-interactive installs can use `--on-warning continue|stop`.
- Severity is optional; invalid values default to `medium` with a warning.
- Investigate option prints a read-only summary (file counts, largest files, binary attachments).
- Investigation includes triage labels and an `open` helper.
- Allow/block config is local-only and not committed to repo.
