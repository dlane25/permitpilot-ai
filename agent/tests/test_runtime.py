from __future__ import annotations

import unittest

from permitpilot.agent import build_permitpilot_agent
from permitpilot.models import ProjectInput, WorkflowStatus
from permitpilot.tools import inspect_project
from permitpilot.workflow import create_initial_workflow_result


class PermitPilotRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectInput(
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

    def test_project_tool_normalizes_input(self) -> None:
        result = inspect_project(
            project_id=self.project.project_id,
            name=self.project.name,
            address=self.project.address,
            project_type=self.project.project_type,
            goal=self.project.goal,
            jurisdiction=self.project.jurisdiction or "",
        )

        self.assertEqual(result["project_id"], "PP-OR-001")
        self.assertEqual(result["project_name"], "Oak Ridge Residence")
        self.assertEqual(result["completeness_score"], 100)
        self.assertEqual(result["jurisdiction"], "Houston, Texas")

    def test_project_tool_detects_missing_required_field(self) -> None:
        result = inspect_project(
            project_id="PP-TEST-002",
            name="",
            address="100 Example Street",
            project_type="Residential addition",
            goal="Prepare project for permit review.",
            jurisdiction="",
        )

        self.assertLess(result["completeness_score"], 100)

        observations = " ".join(result["observations"])
        self.assertIn("name", observations)
        self.assertIn("jurisdiction research is required", observations)

    def test_workflow_requires_verified_research(self) -> None:
        result = create_initial_workflow_result(self.project)

        self.assertEqual(
            result.status,
            WorkflowStatus.DECISION_REQUIRED,
        )
        self.assertEqual(len(result.actions), 1)
        self.assertIsNotNone(result.decision)
        self.assertEqual(
            result.next_action,
            "Research official jurisdiction permit requirements.",
        )

    def test_workflow_preserves_audit_information(self) -> None:
        result = create_initial_workflow_result(self.project)

        action = result.actions[0]

        self.assertEqual(action.action, "inspect_project")
        self.assertEqual(action.confidence, 100)
        self.assertIsNotNone(action.timestamp)
        self.assertIsNotNone(action.projected_impact)

    def test_agent_builds(self) -> None:
        agent = build_permitpilot_agent()

        self.assertEqual(agent.name, "PermitPilot")


if __name__ == "__main__":
    unittest.main()
