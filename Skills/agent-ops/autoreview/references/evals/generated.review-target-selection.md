# target-selection: Review target selection under committed work

Given: The user says the patch has already been committed on a clean main checkout and asks for a final structured review before relying on the change.

Should: The agent should select commit review for HEAD or the named commit, explain why local dirty review would be empty, preserve the review command, and report accepted, rejected, or blocked findings separately from merge readiness.

Expected agent move: Select commit mode, use the bundled autoreview helper or equivalent command with the explicit commit ref, avoid reviewing an empty local diff, verify any accepted findings from source, and include validation evidence.

Expected failure: Claims that a clean local diff proves the committed change was reviewed, or treats review success as merge approval.

Behavior under test: Autoreview must choose the correct target surface and keep review evidence separate from delivery approval.
