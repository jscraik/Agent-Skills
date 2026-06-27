# eval.reader-state-citation-map: Reader-State Citation Map

Knowledge claim: Technical-writer should convert substantial documentation work into reader-state and claim maps before rewriting.
Behavior under test: Reader-state mapping with citation-backed claims.
Expected agent move: Produces a Reader-State Map, a claim-to-citation map, and writer questions for missing foundations before proposing the rewrite.
Failure mode: Rewrites the document directly using generic clarity advice and no citation-backed claim map.
Given: A README explains a new operator workflow with several unstated prerequisites, two command examples, one unverified path, and no reader model.
Should: Build reader-state and claim maps, cite evidence for the command and path claims, and identify which missing foundations require writer input.
Expected failure: Rewrites the document directly using generic clarity advice and no citation-backed claim map.
