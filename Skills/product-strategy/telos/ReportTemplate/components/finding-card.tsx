import { SeverityBadge } from "./severity-badge.js"
import type { Finding } from "@/lib/report-data.js"

export interface FindingCardProps {
  finding: Finding
  index: number
}

/**
 * Renders one evidence-backed finding and its severity.
 *
 * `finding` supplies the title, description, evidence, source, and severity.
 * `index` is zero-based and is displayed as a one-based finding number. The
 * finding severity is passed unchanged to `SeverityBadge`. The card also
 * visibly renders the finding's epistemic status and every source qualifier.
 */
export function FindingCard({ finding, index }: FindingCardProps) {
  return (
    <div className="finding-card">
      <div className="finding-header">
        <div className="flex items-center gap-4">
          <span className="text-primary font-bold text-2xl min-w-[2rem]">
            {index + 1}.
          </span>
          <h3 className="finding-title">{finding.title}</h3>
        </div>
        <SeverityBadge severity={finding.severity} />
      </div>
      <p className="text-foreground mb-2 ml-12">{finding.description}</p>
      <p className="finding-evidence ml-12">
        <span className="font-medium text-foreground">Evidence:</span>{" "}
        {finding.evidence}
      </p>
      <div className="text-xs text-muted mt-2 ml-12">
        <p>
          <span className="font-medium text-foreground">Epistemic status:</span>{" "}
          {finding.epistemicStatus}
        </p>
        {finding.qualifiers.length > 0 && (
          <div className="mt-1">
            <span className="font-medium text-foreground">Qualifiers:</span>
            <ul className="list-disc ml-5" aria-label="Source qualifiers">
              {finding.qualifiers.map((qualifier, qualifierIndex) => (
                <li key={`${finding.id}-qualifier-${qualifierIndex}`}>
                  {qualifier}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      <p className="text-xs text-muted mt-2 italic ml-12">Source: {finding.source}</p>
    </div>
  )
}
