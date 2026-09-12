from __future__ import annotations

from strands import tool


@tool
def calculate_submission_readiness(
    compliance_results: list[dict],
) -> dict:
    """Calculate deterministic permit submission readiness.

    Args:
        compliance_results: Document compliance results from the governed
            compliance workflow.
    """

    blocking_statuses = {
        "missing",
        "partial",
        "needs_human_review",
    }

    blocking_items = []
    non_blocking_items = []
    remediation_actions = []

    weighted_points = 0.0
    total_weight = 0.0

    for index, item in enumerate(compliance_results, start=1):
        status = item["status"]
        requirement = item["requirement"]

        weight = 1.0
        total_weight += weight

        if status == "satisfied":
            weighted_points += weight

        elif status == "conditional":
            weighted_points += 0.5 * weight
            non_blocking_items.append(
                {
                    "requirement": requirement,
                    "status": status,
                    "reason": (
                        "Requirement remains scope-dependent and should be "
                        "validated before final submission."
                    ),
                }
            )

        elif status in blocking_statuses:
            blocking_items.append(
                {
                    "requirement": requirement,
                    "status": status,
                    "remediation": item.get("remediation"),
                }
            )

            remediation_actions.append(
                {
                    "priority": len(remediation_actions) + 1,
                    "requirement": requirement,
                    "status": status,
                    "action": (
                        item.get("remediation")
                        or "Resolve this compliance item before submission."
                    ),
                }
            )

    readiness_score = (
        round((weighted_points / total_weight) * 100)
        if total_weight
        else 0
    )

    missing_count = sum(
        item["status"] == "missing"
        for item in compliance_results
    )

    partial_count = sum(
        item["status"] == "partial"
        for item in compliance_results
    )

    review_count = sum(
        item["status"] == "needs_human_review"
        for item in compliance_results
    )

    estimated_admin_effort_hours = round(
        (missing_count * 1.5)
        + (partial_count * 1.0)
        + (review_count * 0.75),
        1,
    )

    estimated_delay_risk_days = (
        missing_count * 2
        + partial_count
        + review_count
    )

    ready_for_submission = len(blocking_items) == 0

    return {
        "readiness_score": readiness_score,
        "ready_for_submission": ready_for_submission,
        "blocking_items": blocking_items,
        "non_blocking_items": non_blocking_items,
        "remediation_actions": remediation_actions,
        "blocking_count": len(blocking_items),
        "non_blocking_count": len(non_blocking_items),
        "estimated_admin_effort_hours": estimated_admin_effort_hours,
        "estimated_delay_risk_days": estimated_delay_risk_days,
    }
