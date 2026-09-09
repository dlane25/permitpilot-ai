import type {
  AgentActivity,
  DecisionItem,
  ImpactMetric,
  PermitItem,
  ProjectSummary,
} from "@/types/permit";

export const project: ProjectSummary = {
  id: "PP-OR-001",
  name: "Oak Ridge Residence",
  address: "1842 Oak Ridge Drive, Houston, TX",
  jurisdiction: "Houston, Texas",
  projectType: "New single-family residence",
  goal: "Prepare this residential construction project for permit submission.",
  readiness: 87,
  documentsAnalyzed: 14,
  documentsTotal: 14,
  permitsIdentified: 7,
  issuesDetected: 2,
};

export const permits: PermitItem[] = [
  {
    id: "building",
    name: "Building Permit",
    authority: "Houston Permitting Center",
    status: "review",
    readiness: 96,
  },
  {
    id: "electrical",
    name: "Electrical Permit",
    authority: "Houston Permitting Center",
    status: "review",
    readiness: 88,
  },
  {
    id: "plumbing",
    name: "Plumbing Permit",
    authority: "Houston Permitting Center",
    status: "ready",
    readiness: 100,
  },
  {
    id: "mechanical",
    name: "Mechanical Permit",
    authority: "Houston Permitting Center",
    status: "ready",
    readiness: 100,
  },
  {
    id: "driveway",
    name: "Driveway / Approach",
    authority: "Public Works",
    status: "ready",
    readiness: 100,
  },
  {
    id: "stormwater",
    name: "Drainage Review",
    authority: "Houston Public Works",
    status: "missing",
    readiness: 62,
  },
  {
    id: "utility",
    name: "Utility Coordination",
    authority: "Utility Provider",
    status: "pending",
    readiness: 73,
  },
];

export const activities: AgentActivity[] = [
  {
    id: "a1",
    agent: "PermitPilot",
    action: "Project goal received",
    detail: "Autonomous permit preparation workflow initialized.",
    status: "complete",
    timestamp: "10:31:02",
  },
  {
    id: "a2",
    agent: "Intake",
    action: "Project attributes extracted",
    detail: "22 structured project fields validated from intake data.",
    status: "complete",
    timestamp: "10:31:04",
  },
  {
    id: "a3",
    agent: "Jurisdiction",
    action: "Authority identified",
    detail: "Primary permitting jurisdiction resolved to Houston, Texas.",
    status: "complete",
    timestamp: "10:31:07",
  },
  {
    id: "a4",
    agent: "Requirements",
    action: "Permit requirements identified",
    detail: "7 permit and review requirements mapped to project scope.",
    status: "complete",
    timestamp: "10:31:11",
  },
  {
    id: "a5",
    agent: "Documents",
    action: "Project package analyzed",
    detail: "14 of 14 uploaded project documents reviewed.",
    status: "complete",
    timestamp: "10:31:18",
  },
  {
    id: "a6",
    agent: "Compliance",
    action: "Compliance issues detected",
    detail: "2 items require remediation before submission.",
    status: "decision",
    timestamp: "10:31:23",
  },
];

export const decisions: DecisionItem[] = [
  {
    id: "d1",
    title: "Electrical service classification",
    category: "Human decision required",
    confidence: 88,
    recommendation:
      "Add Utility Coordination Review for the proposed 400A electrical service.",
    impact: "May prevent an estimated 3ï¿½7 day correction delay.",
    evidenceCount: 3,
  },
];

export const impactMetrics: ImpactMetric[] = [
  {
    label: "Autonomous actions",
    value: "41",
    detail: "Routine tasks completed",
  },
  {
    label: "Human decisions",
    value: "1",
    detail: "Material judgment requested",
  },
  {
    label: "Admin time saved",
    value: "6.4h",
    detail: "Estimated manual effort avoided",
  },
  {
    label: "Delay exposure",
    value: "3ï¿½7d",
    detail: "Potential correction delay identified",
  },
];
