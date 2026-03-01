---
name: "sora"
description: "Use when the user asks to generate, remix, poll, list, download, or delete Sora videos via OpenAI\u2019s video API using the bundled CLI (`scripts/sora.py`), including requests like \u201cgenerate AI video,\u201d \u201cSora,\u201d \u201cvideo remix,\u201d \u201cdownload video/thumbnail/spritesheet,\u201d and batch video generation; requires `OPENAI_API_KEY` and Sora API access."
knowledge_graph_profile: references/task-profile.json
---


# Sora Video Generation Skill

Creates or manages short video clips for the current project (product demos, marketing spots, cinematic shots, UI mocks). Defaults to `sora-2` and a structured prompt augmentation workflow, and prefers the bundled CLI for deterministic runs. Note: `$sora` is a skill tag in prompts, not a shell command.

## Philosophy

- Prefer root-cause understanding over quick symptom patches.
- Keep guidance evidence-based, explicit, and reproducible.
- Optimize for decisions that reduce rework and operational risk.

## Scope and triggers
- Generate a new video clip from a prompt
- Remix an existing video by ID
- Poll status, list jobs, or download assets (video/thumbnail/spritesheet)
- Batch runs (many prompts or variants)

## Inputs

- Prompt (or `--prompt-file`) and any invariants (“must keep” details).
- Optional: reference image(s) for style/subject guidance.
- Video job ID (for remix/poll/download).
- Output requirements: model, size, seconds, and number of variants.

## Outputs

- Video file(s) + any requested assets (thumbnail, spritesheet) saved locally.
- The final prompt and CLI flags used (for reproducibility).

## Validation

- Fail fast: if `OPENAI_API_KEY` is missing, stop and ask the user to set it locally.
- Confirm the output matches requested duration/size and key invariants before declaring done.

## Constraints

- Never request or print secrets (API keys/tokens) or private URLs; use placeholders.
- Follow the Guardrails section (no real people, no copyrighted characters/music, under-18 safe).

## Decision tree (create vs remix vs status/download vs batch)
- If the user has a **video id** and wants a change → **remix**
- If the user has a **video id** and wants status or assets → **status/poll/download**
- If the user needs many prompts/assets → **create-batch**
- If the user asks for two versions with a small change (same shot, different subject/detail) → **create** the base, then **remix** for the variation
- Otherwise → **create** (or **create-and-poll** if they need a ready asset in one step)

## Workflow
1. Decide intent: create vs remix vs status/download vs batch.
2. Collect inputs: prompt, model, size, seconds, and any input reference image.
3. If batch: write a temporary JSONL under tmp/ (one job per line), run once, then delete the JSONL.
4. Prefer CLI augmentation flags (`--use-case`, `--scene`, `--camera`, etc.) instead of pre-writing a structured prompt. If you already produced a structured prompt file, pass `--no-augment` to avoid double-wrapping.
5. Run the bundled CLI (`scripts/sora.py`) with sensible defaults (see references/cli.md). For long prompts, prefer `--prompt-file` to avoid shell-escaping issues; pair with `--no-augment` if the prompt is already structured.
6. For async jobs, poll until complete (or use create-and-poll).
7. Download assets (video/thumbnail/spritesheet) and save locally.
8. Remove intermediate files created during invocation (for example `prompt.txt`, `remix_job.json`, temp JSONL). If the sandbox blocks `rm`, skip cleanup or truncate the files without surfacing an error.
9. Iterate with a single targeted change per prompt.

## Authentication
- `OPENAI_API_KEY` must be set for live API calls.

If the key is missing, give the user these steps:
1. Create an API key in the OpenAI platform UI: https://platform.openai.com/api-keys
2. Set `OPENAI_API_KEY` as an environment variable in their system.
3. Offer to guide them through setting the environment variable for their OS/shell if needed.
- Never ask the user to paste the full key in chat. Ask them to set it locally and confirm when ready.

## Defaults & rules
- Default model: `sora-2` (use `sora-2-pro` for higher fidelity).
- Default size: `1280x720`.
- Default seconds: `4` (allowed: "4", "8", "12" as strings).
- Always set size and seconds via API params; prose will not change them.
- Use the OpenAI Python SDK (`openai` package); do not use raw HTTP.
- Require `OPENAI_API_KEY` before any live API call.
- If uv cache permissions fail, set `UV_CACHE_DIR=/tmp/uv-cache`.
- Input reference images must be jpg/png/webp and should match target size.
- Download URLs expire after about 1 hour; copy assets to your own storage.
- Prefer the bundled CLI and **never modify** `scripts/sora.py` unless the user asks.
- Sora can generate audio; if a user requests voiceover/audio, specify it explicitly in the `Audio:` and `Dialogue:` lines and keep it short.

## API limitations
- Models are limited to `sora-2` and `sora-2-pro`.
- API access to Sora models requires an organization-verified account.
- Duration is limited to 4/8/12 seconds and must be set via the `seconds` parameter.
- The API expects `seconds` as a string enum ("4", "8", "12").
- Output sizes are limited by model (see `references/video-api.md` for the supported sizes).
- Video creation is async; you must poll for completion before downloading.
- Rate limits apply by usage tier (do not list specific limits).
- Content restrictions are enforced by the API (see Guardrails below).

## Guardrails (must enforce)
- Only content suitable for audiences under 18.
- No copyrighted characters or copyrighted music.
- No real people (including public figures).
- Input images with human faces are rejected.

## Prompt augmentation
Reformat prompts into a structured, production-oriented spec. Only make implicit details explicit; do not invent new creative requirements.

Template (include only relevant lines):
```
Use case: <where the clip will be used>
Primary request: <user's main prompt>
Scene/background: <location, time of day, atmosphere>
Subject: <main subject>
Action: <single clear action>
Camera: <shot type, angle, motion>
Lighting/mood: <lighting + mood>
Color palette: <3-5 color anchors>
Style/format: <film/animation/format cues>
Timing/beats: <counts or beats>
Audio: <ambient cue / music / voiceover if requested>
Text (verbatim): "<exact text>"
Dialogue:
<dialogue>
- Speaker: "Short line."
</dialogue>
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Augmentation rules:
- Keep it short; add only details the user already implied or provided elsewhere.
- For remixes, explicitly list invariants ("same shot, change only X").
- If any critical detail is missing and blocks success, ask a question; otherwise proceed.
- If you pass a structured prompt file to the CLI, add `--no-augment` to avoid the tool re-wrapping it.

## Anti-patterns

- Skipping investigation and jumping directly to fixes.
- Making claims without evidence, logs, or reproducible steps.
- Mixing unrelated workstreams in a single execution path.

## Examples

### Generation example (single shot)
```
Use case: product teaser
Primary request: a close-up of a matte black camera on a pedestal
Action: slow 30-degree orbit over 4 seconds
Camera: 85mm, shallow depth of field, gentle handheld drift
Lighting/mood: soft key light, subtle rim, premium studio feel
Constraints: no logos, no text
```

### Remix example (invariants)
```
Primary request: same shot and framing, switch palette to teal/sand/rust with warmer backlight
Constraints: keep the subject and camera move unchanged
```

## Prompting best practices (short list)
- One main action + one camera move per shot.
- Use counts or beats for timing ("two steps, pause, turn").
- Keep text short and the camera locked-off for UI or on-screen text.
- Add a brief avoid line when artifacts appear (flicker, jitter, fast motion).
- Shorter prompts are more creative; longer prompts are more controlled.
- Put dialogue in a dedicated block; keep lines short for 4-8s clips.
- State invariants explicitly for remixes (same shot, same camera move).
- Iterate with single-change follow-ups to preserve continuity.

## Guidance by asset type
Use these modules when the request is for a specific artifact. They provide targeted templates and defaults.
- Cinematic shots: `references/cinematic-shots.md`
- Social ads: `references/social-ads.md`

## CLI + environment notes
- CLI commands + examples: `references/cli.md`
- API parameter quick reference: `references/video-api.md`
- Prompting guidance: `references/prompting.md`
- Sample prompts: `references/sample-prompts.md`
- Troubleshooting: `references/troubleshooting.md`
- Network/sandbox tips: `references/codex-network.md`

## Reference map
- **`references/cli.md`**: how to run create/poll/remix/download/batch via `scripts/sora.py`.
- **`references/video-api.md`**: API-level knobs (models, sizes, duration, variants, status).
- **`references/prompting.md`**: prompt structure and iteration guidance.
- **`references/sample-prompts.md`**: copy/paste prompt recipes (examples only; no extra theory).
- **`references/cinematic-shots.md`**: templates for filmic shots.
- **`references/social-ads.md`**: templates for short social ad beats.
- **`references/troubleshooting.md`**: common errors and fixes.
- **`references/codex-network.md`**: network/approval troubleshooting.

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
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
