/** A finding with role-based evidence attribution. */
export interface Finding {
  id: string
  title: string
  description: string
  evidence: string
  source: string
  severity: "critical" | "high" | "medium" | "low"
  epistemicStatus: "observation" | "inference" | "unknown"
  qualifiers: string[]
}

/** An actionable recommendation with an urgency classification. */
export interface Recommendation {
  id: string
  title: string
  description: string
  priority: "immediate" | "short-term" | "long-term"
}

/** A dated phase in the implementation roadmap. */
export interface TimelinePhase {
  phase: string
  title: string
  description: string
  duration: string
}

/** A normalized risk entry consumed by the report's matrix. */
export interface RiskMatrixEntry {
  risk: string
  probability: "low" | "medium" | "high"
  impact: "low" | "medium" | "high"
  mitigation: string
}

/** The validated, generated data contract for a TELOS report. */
export interface ReportData {
  clientName: string
  organizationName: string
  reportTitle: string
  reportDate: string
  classification: string
  executiveSummary: {
    context: string
    methodology: { interviewCount: number; roles: string[] }
    keyFindings: string[]
    primaryRecommendation: string
    expectedOutcomes: string[]
  }
  situationAssessment: { currentState: string; clientAsk: string; whyNow: string }
  findings: Finding[]
  riskAnalysis: {
    existentialRisks: string[]
    competitiveThreats: string[]
    timelinePressures: string
    matrix: RiskMatrixEntry[]
  }
  strategicOpportunity: { goodNews: string; requirements: string[] }
  recommendations: Recommendation[]
  targetState: {
    description: string
    keyCapabilities: string[]
    successMetrics: string[]
  }
  roadmap: TimelinePhase[]
  callToAction: {
    immediateSteps: string[]
    decisionPoints: string[]
    commitmentRequired: string
  }
}

/** Empty until a validated artifact set is generated for a specific report. */
export const reportData: ReportData | null = null
