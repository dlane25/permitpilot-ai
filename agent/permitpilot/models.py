from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    ANALYZING = "analyzing"
    DECISION_REQUIRED = "decision_required"
    EVIDENCE_READY = "evidence_ready"
    APPLICABILITY_READY = "applicability_ready"
    READY = "ready"
    FAILED = "failed"


class ApprovalState(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"


class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class ApplicabilityClassification(str, Enum):
    APPLICABLE = "applicable"
    CONDITIONAL = "conditional"
    NOT_APPLICABLE = "not_applicable"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class ProjectInput(BaseModel):
    project_id: str
    name: str
    address: str
    jurisdiction: str | None = None
    project_type: str
    goal: str


class ProjectInspection(BaseModel):
    project_id: str
    project_name: str
    project_type: str
    address: str
    jurisdiction: str | None
    goal: str
    completeness_score: int = Field(ge=0, le=100)
    observations: list[str] = Field(default_factory=list)


class EvidenceSource(BaseModel):
    source_name: str
    source_url: str
    source_type: str
    verified: bool
    requirements: list[str] = Field(default_factory=list)
    notes: str | None = None


class JurisdictionEvidence(BaseModel):
    jurisdiction: str | None
    authority: str | None = None
    status: EvidenceStatus
    verified: bool
    sources: list[EvidenceSource] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)


class ApplicabilityDetermination(BaseModel):
    requirement: str
    classification: ApplicabilityClassification
    confidence: int = Field(ge=0, le=100)
    rationale: str
    projected_impact: str
    source_name: str | None = None
    source_url: str | None = None


class ApplicabilityAnalysis(BaseModel):
    project_type: str
    jurisdiction: str
    determinations: list[ApplicabilityDetermination] = Field(
        default_factory=list
    )
    total_requirements: int
    applicable_count: int
    conditional_count: int
    not_applicable_count: int
    needs_human_review_count: int


class AgentAction(BaseModel):
    action: str
    explanation: str
    confidence: int | None = Field(default=None, ge=0, le=100)
    projected_impact: str | None = None
    approval_state: ApprovalState = ApprovalState.NOT_REQUIRED
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class HumanDecision(BaseModel):
    decision_id: str
    title: str
    recommendation: str
    explanation: str
    confidence: int = Field(ge=0, le=100)
    projected_impact: str
    evidence: list[str] = Field(default_factory=list)
    approval_state: ApprovalState = ApprovalState.PENDING


class WorkflowResult(BaseModel):
    project_id: str
    status: WorkflowStatus
    summary: str
    actions: list[AgentAction] = Field(default_factory=list)
    jurisdiction_evidence: JurisdictionEvidence | None = None
    applicability_analysis: ApplicabilityAnalysis | None = None
    decision: HumanDecision | None = None
    next_action: str | None = None
