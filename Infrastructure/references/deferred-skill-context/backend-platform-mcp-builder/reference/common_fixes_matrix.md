# Common Fixes Matrix

Use this as a quick map from symptom to likely fix.

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Tool not selected | Vague description or generic name | Rewrite description to "Use this when..." and make name action-specific |
| Model sends wrong args | Loose schema or missing enums | Tighten `inputSchema`, add enums/defaults |
| Widget blank | Wrong `mimeType` or missing template URI | Use `text/html+skybridge`, set `_meta["openai/outputTemplate"]` |
| Auth fails | Wrong `aud` or issuer mismatch | Align Auth0 API identifier and token validation |
| Pagination mismatch | Inconsistent fields | Standardize on `limit` + `offset` or `cursor` |
| Output ignored | Missing `structuredContent` | Add `outputSchema` and return `structuredContent` + text JSON fallback |
| Tool errors silent | Throwing instead of error response | Return `isError: true` with structured error payload |
