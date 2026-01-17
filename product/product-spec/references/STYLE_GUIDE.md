# BrAInwav Product & Engineering Documentation Style Guide

Purpose: keep docs clear, testable, and production-oriented. This guide applies to PRDs, tech specs, review reports, ADRs, and root READMEs.

---

## 1) Voice and Tone
- Prefer short sentences, concrete nouns, and testable statements.
- Avoid hype and marketing language.
- Be explicit about uncertainty: write “unknown” + how you’ll find out.

---

## 2) “Required unless N/A”
If a required section does not apply:
- Write `N/A — <1–2 lines explaining why>`.
- Never leave required sections blank.

---

## 3) Requirements Language
Use precise language:
- PRD: focus on **WHAT / WHY / WHO**. Avoid implementation detail.
- Tech Spec: focus on **HOW** and use clear commitments.
- Use MUST/SHOULD/MAY sparingly, only when you mean it.

---

## 4) Tables
Tables are for:
- keywords, numbers, short phrases, IDs
Avoid putting long prose in tables.

---

## 5) Naming and IDs
- Functional requirements: `FR-1`, `FR-2`, …
- Non-functional requirements: `NFR-1`, `NFR-2`, …
- Risks: `RISK-1`, …
- Open questions: `Q-1`, …
Use consistent terminology across the doc. Add a Glossary when terms are overloaded.

---

## 6) Diagrams (Mermaid-first)
- Embed Mermaid code blocks directly in Markdown.
- Every stateful workflow/component (≥3 states) gets a Mermaid `stateDiagram-v2`.
- Stateless components: use `flowchart` or `sequenceDiagram` instead.
- Ensure diagrams compile. If you need images, render with `mmdc` (mermaid-cli) into `docs/assets/diagrams/`.

---

## 7) Metrics and Measurement
Every KPI/SLO needs:
- numeric target
- measurement window
- measurement method
- source of truth (event name/dashboard)

Avoid “improve” or “increase” without specifying how you’ll measure it.

---

## 8) Security & Privacy baseline
Any doc mentioning user data must answer:
- what data is collected/stored
- classification (PII/PHI/PCI/none)
- retention policy
- access controls (authN/authZ expectations)

---

## 9) BrAInwav Documentation Signature
BrAInwav uses a documentation signature (not a watermark).

Approved footer (preferred):
- **brAInwav**
- _from demo to duty_

Use the official snippet from the brand guidelines skill.

Do:
- Put signature at the bottom of root README.
Don’t:
- place signatures between headings or inside technical sections
- use watermarks

---

## 10) Review gates
Before “final”:
- PRDs must pass `references/PRD_CHECKLIST.md`
- Tech specs must pass `references/TECH_SPEC_CHECKLIST.md`
- Production work should pass ORR / launch checklists when shipping
