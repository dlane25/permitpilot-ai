from __future__ import annotations

from .agent import build_permitpilot_agent
from .models import (
    AgentAction,
    ApprovalState,
    HumanDecision,
    ProjectInput,
    WorkflowResult,
    WorkflowStatus,
)
from .tools import inspect_project


def inspect_project_deterministically(project: ProjectInput) -> dict:
    """Run the project-intake tool without invoking a language model."""

    return inspect_project(
        project_id=project.project_id,
        name=project.name,
        address=project.address,
        project_type=project.project_type,
        goal=project.goal,
        jurisdiction=project.jurisdiction or "",
    )


def create_initial_workflow_result(project: ProjectInput) -> WorkflowResult:
    """Create PermitPilot's initial governed workflow result."""

    inspection = inspect_project_deterministically(project)

    action = AgentAction(
        action="inspect_project",
        explanation=(
            "Normalized the supplied project information and evaluated "
            "whether PermitPilot has enough verified information to proceed."
        ),
        confidence=100,
        projected_impact=(
            "Creates a validated project-intake baseline before permit research."
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
            "PermitPilot has project intake data, but Milestone 2 does not yet "
            "include live official-source jurisdiction research."
        ),
        confidence=100,
        projected_impact=(
            "Prevents unverified permit assumptions from entering the "
            "submission workflow."
        ),
        evidence=inspection["observations"],
        approval_state=ApprovalState.PENDING,
    )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.DECISION_REQUIRED,
        summary=(
            "Project intake completed. PermitPilot requires verified "
            "jurisdiction research before proceeding with permit requirements."
        ),
        actions=[action],
        decision=decision,
        next_action="Research official jurisdiction permit requirements.",
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

Use the project inspection tool first.

Do not invent jurisdiction-specific permit requirements.
Explain the safest next operational step.
""".strip()

    return agent(prompt)
