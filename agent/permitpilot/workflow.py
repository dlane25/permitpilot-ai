from __future__ import annotations

from .agent import build_permitpilot_agent
from .models import (
    AgentAction,
    ApprovalState,
    EvidenceStatus,
    HumanDecision,
    JurisdictionEvidence,
    ProjectInput,
    WorkflowResult,
    WorkflowStatus,
)
from .tools import inspect_project, research_jurisdiction


def inspect_project_deterministically(project: ProjectInput) -> dict:
    """Run project intake without invoking a language model."""

    return inspect_project(
        project_id=project.project_id,
        name=project.name,
        address=project.address,
        project_type=project.project_type,
        goal=project.goal,
        jurisdiction=project.jurisdiction or "",
    )


def research_jurisdiction_deterministically(project: ProjectInput) -> dict:
    """Load jurisdiction evidence without invoking a language model."""

    return research_jurisdiction(project.jurisdiction or "")


def create_initial_workflow_result(project: ProjectInput) -> WorkflowResult:
    """Create PermitPilot's intake-only governed workflow result."""

    inspection = inspect_project_deterministically(project)

    action = AgentAction(
        action="inspect_project",
        explanation=(
            "Normalized supplied project information and evaluated "
            "whether PermitPilot has enough project context to proceed."
        ),
        confidence=100,
        projected_impact=(
            "Creates a validated intake baseline before permit research."
        ),
        approval_state=ApprovalState.NOT_REQUIRED,
    )

    decision = HumanDecision(
        decision_id=f"{project.project_id}-jurisdiction-research",
        title="Jurisdiction requirements must be verified",
        recommendation=(
            "Continue to official jurisdiction research before treating any "
            "permit requirement as authoritative."
        ),
        explanation=(
            "Project intake is complete, but permit requirements require "
            "verified jurisdiction evidence."
        ),
        confidence=100,
        projected_impact=(
            "Prevents unverified assumptions from entering the permit workflow."
        ),
        evidence=inspection["observations"],
        approval_state=ApprovalState.PENDING,
    )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.DECISION_REQUIRED,
        summary=(
            "Project intake completed. Verified jurisdiction evidence "
            "is required before permit requirements can be evaluated."
        ),
        actions=[action],
        decision=decision,
        next_action="Research official jurisdiction permit requirements.",
    )


def create_jurisdiction_workflow_result(
    project: ProjectInput,
) -> WorkflowResult:
    """Create a governed workflow result including jurisdiction evidence."""

    inspection = inspect_project_deterministically(project)
    research = research_jurisdiction_deterministically(project)

    intake_action = AgentAction(
        action="inspect_project",
        explanation="Validated project intake information.",
        confidence=100,
        projected_impact="Provides structured project context.",
    )

    research_action = AgentAction(
        action="research_jurisdiction",
        explanation=(
            "Collected structured jurisdiction evidence from the "
            "official-source-backed competition fixture."
        ),
        confidence=100 if research["verified"] else 60,
        projected_impact=(
            "Reduces the risk of relying on invented or unsupported "
            "permit requirements."
        ),
    )

    status_map = {
        "verified_fixture": EvidenceStatus.VERIFIED,
        "unverified": EvidenceStatus.UNVERIFIED,
        "needs_human_review": EvidenceStatus.NEEDS_HUMAN_REVIEW,
    }

    evidence = JurisdictionEvidence(
        jurisdiction=research.get("jurisdiction"),
        authority=research.get("authority"),
        status=status_map[research["status"]],
        verified=research["verified"],
        sources=research["sources"],
        observations=research["observations"],
    )

    if not research["verified"]:
        decision = HumanDecision(
            decision_id=f"{project.project_id}-jurisdiction-evidence",
            title="Jurisdiction evidence requires review",
            recommendation=(
                "Do not continue permit requirement analysis until "
                "official jurisdiction evidence is available."
            ),
            explanation=(
                "PermitPilot could not verify authoritative source evidence "
                "for the supplied jurisdiction."
            ),
            confidence=100,
            projected_impact=(
                "Prevents unsupported permit guidance from being treated "
                "as authoritative."
            ),
            evidence=research["observations"],
            approval_state=ApprovalState.PENDING,
        )

        return WorkflowResult(
            project_id=project.project_id,
            status=WorkflowStatus.DECISION_REQUIRED,
            summary="Jurisdiction evidence could not be verified.",
            actions=[intake_action, research_action],
            jurisdiction_evidence=evidence,
            decision=decision,
            next_action="Obtain verified official jurisdiction evidence.",
        )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.EVIDENCE_READY,
        summary=(
            "Project intake and jurisdiction evidence are available. "
            "Permit-specific applicability analysis can proceed."
        ),
        actions=[intake_action, research_action],
        jurisdiction_evidence=evidence,
        decision=None,
        next_action=(
            "Determine which verified requirements apply to this project."
        ),
    )


def invoke_agent(project: ProjectInput):
    """Invoke the real Strands PermitPilot agent against a project."""

    agent = build_permitpilot_agent()

    prompt = f"""
Process this PermitPilot project.

Project ID: {project.project_id}
Project name: {project.name}
Address: {project.address}
Supplied jurisdiction: {project.jurisdiction or "Unknown"}
Project type: {project.project_type}
Goal: {project.goal}

Use inspect_project first.
Then use research_jurisdiction.

Do not invent jurisdiction-specific permit requirements.
Distinguish verified evidence from assumptions.
Explain the safest next operational step.
""".strip()

    return agent(prompt)
