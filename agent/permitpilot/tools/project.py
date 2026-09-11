from __future__ import annotations

from strands import tool


@tool
def inspect_project(
    project_id: str,
    name: str,
    address: str,
    project_type: str,
    goal: str,
    jurisdiction: str = "",
) -> dict:
    """Inspect supplied construction project information.

    This tool performs deterministic project intake only.
    It does not research or validate jurisdiction-specific permit requirements.

    Args:
        project_id: Unique PermitPilot project identifier.
        name: Human-readable project name.
        address: Project street address.
        project_type: Construction project classification.
        goal: Operational goal PermitPilot should work toward.
        jurisdiction: Supplied jurisdiction, if known.
    """

    required_fields = {
        "project_id": project_id,
        "name": name,
        "address": address,
        "project_type": project_type,
        "goal": goal,
    }

    missing = [
        field_name
        for field_name, value in required_fields.items()
        if not value or not value.strip()
    ]

    completeness_score = round(
        ((len(required_fields) - len(missing)) / len(required_fields)) * 100
    )

    observations: list[str] = []

    if jurisdiction.strip():
        observations.append(
            f"Supplied jurisdiction is {jurisdiction.strip()}, but it has not "
            "yet been independently verified."
        )
    else:
        observations.append(
            "No jurisdiction was supplied; jurisdiction research is required."
        )

    if missing:
        observations.append(
            f"Missing required intake fields: {', '.join(missing)}."
        )
    else:
        observations.append("Project intake is structurally complete.")

    observations.append(
        "Jurisdiction-specific permit requirements have not yet been researched."
    )

    return {
        "project_id": project_id,
        "project_name": name,
        "project_type": project_type,
        "address": address,
        "jurisdiction": jurisdiction.strip() or None,
        "goal": goal,
        "completeness_score": completeness_score,
        "observations": observations,
    }
