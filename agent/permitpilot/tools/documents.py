from __future__ import annotations

from strands import tool


@tool
def analyze_document_compliance(
    requirements: list[dict],
    documents: list[dict],
) -> dict:
    """Evaluate project documents against classified permit requirements."""

    results: list[dict] = []

    normalized_docs = {
        doc["document_type"]: doc
        for doc in documents
    }

    for item in requirements:
        requirement = item["requirement"]
        classification = item["classification"]
        normalized = requirement.lower()

        if classification == "not_applicable":
            continue

        if (
            "submitted electronically" in normalized
            or "projectdox" in normalized
        ):
            results.append(
                {
                    "requirement": requirement,
                    "status": "satisfied",
                    "document_type": None,
                    "document_name": None,
                    "confidence": 95,
                    "rationale": (
                        "This requirement concerns the verified submission "
                        "channel rather than presence of a specific document."
                    ),
                    "remediation": None,
                }
            )
            continue

        if (
            classification == "conditional"
            and (
                "site development review may involve" in normalized
                or (
                    "architectural" in normalized
                    and "structural" in normalized
                    and "depending on project scope" in normalized
                )
            )
        ):
            results.append(
                {
                    "requirement": requirement,
                    "status": "conditional",
                    "document_type": None,
                    "document_name": None,
                    "confidence": 90,
                    "rationale": (
                        "The supporting disciplines depend on project scope "
                        "and cannot yet be treated as universally required."
                    ),
                    "remediation": (
                        "Confirm project scope and determine which discipline "
                        "drawings are required."
                    ),
                }
            )
            continue

        if (
            "building permit application" in normalized
            and "complete set of plans" in normalized
        ):
            application = normalized_docs.get("building_permit_application")
            plans = normalized_docs.get("architectural_plans")

            application_ready = bool(
                application
                and application.get("present")
                and application.get("status") == "complete"
            )

            plans_ready = bool(
                plans
                and plans.get("present")
                and plans.get("status") == "complete"
            )

            if application_ready and plans_ready:
                status = "satisfied"
                confidence = 100
                rationale = (
                    "The project package contains both the building permit "
                    "application and a complete architectural plan set."
                )
                remediation = None
            elif application_ready or plans_ready:
                status = "partial"
                confidence = 100
                rationale = (
                    "Only part of the required application-and-plan package "
                    "is complete."
                )
                remediation = (
                    "Complete the missing application or plan component."
                )
            else:
                status = "missing"
                confidence = 100
                rationale = (
                    "The required building application and plan package "
                    "is not present."
                )
                remediation = (
                    "Add the building permit application and complete plans."
                )

            results.append(
                {
                    "requirement": requirement,
                    "status": status,
                    "document_type": "application_and_plans",
                    "document_name": (
                        "Building Permit Application + Architectural Plan Set"
                    ),
                    "confidence": confidence,
                    "rationale": rationale,
                    "remediation": remediation,
                }
            )
            continue

        required_document_type = None

        if "building permit is required" in normalized:
            required_document_type = "building_permit_application"
        elif "new single family prerequisite checklist" in normalized:
            required_document_type = "prerequisite_checklist"
        elif "deed restrictions declaration" in normalized:
            required_document_type = "deed_restrictions_declaration"
        elif "wastewater capacity reservation" in normalized:
            required_document_type = "wastewater_capacity_letter"
        elif normalized.startswith("electrical"):
            required_document_type = "electrical_plans"
        elif normalized.startswith("plumbing"):
            required_document_type = "plumbing_plans"
        elif normalized.startswith("mechanical"):
            required_document_type = "mechanical_plans"

        if required_document_type is None:
            results.append(
                {
                    "requirement": requirement,
                    "status": (
                        "conditional"
                        if classification == "conditional"
                        else "needs_human_review"
                    ),
                    "document_type": None,
                    "document_name": None,
                    "confidence": 70,
                    "rationale": (
                        "No deterministic document mapping exists for "
                        "this requirement."
                    ),
                    "remediation": (
                        "Review project scope and determine the supporting "
                        "document required."
                    ),
                }
            )
            continue

        document = normalized_docs.get(required_document_type)

        if document is None or not document.get("present"):
            status = "missing"
            confidence = 100
            document_name = document.get("name") if document else None
            rationale = (
                "The required supporting document is not present "
                "in the project package."
            )
            remediation = (
                "Obtain and add the required document before permit submission."
            )

        elif document.get("status") == "partial":
            status = "partial"
            confidence = 95
            document_name = document.get("name")
            rationale = (
                "The supporting document exists but is marked incomplete."
            )
            remediation = (
                "Complete and validate the document before submission."
            )

        else:
            status = "satisfied"
            confidence = 100
            document_name = document.get("name")
            rationale = (
                "The project package contains the required supporting document."
            )
            remediation = None

        results.append(
            {
                "requirement": requirement,
                "status": status,
                "document_type": required_document_type,
                "document_name": document_name,
                "confidence": confidence,
                "rationale": rationale,
                "remediation": remediation,
            }
        )

    return {
        "results": results,
        "total_checks": len(results),
        "satisfied_count": sum(
            item["status"] == "satisfied"
            for item in results
        ),
        "missing_count": sum(
            item["status"] == "missing"
            for item in results
        ),
        "partial_count": sum(
            item["status"] == "partial"
            for item in results
        ),
        "conditional_count": sum(
            item["status"] == "conditional"
            for item in results
        ),
        "needs_human_review_count": sum(
            item["status"] == "needs_human_review"
            for item in results
        ),
    }
