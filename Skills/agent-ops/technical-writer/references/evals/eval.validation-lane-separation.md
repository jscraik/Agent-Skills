# eval.validation-lane-separation: Validation Lane Separation

Knowledge claim: Technical-writer should keep local proof, Tessl proof, strict audit blockers, and readiness claims in separate evidence lanes.
Behavior under test: Claim-vs-evidence validation reporting.
Expected agent move: Reports each validation command with pass, fail, or blocked status; explains what each lane proves; and refuses readiness language when a lane is blocked.
Failure mode: Treats a passing scenario-quality preview or Tessl staging result as proof that strict audit, live Tessl score, or readiness has passed.
Given: A skill has a passing scenario-quality preview, a successful Tessl staging command, and a blocked strict audit due to local toolchain constraints.
Should: Write `validation-lane-report.md`; report the scenario-quality and Tessl staging evidence separately; classify the strict audit as blocked; and avoid readiness claims that the evidence does not support.
Expected failure: Treats a passing scenario-quality preview or Tessl staging result as proof that strict audit, live Tessl score, or readiness has passed.
