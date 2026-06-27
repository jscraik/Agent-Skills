# eval.glossary-workspace-authority: Glossary Workspace Authority

Knowledge claim: Technical-writer should search active glossary or ubiquitous-language surfaces before introducing durable domain terms.
Behavior under test: Glossary-backed terminology and workspace authority.
Expected agent move: Checks the glossary or ubiquitous-language file, uses the canonical term when present, and adds a plain durable term with citation evidence when the term is missing.
Failure mode: Introduces a new workspace or product term from memory without checking the glossary or recording the term in a durable surface.
Given: A docs update names a Tessl workspace and a new proof lane, but the current wording conflicts with the repo glossary.
Should: Resolve the terminology against the active glossary, use the canonical workspace term, and add or update the glossary only when a durable term is genuinely missing.
Expected failure: Introduces a new workspace or product term from memory without checking the glossary or recording the term in a durable surface.
