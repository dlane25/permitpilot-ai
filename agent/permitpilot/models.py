from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    ANALYZING = "analyzing"
    DECISION_REQUIRED = "decision_required"
    READY = "ready"
    FAILED = "failed"


class ApprovalState(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"


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
    decision: HumanDecision | None = None
    next_action: str | None = None
