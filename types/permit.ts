export type PermitStatus =
  | "ready"
  | "review"
  | "missing"
  | "pending";

export type ActivityStatus =
  | "complete"
  | "active"
  | "waiting"
  | "decision";

export interface PermitItem {
  id: string;
  name: string;
  authority: string;
  status: PermitStatus;
  readiness: number;
}

export interface AgentActivity {
  id: string;
  agent: string;
  action: string;
  detail: string;
  status: ActivityStatus;
  timestamp: string;
}

export interface DecisionItem {
  id: string;
  title: string;
  category: string;
  confidence: number;
  recommendation: string;
  impact: string;
  evidenceCount: number;
}

export interface ImpactMetric {
  label: string;
  value: string;
  detail: string;
}

export interface ProjectSummary {
  id: string;
  name: string;
  address: string;
  jurisdiction: string;
  projectType: string;
  goal: string;
  readiness: number;
  documentsAnalyzed: number;
  documentsTotal: number;
  permitsIdentified: number;
  issuesDetected: number;
}
