from __future__ import annotations

import json

from permitpilot.models import ProjectInput
from permitpilot.workflow import create_initial_workflow_result


def main() -> None:
    project = ProjectInput(
        project_id="PP-OR-001",
        name="Oak Ridge Residence",
        address="1842 Oak Ridge Drive, Houston, TX",
        jurisdiction="Houston, Texas",
        project_type="New single-family residence",
        goal=(
            "Prepare this residential construction project "
            "for permit submission."
        ),
    )

    result = create_initial_workflow_result(project)

    print("PermitPilot Milestone 2 Runtime")
    print("=" * 40)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
