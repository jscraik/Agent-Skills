# Deepening Workflow

Use this when the user wants deepening opportunities, architecture search, or a grilling conversation before implementation.

## Vocabulary And Decisions

Read the repo vocabulary and decision surfaces before naming candidates:

- Vocabulary: prefer repo-root `UBIQUITOUS_LANGUAGE.md`; if a repo uses `UBIQUITOUS.md`, use that local equivalent.
- Decisions and ADRs: search `.harness/**` first, including decisions, knowledge, plans, review logs, and ADR-like notes.
- Use architecture language consistently: Module, Interface, Implementation, Depth, Seam, Adapter, Leverage, and Locality.
- Prefer **Seam** when discussing where an Interface lives. Use **boundary** only for existing repo terms, bounded contexts, or the explicit `agent_safe_boundary` output field.

If a candidate depends on a term missing from the vocabulary surface, use `$ubiquitous-language` or update the repo-approved vocabulary surface when the user agrees. Do not invent durable names silently.

## Explore

Explore organically from the named repo area, but keep a repeatable evidence order. If a question can be answered by reading code, tests, docs, or `.harness/**`, explore instead of asking the user.

Default discovery order:

1. Local instructions and validation guidance.
2. Vocabulary surface: `UBIQUITOUS_LANGUAGE.md` or repo equivalent.
3. Decision surface: `.harness/**`.
4. Entrypoints and public Interfaces for the target Module.
5. Callers and imports that cross the Seam.
6. Seam/regression tests and production-like validators.
7. Failure reports, review comments, or tracker/workpad evidence.

Widen only when the current evidence cannot identify owner, public Interface, caller contract, tests, or verifier.

When available, use these reviewers to search the architecture before selecting candidates:

- `agent-native-reviewer`: checks whether humans and agents can both navigate and execute the workflow.
- `api-contract-reviewer`: checks public Interfaces, output contracts, schema compatibility, and caller-observable behavior.
- `architecture-strategist`: checks Module shape, Depth, Seam placement, layering, and strategic fit.

If a reviewer is unavailable, continue locally and mark `reviewer_coverage` as blocked for that role.

Look for friction:

- understanding one concept requires bouncing across many small Modules.
- a Module is shallow: its Interface is nearly as complex as its Implementation.
- pure functions were extracted for testability, but bugs hide in caller choreography.
- tightly-coupled Modules leak facts across Seams.
- tests cannot exercise behavior through the current Interface.
- callers route around the public Interface.

Apply the deletion test to suspected shallow Modules. If deleting the Module makes complexity vanish, it was pass-through. If complexity reappears across callers, it was earning its keep.

## Present Candidates

Present numbered deepening opportunities before proposing any new Interface. For each candidate include:

- Files: involved Modules and callers.
- Problem: the friction and complexity symptom.
- Solution: plain English description of what would change.
- Benefits: Leverage for callers, Locality for maintainers, and how tests improve.
- Agent-safe classification: safe, risky, or blocked with public Interface, Seam tests, caller contract, owner layer, blast radius, and blocker.
- Decision evidence: relevant `UBIQUITOUS_LANGUAGE.md` terms and `.harness/**` decisions or ADR conflicts.

For each candidate, include a compact comparison matrix:

- patch_design: cost, reversibility, blast radius, owner layer impact, verifier.
- interface_design: cost, reversibility, blast radius, owner layer impact, verifier.
- stress check: how this fails, what breaks first, rollback trigger.

If a candidate contradicts a `.harness/**` decision or ADR, surface it only when the friction is real enough to revisit that decision. Mark the conflict clearly.

Do not propose Interfaces yet. Ask which candidate the user wants to explore.

## Grilling Loop

Once the user picks a candidate, interview relentlessly until there is shared understanding. Walk one branch of the design tree at a time, resolving dependencies between decisions one-by-one.

Rules:

- Ask one question at a time and wait for feedback before continuing.
- For each question, provide the recommended answer first, with the tradeoff in plain language.
- Use `request_user_input` for each structural design decision. If unavailable, block instead of choosing.
- If codebase exploration can answer the question, explore rather than asking.
- Track dependencies between answers so later questions do not reopen settled choices without new evidence.

Every grilling response must include:

- `grilling_loop.status`: `active`, `complete`, or `blocked`.
- `grilling_loop.current_question`: the single question being asked now, or `null` if complete.
- `grilling_loop.recommended_answer`: the recommended answer and tradeoff, or code evidence if exploration answered it.
- `grilling_loop.decision_dependency`: which earlier answer or unresolved branch this depends on.
- `grilling_loop.answered_by_code_exploration`: `true` when repo evidence answered the question instead of asking the user.
- `grilling_loop.next_question_blocked_until_user_feedback`: `true` whenever a user answer is required before continuing.

Do not ask a second grilling question in the same response. Do not select the
Interface or first move while `next_question_blocked_until_user_feedback` is
true.

Side effects as decisions crystallize:

- New durable term: update the repo vocabulary surface through `$ubiquitous-language` or ask before editing it directly.
- Fuzzy term sharpened: update the vocabulary surface when the wording becomes load-bearing.
- User rejects a candidate for a load-bearing reason: offer to record an ADR/decision under `.harness/**`.
- Interface alternatives needed: move to Interface Design and keep the final choice behind `request_user_input`.

Offer a `.harness/**` ADR/decision only when the choice is hard to reverse, surprising without context, and the result of a real tradeoff. Keep it short: context, decision, and why.
