# eval.visual-evidence-decision: Visual Evidence Decision

Knowledge claim: Technical-writer should choose diagrams, screenshots, images, tables, or prose based on reader search cost and evidence needs.
Behavior under test: Format choice for visual documentation.
Expected agent move: Explains whether the reader needs a screenshot, diagram, table, or prose; chooses the smallest useful visual form; and cites the real UI, artifact, command, or state the visual would represent.
Failure mode: Adds decorative visuals, avoids needed screenshots, or makes a visual recommendation without tying it to reader search cost or real evidence.
Given: A release note describes a changed dashboard state that reviewers need to recognize, but the text alone makes the before and after hard to verify. The staged input includes this text: "The deployment dashboard now shows queued checks separately from blocked checks. Reviewers need to recognize the new state before approving release notes."
Should: Write `visual-evidence-decision.md`; decide whether a screenshot, table, diagram, or prose is needed; tie the choice to reader search cost; and identify the concrete UI state or artifact that must be captured.
Expected failure: Adds decorative visuals, avoids needed screenshots, or makes a visual recommendation without tying it to reader search cost or real evidence.
