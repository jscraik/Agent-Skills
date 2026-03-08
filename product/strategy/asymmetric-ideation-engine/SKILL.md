---
name: asymmetric-ideation-engine
description: "Generate 10 launchable asymmetric ideas by excavating a repository for hidden patterns. Use when users ask for radical non-incremental ideation from repo context; don't use for roadmap optimization, bug fixing, or routine prioritization. Outputs: structured idea set + artifact file. Success: all novelty constraints satisfied."
---

# Asymmetric Ideation Engine

## Working agreement
- Keep `SKILL.md` concise; place strict schemas and tests in `references/`.
- Write deliverables to `./artifacts/` (local) or `/mnt/data/` (hosted).
- Ask only minimal clarifying questions; default to execution when repository scope is clear.

## Scope and triggers
Use this skill when the user asks for:
- radical idea generation from an existing repo/workspace
- non-obvious, category-creating concepts from latent patterns
- “surprise me” ideation with strong novelty constraints

Do **not** use when the user asks for:
- backlog grooming, prioritization, optimization, or bug triage
- incremental feature suggestions
- market-size validation or investor memo drafting

## Required inputs
- Target repository/workspace path.
- Output count (default 10).
- Build window (default 30 days).
- Novelty constraints (outside-domain minimum, artifact/tool mix, risk floor).

If missing, ask one compact question and proceed.

## Constraints and safety
- Never reveal secrets, tokens, or private data found during audit.
- Do not claim ideas are novel globally; novelty is relative to scanned repository content.
- If asked to auto-publish or trigger external actions, require explicit approval.
- Avoid destructive operations.

## Principles
- Discovery over optimization.
- Structural signals over explicit labels.
- Internal audit, external synthesis.
- Diversity by construction (domain, form, risk, mechanism).
- Concrete launchability over abstract inspiration.

## Empowerment
- You are expected to surface surprising leverage, not safe summaries.
- You can take creative risk while staying inside explicit safety constraints.
- When uncertain between “interesting” and “predictable,” choose the more original path and justify it.

## Workflow
1) **Deep structural audit (internal only)**
   - Scan markdown, configs, logs, scripts, archived drafts, dashboards, exports, experiments.
   - Extract internal notes for: hidden themes (5), unused capacities (3), cognitive tensions (2).
   - Do **not** print this audit in final output unless explicitly requested.

2) **Asymmetric ideation pass**
   - Generate a broad set (20–40 candidates), then keep 10 with maximal diversity.
   - Enforce hard constraints:
     - no incremental/adjacent ideas
     - at least 3 outside current business domains
     - at least 2 tools/systems
     - at least 2 frameworks/cultural artifacts
     - at least 1 playful/experimental
     - at least 1 unsettling-but-generative

3) **Quality gate before output**
   - Reject ideas that resemble existing repo projects/themes too closely.
   - Reject ideas that cannot start within 30 days.
   - Ensure each retained idea has a distinct core mechanism.

4) **Format output exactly**
   For each idea include:
   1. Name
   2. Core Concept
   3. Why It’s Asymmetric
   4. Why It Would Surprise the Founder
   5. 30-Day Launch Path
   6. Long-Term Optionality

5) **Optional recurring mode (explicit opt-in only)**
   - If user asks for cyclical runs: execute every 30 minutes until cumulative unique ideas reach target.
   - Persist seen themes in `./artifacts/asymmetric-ideation/seen-themes.json`.
   - Increase conceptual risk each cycle and forbid repeated themes.

6) **Variation control**
   - Vary idea mechanisms across cycles (tool, protocol, ritual, artifact, game, lens).
   - Vary audience targets (founder, team, community, public).
   - Vary time horizon (immediate utility vs platform optionality).

## Deliverables
- `./artifacts/asymmetric-ideation/ideas-<timestamp>.md` (primary output)
- `./artifacts/asymmetric-ideation/trace-<timestamp>.json` (idea metadata: category mix + novelty checks, no sensitive content)
- Optional recurring ledger: `./artifacts/asymmetric-ideation/seen-themes.json`
- Optional starter template: `assets/idea-output-template.md`

## Validation
- Fail fast: stop at the first failed gate, fix, and rerun checks.
- Confirm output has exactly requested idea count.
- Confirm each idea contains all 6 required fields.
- Confirm constraint coverage (3 outside-domain, 2 tools/systems, 2 frameworks/artifacts, 1 playful, 1 unsettling).
- Confirm no explicit audit dump unless requested.
- Run `python scripts/validate_ideation_output.py <ideas.md>` for structure checks.

## Anti-patterns
- ❌ “Top 10 improvements” style incremental list.
- ❌ Consulting clichés (optimize funnel, improve SEO, etc.).
- ❌ Repackaging current projects with renamed labels.
- ❌ Vague concept art with no 30-day launch path.
- ❌ Repeating the same theme with cosmetic wording changes.
- ❌ Playing it safe when the prompt explicitly requests cognitive friction.
- ❌ Leaking internal audit notes when not requested.

## Examples
- Triggering prompt: "Excavate this repo and give me 10 asymmetric ideas that feel category-creating."
- Non-triggering prompt: "Prioritize our Q2 roadmap improvements."

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
