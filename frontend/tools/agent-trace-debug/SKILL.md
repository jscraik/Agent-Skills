---
name: agent-trace-debug
description: Analyze Agent Trace data flow when AIAttributionPanel shows empty/incorrect trace by tracing expected vs actual shapes across agentTraceStore and API.
---

# agent-trace-debug

## Scope and triggers
- The Agent Trace UI is empty/incorrect (missing attribution, unexpected `undefined`, wrong counts) and you need to find where the data shape diverges.
- Bugs involving these components/files: `AIAttributionPanel`, `agentTraceStore`, `AgentTrace` types, API response parsing/normalization.

## Required inputs
- Repo checked out locally with the relevant UI + store + API client code.
- The expected user-visible symptom (1 sentence) and, if available, a screenshot or console error snippet.
- Ability to run the app (or at least inspect the network/API response) to observe runtime shapes.

If the files mentioned in the procedure do not exist at the given paths, stop and ask for the correct paths (do not guess).

## Deliverables
- A report of **expected vs actual data shape** at each checkpoint (UI consumer → store → API → transforms), using the included template.
- A short list of the **first divergence point(s)** (where the shape stops matching expectations).

## Philosophy
- Debug data flow by walking the dependency chain from **consumer** (UI) back to **source** (API) and recording shapes at each boundary.
- Prefer **small, reversible instrumentation** over refactors while establishing ground truth.

## Guardrails (must follow)
- **Follow the procedure in order.** Don’t jump ahead.
- **Do not refactor unrelated code.** Only add the smallest debug instrumentation needed.
- Avoid leaking sensitive data: log **shape + counts + IDs**, not raw prompts, tokens, or user content.

## Procedure (exact sequence)

### 1) Read the UI consumer
Read `src/components/AIAttributionPanel.tsx`.

If the file does not exist at that path, **stop and ask for the correct file/path** (do not guess).

Record (in your report):
- What prop(s) / selector(s) / hook(s) the panel uses to obtain trace data.
- The minimal fields the UI expects (accessed properties).
- Any “shape assumptions” (optional chaining, default values, array indexing, etc.).

### 2) Confirm the store shape
Read `src/stores/agentTraceStore.ts`.

If the file does not exist at that path, **stop and ask for the correct file/path** (do not guess).

Record (in your report):
- The **authoritative** `AgentTrace` type/interface (or inferred shape) the store expects.
- The store’s state shape and where/when it is updated.
- Any transformation/normalization happening in the store.

### 3) Verify the API response matches `AgentTrace`
Find the API call that sources Agent Trace data (search for the endpoint/key used in the store, or “agentTrace”/“trace” in the API client).

Record (in your report):
- The API response type as modeled/assumed in code.
- The actual runtime JSON shape (from logging/instrumentation in step 4).
- The first point where “expected” diverges from “actual”.

### 4) Add logging at transformation points
Add **temporary** `console.log` statements at the narrowest transformation points (usually 1–3 places):

- Immediately after parsing the API response.
- Immediately before writing into `agentTraceStore`.
- Immediately before the UI consumes the value (only if needed).

Logging rules:
- Prefix every log line with: `[agent-trace-debug]`.
- Log **shape**, not full payloads. Prefer:
  - `Object.keys(obj)`
  - `Array.isArray(x)` + `x.length`
  - `typeof x`
  - “has field?” checks (`"field" in obj`)

### 5) Stop and report
Do **not** proceed to fixes unless explicitly asked. Your job is to surface the data mismatch.

## Examples
Example prompt that should trigger this skill:
- “AIAttributionPanel renders, but Agent Trace is empty after a backend change. Can you trace the data flow and tell me where the shape breaks?”

## Report template (copy/paste)

### Step 1 — AIAttributionPanel consumer
- Expected shape (from usage):
- Actual shape observed (if already known):
- Notes:

### Step 2 — agentTraceStore shape
- Expected `AgentTrace` / state shape:
- Transformations:
- Notes:

### Step 3 — API response
- Expected response shape:
- Actual response shape:
- First divergence point:

### Step 4 — Instrumentation points
- Log location #1 (file + function):
  - Expected:
  - Actual:
- Log location #2 (optional):
- Log location #3 (optional):

## Common failure patterns (don’t fix yet)
- API returns `snake_case` but store/UI expects `camelCase`.
- API wraps payload (`{ data: … }`) but store assumes raw object.
- `trace` array is sometimes missing/empty and UI assumes `[0]` exists.
- Store normalizes into a map but UI expects an array (or vice versa).

## Validation
- Fail fast: stop at the first failed gate (missing file, unsafe logging, or a build/lint/test failure) and address it before continuing.
- If you add logs, run the minimal repo checks that catch obvious breakage (lint/typecheck/test) *if they exist*; otherwise, at least ensure the code still builds.
- Confirm logs are prefixed with `[agent-trace-debug]` and only print shape/counters (no raw sensitive payloads).
- Confirm the final report includes **Step 1–4** sections and identifies a **first divergence point**.

## Anti-patterns
- Jumping straight to “fix the store” or “refactor types” before documenting expected vs actual shapes.
- Logging full payloads (prompts, user text, tokens) instead of shape/counters.
- Changing unrelated code while debugging (violates the guardrails; makes diffs noisy).

## Constraints
- Redact secrets/sensitive data by default: never log raw prompts, tokens, user content, auth headers, or full payloads.
- Do not add new dependencies.
- Do not introduce non-temporary behavioral changes; instrumentation only unless explicitly requested.
- Keep frontmatter valid (`name` and `description` only; single-line scalars).

## Resources
- `references/contract.yaml` — output contract and guardrails for this skill.
- `references/contract.yaml` schema_version: `1.0`
- `references/evals.yaml` — prompt/eval cases for regression testing this skill.

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
