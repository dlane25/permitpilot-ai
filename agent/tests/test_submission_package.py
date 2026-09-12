from __future__ import annotations

import unittest

from permitpilot.models import ProjectInput, WorkflowStatus
from permitpilot.tools import prepare_submission_package
from permitpilot.workflow import create_submission_package_workflow_result


class SubmissionPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = ProjectInput(
            project_id="PP-OR-001",
            name="Oak Ridge Residence",
            address="1842 Oak Ridge Drive, Houston, TX",
            jurisdiction="Houston, Texas",
            project_type="New single-family residence",
            goal="Prepare this project for permit submission.",
        )

        self.approved_updates = [
            {
                "document_type": "wastewater_capacity_letter",
                "approved": True,
                "present": True,
                "status": "complete",
            },
            {
                "document_type": "prerequisite_checklist",
                "approved": True,
                "present": True,
                "status": "complete",
            },
        ]

    def test_prepared_package_requires_ready_state(self) -> None:
        result = prepare_submission_package(
            project={
                "project_id": "PP-TEST",
                "name": "Test",
                "jurisdiction": "Test",
                "project_type": "Residential",
                "goal": "Test",
            },
            documents=[],
            readiness={
                "readiness_score": 50,
                "ready_for_submission": False,
            },
            evidence_sources=[],
            conditional_items=[],
            audit_summary=[],
        )

        self.assertEqual(result["package_status"], "blocked")

    def test_package_workflow_is_ready_for_submission(self) -> None:
        result = create_submission_package_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertEqual(
            result.status,
            WorkflowStatus.READY_FOR_SUBMISSION,
        )

    def test_submission_package_is_prepared(self) -> None:
        result = create_submission_package_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertIsNotNone(result.submission_package)
        self.assertEqual(
            result.submission_package.package_status,
            "prepared",
        )
        self.assertTrue(
            result.submission_package.ready_for_submission
        )

    def test_package_contains_documents(self) -> None:
        result = create_submission_package_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertGreater(
            result.submission_package.included_document_count,
            0,
        )

    def test_package_preserves_evidence_sources(self) -> None:
        result = create_submission_package_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertGreater(
            result.submission_package.evidence_source_count,
            0,
        )

    def test_final_submission_stays_human_gated(self) -> None:
        result = create_submission_package_workflow_result(
            self.project,
            self.approved_updates,
        )

        self.assertIsNotNone(result.decision)
        self.assertEqual(
            result.decision.approval_state.value,
            "pending",
        )
        self.assertEqual(
            result.next_action,
            "Review and approve or reject final permit submission.",
        )


if __name__ == "__main__":
    unittest.main()
