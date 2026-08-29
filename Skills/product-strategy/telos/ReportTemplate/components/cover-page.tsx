export interface CoverPageProps {
  clientName: string
  organizationName: string
  reportTitle: string
  reportDate: string
  classification: string
}

/** Renders the report cover using caller-supplied metadata only. */
export function CoverPage({
  clientName,
  organizationName,
  reportTitle,
  reportDate,
  classification,
}: CoverPageProps) {
  return (
    <div className="cover-page">
      <div className="cover-classification">{classification}</div>

      <div className="flex-1 flex flex-col justify-center">
        <div className="font-accent text-lg tracking-[0.25em] text-primary uppercase mb-4">
          {organizationName}
        </div>
        <h1 className="cover-title">{reportTitle}</h1>
        <p className="cover-subtitle">Prepared for {clientName}</p>
      </div>

      <div className="cover-meta">
        <p className="cover-date">{reportDate}</p>
        <p className="text-muted-dark text-sm mt-2">
          TELOS Assessment
        </p>
      </div>
    </div>
  )
}
