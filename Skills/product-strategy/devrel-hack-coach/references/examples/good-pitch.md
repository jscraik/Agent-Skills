# Good Pitch Example: CacheScope

## Sentence 1 - The Wedge

"When you add a timestamp to your Claude system prompt, you burn your entire prompt cache on every call."

## Sentence 2 - The Move

"We built CacheScope, a CLI that diffs two API calls and shows which line cost
you money."

## Sentence 3 - The Moment

"Watch this."

Then run the live demo: paste prompts, show red line, show "$340 last month."

## Judge Experience

- What the judge assumes before the demo: prompt cost is hard to attribute.
- What the judge must understand first: one volatile line can erase caching.
- Reveal order: paste prompts, show diff, show monthly cost, show one fix.

## Judge Q&A

1. How does this scale?
   It reads request logs once and runs the prompt diff offline.
2. Why not just use Helicone or LangSmith?
   Those show total spend; this shows the exact line that caused the spike.
3. What happens when the LLM hallucinates?
   Nothing; this is static request analysis, not inference.
4. Who pays for this?
   The same team paying the API bill.
5. What's your moat?
   The PR integration that shows monthly cache impact before code merges.

## Real Vs Mocked

- Live golden path: prompt diff and cost calculation from two request fixtures.
- Mocked or stubbed: billing export import.
- Deferred after the hack: provider-wide dashboard and PR bot.
