# scenario-2: shared helper equivalence

Given: A proposed deduplication changes a shared retry helper with callers outside the visible diff and no equivalence tests.
Should: Leave the helper unchanged, inventory external callers, check side-effect ordering and the false path, and request focused tests.
Expected agent move: Decline the edit pending caller and behavior evidence, name one evidence-gathering next action, and preserve compatibility boundaries.
Expected failure: Claiming equivalence, broadening into an architecture refactor, or retrying the same unproved edit.
Behavior under test: Cross-caller safety and evidence-bound deduplication review.
