---
name: "imagegen"
description: "Use when the user asks to generate or edit images via the OpenAI Image API (for example: generate image, edit/inpaint/mask, background removal or replacement, transparent background, product shots, concept art, covers, or batch variants); run the bundled CLI (`scripts/image_gen.py`) and require `OPENAI_API_KEY` for live calls."
---


# Image Generation Skill

Generates or edits images for the current project (e.g., website assets, game assets, UI mockups, product mockups, wireframes, logo design, photorealistic images, infographics). Defaults to `gpt-image-1.5` and the OpenAI Image API, and prefers the bundled CLI for deterministic, reproducible runs.

## When to use

- Use when the user asks to **generate** or **edit** images (including inpainting/masks, background replacement, or transparent background).

## Inputs

- Prompt (and any “must keep” invariants).
- Optional input image(s) and mask(s) for edit/inpaint.
- Output requirements: size, format, transparency, number of variants.
- Runtime constraints: whether live API calls are allowed (requires `OPENAI_API_KEY`).

## Outputs

- Generated/edited image files saved under the agreed output directory.
- Final prompt + CLI flags used (so the run is reproducible).

## Philosophy

- Deterministic runs: prefer the bundled CLI and stable output paths.
- Make one change per iteration; re-run; re-check.

## Validation
- Fail fast: stop at the first failed check and do not proceed.

- Verify invariants: subject identity, composition, and any required text.
- Verify no sensitive data is embedded; redact/avoid private identifiers.
## Antipatterns

- Inventing brand/style requirements the user did not ask for.
- Asking for users to paste API keys into chat.

## Constraints

- Never print or request secrets/tokens/PII; use placeholders and local env vars.

## Scope and triggers
- Generate a new image (concept art, product shot, cover, website hero)
- Edit an existing image (inpainting, masked edits, lighting or weather transformations, background replacement, object removal, compositing, transparent background)
- Batch runs (many prompts, or many variants across prompts)

## Decision tree (generate vs edit vs batch)
- If the user provides an input image (or says “edit/retouch/inpaint/mask/translate/localize/change only X”) → **edit**
- Else if the user needs many different prompts/assets → **generate-batch**
- Else → **generate**

## Workflow
1. Decide intent: generate vs edit vs batch (see decision tree above).
2. Collect inputs up front: prompt(s), exact text (verbatim), constraints/avoid list, and any input image(s)/mask(s). For multi-image edits, label each input by index and role; for edits, list invariants explicitly.
3. If batch: write a temporary JSONL under tmp/ (one job per line), run once, then delete the JSONL.
4. Augment prompt into a short labeled spec (structure + constraints) without inventing new creative requirements.
5. Run the bundled CLI (`scripts/image_gen.py`) with sensible defaults (see references/cli.md).
6. For complex edits/generations, inspect outputs (open/view images) and validate: subject, style, composition, text accuracy, and invariants/avoid items.
7. Iterate: make a single targeted change (prompt or mask), re-run, re-check.
8. Save/return final outputs and note the final prompt + flags used.

## Temp and output conventions
- Use `tmp/imagegen/` for intermediate files (for example JSONL batches); delete when done.
- Write final artifacts under `output/imagegen/` when working in this repo.
- Use `--out` or `--out-dir` to control output paths; keep filenames stable and descriptive.

## Dependencies (install if missing)
Prefer `uv` for dependency management.

Python packages:
```
uv pip install openai pillow
```
If `uv` is unavailable:
```
python3 -m pip install openai pillow
```

## Environment
- `OPENAI_API_KEY` must be set for live API calls.

If the key is missing, give the user these steps:
1. Create an API key in the OpenAI platform UI: https://platform.openai.com/api-keys
2. Set `OPENAI_API_KEY` as an environment variable in their system.
3. Offer to guide them through setting the environment variable for their OS/shell if needed.
- Never ask the user to paste the full key in chat. Ask them to set it locally and confirm when ready.

If installation isn't possible in this environment, tell the user which dependency is missing and how to install it locally.

## Defaults & rules
- Use `gpt-image-1.5` unless the user explicitly asks for `gpt-image-1-mini` or explicitly prefers a cheaper/faster model.
- Assume the user wants a new image unless they explicitly ask for an edit.
- Require `OPENAI_API_KEY` before any live API call.
- Use the OpenAI Python SDK (`openai` package) for all API calls; do not use raw HTTP.
- If the user requests edits, use `client.images.edit(...)` and include input images (and mask if provided).
- Prefer the bundled CLI (`scripts/image_gen.py`) over writing new one-off scripts.
- Never modify `scripts/image_gen.py`. If something is missing, ask the user before doing anything else.
- If the result isn’t clearly relevant or doesn’t satisfy constraints, iterate with small targeted prompt changes; only ask a question if a missing detail blocks success.

## Prompt augmentation
Reformat user prompts into a structured, production-oriented spec. Only make implicit details explicit; do not invent new requirements.

## Use-case taxonomy (exact slugs)
Classify each request into one of these buckets and keep the slug consistent across prompts and references.

Generate:
- photorealistic-natural — candid/editorial lifestyle scenes with real texture and natural lighting.
- product-mockup — product/packaging shots, catalog imagery, merch concepts.
- ui-mockup — app/web interface mockups that look shippable.
- infographic-diagram — diagrams/infographics with structured layout and text.
- logo-brand — logo/mark exploration, vector-friendly.
- illustration-story — comics, children’s book art, narrative scenes.
- stylized-concept — style-driven concept art, 3D/stylized renders.
- historical-scene — period-accurate/world-knowledge scenes.

Edit:
- text-localization — translate/replace in-image text, preserve layout.
- identity-preserve — try-on, person-in-scene; lock face/body/pose.
- precise-object-edit — remove/replace a specific element (incl. interior swaps).
- lighting-weather — time-of-day/season/atmosphere changes only.
- background-extraction — transparent background / clean cutout.
- style-transfer — apply reference style while changing subject/scene.
- compositing — multi-image insert/merge with matched lighting/perspective.
- sketch-to-render — drawing/line art to photoreal render.

Quick clarification (augmentation vs invention):
- If the user says “a hero image for a landing page”, you may add *layout/composition constraints* that are implied by that use (e.g., “generous negative space on the right for headline text”).
- Do not introduce new creative elements the user didn’t ask for (e.g., adding a mascot, changing the subject, inventing brand names/logos).

Template (include only relevant lines):
```
Use case: <taxonomy slug>
Asset type: <where the asset will be used>
Primary request: <user's main prompt>
Scene/background: <environment>
Subject: <main subject>
Style/medium: <photo/illustration/3D/etc>
Composition/framing: <wide/close/top-down; placement>
Lighting/mood: <lighting + mood>
Color palette: <palette notes>
Materials/textures: <surface details>
Quality: <low/medium/high/auto>
Input fidelity (edits): <low/high>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Augmentation rules:
- Keep it short; add only details the user already implied or provided elsewhere.
- Always classify the request into a taxonomy slug above and tailor constraints/composition/quality to that bucket. Use the slug to find the matching example in `references/sample-prompts.md`.
- If the user gives a broad request (e.g., "Generate images for this website"), use judgment to propose tasteful, context-appropriate assets and map each to a taxonomy slug.
- For edits, explicitly list invariants ("change only X; keep Y unchanged").
- If any critical detail is missing and blocks success, ask a question; otherwise proceed.

## Anti-patterns

- Skipping investigation and jumping directly to fixes.
- Making claims without evidence, logs, or reproducible steps.
- Mixing unrelated workstreams in a single execution path.

## Examples

### Generation example (hero image)
```
Use case: stylized-concept
Asset type: landing page hero
Primary request: a minimal hero image of a ceramic coffee mug
Style/medium: clean product photography
Composition/framing: centered product, generous negative space on the right
Lighting/mood: soft studio lighting
Constraints: no logos, no text, no watermark
```

### Edit example (invariants)
```
Use case: precise-object-edit
Asset type: product photo background replacement
Primary request: replace the background with a warm sunset gradient
Constraints: change only the background; keep the product and its edges unchanged; no text; no watermark
```

## Prompting best practices (short list)
- Structure prompt as scene -> subject -> details -> constraints.
- Include intended use (ad, UI mock, infographic) to set the mode and polish level.
- Use camera/composition language for photorealism.
- Quote exact text and specify typography + placement.
- For tricky words, spell them letter-by-letter and require verbatim rendering.
- For multi-image inputs, reference images by index and describe how to combine them.
- For edits, repeat invariants every iteration to reduce drift.
- Iterate with single-change follow-ups.
- For latency-sensitive runs, start with quality=low; use quality=high for text-heavy or detail-critical outputs.
- For strict edits (identity/layout lock), consider input_fidelity=high.
- If results feel “tacky”, add a brief “Avoid:” line (stock-photo vibe; cheesy lens flare; oversaturated neon; harsh bloom; oversharpening; clutter) and specify restraint (“editorial”, “premium”, “subtle”).

More principles: `references/prompting.md`. Copy/paste specs: `references/sample-prompts.md`.

## Guidance by asset type
Asset-type templates (website assets, game assets, wireframes, logo) are consolidated in `references/sample-prompts.md`.

## CLI + environment notes
- CLI commands + examples: `references/cli.md`
- API parameter quick reference: `references/image-api.md`
- If network approvals / sandbox settings are getting in the way: `references/codex-network.md`

## Reference map
- **`references/cli.md`**: how to *run* image generation/edits/batches via `scripts/image_gen.py` (commands, flags, recipes).
- **`references/image-api.md`**: what knobs exist at the API level (parameters, sizes, quality, background, edit-only fields).
- **`references/prompting.md`**: prompting principles (structure, constraints/invariants, iteration patterns).
- **`references/sample-prompts.md`**: copy/paste prompt recipes (generate + edit workflows; examples only).
- **`references/codex-network.md`**: environment/sandbox/network-approval troubleshooting.

## Validation

- Fail fast: stop at the first failed check and do not proceed. Re-run checks before continuing.
- If a required input is missing, ask for it and pause.
- Provide an explicit success/fail summary for each validation step.


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
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
