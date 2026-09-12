from __future__ import annotations

from datetime import datetime, timezone

from strands import tool


@tool
def prepare_submission_package(
    project: dict,
    documents: list[dict],
    readiness: dict,
    evidence_sources: list[dict],
    conditional_items: list[dict],
    audit_summary: list[str],
) -> dict:
    """Prepare a deterministic permit submission package manifest."""

    included_documents = [
        {
            "document_id": item.get("document_id"),
            "name": item.get("name"),
            "document_type": item.get("document_type"),
            "status": item.get("status"),
        }
        for item in documents
        if item.get("present") is True
    ]

    unresolved_conditions = [
        {
            "requirement": item.get("requirement"),
            "status": item.get("status"),
            "reason": item.get("reason"),
        }
        for item in conditional_items
    ]

    sources = [
        {
            "source_name": item.get("source_name"),
            "source_url": item.get("source_url"),
            "source_type": item.get("source_type"),
        }
        for item in evidence_sources
    ]

    package_status = (
        "prepared"
        if readiness.get("ready_for_submission") is True
        else "blocked"
    )

    return {
        "package_id": f"{project['project_id']}-submission-package",
        "project_id": project["project_id"],
        "project_name": project["name"],
        "jurisdiction": project.get("jurisdiction"),
        "project_type": project["project_type"],
        "goal": project["goal"],
        "package_status": package_status,
        "readiness_score": readiness.get("readiness_score", 0),
        "ready_for_submission": readiness.get(
            "ready_for_submission",
            False,
        ),
        "included_documents": included_documents,
        "included_document_count": len(included_documents),
        "unresolved_conditions": unresolved_conditions,
        "unresolved_condition_count": len(unresolved_conditions),
        "evidence_sources": sources,
        "evidence_source_count": len(sources),
        "audit_summary": audit_summary,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "PermitPilot package readiness is an internal workflow "
            "assessment and is not an official jurisdiction approval."
        ),
    }
