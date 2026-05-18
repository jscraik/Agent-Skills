# Systems Thinking Product Rule

Systems thinking means spotting blockers, designing ways for people and agents
to systematically overcome them, and explaining how code makes that possible.

This is the umbrella rule for the adjacent product contracts: high-signal
steering uptake, misuse-resistant interfaces, and zero-setup agent workspaces.
Those rules are not separate instincts. They are one operating loop.

## Operating Loop

1. Spot the blocker.
2. Classify who is blocked and why.
3. Identify the smallest durable capability that would unblock them next time.
4. Encode that capability in code, contract, metadata, validator, or workflow.
5. Validate that the blocker is now easier to diagnose or overcome.
6. Explain the before and after in plain operational terms.

When the blocker is the agent operating loop itself, the same rule applies. The
agent must stop the stale lane, refine the environment, and prove the new
mechanism before resuming. Continuing the old task while promising better
behavior is evidence that the blocker has not been systematized.

## Blocker Literacy

A useful agent does not flatten every failure into generic setup, docs, or
environment trouble. It classifies blockers so the next action is obvious.

Use concrete blocker classes such as:

- missing capability;
- missing permission;
- missing credential;
- missing workspace contract;
- drifted projection;
- ambiguous ownership;
- repo-surface ownership debt;
- unclassified diagnostic debt;
- unsafe interface shape;
- weak validation;
- stale or missing context.

Each blocker should have an owner, a next command or decision, and a reason it
cannot be silently worked around.

High-count diagnostics need a category breakdown before closeout language calls
them nonblocking. A count is not an explanation. Report the dominant categories,
the owner or decision boundary, and the next action that can reduce or
intentionally retain the debt.

## Empowerment Design

Code should reduce the amount of integration, memory, and process discipline
required from the customer. Prefer product surfaces that let people and agents
recover systematically: doctor checks, structured readiness reports, typed
metadata, narrow permission requests, contextual errors, resumable workflows,
and validators that make drift visible.

For high-level workflow skills, the empowerment mechanism should usually be a
CTF-style eval loop: plant a flag, run the skill, capture or miss the flag,
reflect on the evidence, commit the smallest refinement, and repeat until the
skill is reliable against the live workflow.

If the answer to a blocker is only more prose, the system probably has not been
designed yet. The code should carry the repeatable part of the answer.

## Explanation Rule

When explaining a systems-thinking change, use this shape:

- blocker: what prevented progress or caused repeated correction;
- mechanism: what code, contract, or workflow now helps overcome it;
- proof: what command, artifact, or test shows the mechanism works;
- remaining limit: what still requires human decision or external state.

Do not present a polished concept as a solved system unless there is a
mechanism and proof behind it.
