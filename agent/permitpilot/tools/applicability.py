from __future__ import annotations

from strands import tool


@tool
def analyze_permit_applicability(
    project_type: str,
    jurisdiction: str,
    requirements: list[str],
) -> dict:
    """Classify verified permit requirements for project applicability.

    This deterministic competition-demo tool evaluates only supplied,
    previously verified requirements. It does not invent new requirements.

    Args:
        project_type: Construction project classification.
        jurisdiction: Verified project jurisdiction.
        requirements: Verified jurisdiction requirements to evaluate.
    """

    normalized_project_type = project_type.strip().lower()

    residential_project = any(
        keyword in normalized_project_type
        for keyword in [
            "residential",
            "residence",
            "single-family",
            "single family",
        ]
    )

    new_residential_project = residential_project and any(
        keyword in normalized_project_type
        for keyword in [
            "new",
            "new construction",
        ]
    )

    determinations: list[dict] = []

    for requirement in requirements:
        normalized = requirement.lower()

        if (
            "building permit is required" in normalized
            and residential_project
        ):
            classification = "applicable"
            confidence = 100
            rationale = (
                "The verified requirement explicitly states that a building "
                "permit is required for most residential projects, and the "
                "supplied project is residential."
            )
            projected_impact = (
                "Treating the building permit as applicable prevents the "
                "primary permit package from being omitted."
            )

        elif (
            "submitted electronically" in normalized
            or "projectdox" in normalized
        ):
            classification = "applicable"
            confidence = 95
            rationale = (
                "The verified source identifies electronic submission as part "
                "of the jurisdiction's submission workflow for this project."
            )
            projected_impact = (
                "Identifies the required submission channel before package "
                "preparation and avoids an incorrect delivery workflow."
            )

        elif (
            "required for residential site development review" in normalized
            and residential_project
        ):
            classification = "conditional"
            confidence = 90
            rationale = (
                "The documents are required when residential site development "
                "review applies, but applicability of that review still depends "
                "on project scope and conditions."
            )
            projected_impact = (
                "Preserves the document requirement without incorrectly "
                "assuming that site development review always applies."
            )

        elif any(
            keyword in normalized
            for keyword in [
                "may involve",
                "may be required",
                "depending on project scope",
                "depending on project conditions",
            ]
        ):
            classification = "conditional"
            confidence = 90
            rationale = (
                "The verified source makes applicability dependent on project "
                "scope or conditions that have not yet been fully evaluated."
            )
            projected_impact = (
                "Flags a requirement for scope validation before submission "
                "without prematurely treating it as mandatory."
            )

        elif any(
            keyword in normalized
            for keyword in [
                "new residential applicants should",
                "new construction requires",
                "required before submitting plans",
            ]
        ) and new_residential_project:
            classification = "applicable"
            confidence = 95
            rationale = (
                "The verified requirement applies specifically to new "
                "residential construction, matching the supplied project type."
            )
            projected_impact = (
                "Identifies a likely submission prerequisite early enough "
                "to reduce permit-package rework."
            )

        elif "permit portal supports" in normalized:
            classification = "not_applicable"
            confidence = 100
            rationale = (
                "This statement describes portal capability rather than a "
                "project-specific permit requirement."
            )
            projected_impact = (
                "Prevents operational portal information from being "
                "misclassified as a permit requirement."
            )

        else:
            classification = "needs_human_review"
            confidence = 60
            rationale = (
                "The verified evidence is not specific enough for a safe "
                "deterministic applicability decision."
            )
            projected_impact = (
                "Avoids converting ambiguous source language into an "
                "unsupported compliance requirement."
            )

        determinations.append(
            {
                "requirement": requirement,
                "classification": classification,
                "confidence": confidence,
                "rationale": rationale,
                "projected_impact": projected_impact,
            }
        )

    return {
        "project_type": project_type,
        "jurisdiction": jurisdiction,
        "determinations": determinations,
        "total_requirements": len(determinations),
        "applicable_count": sum(
            item["classification"] == "applicable"
            for item in determinations
        ),
        "conditional_count": sum(
            item["classification"] == "conditional"
            for item in determinations
        ),
        "not_applicable_count": sum(
            item["classification"] == "not_applicable"
            for item in determinations
        ),
        "needs_human_review_count": sum(
            item["classification"] == "needs_human_review"
            for item in determinations
        ),
    }
