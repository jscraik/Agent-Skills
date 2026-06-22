# Tessl Evidence

This directory is the repo-local forensic trail for live Tessl skill evals.

- \`index.jsonl\` is the compact review and handoff ledger. It records run id,
  artifact type, raw evidence path, content hash, byte count, status, and score
  summary when the Tessl view has scored results.
- Raw run artifacts such as \`*/<run-id>/tessl-eval-view.json\` and
  \`*/<run-id>/tessl-eval-submission.json\` are intentionally local evidence.
  They can be large and may contain private run details, so they are ignored by
  Git but must be preserved for failure analysis.
- \`_archive/\` contains overwritten raw artifacts when the same run/file is
  refreshed. Do not delete it to clean \`git status\`; use the compact index for
  tracked review and raw files for forensic debugging.

If this directory appears noisy, fix the retention policy or ignore rules. Do
not remove raw Tessl evidence unless the operator explicitly asks to discard
forensic run history.
