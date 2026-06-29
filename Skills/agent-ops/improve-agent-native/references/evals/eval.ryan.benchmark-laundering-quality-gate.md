# eval.ryan.benchmark-laundering-quality-gate: Benchmark Laundering Quality Gate

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.benchmark-laundering-quality-gate.md

Knowledge claim: Principle under test: The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior.
Behavior under test: Observable agent behavior when an proposed agent eval rewards code output volume or benchmark pass rate while ignoring synthesis quality, accessibility, maintainability, and whether the work behaves like software engineering.
Failure mode: The agent accepts the benchmark result as sufficient proof that the model or harness behaves like a software engineer.
Expected agent move: The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior.
Skill lift before failure: The agent accepts the benchmark result as sufficient proof that the model or harness behaves like a software engineer.
Skill lift after behavior: The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior.
Observable delta: The response avoids the weak pattern (The agent accepts the benchmark result as sufficient proof that the model or harness behaves like a software engineer) and instead shows the expected behavior (The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior).

Given: A proposed agent eval rewards code output volume or benchmark pass rate while ignoring synthesis quality, accessibility, maintainability, and whether the work behaves like software engineering.
Should: The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior.
Expected failure: The agent accepts the benchmark result as sufficient proof that the model or harness behaves like a software engineer.

Bad answer patterns:
- The agent accepts the benchmark result as sufficient proof that the model or harness behaves like a software engineer.

Good answer patterns:
- The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
