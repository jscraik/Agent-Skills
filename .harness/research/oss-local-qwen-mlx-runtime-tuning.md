# OSS-Local Qwen MLX Runtime Tuning Research

Date checked: 2026-07-02

## Scope

This research supports the bounded `oss-local` smoke lane for `qwen3.5:9b-mlx`. It does not authorize `oss-cloud`, Tessl dry-run, Tessl live, publish, or release movement.

Current blocker from local evidence:

- `codex exec --profile oss-local` selected `qwen3.5:9b-mlx`.
- The smoke output reported missing model metadata/fallback metadata.
- The smoke used 8,279 tokens, above the 5,000-token guard.
- The runner did not write its normal receipt file after the abnormal tool return.

## Sources Checked

### Ollama model page

URL: https://ollama.com/library/qwen3.5

Finding: Ollama lists `qwen3.5` variants including `qwen3.5:9b-mlx`; the family page shows 256K context for the 9B MLX variant and lists Codex as an Ollama application surface.

Confidence: high. This is the official Ollama model page.

Relevance: Confirms that `qwen3.5:9b-mlx` is an Ollama-supported model tag, not a Hugging Face-only model name.

Proposed config/smoke change: Keep the model id as `qwen3.5:9b-mlx`; do not silently substitute `qwen3.5:9b`, `qwen3.5:latest`, or another provider.

Validator/guardrail: deterministic enough. The smoke receipt must record the exact observed model id.

### Ollama exact model page

URL: https://ollama.com/library/qwen3.5:9b-mlx

Finding: The exact model page reports model id `203e30078279`, size `8.9GB`, and a 256K context window for `qwen3.5:9b-mlx`.

Confidence: high. This is the official Ollama exact model page.

Relevance: Confirms the SDK profile metadata currently recorded in `eval_profiles.py`: model id, size, architecture family, and context assumptions.

Proposed config/smoke change: Keep SDK receipt metadata aligned to `203e30078279` and 256K model capability, but do not use the full context for marker smoke.

Validator/guardrail: deterministic enough. Profile preview tests can assert the exact model id and context metadata.

### Ollama exact model params blob

URL: https://ollama.com/library/qwen3.5:9b-mlx/blobs/86eff881e8d2

Finding: Ollama's model params blob lists defaults: `temperature=1`, `top_p=0.95`, `top_k=20`, `presence_penalty=1.5`, `repeat_penalty=1`, `min_p=0`.

Confidence: high. This is an official Ollama model blob.

Relevance: The SDK local-eval profile intentionally overrides model sampling to `temperature=0.1`, `top_p=0.9`, and `num_predict=1024` for eval stability, but the Codex profile file does not expose those Ollama-native options directly.

Proposed config/smoke change: Do not add unsupported TOML keys to `oss-local.config.toml`. Keep sampling/output caps in SDK receipt metadata and enforce smoke-budget via the smoke-output checker.

Validator/guardrail: partially deterministic. The configs validator can reject unsupported profile keys; the smoke checker can enforce token budget after capture.

### Ollama exact model config blob

URL: https://ollama.com/library/qwen3.5:9b-mlx/blobs/d0883072e018

Finding: The config blob identifies architecture `Qwen3_5ForConditionalGeneration`, model type `qwen3_5`, and `max_position_embeddings=262144`.

Confidence: high. This is an official Ollama model blob.

Relevance: Confirms the local `ollama show` architecture/context output and supports keeping the model in the qwen3.5 MLX lane.

Proposed config/smoke change: For marker smoke, avoid loading repo AGENTS/project context because model capability is not the issue; repo context dominates token usage. Use an empty temp workdir for the model-viability smoke and keep release evals separate.

Validator/guardrail: deterministic enough. The smoke runner can close stdin, pass `--json`, and allow the caller to choose an empty `--work-dir`.

### Local Ollama runtime check

Command: `ollama show qwen3.5:9b-mlx | sed -n '1,160p'`

Finding: Local runtime reports architecture `qwen3_5`, parameters `9.4B`, context length `262144`, quantization `nvfp4`, capabilities `completion`, `vision`, `thinking`, `tools`, and params matching the Ollama page.

Confidence: high for this workstation.

Relevance: Confirms the model is installed and the tag resolves locally. The blocker is not missing Ollama model installation.

Proposed config/smoke change: Keep the model tag. Treat Codex metadata fallback as a Codex/catalog compatibility issue or profile metadata issue, not an Ollama install miss.

Validator/guardrail: deterministic enough for local preflight if `ollama show` is available; otherwise classify as `blocked_runtime`.

### OpenAI Codex config reference

URL: https://developers.openai.com/codex/config-reference

Finding: Codex profile files live next to `config.toml` as `$CODEX_HOME/profile-name.config.toml`; `--profile profile-name` selects that file. The reference also documents `model`, `model_provider`, `model_context_window`, `model_reasoning_summary`, and `model_reasoning_effort`.

Confidence: high. This is official OpenAI Codex documentation.

Relevance: Confirms that `oss-local.config.toml` is the correct runtime control surface and that project-local config cannot own provider/profile routing. It also supports the current validator rule that OSS-local profile selection belongs in the user/profile layer.

Proposed config/smoke change: Keep `/Users/jamiecraik/.codex/oss-local.config.toml` symlinked to the configs repo profile. Do not add provider/profile keys to project-local `.codex/config.toml`.

Validator/guardrail: deterministic enough. Config-drift and symlink-audit checks should continue to prove the home profile points to the configs profile.

### OpenAI Codex exec help

Command: `codex exec --help | sed -n '1,160p'`

Finding: The installed Codex CLI supports `--profile`, `--sandbox`, `--ephemeral`, `--json`, `--ignore-rules`, and `--output-last-message`.

Confidence: high for this workstation.

Relevance: The previous smoke runner did not use `--json`, inherited stdin, and ran in the repo workdir. The captured stderr showed "Reading additional input from stdin..." and loaded repo context before answering the marker.

Proposed config/smoke change: Update `run_oss_local_smoke.py` to pass `--json`, `--ignore-rules`, and `stdin=subprocess.DEVNULL`. Run the marker smoke from an empty temp directory when proving model/profile viability.

Validator/guardrail: deterministic enough. Unit tests can assert the command includes `--json` and `--ignore-rules`; smoke-output checker can parse JSONL usage events.

## Conclusions

1. `qwen3.5:9b-mlx` is a valid Ollama model tag and resolves locally.
2. The metadata fallback is not caused by missing Ollama installation; it is a Codex/runtime metadata compatibility or model-catalog issue.
3. The token blowout in the first smoke was amplified by repo/session context and inherited stdin, not by the marker prompt itself.
4. A valid local smoke should be a model/profile viability check, not a full repo-agent behavior eval.
5. Release evals must still run in the target repo context later; a passing marker smoke only proves the local runtime lane can produce bounded, quantifiable evidence.

## Proposed Deterministic Changes

- Close child stdin in `run_oss_local_smoke.py`.
- Add `--json` to the Codex smoke command.
- Add `--ignore-rules` for the marker smoke so AGENTS/project instructions do not dominate model-viability token usage.
- Keep `--output-last-message` as a receipt surface.
- Keep `check_oss_local_smoke_output.py` hard-failing on metadata fallback, visible thinking, and token-budget excess.
- Record `runtime_observations` in smoke-output receipts so blocked runs still provide model/provider/session/token evidence.

## What Not To Do

- Do not substitute another model if `qwen3.5:9b-mlx` fails smoke.
- Do not run `oss-cloud`, Tessl dry-run, or Tessl live from a marker-smoke result.
- Do not add unsupported Ollama sampling keys to Codex profile TOML without config-validator support.
- Do not treat a marker smoke as release behavior proof.
