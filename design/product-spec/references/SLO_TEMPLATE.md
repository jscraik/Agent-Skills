# SLO Template (minimal)

> Define SLI → SLO → error budget → policy. If N/A, state why and who accepted the risk.

## Service / Feature
- Name: <service/feature>
- Owner: <team/individual>

## SLIs
List 2–3 core SLIs (availability, latency, correctness, freshness, etc.)

| SLI              | Definition                         | Measurement source          |
| ---------------- | ---------------------------------- | --------------------------- |
| Availability     | successful responses / total       | <metrics name/dashboard>    |
| Latency (p95)    | p95 over rolling 5m                 | <metrics name/dashboard>    |
| Error rate       | 5xx + defined client errors / total| <metrics name/dashboard>    |

## SLOs
| SLI          | Target | Window  |
| ------------ | ------ | ------- |
| Availability | 99.9%  | 30 days |
| Latency p95  | <X ms> | 30 days |
| Error rate   | <Y %>  | 30 days |

## Error budget
- Error budget = 1 − SLO (per window).
- Consumption policy: <what happens when 25%/50%/75%/100% budget is consumed>
  - e.g., pause launches at 50%, halt launches + incident at 100%.

## Alerting policy
- Page on: <condition tied to SLI burn rate>
- Ticket on: <condition>
- Dashboards: <links>

## Reviews
- Cadence: <e.g., monthly>
- Last review: <date>
- Next review: <date>
