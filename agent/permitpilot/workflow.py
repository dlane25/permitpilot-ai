from __future__ import annotations

import json
from pathlib import Path

from .agent import build_permitpilot_agent
from .models import (
    AgentAction,
    ApplicabilityAnalysis,
    DocumentComplianceAnalysis,
    SubmissionReadinessAnalysis,
    RemediationExecutionAnalysis,
    ApprovalState,
    EvidenceStatus,
    HumanDecision,
    JurisdictionEvidence,
    ProjectInput,
    WorkflowResult,
    WorkflowStatus,
)
from .tools import (
    apply_approved_remediation,
    analyze_document_compliance,
    calculate_submission_readiness,
    analyze_permit_applicability,
    inspect_project,
    research_jurisdiction,
)


def inspect_project_deterministically(project: ProjectInput) -> dict:
    return inspect_project(
        project_id=project.project_id,
        name=project.name,
        address=project.address,
        project_type=project.project_type,
        goal=project.goal,
        jurisdiction=project.jurisdiction or "",
    )


def research_jurisdiction_deterministically(project: ProjectInput) -> dict:
    return research_jurisdiction(project.jurisdiction or "")


def create_initial_workflow_result(project: ProjectInput) -> WorkflowResult:
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


def create_applicability_workflow_result(
    project: ProjectInput,
) -> WorkflowResult:
    jurisdiction_result = create_jurisdiction_workflow_result(project)

    if (
        jurisdiction_result.status
        != WorkflowStatus.EVIDENCE_READY
        or jurisdiction_result.jurisdiction_evidence is None
    ):
        return jurisdiction_result

    evidence = jurisdiction_result.jurisdiction_evidence

    requirements: list[str] = []
    source_map: dict[str, tuple[str, str]] = {}

    for source in evidence.sources:
        for requirement in source.requirements:
            requirements.append(requirement)
            source_map[requirement] = (
                source.source_name,
                source.source_url,
            )

    raw_analysis = analyze_permit_applicability(
        project_type=project.project_type,
        jurisdiction=evidence.jurisdiction or "",
        requirements=requirements,
    )

    enriched = []

    for item in raw_analysis["determinations"]:
        source_name, source_url = source_map.get(
            item["requirement"],
            (None, None),
        )

        enriched.append(
            {
                **item,
                "source_name": source_name,
                "source_url": source_url,
            }
        )

    analysis = ApplicabilityAnalysis(
        project_type=raw_analysis["project_type"],
        jurisdiction=raw_analysis["jurisdiction"],
        determinations=enriched,
        total_requirements=raw_analysis["total_requirements"],
        applicable_count=raw_analysis["applicable_count"],
        conditional_count=raw_analysis["conditional_count"],
        not_applicable_count=raw_analysis["not_applicable_count"],
        needs_human_review_count=raw_analysis[
            "needs_human_review_count"
        ],
    )

    actions = list(jurisdiction_result.actions)
    actions.append(
        AgentAction(
            action="analyze_permit_applicability",
            explanation=(
                "Classified verified jurisdiction requirements against "
                "the supplied project type."
            ),
            confidence=95,
            projected_impact=(
                "Converts verified source evidence into an actionable "
                "permit-readiness decision set."
            ),
        )
    )

    if analysis.needs_human_review_count > 0:
        ambiguous = [
            item.requirement
            for item in analysis.determinations
            if item.classification.value == "needs_human_review"
        ]

        decision = HumanDecision(
            decision_id=f"{project.project_id}-applicability-review",
            title="Permit applicability requires human review",
            recommendation=(
                "Review ambiguous requirements before advancing the "
                "submission package."
            ),
            explanation=(
                "One or more verified requirements could not be safely "
                "classified from the currently available project facts."
            ),
            confidence=100,
            projected_impact=(
                "Prevents ambiguous source language from becoming an "
                "unsupported permit obligation."
            ),
            evidence=ambiguous,
            approval_state=ApprovalState.PENDING,
        )

        return WorkflowResult(
            project_id=project.project_id,
            status=WorkflowStatus.DECISION_REQUIRED,
            summary=(
                "Permit applicability analysis completed with items "
                "requiring human review."
            ),
            actions=actions,
            jurisdiction_evidence=evidence,
            applicability_analysis=analysis,
            decision=decision,
            next_action="Resolve ambiguous applicability determinations.",
        )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.APPLICABILITY_READY,
        summary=(
            "Verified jurisdiction requirements have been classified "
            "for project applicability."
        ),
        actions=actions,
        jurisdiction_evidence=evidence,
        applicability_analysis=analysis,
        decision=None,
        next_action=(
            "Analyze project documents against applicable and "
            "conditional requirements."
        ),
    )



def create_document_compliance_workflow_result(
    project: ProjectInput,
) -> WorkflowResult:
    """Evaluate the Oak Ridge document package against applicable requirements."""

    applicability_result = create_applicability_workflow_result(project)

    if (
        applicability_result.status
        != WorkflowStatus.APPLICABILITY_READY
        or applicability_result.applicability_analysis is None
        or applicability_result.jurisdiction_evidence is None
    ):
        return applicability_result

    applicability = applicability_result.applicability_analysis
    evidence = applicability_result.jurisdiction_evidence

    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "oak-ridge"
        / "document-inventory.json"
    )

    document_fixture = json.loads(
        fixture_path.read_text(encoding="utf-8-sig")
    )

    requirements = [
        {
            "requirement": item.requirement,
            "classification": item.classification.value,
        }
        for item in applicability.determinations
    ]

    raw_compliance = analyze_document_compliance(
        requirements=requirements,
        documents=document_fixture["documents"],
    )

    source_map = {
        item.requirement: (
            item.source_name,
            item.source_url,
        )
        for item in applicability.determinations
    }

    enriched_results = []

    for item in raw_compliance["results"]:
        source_name, source_url = source_map.get(
            item["requirement"],
            (None, None),
        )

        enriched_results.append(
            {
                **item,
                "source_name": source_name,
                "source_url": source_url,
            }
        )

    compliance = DocumentComplianceAnalysis(
        results=enriched_results,
        total_checks=raw_compliance["total_checks"],
        satisfied_count=raw_compliance["satisfied_count"],
        missing_count=raw_compliance["missing_count"],
        partial_count=raw_compliance["partial_count"],
        conditional_count=raw_compliance["conditional_count"],
        needs_human_review_count=raw_compliance[
            "needs_human_review_count"
        ],
    )

    actions = list(applicability_result.actions)
    actions.append(
        AgentAction(
            action="analyze_document_compliance",
            explanation=(
                "Compared applicable and conditional permit requirements "
                "against the Oak Ridge document inventory."
            ),
            confidence=98,
            projected_impact=(
                "Identifies missing or incomplete permit documents before "
                "submission."
            ),
        )
    )

    blocking_items = [
        item
        for item in compliance.results
        if item.status.value in {
            "missing",
            "partial",
            "needs_human_review",
        }
    ]

    if blocking_items:
        evidence_items = [
            (
                f"{item.requirement} -> {item.status.value}"
                + (
                    f": {item.remediation}"
                    if item.remediation
                    else ""
                )
            )
            for item in blocking_items
        ]

        decision = HumanDecision(
            decision_id=f"{project.project_id}-document-compliance",
            title="Permit package requires remediation",
            recommendation=(
                "Resolve missing and incomplete project documents before "
                "advancing to submission readiness."
            ),
            explanation=(
                "PermitPilot identified one or more documentation gaps "
                "against verified applicable requirements."
            ),
            confidence=100,
            projected_impact=(
                "Reduces the risk of permit rejection, resubmission, and "
                "avoidable review delays."
            ),
            evidence=evidence_items,
            approval_state=ApprovalState.PENDING,
        )

        return WorkflowResult(
            project_id=project.project_id,
            status=WorkflowStatus.DECISION_REQUIRED,
            summary=(
                "Document compliance analysis found blocking package gaps."
            ),
            actions=actions,
            jurisdiction_evidence=evidence,
            applicability_analysis=applicability,
            document_compliance=compliance,
            decision=decision,
            next_action=(
                "Resolve missing and incomplete permit documents."
            ),
        )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.COMPLIANCE_READY,
        summary=(
            "Applicable permit requirements have supporting project "
            "documentation."
        ),
        actions=actions,
        jurisdiction_evidence=evidence,
        applicability_analysis=applicability,
        document_compliance=compliance,
        decision=None,
        next_action="Prepare the permit submission package.",
    )



def create_submission_readiness_workflow_result(
    project: ProjectInput,
) -> WorkflowResult:
    """Calculate permit submission readiness from compliance results."""

    compliance_result = create_document_compliance_workflow_result(project)

    if (
        compliance_result.document_compliance is None
        or compliance_result.jurisdiction_evidence is None
        or compliance_result.applicability_analysis is None
    ):
        return compliance_result

    compliance = compliance_result.document_compliance

    raw_readiness = calculate_submission_readiness(
        compliance_results=[
            {
                "requirement": item.requirement,
                "status": item.status.value,
                "remediation": item.remediation,
            }
            for item in compliance.results
        ]
    )

    readiness = SubmissionReadinessAnalysis(**raw_readiness)

    actions = list(compliance_result.actions)
    actions.append(
        AgentAction(
            action="calculate_submission_readiness",
            explanation=(
                "Calculated submission readiness, blocking gaps, "
                "remediation priority, and estimated delay risk."
            ),
            confidence=100,
            projected_impact=(
                "Provides a quantified go/no-go decision before permit "
                "submission."
            ),
        )
    )

    if not readiness.ready_for_submission:
        evidence_items = [
            (
                f"Priority {item.priority}: "
                f"{item.requirement} -> {item.action}"
            )
            for item in readiness.remediation_actions
        ]

        decision = HumanDecision(
            decision_id=f"{project.project_id}-submission-readiness",
            title="Permit package is not ready for submission",
            recommendation=(
                "Complete blocking remediation actions before authorizing "
                "permit submission."
            ),
            explanation=(
                f"PermitPilot calculated a readiness score of "
                f"{readiness.readiness_score}/100 with "
                f"{readiness.blocking_count} blocking item(s)."
            ),
            confidence=100,
            projected_impact=(
                f"Resolving the identified blockers may avoid approximately "
                f"{readiness.estimated_delay_risk_days} days of preventable "
                f"review delay."
            ),
            evidence=evidence_items,
            approval_state=ApprovalState.PENDING,
        )

        return WorkflowResult(
            project_id=project.project_id,
            status=WorkflowStatus.READINESS_REVIEW,
            summary=(
                "PermitPilot completed submission-readiness analysis and "
                "identified blocking remediation actions."
            ),
            actions=actions,
            jurisdiction_evidence=compliance_result.jurisdiction_evidence,
            applicability_analysis=compliance_result.applicability_analysis,
            document_compliance=compliance,
            submission_readiness=readiness,
            decision=decision,
            next_action="Complete prioritized remediation actions.",
        )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.READY_FOR_SUBMISSION,
        summary=(
            "PermitPilot found no blocking compliance gaps. "
            "The package is ready for human submission approval."
        ),
        actions=actions,
        jurisdiction_evidence=compliance_result.jurisdiction_evidence,
        applicability_analysis=compliance_result.applicability_analysis,
        document_compliance=compliance,
        submission_readiness=readiness,
        decision=HumanDecision(
            decision_id=f"{project.project_id}-submission-approval",
            title="Approve permit submission",
            recommendation=(
                "Approve the prepared permit package for submission."
            ),
            explanation=(
                "No blocking document-compliance gaps remain."
            ),
            confidence=100,
            projected_impact=(
                "Advances the project to submission while preserving "
                "human control over the consequential external action."
            ),
            evidence=[
                f"Readiness score: {readiness.readiness_score}/100",
                "Blocking items: 0",
            ],
            approval_state=ApprovalState.PENDING,
        ),
        next_action="Request human approval to submit permit package.",
    )



def create_remediation_execution_workflow_result(
    project: ProjectInput,
    approved_updates: list[dict],
) -> WorkflowResult:
    """Apply approved remediation and recalculate submission readiness."""

    applicability_result = create_applicability_workflow_result(project)

    if (
        applicability_result.status
        != WorkflowStatus.APPLICABILITY_READY
        or applicability_result.applicability_analysis is None
        or applicability_result.jurisdiction_evidence is None
    ):
        return applicability_result

    applicability = applicability_result.applicability_analysis
    evidence = applicability_result.jurisdiction_evidence

    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "oak-ridge"
        / "document-inventory.json"
    )

    document_fixture = json.loads(
        fixture_path.read_text(encoding="utf-8-sig")
    )

    execution = apply_approved_remediation(
        documents=document_fixture["documents"],
        approved_updates=approved_updates,
    )

    requirements = [
        {
            "requirement": item.requirement,
            "classification": item.classification.value,
        }
        for item in applicability.determinations
    ]

    raw_compliance = analyze_document_compliance(
        requirements=requirements,
        documents=execution["documents"],
    )

    source_map = {
        item.requirement: (
            item.source_name,
            item.source_url,
        )
        for item in applicability.determinations
    }

    enriched_results = []

    for item in raw_compliance["results"]:
        source_name, source_url = source_map.get(
            item["requirement"],
            (None, None),
        )

        enriched_results.append(
            {
                **item,
                "source_name": source_name,
                "source_url": source_url,
            }
        )

    compliance = DocumentComplianceAnalysis(
        results=enriched_results,
        total_checks=raw_compliance["total_checks"],
        satisfied_count=raw_compliance["satisfied_count"],
        missing_count=raw_compliance["missing_count"],
        partial_count=raw_compliance["partial_count"],
        conditional_count=raw_compliance["conditional_count"],
        needs_human_review_count=raw_compliance[
            "needs_human_review_count"
        ],
    )

    raw_readiness = calculate_submission_readiness(
        compliance_results=[
            {
                "requirement": item.requirement,
                "status": item.status.value,
                "remediation": item.remediation,
            }
            for item in compliance.results
        ]
    )

    readiness = SubmissionReadinessAnalysis(**raw_readiness)

    audit_events = []

    for item in execution["applied_updates"]:
        audit_events.append(
            {
                "document_type": item["document_type"],
                "document_name": item.get("document_name"),
                "approved": True,
                "previous_present": item["previous_state"].get("present"),
                "previous_status": item["previous_state"].get("status"),
                "new_present": item["new_state"].get("present"),
                "new_status": item["new_state"].get("status"),
                "outcome": "applied",
            }
        )

    for item in execution["rejected_updates"]:
        audit_events.append(
            {
                "document_type": item.get("document_type") or "unknown",
                "document_name": None,
                "approved": False,
                "outcome": "rejected",
                "reason": item.get("reason"),
            }
        )

    remediation_execution = RemediationExecutionAnalysis(
        applied_count=execution["applied_count"],
        rejected_count=execution["rejected_count"],
        audit_events=audit_events,
    )

    actions = list(applicability_result.actions)

    actions.append(
        AgentAction(
            action="apply_approved_remediation",
            explanation=(
                "Applied only human-approved project document updates and "
                "recorded the before-and-after execution state."
            ),
            confidence=100,
            projected_impact=(
                "Closes approved permit-package gaps while preserving "
                "human control and an auditable execution trail."
            ),
            approval_state=ApprovalState.APPROVED,
        )
    )

    actions.append(
        AgentAction(
            action="recalculate_submission_readiness",
            explanation=(
                "Re-ran document compliance and submission readiness "
                "after approved remediation."
            ),
            confidence=100,
            projected_impact=(
                "Provides a current go/no-go submission decision after "
                "execution."
            ),
        )
    )

    if not readiness.ready_for_submission:
        decision = HumanDecision(
            decision_id=f"{project.project_id}-remaining-remediation",
            title="Additional remediation remains",
            recommendation=(
                "Resolve the remaining blocking items before permit submission."
            ),
            explanation=(
                f"Approved remediation was executed, but "
                f"{readiness.blocking_count} blocking item(s) remain."
            ),
            confidence=100,
            projected_impact=(
                "Prevents submission while unresolved blocking compliance "
                "gaps remain."
            ),
            evidence=[
                f"{item.requirement} -> {item.status}"
                for item in readiness.blocking_items
            ],
            approval_state=ApprovalState.PENDING,
        )

        return WorkflowResult(
            project_id=project.project_id,
            status=WorkflowStatus.READINESS_REVIEW,
            summary=(
                "Approved remediation executed, but the package still "
                "contains blocking items."
            ),
            actions=actions,
            jurisdiction_evidence=evidence,
            applicability_analysis=applicability,
            document_compliance=compliance,
            submission_readiness=readiness,
            remediation_execution=remediation_execution,
            decision=decision,
            next_action="Resolve remaining blocking remediation items.",
        )

    return WorkflowResult(
        project_id=project.project_id,
        status=WorkflowStatus.READY_FOR_SUBMISSION,
        summary=(
            "Approved remediation was executed successfully and no "
            "blocking compliance gaps remain."
        ),
        actions=actions,
        jurisdiction_evidence=evidence,
        applicability_analysis=applicability,
        document_compliance=compliance,
        submission_readiness=readiness,
        remediation_execution=remediation_execution,
        decision=HumanDecision(
            decision_id=f"{project.project_id}-final-submission-approval",
            title="Approve permit submission",
            recommendation=(
                "Approve the remediated permit package for submission."
            ),
            explanation=(
                "PermitPilot executed the approved remediation and found "
                "no remaining blocking compliance gaps."
            ),
            confidence=100,
            projected_impact=(
                "Advances the project to permit submission while preserving "
                "explicit human authorization for the external action."
            ),
            evidence=[
                f"Readiness score: {readiness.readiness_score}/100",
                "Blocking items: 0",
                f"Approved remediation actions: {execution['applied_count']}",
            ],
            approval_state=ApprovalState.PENDING,
        ),
        next_action="Request final human approval to submit permit package.",
    )


def invoke_agent(project: ProjectInput):
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
Then use analyze_permit_applicability only on verified requirements.
Then use analyze_document_compliance against the available project documents.
Then use calculate_submission_readiness to quantify blockers and readiness.
Never use apply_approved_remediation unless the proposed update has explicit human approval.

Do not invent jurisdiction-specific permit requirements.
Distinguish verified evidence from assumptions.
Escalate ambiguous applicability decisions.
Explain the safest next operational step.
""".strip()

    return agent(prompt)
