---
schema_version: 1
purpose: Per-project agent knowledge base — repo-specific gotchas and hard-won fixes.
scope: This repo only.
update_policy: |
  Append after any bug, tool failure, or extra-effort fix specific to this repo.
  Universal gotchas go in ~/.codex/instructions/Learnings.md instead.
  Do NOT delete entries. Append only.
  Format: **YYYY-MM-DD [Agent]:** <problem> → <fix>
---

# Learnings

Repo-specific agent knowledge base. Append-only.

> **Scope:** This repo only. Universal gotchas → `~/.codex/instructions/Learnings.md`.
> **Format:** `**YYYY-MM-DD [Agent]:** <problem> → <fix>`

- **2026-06-24 [Codex]:** Skills SDK handoff bundles that use placeholder commands like `<teach-ab-run-receipt.json>` turn missing receipts into pipeline stoppers. → Treat unresolved placeholders as validation blockers, point OSS lanes at executable `sdk eval run ... --codex-profile <lane>` commands, use `--timeout-seconds` to force typed `timeout_no_output` receipts, and keep live Tessl blocked while preserving `blocked_runtime` evidence for diagnostic continuation.

- **2026-03-09 [Codex]:** `Infrastructure/scripts/docs_lint.py` does not accept a `--files` selector; passing it exits with argparse error. Use supported global flags (`--mode`, `--config`, optional report flags) and lint the configured scope.

- **2026-03-12 [Codex]:** `run_skill_evals.py --smoke` uses a contract-derived discovery response rather than domain-specific skill output; avoid false regex failures by defining dedicated `smoke_mode` cases and filtering smoke runs to those cases.

- **2026-03-11 [Codex]:** `run_skill_evals.py --runner codex` can fail with `mise ERROR No version is set for shim: codex` even when the skill reports look like content failures. Fix the shim first with `mise use -g npm:@openai/codex@0.114.0`; for `verify_recursive_skill_graph_artifacts --strict --run-state-check`, preserve historical run directories and record explicit waivers instead of backfilling synthetic mandatory artifacts.

- **2026-03-11 [Codex]:** Validator examples inside `SKILL.md` can drift from the actual script layout. The canonical validator entrypoints live under `Skills/skill-builder/Infrastructure/scripts/` rather than repo-root `Infrastructure/scripts/`, so verify the executable path before treating a validation example as authoritative.

- **2026-03-11 [Codex]:** Timeout tuning for Codex evals can make isolated case reruns pass while the same cases still time out inside a full-suite run. Treat timeout increases as provisional until the full suite reproduces the improvement, not just the filtered case.

- **2026-03-11 [Codex]:** In eval artifacts, `exit_code=124` plus `selected_skill=null`, zero trace events, empty `final.txt`, and empty `stdout.txt` means the case likely died before first response generation; treat it as startup/suite-budget contention, not as evidence that the skill wording or acceptance regex is wrong.

- **2026-03-11 [Codex]:** `run_skill_evals.py` can falsely mark `should_trigger: false` as selected when the model mentions a skill name while explicitly refusing it (for example, project-improver is overkill). Treat explicit final-response refusals as stronger evidence than reasoning or event mentions before scoring trigger selection.

- **2026-03-11 [Codex]:** When MCP filesystem read/write calls drop with `Transport closed` during small skill-doc edits, fall back to direct shell reads/writes for the exact target files, then run the canonical skill validators to confirm no drift.

- **2026-03-11 [Codex]:** In Agentation evals, `watch-mode-contract`, `critique-mode`, and `self-driving-compat` timed out at the default 60-second budget during a supposed fast-shard rerun, so they belong in the heavy-diagnostic lane with Codex-heavy timeouts rather than the quick regression lane.

- **2026-03-11 [Codex]:** In Agentation evals, `annotation-lifecycle` and `mobile-support-limit` also timed out at the default 60-second budget during the trimmed fast-shard run, so they belong in the heavy-diagnostic lane with Codex-heavy timeouts rather than the quick regression lane.

- **2026-03-11 [Codex]:** In isolated Agentation eval reruns, a Codex usage-limit failure can surface as exit code `1`, empty final output, and downstream regex misses. Check stderr for the explicit usage-limit message before treating the case as a skill regression.

- **2026-03-12 [Codex]:** In isolated Agentation heavy reruns, restored quota does not guarantee usable results: `mobile-support-limit` timed out with empty `final.txt` and `stdout.txt` on both Codex (180s) and Gemini (300s), and `watch-mode-contract` showed the same empty-output Codex timeout. Treat that signature as runner stall, not as evidence that the skill wording missed the regex.

- **2026-03-12 [Codex]:** In the same Agentation lane, runner health can differ by case and channel within minutes: `mobile-support-limit` moved from repeated LF timeouts to Gemini PASS with non-empty output, while `watch-mode-contract` remained LF on both Codex and Gemini. Gate queue progression per-case with the LF classifier instead of assuming whole-suite recovery.

- **2026-03-12 [Codex]:** `Skills/skill-builder/SKILL.md` can point at nonexistent `Infrastructure/scripts/quick_validate.py`-style validator paths. Use `Skills/skill-builder/Infrastructure/scripts/{quick_validate,skill_gate,analyze_skill,openclaw_skill_guard,run_skill_evals}.py` instead of repo-root `Infrastructure/scripts/` paths.

- **2026-03-12 [Codex]:** In Ars Contexta queue updates, jq update expressions that use shell-expanded timestamps can silently fail or compile-break when variable escaping is wrong; use direct field assignments (status/completed) with explicit quoted timestamp strings, then immediately verify with jq selection.

- **2026-03-12 [Codex]:** In Ars Contexta skill-source lookups, `fd` with quoted wildcards like `fd "*pipeline*"` is parsed as regex and fails (`repetition operator missing expression`); use `fd --glob "*pipeline*"` for filename matching.

- **2026-03-15 [Gemini]:** Antigravity `/` slash command shows no skills when `~/.gemini/antigravity/skills` symlink and `~/.gemini/antigravity/skills.txt` are missing, or when `skills-antigravity/` in the repo is empty. → Run `bash Infrastructure/scripts/sync_skills.sh` (or `just sync`) from this repo to rebuild the `skills-antigravity/` projection, create the symlink at `~/.gemini/antigravity/skills`, and write `skills.txt`. Also run `python3 Infrastructure/scripts/sync_mcp.py` if MCP tools are missing. Restart Antigravity or type `/refresh` after syncing.

- **2026-03-16 [Gemini]:** Skill graph had 92 isolated nodes and 0 density. → Created 7 topic-map MOC files under `docs/skill-graphs/topic-maps/` (frontend-ui, backend-platform, agent-ops, product-strategy, security-ops, content-publishing, mobile-native, plus `index.md`) and added `## See Also` tables to 19 SKILL.md files with `[[wiki-link]]` cross-refs. After running `bash feedback-loop.sh`, graph health moved from HIGH drift to LOW/stable_state. Sync with `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` after any batch SKILL.md edit.

- **2026-03-16 [Gemini]:** `docs_lint.py` interprets phrases like "config file" or "role config file" in markdown as `vague-file-reference` warnings — even inside wiki-link list items. → Replace generic phrasing with explicit path syntax like `agents/` dirs and named file extensions (e.g. `openai.yaml`) to silence the rule.

- **2026-03-17 [Gemini]:** Bulk-patching `## See Also` tables into SKILL.md files is safe for skill functionality and CI validation. The `structure-gate` and `skill-diagnostics` checks validate YAML frontmatter and required instruction sections — not trailing markdown metadata. `docs_lint.py` passes with 0 warnings provided wikilinks don't contain vague file references. See Also sections and `**Topic map:**` lines are invisible to agent invocation.

- **2026-03-17 [Gemini]:** Skill graph sink nodes (in-degree=0) make skills invisible to autonomous agent routing — an agent following See Also chains will never discover them. Fix: identify upstream skills that precede the sink in real workflows and add honest backlinks there, not vanity self-references. After fix: 7 sinks → 0.

- **2026-03-17 [Gemini]:** Static hand-authored See Also adjacency (hardcoded in a Python dict) becomes stale as skills are added. → Extract adjacency to `docs/skill-graphs/adjacency.yaml` so new skills update the data file, not the patcher script. `extract-skill-edges.py` can merge YAML seed with auto-extracted SKILL.md refs.

- **2026-03-17 [Gemini]:** `build-adjacency-yaml.py` deduplicates by `str(md.resolve())` but when symlinked skill copies (`skills-antigravity/` vs `Skills/`) resolve to different real paths, both are processed and the second write wins — causing `adjacency.yaml` to capture content from the wrong copy. → Always prefer the canonical location (e.g. `Skills/`) when deduplicating across symlinked skill projections; use `Skills/` as the sort priority or ignore `skills-antigravity/` in the builder.

- **2026-03-17 [Gemini]:** The `feedback-loop.sh` health report reads the Obsidian wikilink graph (topic-map MOC files in `docs/skill-graphs/topic-maps/`) not the SKILL.md See Also graph. The two are fundamentally different formats. The fix is not to change the `notes_dir` but to add a second SKILL.md-native stats block using `skill-edges.json` directly.

- **2026-03-17 [Gemini]:** When validating SKILL.md See Also vs adjacency.yaml drift, a threshold of 0 is too strict if the YAML is rebuilt from a different canonical SKILL.md than what the validator walks. Use `DRIFT_THRESHOLD=5` in CI and run `build-adjacency-yaml.py` + `validate-adjacency.py` in sequence to detect real drift vs. symlink-induced false positives.

- **2026-03-17 [Gemini]:** `Infrastructure/scripts/query-graph.py` provides BFS-based skill routing with colour output, weight display, and `--reverse` in-link traversal. This is the fastest way for agents to answer "what should I chain with skill X" — append the one-liner to the agent-ops topic map and repo README to ensure discoverability.

- **2026-03-17 [Codex]:** `run_skill_evals.py` case failures with empty final output can be environment-caused (usage-limit/auth errors) rather than skill regression → inspect report `codex/stderr.txt` and `stdout.txt` before changing skill logic.

- **2026-03-17 [Codex]:** `run_skill_evals.py` and `docs_lint.py` false negatives are often caused by stale or missing skill sync artifacts; rebuild projections with `bash Infrastructure/scripts/sync_skills.sh` and verify `/skills-antigravity/` plus `skills.txt` before blaming skill logic for missing invocations.

- **2026-03-17 [Codex]:** During skill install review, validating import quality before enforcing a full fold/merge-first deconflict pass against existing operational skills can delay the correct consolidation call. → Fix: run a mandatory capability overlap matrix first (existing skills vs incoming skill), record an explicit `merge|fold|improve-existing|install-new` decision before any install edits, and treat prior duplicate incidents as hard guardrails.

- **2026-03-27 [Codex]:** Local plugin marketplaces named `openai-curated` can collide with Codex's official synced marketplace namespace and surface `Plugin detail unavailable` or plugin read failures in the TUI. -> Use a unique local marketplace name (for example `agent-skills-local`) and keep local plugin manifests to the known runtime top-level shape without extra metadata keys.

- **2026-03-28 [Codex]:** Codex app-server resolves marketplace `source.path` from the repo root, not from the directory containing `marketplace.json`. -> Keep local marketplace entries as repo-root-relative paths like `./Plugins/<plugin-name>` even when the marketplace file itself lives under `Plugins/` or `.agents/Plugins/`.

- **2026-03-30 [Codex]:** `run_skill_evals.py --runner discovery-smoke` can fail every smoke case when a skill is missing discovery contract markers (`## Discovery interview`, one-round-at-a-time guidance, plain-language question guidance, `Why this matters`, no-full-plan-dump wording, and `Infrastructure/references/discovery-interview.md`). -> Add the exact contract phrases in `SKILL.md` and provide `Infrastructure/references/discovery-interview.md` with mini-templates, payload examples, intuitive round-1 wording, and round-6 confirmation guidance before trusting smoke results.

- **2026-03-30 [Codex]:** In `zsh`, `status` is a read-only special variable and using it in shell loops causes `read-only variable: status`. -> Use a different variable name (for example `gate_status`) in validation scripts and result collectors.

- **2026-04-05 [Codex]:** Equivalent CI gates in this repo can drift on Python dependency setup (`repo-validate` vs `authoring-family-gate`) and produce contradictory outcomes on the same commit. -> Keep parity by installing shared deps (for example `pyyaml`) in each equivalent lane or centralizing setup in the workflow.

- **2026-04-05 [Codex]:** `skill-installer` diagnostic logs that echo override payloads can trigger CodeQL `Clear-text logging of sensitive information` alerts. -> Log redacted metadata (for example override count/presence) instead of raw override values.

- **2026-04-07 [Codex]:** `python3 Infrastructure/scripts/sync_mcp.py` can fail on macOS when system Python 3.9 lacks `tomli`, and `shutil.which("python3.12")` can still miss the interpreter in constrained PATH sessions. -> Add a TOML-load fallback that probes absolute interpreter paths (`/usr/local/bin/python3.12`, `/opt/homebrew/bin/python3.12`, etc.) and parses via `tomllib` in that subprocess.

- **2026-04-08 [Codex]:** Repo harness: login-shell automation used by this repo can fail with `Could not open a connection to your authentication agent` when `SSH_AUTH_SOCK` is exported only in `.zshrc`. -> Export the 1Password agent socket from `.zprofile` (and keep `.zshrc` aligned), then verify with `zsh -lc 'ssh-add -l'` and `ssh -T git@github.com` before running repo workflows. GitHub SSH success may still return exit code `1`; for harness checks, match the banner `Hi USERNAME! You've successfully authenticated, but GitHub does not provide shell access.` instead of relying on exit code alone.

- **2026-04-08 [Codex]:** Repo harness safety check: if this repo session starts rejecting commands with `AskForApproval is set to Never`, verify effective runtime policy first with `codex debug prompt-input "policy check"` before running harness workflows. If policy is wrong for the repo task, restart with explicit flags (`codex --profile d -a on-request -s workspace-write` or `codex -a on-request -s danger-full-access`) and re-check policy before continuing.

- **2026-04-12 [Codex]:** Plugin disappearance in `~/.codex-red` came from cache layout mismatch: runtime resolves plugins at `~/.codex-*/Plugins/cache/<marketplace>/<plugin>`, but cache content had been nested under `local/` or `<version|sha>/`, causing `failed to load plugin: plugin is not installed`. -> Fix by flattening cache roots during sync and in overlap-remediation paths.
- **2026-04-12 [Codex]:** Cache-path separation alone was insufficient: Codex profile homes also require projected `Plugins/marketplace.json` plus repaired plugin-cache roots. -> Keep plugin families loaded from plugin scope and repair cache roots before overlap checks in Codex homes.
- **2026-04-12 [Codex]:** Duplicate prevention policy in this repo no longer keeps plugin families in flat projection. -> `Infrastructure/scripts/sync_skills.sh` must gate plugin-owned skills through `is_plugin_visible_router_skill_name`; default policy keeps router list empty and allows only the `.system` bridge quartet in flat projection.
- **2026-04-12 [Codex]:** Overlap auditing must allow both configured router exceptions and `system_bridge_skill_names` (`skill-creator`, `skill-installer`, `plugin-creator`, `plugin-installer`) so runtime checks fail only on real unintended duplication.
- **2026-04-12 [Codex]:** In non-symlinked Codex profile homes (for example `~/.codex-red/plugins` as a real directory), projecting `marketplace.json` without `~/.codex-*/Plugins/<plugin>` source mirrors breaks `./Plugins/<plugin>` resolution and can hide local plugin families. -> During profile sync, create/update per-plugin source symlinks under the profile `Plugins/` directory.
- **2026-04-12 [Codex]:** Cache flattening failed silently when rsync tried to prune stale nested plugin directories without force-delete semantics (`cannot delete non-empty directory: 0.1.0/...`). -> Use `rsync --delete --force` in runtime cache projection and remediation paths so versioned cache ghosts are actually removed.
- **2026-04-12 [Codex]:** `.system` bridge policy must stay explicit: only `skill-creator`, `skill-installer`, `plugin-creator`, and `plugin-installer` should route through `.agents/skills/.system/*`; route them after `.system` link creation to keep plugin picker visibility stable while avoiding broad hidden-lane drift.

- **2026-04-17 [Codex]:** Repository script paths evolved after March/April refactors (`sync_skills.sh`, `verify-work.sh`, and `docs_lint.py` moved into scoped directories), but this file remains append-only. Preserve historical command strings as-run and append new entries for current-equivalent paths instead of rewriting older bullets in place.

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /Users/jamiecraik/dev/agent-skills && sed -n "1,220p" Infrastructure/artifacts/skills/autofix/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2819853580)

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /Users/jamiecraik/dev/agent-skills && sed -n "1,220p" Infrastructure/artifacts/skills/triage/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:249380224)

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /Users/jamiecraik/dev/agent-skills && sed -n "1,220p" Infrastructure/artifacts/skills/fallback-release/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1691652568)

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /Users/jamiecraik/dev/agent-skills && sed -n "1,220p" Infrastructure/artifacts/skills/production-deployment/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:501290506)

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /Users/jamiecraik/dev/agent-skills && cat Infrastructure/artifacts/skills/autofix/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2646869697)

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /tmp/agent-skills-pr133-merge && cat Infrastructure/artifacts/skills/skill-refactor/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3208018670)

- **2026-04-23 [Codex]:** Bash command 'zsh -lc 'cd /tmp/agent-skills-pr133-merge && cat Infrastructure/artifacts/skills/skillify/structure-gate.json'' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:325006765)

- **2026-05-01 [Codex]:** Bash command 'python3' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:3330151315)

- **2026-05-01 [Codex]:** Bash command 'jq' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:79624506)

- **2026-05-01 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:429827414)

- **2026-05-01 [Codex]:** Bash command 'sed' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:2762304617)

- **2026-05-01 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:2708472663)

- **2026-05-02 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:2643958404)

- **2026-05-02 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:3933523635)

- **2026-05-03 [Codex]:** Bash command 'jq' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:966319190)

- **2026-05-03 [Codex]:** Bash command 'jq' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:3855667086)

- **2026-05-03 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:1052531758)

- **2026-05-03 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:1596859018)

- **2026-05-03 [Codex]:** Bash command 'cat' failed with exit code 2, but the auto-capture entry omitted argv/cwd/input path -> treat basename-only entries as incomplete debugging evidence and rerun with full command logging before repeating the command (auto-key:122602518)

- **2026-05-08 [Codex]:** When HE skills are used as a replacement for Jamie's older long-form prompt pipeline, the outputs can look complete while only carrying sampled evidence. -> Preserve the original prompt text as source evidence, load the stage-specific references (`source-prompt-preservation`, output contract, stage context, artifact routing, and agent-native compression where relevant), and record `evidence_depth`, `coverage_scope`, `coverage_gaps`, `original_prompt_coverage`, and `downstream_confidence` before treating downstream refactor or Linear artifacts as authoritative.

- **2026-05-09 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1403384718)

- **2026-05-09 [Codex]:** Bash command 'jq' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:3185924118)

- **2026-05-09 [Codex]:** Bash command 'jq' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:903979408)

- **2026-05-09 [Codex]:** Bash command 'python3' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2881738601)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2026069844)

- **2026-05-10 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1038069408)

- **2026-05-10 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1573202687)

- **2026-05-10 [Codex]:** Bash command 'timeout' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2521960083)

- **2026-05-10 [Codex]:** Bash command 'timeout' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1571589890)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:547996451)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:361770505)

- **2026-05-10 [Codex]:** Bash command 'python3' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1958951487)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4013853280)

- **2026-05-10 [Codex]:** Bash command 'python3' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3512772383)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3985522864)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3301168806)

- **2026-05-10 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3597461996)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:2938047643)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:569348896)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:435248240)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2088681696)

- **2026-05-10 [Codex]:** Bash command 'python3' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4034958634)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4262723668)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1734630051)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1589171893)

- **2026-05-10 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4203147734)

**2026-05-11 [Codex]:** Bash command 'cat' failed with exit code 1 while reading an unavailable local path -> File read failed; verify the target path exists and is readable, check permissions, confirm the working directory is correct, then use an alternative read method or correct the path before retrying. argv/cwd/target-path not captured in runtime log; no artifact at .harness/memory/command-failure-3040072751.log. Recommended diagnostic: run `ls -la` on the suspected target directory to confirm file presence and permissions before retrying. [low-signal-suppressed: provenance cannot be recovered retroactively] (auto-key:3040072751)

**2026-05-12 [Codex]:** Bash command 'cat' failed with exit code 2 -> argv/cwd not captured; no artifact at .harness/memory/command-failure-2293629618.log. Verify target path exists, check cwd, and use Read tool instead of shell cat for file access. [low-signal-suppressed: provenance cannot be recovered retroactively] (auto-key:2293629618)

**2026-06-24 [Codex]:** Skills SDK OSS judge pipeline must stop at oss-local when the internal Codex runner emits a typed blocked_runtime; do not advance to oss-cloud, Tessl dry run, or live Tessl from a local runtime blocker. A Codex final answer can exit 0 while saying it is blocked (sandbox-exec: sandbox_apply: Operation not permitted or failed workspace writes), so Skill Factory eval classification must scan blocker markers before scoring expected-signal assertions. Validation: PYTHONDONTWRITEBYTECODE=1 python3 Plugins/skill-factory/scripts/skill-builder/test_run_skill_evals.py -> pass; ./bin/ask sdk eval run Skills/github/teach --mode smoke --case happy-first-lesson --codex-profile oss-local --json --robot -> blocked with blocker_class=blocked_runtime and no fake Teach behavior failure.

**2026-05-12 [Codex]:** Bash command 'cat' failed with exit code 2 -> argv/cwd not captured; no artifact at .harness/memory/command-failure-3406616513.log. Verify target path exists, check cwd, and use Read tool instead of shell cat for file access. [low-signal-suppressed: provenance cannot be recovered retroactively] (auto-key:3406616513)

**2026-05-13 [Codex]:** Bash command 'cat' failed with exit code 2 -> argv/cwd not captured; no artifact at .harness/memory/command-failure-1318967753.log. Verify target path exists, check cwd, and use Read tool instead of shell cat for file access. [low-signal-suppressed: provenance cannot be recovered retroactively] (auto-key:1318967753)

**2026-05-14 [Codex]:** Bash command 'cat' failed with exit code 2 -> argv/cwd not captured; no artifact at .harness/memory/command-failure-3199628742.log. Verify target path exists, check cwd, and use Read tool instead of shell cat for file access. [low-signal-suppressed: provenance cannot be recovered retroactively] (auto-key:3199628742)

**2026-05-14 [Codex]:** Bash command 'python3' failed with exit code 2 -> argv/cwd not captured; no artifact at .harness/memory/command-failure-2135778639.log. Verify target path exists, check cwd, and use Read tool instead of shell python3 for file access. [low-signal-suppressed: provenance cannot be recovered retroactively] (auto-key:2135778639)

**2026-05-18 [Codex]:** Bash command 'python3' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:3201373903)

**2026-05-18 [Codex]:** Tessl eval steering -> when running skill/plugin evals, use the installed local `tessl` CLI every time, but stage only controlled input files into a temporary directory and run `tessl eval run --json <staged-temp-source>`; never point Tessl at the live repo source tree, never use `npx tessl`, and never use publish/registry upload paths.

**2026-05-19 [Codex]:** Tessl sandbox steering -> the durable eval lane is local Tessl CLI plus temp-staged project input under `/tmp`, not a live-source or registry operation. Do not request Codex sandbox network permission up front for `ask evals run`; doing so misclassifies the local temp-staged Tessl lane as an external export. Run the wrapper normally, then classify the actual Tessl CLI output.

**2026-05-19 [Codex]:** Tessl automatic eval preference -> Jamie explicitly wants `ask evals run` to run the temp-staged Tessl eval lane automatically every time evals run. Preserve the hard boundaries (native local `tessl`, staged temp source, no live source path, no `npx`, no publish or registry upload) and do not add manual approval or network-permission preflights unless the Tessl CLI itself returns a concrete blocker.

**2026-05-19 [Codex]:** PR green sweep repeated `gh` failures as if GitHub were down, but `gh api rate_limit` and `curl -I https://api.github.com` passed when the command was run with explicit Codex sandbox network permission; `gh run view --log-failed` also proved run-log caches default to `~/.cache/gh` unless `XDG_CACHE_HOME` is set. -> For all PR/CircleCI/Snyk live-state commands in this repo, use explicit network permission first and set `XDG_CACHE_HOME`, `XDG_STATE_HOME`, `MISE_CACHE_DIR`, and `UV_CACHE_DIR` as applicable when `gh`, `mise`, or `uv` may run; after two equivalent failures, stop and refine the environment contract before retrying.

**2026-05-19 [Codex]:** High-signal Jamie steering about agent behavior must stop the active delivery lane before more feature work. -> Use `Docs/agents/19-high-signal-steering-feedback.md`, record uptake in `.harness/quality/steering-uptake.md`, and run `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json` plus `python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q` before resuming.

**2026-05-23 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1674806130)

**2026-05-23 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3928164400)

**2026-05-24 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4290066598)

**2026-05-24 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2247959536)

**2026-05-24 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:495042441)

**2026-05-24 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:607480773)

**2026-05-24 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3127905167)

**2026-05-24 [Codex]:** Bash command 'cat' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:2263204724)

**2026-05-25 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4246922559)

**2026-05-26 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1625694350)

**2026-05-26 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:199742871)

**2026-05-27 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1225174823)

**2026-05-27 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:159795417)

**2026-05-28 [Codex]:** Bash command 'cat' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:2462131021)

**2026-05-28 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1358686701)

**2026-05-28 [Codex]:** Bash command 'jq' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:1679367281)

**2026-06-07 [Codex]:** Local Codex plugin GUI failures can persist after the plugin package and repo cache look healthy when active config, marketplace metadata, profile mirrors, and Desktop loader state are not validated as separate proof lanes -> for plugin GUI closeout, validate config drift, cache content readiness, Codex marketplace source paths, home-profile runtime mirrors, and loader-visible plugin IDs in one window before claiming the plugin is usable.

**2026-06-07 [Codex]:** Stale local plugin enablement can reappear in projected Codex config after manual deletion because Desktop/config preference writes may rewrite older in-memory state -> treat deletion as insufficient; use \`./bin/ask plugins prune-stale-config --json --robot\` so removal is driven by \`data.desktop_readiness_state.stale_enabled_plugin_ids\` and watched across the stability window, then keep Desktop-loadability blocked until the active config has no stale local plugin IDs.

**2026-06-07 [Codex]:** Codex Desktop plugin loader resolves local marketplace `source.path` against the supported marketplace root, not blindly against the JSON file parent or profile home -> for profile mirrors at `~/.codex/.agents/plugins/marketplace.json`, write `./.agents/plugins/<plugin-name>` when the copied plugin directory lives under `~/.codex/.agents/plugins/<plugin-name>`; preserve manifest-declared skills in loader caches and put duplicate suppression in picker/projection surfaces.

**2026-06-07 [Codex]:** The canonical personal marketplace file is `~/.agents/plugins/marketplace.json` -> all local plugin `source.path` entries must be root-relative to that marketplace (begin with `./` and resolve inside `~/.agents/plugins/`), not absolute or profile-home-relative paths. The legacy path `./.codex/plugins/<plugin-name>` is an explicit compatibility mirror for Desktop loader versions that may require it, separately labeled from the canonical marketplace root. Code that writes or validates `marketplace.json` must ensure `source.path` stays within the marketplace root directory (validation note: symlink targets may reside outside, but the declared path itself must be marketplace-relative).

**2026-06-07 [Codex]:** Compatibility plugin mirrors are aliases, not payload owners -> local plugin sync must materialize exactly one profile payload at `~/.codex/plugins/<plugin-name>`, make loader-visible compatibility paths such as `~/.codex/.agents/plugins/<plugin-name>` symlink to that payload, skip case-only samefile roots such as `Plugins` vs `plugins`, and make Desktop readiness fail when a compatibility path is an independent copied directory or resolves to a different realpath.

**2026-06-07 [Codex]:** Symlinking the official personal marketplace into the project is safe only when it targets a dedicated personal projection, not the repo plugin source tree -> on case-insensitive filesystems, `plugins` and `Plugins` can be the same directory, so `~/.agents/plugins -> <repo>/plugins` can overwrite `Plugins/marketplace.json` with personal `./.codex/plugins/<plugin-name>` paths; use `<repo>/.agents/personal-plugins` as the symlink target and keep repo marketplaces on `./Plugins/<plugin-name>`.

**2026-06-13 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3646583035)

**2026-06-13 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:3432406106)

**2026-06-16 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:1675407108)

**2026-06-16 [Codex]:** Bash command 'zsh' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:613334459)

**2026-06-21 [Codex]:** Bash command 'zsh' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:318241816)

**2026-06-24 [Codex]:** Bash command 'jq' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:3696954620)

**2026-06-24 [Codex]:** Bash command 'jq' failed with exit code 1 -> summarize the failure and change approach before rerunning the same command (auto-key:2893193666)

**2026-06-24 [Codex]:** Bash command 'jq' failed with exit code 2 -> summarize the failure and change approach before rerunning the same command (auto-key:4179815513)

**2026-06-24 [Codex]:** Tessl dry-run staging can pass while copying ignored platform metadata into the evidence payload -> filter `.DS_Store`, `.AppleDouble`, and `__MACOSX` at the shared Tessl staging copy boundary, prove the staged file list and staged directory are clean, and write handoff readiness preview output to a separate receipt instead of overwriting the lane manifest.

**2026-06-24 [Codex]:** Tessl local development proof is a distinct bridge from Tessl Distribution to Local Runtime Truth, not a substitute for oss-local, oss-cloud, live Tessl scoring, or persistent user runtime activation -> add `ask sdk eval tessl-local-proof` so the SDK stages a controlled package, runs native `tessl plugin lint`, `tessl plugin pack --output <file>.tgz`, temp `tessl install file:` in `/tmp/ask-tessl-local-install`, and optional explicit `tessl review run`; make handoff readiness require the executed local-proof receipt before live Tessl dry-run/scoring claims.

**2026-06-24 [Codex]:** Plugin creation is part of the Skills SDK professional lifecycle, not a separate memory burden for the operator -> expose `ask sdk plugin create|review|install|save-registry` for both `--kind skill` and `--kind plugin`, delegate to existing bounded skills/plugins commands, save only to local skill registry or local plugin marketplace unless a future remote-publish authority lane exists, and keep `remote_publish_performed=false` in registry-save receipts.
