# eval.writer-gap-gathering: Writer Gap Gathering

Knowledge claim: Technical-writer should raise missing information with the writer instead of cutting, inventing, or burying gaps.
Behavior under test: Writer-facing gap escalation.
Expected agent move: Names the missing owner, proof, recovery path, or screenshot; asks the writer for the missing information; and blocks the affected claim until the gap is resolved.
Failure mode: Deletes the unsupported section, invents a plausible recovery command, or hides the gap in a vague unknowns note.
Given: A runbook asks for a recovery section, but the repository contains no rollback command, owner, or operational receipt for that path.
Should: Treat the recovery content as blocked, ask the writer for the missing owner or proof, and avoid inventing or silently removing the recovery path.
Expected failure: Deletes the unsupported section, invents a plausible recovery command, or hides the gap in a vague unknowns note.
