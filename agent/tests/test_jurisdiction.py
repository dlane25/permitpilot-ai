from __future__ import annotations

import unittest

from permitpilot.models import (
    EvidenceStatus,
    ProjectInput,
    WorkflowStatus,
)
from permitpilot.tools import research_jurisdiction
from permitpilot.workflow import create_jurisdiction_workflow_result


class JurisdictionIntelligenceTests(unittest.TestCase):
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

    def test_houston_fixture_is_verified(self) -> None:
        result = research_jurisdiction("Houston, Texas")

        self.assertTrue(result["verified"])
        self.assertEqual(result["authority"], "City of Houston")
        self.assertGreaterEqual(len(result["sources"]), 3)

    def test_unknown_jurisdiction_is_not_verified(self) -> None:
        result = research_jurisdiction("Example City")

        self.assertFalse(result["verified"])
        self.assertEqual(result["status"], "unverified")

    def test_missing_jurisdiction_requires_review(self) -> None:
        result = research_jurisdiction("")

        self.assertFalse(result["verified"])
        self.assertEqual(result["status"], "needs_human_review")

    def test_verified_workflow_advances_to_evidence_ready(self) -> None:
        result = create_jurisdiction_workflow_result(self.project)

        self.assertEqual(
            result.status,
            WorkflowStatus.EVIDENCE_READY,
        )

        self.assertIsNotNone(result.jurisdiction_evidence)
        self.assertEqual(
            result.jurisdiction_evidence.status,
            EvidenceStatus.VERIFIED,
        )
        self.assertIsNone(result.decision)

    def test_unknown_jurisdiction_stops_for_human_review(self) -> None:
        project = self.project.model_copy(
            update={"jurisdiction": "Example City"}
        )

        result = create_jurisdiction_workflow_result(project)

        self.assertEqual(
            result.status,
            WorkflowStatus.DECISION_REQUIRED,
        )
        self.assertIsNotNone(result.decision)


if __name__ == "__main__":
    unittest.main()
