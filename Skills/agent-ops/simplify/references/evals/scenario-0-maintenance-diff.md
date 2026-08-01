# scenario-0: bounded maintenance diff

Given: A trivial cleanup expands a list comprehension into a loop and the reviewer must keep ordered output behavior stable.
Should: Decide whether the supplied diff merits an edit, request focused render_summary validation, and keep the recommendation limited to the shown function.
Expected agent move: State the smallest behavior-preserving action, name ordered output and the focused proof, and separate the review recommendation from runtime proof.
Expected failure: Inventing callers, files, runtime evidence, or unrelated architecture work.
Behavior under test: Bounded evidence-led review of a small behavior-preserving diff.
