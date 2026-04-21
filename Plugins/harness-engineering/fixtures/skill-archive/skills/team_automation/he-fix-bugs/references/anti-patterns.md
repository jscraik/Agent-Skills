# Debugging Anti-Patterns

Read this before forming hypotheses. These patterns describe the most common ways debugging goes wrong.

## Prediction Quality

The prediction requirement prevents symptom fixing. A prediction should test whether your understanding of the bug is correct, not only whether the error disappeared.

Bad prediction:
> Hypothesis: The null pointer happens because `user` is not initialized.  
> Prediction: `user` will be null.

This restates the symptom.

Good prediction:
> Hypothesis: Auth middleware skips initialization on cached requests.  
> Prediction: Non-cached requests to the same endpoint should not fail, and failing requests should include cache headers.

This checks a separate path and can disprove the hypothesis.

Rule of thumb: a useful prediction names a new observation, not the same line you already inspected.

## Shotgun Debugging

Changing multiple things at once to "see if it helps."

Why it fails:
- if the bug disappears, cause remains unknown,
- if the bug persists, relevant signal is buried by noise.

Use one hypothesis, one meaningful change, one verification.

## Confirmation Bias

Ambiguous evidence often gets interpreted as support for the current theory.

Common traps:
- treating weak log hints as proof,
- assuming a passing test covers the failure path when it does not,
- interpreting changed error text as progress without causal evidence.

Countermeasure: state one observation that would disprove the hypothesis before claiming confirmation.

## "It Works Now, Move On"

When the symptom disappears, there is pressure to stop.

This is unsafe when causal explanation is incomplete. You may have:
- masked a symptom,
- changed timing without fixing cause,
- moved failure to a nearby path.

Gate: explain the full causal chain without "somehow" or "probably."

## Shortcut Warning Signs

- Proposing fixes before stating root cause.
- Starting attempt N+1 without new information from failed attempts.
- Certainty before reading relevant code paths.
- Dismissing environment differences during local-vs-CI/prod drift.

## Smart Escalation Patterns

After 2-3 exhausted hypotheses, diagnose the pattern:

| Pattern | Diagnosis | Next move |
|---|---|---|
| Hypotheses scatter across subsystems | likely boundary/design issue | route to `he-brainstorm` after sharing evidence |
| Evidence conflicts with code expectations | mental model mismatch | reset and retrace from entrypoint |
| Works locally but not CI/prod | environment divergence | diff config, runtime, data, and timing |
| Fix works but prediction failed | symptom patch | continue investigation; root cause remains |
