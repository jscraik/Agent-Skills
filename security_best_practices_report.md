# Security Best Practices Report

**Date:** 2026-02-23
**Target:** `docs/plans/2026-02-23-feat-recursive-skill-graph-parity-pass-plan.md`

## Executive summary
The plan already covers several strong controls for governance and rollback, but as written it leaves multiple high-impact trust-boundary gaps for the approval and artifact pipelines. The highest remaining risk is an insufficiently tamper-resistant approval-to-write path: if a malicious or compromised actor can alter decision artifacts or control metadata inputs, canonical lesson promotion can occur outside the intended reviewer flow.

## Method
- Skill instructions were followed from `security-best-practices` and all language/framework references available under `/Users/jamiecraik/.agents/skills/security-best-practices/references` were considered.
- No dedicated Python web-framework reference matches these CLI-only scripts exactly, so plan-level security review and known secure defaults were applied.
- Findings are scoped to this plan content and referenced with exact plan line numbers.

## Critical findings

### C-01: Canonical lesson write path lacks a cryptographic trust boundary
**Severity:** Critical
**Impact (one sentence):** If an attacker can alter approval inputs or inject a crafted promotion decision, canonical lesson writes can be performed without a verifiable human-authority proof, causing irreversible governance corruption.
**Location:** `docs/plans/2026-02-23-feat-recursive-skill-graph-parity-pass-plan.md` lines 95-104, 134-137, 158

- Plan requires `--expected-version` CAS and immutable decision hash, but does not require signature verification for `promotion_decision.json` before applying canonical writes.
- The approval and policy checks are planned for local script-level enforcement, yet there is no explicit binding to strong actor identity or signed attestations.
- `human_promote_recursive_run.sh` is the approval choke-point but the proposal does not explicitly prevent tampering with attacker-controlled payload files before execution.

**Recommended fix:**
- Require signed approval artifacts (e.g., script-enforced detached signature or CI-issued one-time approval token).
- Verify signature + reviewer identity + decision hash before any canonical mutation.
- Record signed append-only audit evidence alongside `canonical-lessons.jsonl`.

## High findings

### H-01: Telemetry/CI upload path can unintentionally exfiltrate sensitive artifacts
**Severity:** High
**Impact (one sentence):** Uploading broader telemetry outputs without explicit redaction can leak secrets, internal prompts, or sensitive evaluation artifacts into CI artifacts and long-lived logs.
**Location:** lines 106-117, 119-120

- B2/B3 add new telemetry artifacts and workflow upload, but there is no explicit sanitization/allowlist policy in the plan.
- The report outputs include run and promotion artifacts that may carry sensitive reviewer notes, environment-derived paths, or embedded tokens from command outputs.

**Recommended fix:**
- Define a strict artifact allowlist and redact known secret patterns (`api_key`, `token`, `bearer`, etc.).
- Add a CI pre-upload scan to fail on likely secrets and default to minimal/required telemetry fields.

### H-02: Kill-switch control input needs hardened trust boundary and immutable precedence
**Severity:** High
**Impact (one sentence):** If kill-switch path/input is user- or PR-influenced, an attacker could trigger abort/rollback behavior to disrupt runs or hide malicious activity by forcing false terminal states.
**Location:** lines 57-60, 139-142

- Plan adds kill-switch via CLI/env path but does not specify path allowlist, ownership checks, or symlink/tamper protection.
- Kill-switch is high-precedence and should be protected from untrusted runtime configuration.

**Recommended fix:**
- Restrict kill-switch path to immutable runtime-owned file locations.
- Validate path against canonical allowlist and file ownership/perms before each check.
- Include anti-tamper marker (e.g., immutable flag or restricted directory) for kill-switch files.

### H-03: Reviewer allowlist policy location can be a mutable trust boundary
**Severity:** High
**Impact (one sentence):** Storing allowlist policy in a mutable repo file without integrity checks can be altered during change flow, bypassing intended reviewer controls.
**Location:** lines 134-137

- Suggested reviewer policy file can be overridden without explicit integrity controls in the plan.
- No explicit requirement for branch protection, required reviews, or signed policy updates for this trust artifact is stated.

**Recommended fix:**
- Keep allowlist in a branch-protected, review-gated source, and verify checks in validation path.
- Add integrity checks (hash/signature) for policy file reads.

## Medium findings

### M-01: `run_id`/`lesson_id` path and artifact derivation controls are under-specified
**Severity:** Medium
**Impact (one sentence):** Without strict identifier normalization, path or replay attacks could target unexpected artifact locations and corrupt state.
**Location:** lines 51-53, 64-67, 88-93, 124-126

- Plan documents robust lock/idempotency ideas but does not define canonical validation of run IDs, resume tokens, or artifact path derivation rules.
- The plan should specify strict format constraints and normalized path-safe encoding before creating directories/files.

### M-02: No explicit least-privilege execution model for validation/automation jobs
**Severity:** Medium
**Impact (one sentence):** Privileged execution of repair/validation scripts in CI can widen blast radius if scripts gain broader filesystem or network access during incident conditions.
**Location:** lines 145-149, 174-178, 180-186

- Plan lists validation and CI orchestration, but does not define restricted execution environment assumptions.
- Add explicit runtime sandboxing (least filesystem scope, non-root, no secret logging).

### M-03: Rollback requirement lacks explicit retention/immutability controls
**Severity:** Medium
**Impact (one sentence):** Rollback can be ineffective if rollback evidence is overwritten or not retained with immutable metadata.
**Location:** lines 61-62, 161-163

- Rollback lineage is planned, but no retention policy for `rollback_recommendation.json` and event logs is defined.
- Add retention + immutability (append-only + write-once per run record) to preserve forensic value.

## Low findings

### L-01: Verification commands do not include a secrets-leak assertion
**Severity:** Low
**Impact (one sentence):** CI may pass while still producing secret-bearing artifacts.
**Location:** lines 180-186

- Add a secrets scanning step (e.g., `gitleaks detect` / regex-based scan) on generated telemetry and canonical artifacts before artifact upload.

## Immediate next-step recommendations

1. Add integrity and identity binding to approval flow:
   - signature verification for `promotion_decision.json`
   - policy file integrity checks
2. Harden kill-switch and run identifier inputs:
   - fixed-path allowlist and ownership checks
   - strict identifier format validation
3. Add secure artifact controls:
   - allowlist + redaction + secret scanning pre-upload
4. Define least-privilege execution and artifact retention policy for replay/rollback evidence.

## Suggested verification checklist

- [ ] Add/execute a test case where an unsigned promotion decision is rejected.
- [ ] Add/execute a test case where an allowlisted reviewer is required and non-allowlisted path is blocked.
- [ ] Add/execute a test case where maliciously named `run_id` with traversal-like characters is rejected.
- [ ] Add/execute a test case where CI artifact upload is rejected on secret-pattern match.
- [ ] Validate rollback evidence is immutable, append-only, and retained with run lineage.

