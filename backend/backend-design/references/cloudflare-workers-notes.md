# Cloudflare Workers Notes

## Execution Model
- Isolate-based runtime; design for stateless execution.
- Use Durable Objects or external storage for state.

## Limits and Performance
- Use streaming responses for large payloads.
- Be mindful of CPU and memory limits; avoid long-running tasks.
- Paid plans can opt into higher CPU limits (up to 5 minutes) via configuration.

## Security
- Validate input and enforce strict CORS.
- Use environment variables or secret bindings for credentials.

## References
- Workers overview: https://developers.cloudflare.com/workers/
- Limits: https://developers.cloudflare.com/workers/platform/limits/
- Higher CPU limits changelog: https://developers.cloudflare.com/changelog/2025-03-25-higher-cpu-limits/
- Security model: https://developers.cloudflare.com/workers/learning/security-model/
