import React from "react";

type RecordLike = Record<string, unknown>;

function asArray<T = RecordLike>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function asRecord(value: unknown): RecordLike {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as RecordLike) : {};
}

function text(value: unknown, fallback = "-"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return JSON.stringify(value);
}

function statusClass(value: unknown): string {
  const normalized = text(value).toLowerCase();
  if (["pass", "passed", "true", "ready"].includes(normalized)) {
    return "evalStatus evalStatusPass";
  }
  if (["blocked", "fail", "failed", "false"].includes(normalized)) {
    return "evalStatus evalStatusFail";
  }
  return "evalStatus";
}

export function EvidenceStrip(props: RecordLike) {
  return (
    <section className="evalEvidenceStrip">
      {Object.entries(props).map(([key, value]) => (
        <div className="evalEvidenceItem" key={key}>
          <span>{key}</span>
          <strong>{text(value)}</strong>
        </div>
      ))}
    </section>
  );
}

export function ClaimCoverage({
  claims,
  cases,
}: {
  claims?: unknown;
  cases?: unknown;
  results?: unknown;
}) {
  const caseRows = asArray<RecordLike>(cases);
  return (
    <section className="evalPanel">
      <table>
        <thead>
          <tr>
            <th>Claim</th>
            <th>Risk</th>
            <th>Hard Gate</th>
            <th>Cases</th>
          </tr>
        </thead>
        <tbody>
          {asArray<RecordLike>(claims).map((claim) => {
            const id = text(claim.id);
            const linkedCases = caseRows
              .filter((item) => asArray<string>(item.claim_ids).includes(id))
              .map((item) => text(item.id));
            return (
              <tr key={id}>
                <td>{id}</td>
                <td>{text(claim.risk)}</td>
                <td>{text(claim.hard_gate)}</td>
                <td>{linkedCases.length ? linkedCases.join(", ") : "missing"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}

export function ScoreVector({
  scores,
  thresholds,
  hardGateStatus,
}: {
  scores?: unknown;
  thresholds?: unknown;
  hardGateStatus?: unknown;
}) {
  const scoreMap = asRecord(scores);
  const thresholdMap = asRecord(thresholds);
  return (
    <section className="evalPanel evalScoreVector">
      {Object.entries(scoreMap).map(([dimension, value]) => (
        <div className="evalScore" key={dimension}>
          <span>{dimension}</span>
          <strong>{text(value)}</strong>
          <small>threshold {text(thresholdMap[dimension])}</small>
        </div>
      ))}
      <div className={statusClass(hardGateStatus)}>
        Hard gates: {text(hardGateStatus)}
      </div>
    </section>
  );
}

export function ScenarioMatrix({
  cases,
  groupBy = "category",
}: {
  cases?: unknown;
  results?: unknown;
  groupBy?: string;
  showBaselineDelta?: boolean;
}) {
  return (
    <section className="evalPanel">
      <table>
        <thead>
          <tr>
            <th>Case</th>
            <th>{groupBy}</th>
            <th>Claims</th>
            <th>Realistic</th>
            <th>Baseline</th>
          </tr>
        </thead>
        <tbody>
          {asArray<RecordLike>(cases).map((item) => (
            <tr key={text(item.id)}>
              <td>{text(item.id)}</td>
              <td>{text(item[groupBy])}</td>
              <td>{asArray<string>(item.claim_ids).join(", ") || "-"}</td>
              <td>{text(item.realistic)}</td>
              <td>{text(item.baseline_id || item.baseline_type)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export function HardGateStatus({ gates, blockers }: { gates?: unknown; blockers?: unknown }) {
  return (
    <section className="evalPanel">
      <h3>Hard Gate Status</h3>
      <ul>
        {asArray<RecordLike>(gates).map((gate, index) => (
          <li className={statusClass(gate.status)} key={text(gate.id, String(index))}>
            {text(gate.id || gate.name)}: {text(gate.status)}
          </li>
        ))}
      </ul>
      {asArray<RecordLike>(blockers).length > 0 && (
        <ol>
          {asArray<RecordLike>(blockers).map((blocker, index) => (
            <li key={index}>{text(blocker.message || blocker.type || blocker)}</li>
          ))}
        </ol>
      )}
    </section>
  );
}

export function BaselineDelta({
  candidate,
  baselines,
  dimensions,
}: {
  candidate?: unknown;
  baselines?: unknown;
  dimensions?: string[];
}) {
  const candidateRecord = asRecord(candidate);
  return (
    <section className="evalPanel">
      <table>
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Candidate</th>
            <th>Baselines</th>
          </tr>
        </thead>
        <tbody>
          {asArray<string>(dimensions).map((dimension) => (
            <tr key={dimension}>
              <td>{dimension}</td>
              <td>{text(candidateRecord[dimension])}</td>
              <td>{asArray<RecordLike>(baselines).map((baseline) => text(baseline[dimension])).join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export function TraceEvidence({
  traces,
  artifacts,
  redactionPolicy,
}: {
  traces?: unknown;
  artifacts?: unknown;
  redactionPolicy?: string;
}) {
  return (
    <section className="evalPanel">
      <p>{redactionPolicy}</p>
      <h3>Traces</h3>
      <ul>{asArray<RecordLike>(traces).map((trace, index) => <li key={index}>{text(trace.path || trace.id || trace)}</li>)}</ul>
      <h3>Artifacts</h3>
      <ul>{asArray<RecordLike>(artifacts).map((artifact, index) => <li key={index}>{text(artifact.path || artifact.id || artifact)}</li>)}</ul>
    </section>
  );
}

export function MacroEvalTotals({ totals }: { totals?: unknown }) {
  const totalMap = asRecord(totals);
  return (
    <section className="evalEvidenceStrip macroEvalTotals">
      {["summaries_scanned", "events", "skills", "behavior_patterns"].map((key) => (
        <div className="evalEvidenceItem" key={key}>
          <span>{key}</span>
          <strong>{text(totalMap[key], "0")}</strong>
        </div>
      ))}
    </section>
  );
}

export function MacroEvalArtifacts({ artifacts }: { artifacts?: unknown }) {
  const artifactMap = asRecord(artifacts);
  return (
    <section className="evalPanel">
      <table>
        <thead>
          <tr>
            <th>Artifact</th>
            <th>Path</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(artifactMap).map(([name, path]) => (
            <tr key={name}>
              <td>{name}</td>
              <td><code>{text(path)}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export function MacroEvalLeaderboard({
  rows,
  labelField,
  limit = 10,
}: {
  rows?: unknown;
  labelField: string;
  limit?: number;
}) {
  const rankedRows = asArray<RecordLike>(rows).slice(0, limit);
  return (
    <section className="evalPanel">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>{labelField}</th>
            <th>Trace Count</th>
          </tr>
        </thead>
        <tbody>
          {rankedRows.map((row, index) => (
            <tr key={text(row[labelField], String(index))}>
              <td>{index + 1}</td>
              <td>{text(row[labelField])}</td>
              <td>{text(row.trace_count, "0")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export function MacroEvalFlowTable({ rows, limit = 12 }: { rows?: unknown; limit?: number }) {
  const flowRows = asArray<RecordLike>(rows).slice(0, limit);
  const columns = Array.from(
    flowRows.reduce((keys, row) => {
      Object.keys(row).forEach((key) => keys.add(key));
      return keys;
    }, new Set<string>())
  );
  const orderedColumns = [
    ...columns.filter((column) => column !== "trace_count"),
    ...columns.filter((column) => column === "trace_count"),
  ];
  return (
    <section className="evalPanel">
      <table>
        <thead>
          <tr>
            {orderedColumns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {flowRows.map((row, index) => (
            <tr key={index}>
              {orderedColumns.map((column) => (
                <td key={column}>{text(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
