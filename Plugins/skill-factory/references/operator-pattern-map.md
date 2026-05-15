# Operator Pattern Map

This map keeps the useful external skill patterns in Skill Factory without
copying another author's local paths, prose style, or runtime assumptions.

## Positive Patterns To Preserve

| Pattern | Skill Factory contract | Validation or eval surface |
|---|---|---|
| Routing descriptions are payloads | Descriptions should name domain, verbs, artifacts, and constraints. | Skill audit checks description focus; router evals cover false positives. |
| Executable posture first | Hot-path skills state the stance and first action before background. | Strict skill audit and smoke evals. |
| First tool or source is explicit | Skills name the first command, helper, or evidence source when one exists. | Evals require canonical first step or conservative assumption. |
| Tool resolution is logic | Preferred tool, fallback, and status/doctor checks live in the relevant reference. | Builder fast validation checks referenced scripts and helpers exist. |
| Narrow default scope | Default to the smallest safe scope; broaden only on named triggers. | Router and builder evals test ambiguous and broad requests. |
| Mode-specific flows | Broad/release/deep modes are separate from fast edits. | Tiered validation contract in `skill-builder`. |
| Source order and freshness | Local truth, bounded evidence, live state before writes, then user confirmation when needed. | Builder/refactor evals and validation evidence fields. |
| Write verification | Verify action-state immediately before writes and targeted readback after writes. | Operational/install evals and closeout contract. |
| Batch and machine-readable output | Prefer narrow JSON/batch commands where available. | Script/reference audit and helper tests. |
| Failure ladder | Retry counts, stop conditions, and next commands are concrete. | Builder output and failure-mode evals. |
| Decision checklist | Review/judgment skills ask fixed domain questions before findings. | Review archetype evals and contract references. |
| Call-path reading | Review skills read past touched files into callers/callees/config. | Builder hardening references. |
| Dependency claims verified | Dependency behavior routes to docs/source/types. | Validation evidence and external-doc decision field. |
| Findings require failure mode | Findings must include impact, reproduction path, or concrete risk. | Review/output evals reject vague "consider" findings. |
| Permission boundary | External writes, destructive work, and publication need explicit intent. | Prompt-injection and hidden-mutation evals. |
| Short closeout | Default closeout is changed files, decisions, validation, residual risks. | Builder/creator output contracts. |
| Minimal clarification | Ask only when missing input changes ownership, destructive behavior, packaging, or external publication. | Ambiguous-request evals. |
| State model for auth/secrets | Sensitive workflows document session continuity and redacted debugging. | Security-sensitive archetype references. |
| Independent proof | Artifact/UI/GUI proof should not rely only on the tool under test. | Generated-artifact and visual proof references. |
| Fresh selectors/snapshots | UI snapshot IDs/selectors must be current before action. | Browser/GUI archetype references. |
| Artifact naming and location | Generated artifacts declare output directory and reproducible names. | Generated-artifact policy reference. |

## Negative Patterns To Block

| Pattern | Regression rule |
|---|---|
| Archive-backed active files | Active plugin or system extension files must not resolve through `fixtures/budget-archive/**`. |
| Forked system bridge skills | `skill-creator` and `skill-installer` stay Codex `.system` skills; Skill Factory adds references/evals, not standalone plugin SKILL.md forks. |
| Governance in every hot path | First-principles, evidence ledgers, and deep validation stay conditional unless the request is release/audit/session-evidence work. |
| Session mining by default | Session collector evidence is loaded only when supplied or explicitly requested. |
| Giant validation matrix | Use fast/standard/deep tiers; do not report optional unavailable gates as blockers. |
| Heavy output ledgers by default | Full ledgers are for audits, releases, multi-skill work, or explicit requests. |
| Project-specific mappings in general skills | Domain mappings live in references loaded only by matching evidence. |
| Media policy in ordinary skill hardening | Generated-artifact rules stay in references and trigger only for artifact-producing work. |
| Helper references without live helpers | Referenced scripts must exist in the live active path, not only in archives. |
| Blocked-first posture | Infer conservatively and record assumptions unless the missing input changes ownership, destructive behavior, publication, or external writes. |

## Enforcement

- Run `check_plugin_active_archive_links.py --plugin skill-factory` after
  changing plugin layout.
- Run `check_skill_factory_system_overlays.py` after changing Skill Factory
  bridges, references, evals, or manifests.
- Add eval cases when a positive pattern becomes a new contract or a negative
  pattern caused a real regression.
