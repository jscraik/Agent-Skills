# Insight Report Scripts

This directory keeps the documented insight-report command path runnable:

```bash
python3 Skills/agent-ops/insight-report/scripts/run_insight_report.py --days 7 --no-open
```

The runner delegates to the canonical deferred implementation in
`Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py`.
Keep this compatibility entrypoint whenever the skill or generated plugin
projection changes, unless all skill docs and call sites migrate in the same
change.
